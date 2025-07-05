from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime
from fastapi import Query


from config.database import get_db
from utils.response import (
    success_response,
    not_found_response,
    param_error_response,
    internal_error_response,
)
from models.fee import (
    Fee,
    FeeListRequest,
    FeeResponse,
    FeeListResponse,
)
from websocket.manager import send_message_to_type
from models.enums import OrderStatusEnum

router = APIRouter(
    prefix="/driver",
    tags=["司机管理"],
)


class DriverSubmitRequest(BaseModel):
    driver_id: str = Field(..., description="司机ID", example="")
    order_id: str = Field(..., description="订单ID", example="")
    path_id: str = Field(..., description="运单ID", example="")
    highway_fee: int = Field(..., description="高速费（分）")
    parking_fee: int = Field(..., description="停车费（分）")
    carry_fee: int = Field(..., description="搬运费（分）")
    wait_fee: int = Field(..., description="逾时等候费（分）")
    highway_bill_imgs: Optional[str] = Field("", description="高速费图片路径")
    parking_bill_imgs: Optional[str] = Field("", description="停车费图片路径")


class DriverResponse(BaseModel):
    highway_fee: int
    parking_fee: int
    carry_fee: int
    wait_fee: int
    highway_bill_imgs: Optional[str] = ""
    parking_bill_imgs: Optional[str] = ""
    except_highway_fee: int
    except_parking_fee: int
    except_carry_fee: int
    except_wait_fee: int


class DriverConfirmRequest(BaseModel):
    driver_id: str = Field(..., description="司机ID", example="")
    order_id: str = Field(..., description="订单ID", example="")
    path_id: str = Field(..., description="运单ID", example="")


@router.post("", summary="司机提交费用")
async def submit_driver_fee(
    data: DriverSubmitRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        # 校验字段
        if not all(
            [
                data.driver_id,
                data.order_id,
                data.path_id,
                data.highway_fee,
                data.parking_fee,
                data.carry_fee,
                data.wait_fee,
            ]
        ):
            return param_error_response("所有费用字段均不能为空")

        new_fee = Fee(
            fee_id=str(uuid4()),
            path_id=data.path_id,
            order_id=data.order_id,
            highway_fee=data.highway_fee,
            parking_fee=data.parking_fee,
            carry_fee=data.carry_fee,
            wait_fee=data.wait_fee,
            highway_bill_imgs=data.highway_bill_imgs,
            parking_bill_imgs=data.parking_bill_imgs,
            order_time=datetime.utcnow(),
        )

        db.add(new_fee)
        db.commit()
        db.refresh(new_fee)

        # 构建推送消息
        push_message = {
            "type": "fee_submitted",
            "data": {
                "driver_id": data.driver_id,
                "order_id": data.order_id,
                "path_id": data.path_id,
                "highway_fee": data.highway_fee,
                "parking_fee": data.parking_fee,
                "carry_fee": data.carry_fee,
                "wait_fee": data.wait_fee,
                "highway_bill_imgs": data.highway_bill_imgs,
                "parking_bill_imgs": data.parking_bill_imgs,
                "submit_time": datetime.utcnow().isoformat(),
            },
        }

        # 只推送给平台端和客户端，不推送给司机端
        await send_message_to_type("platform", push_message)
        await send_message_to_type("client", push_message)

        response_data = {
            "fee_id": new_fee.fee_id,
            "path_id": new_fee.path_id,
            "order_id": new_fee.order_id,
            "highway_fee": new_fee.highway_fee,
            "parking_fee": new_fee.parking_fee,
            "carry_fee": new_fee.carry_fee,
            "wait_fee": new_fee.wait_fee,
            "highway_bill_imgs": new_fee.highway_bill_imgs,
            "parking_bill_imgs": new_fee.parking_bill_imgs,
            "submit_time": new_fee.created_at.isoformat(),
        }

        return success_response(message="司机提交费用成功", data=response_data)

    except Exception as e:
        db.rollback()
        print(f"司机提交费用错误: {e}")
        return internal_error_response("费用提交失败")


@router.get("", response_model=DriverResponse, summary="司机获取费用")
async def get_fee(
    order_id: str, path_id: str, driver_id: str, db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        fee = db.query(Fee).filter_by(order_id=order_id, path_id=path_id).first()
        if not fee:
            return not_found_response("费用不存在")

        return success_response(
            message="获取费用成功",
            data=DriverResponse(
                highway_fee=fee.highway_fee,
                parking_fee=fee.parking_fee,
                carry_fee=fee.carry_fee,
                wait_fee=fee.wait_fee,
                highway_bill_imgs=fee.highway_bill_imgs,
                parking_bill_imgs=fee.parking_bill_imgs,
                except_highway_fee=fee.highway_fee,
                except_parking_fee=fee.parking_fee,
                except_carry_fee=fee.carry_fee,
                except_wait_fee=fee.wait_fee,
            ),
        )

    except Exception as e:
        print(f"获取费用错误: {e}")
        return internal_error_response("获取费用失败")


@router.post("/confirm", summary="司机确认费用")
async def confirm_fee(
    data: DriverConfirmRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    if not all([data.driver_id, data.order_id, data.path_id]):
        return param_error_response("所有字段均不能为空")

    # 更新费用表，status 为PENDING_PAYMENT
    fee = db.query(Fee).filter_by(order_id=data.order_id, path_id=data.path_id).first()
    if not fee:
        return not_found_response("费用不存在")

    fee.status = OrderStatusEnum.PENDING_PAYMENT
    db.commit()
    db.refresh(fee)

    # 构建确认消息
    confirm_message = {
        "type": "fee_confirmed",
        "data": {
            "driver_id": data.driver_id,
            "order_id": data.order_id,
            "path_id": data.path_id,
            "confirm_time": datetime.utcnow().isoformat(),
        },
    }

    # 推送给平台端和客户端
    await send_message_to_type("platform", confirm_message)
    await send_message_to_type("client", confirm_message)

    return success_response("费用确认成功")


@router.get(
    "/list",
    summary="分页查询费用列表",
    description="分页查询费用信息，根据订单号搜索和状态筛选",
)
async def get_fee_list(
    page: int = Query(1, description="当前页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1),
    status: Optional[str] = Query(None, description="状态（可选）"),
    search: Optional[str] = Query(None, description="订单号搜索关键词（可选）"),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    分页查询费用列表
    """

    try:
        query = select(Fee)

        if status:
            query = query.where(Fee.status == status)

        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.where(Fee.order_id.like(search_term))

        count_query = select(func.count(Fee.fee_id))

        if status:
            count_query = count_query.where(Fee.status == status)
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            count_query = count_query.where(Fee.order_id.like(search_term))

        total = db.exec(count_query).first()

        offset = (page - 1) * size
        total_pages = (total + size - 1) // size

        query = query.offset(offset).limit(size)
        query = query.order_by(Fee.created_at.desc())

        fees = db.exec(query).all()

        fee_items = [
            FeeResponse(
                fee_id=fee.fee_id,
                path_id=fee.path_id,
                order_id=fee.order_id,
                status=fee.status,
                total_price=fee.total_price,
                driver_fee=fee.driver_fee,
                highway_fee=fee.highway_fee,
                parking_fee=fee.parking_fee,
                carry_fee=fee.carry_fee,
                wait_fee=fee.wait_fee,
                order_time=fee.order_time.isoformat() if fee.order_time else "",
                highway_bill_imgs=fee.highway_bill_imgs,
                parking_bill_imgs=fee.parking_bill_imgs,
                company_id=fee.company_id,
                created_at=fee.created_at.isoformat(),
                updated_at=fee.updated_at.isoformat(),
            )
            for fee in fees
        ]

        response_data = FeeListResponse(
            items=fee_items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

        return success_response(
            data=jsonable_encoder(response_data),
            message="获取费用列表成功",
        )

    except Exception as e:
        print(f"获取费用列表错误: {e}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("获取费用列表失败")
