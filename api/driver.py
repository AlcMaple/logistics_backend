from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlmodel import Session, select, func, and_
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
    FeePayRequest,
)
from models.account import Account
from models.driver import Driver
from websocket.manager import send_message_to_type
from models.enums import OrderStatusEnum
from models.order_detail import OrderDetail
from models.driver import Driver

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
    order_id: str, path_id: str, db: Session = Depends(get_db)
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

    # 更新费用表，status SETTLED
    fee = db.query(Fee).filter_by(order_id=data.order_id, path_id=data.path_id).first()
    if not fee:
        return not_found_response("费用不存在")

    fee.status = OrderStatusEnum.SETTLED
    db.add(fee)
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
    description="分页查询费用信息，根据订单号搜索、状态筛选和时间范围查询",
)
async def get_fee_list(
    page: int = Query(1, description="当前页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1),
    status: Optional[str] = Query(None, description="状态（可选）"),
    keyword: Optional[str] = Query(None, description="订单号搜索关键词（可选）"),
    start_time: Optional[str] = Query(None, description="开始时间（格式：YYYY-MM-DD）"),
    end_time: Optional[str] = Query(None, description="结束时间（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    分页查询费用列表
    """
    try:
        query = select(Fee)

        # 状态筛选（前端传"已支付"时，实际查询"已结算"）
        if status:
            if status == "已支付":
                query = query.where(Fee.status == "已结算")
            else:
                query = query.where(Fee.status == status)

        # 订单号搜索
        if keyword and keyword.strip():
            search_term = f"%{keyword.strip()}%"
            query = query.where(Fee.order_id.like(search_term))

        # 时间范围筛选
        if start_time and end_time:
            try:
                start_date = datetime.strptime(start_time, "%Y-%m-%d")
                end_date = datetime.strptime(end_time, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.where(
                    Fee.created_at >= start_date, Fee.created_at <= end_date
                )
            except ValueError:
                return param_error_response("时间格式不正确，请使用YYYY-MM-DD格式")

        # 计算总数（同样应用状态映射逻辑）
        count_query = select(func.count(Fee.fee_id))

        if status:
            if status == "已支付":
                count_query = count_query.where(Fee.status == "已结算")
            else:
                count_query = count_query.where(Fee.status == status)
        if keyword and keyword.strip():
            search_term = f"%{keyword.strip()}%"
            count_query = count_query.where(Fee.order_id.like(search_term))
        if start_time and end_time:
            try:
                start_date = datetime.strptime(start_time, "%Y-%m-%d")
                end_date = datetime.strptime(end_time, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
                count_query = count_query.where(
                    Fee.created_at >= start_date, Fee.created_at <= end_date
                )
            except ValueError:
                pass  # 前面已经处理过错误

        total = db.exec(count_query).first()

        # 分页处理
        offset = (page - 1) * size
        total_pages = (total + size - 1) // size

        query = query.offset(offset).limit(size)
        query = query.order_by(Fee.created_at.desc())

        fees = db.exec(query).all()

        # 构建响应数据（将"已结算"映射为"已支付"返回）
        fee_items = []
        for fee in fees:
            # 状态映射：数据库里的"已结算" → 返回前端的"已支付"
            display_status = "已支付" if fee.status == "已结算" else fee.status

            fee_items.append(
                FeeResponse(
                    fee_id=fee.fee_id,
                    path_id=fee.path_id,
                    order_id=fee.order_id,
                    status=display_status,  # 使用映射后的状态
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
            )

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


@router.patch("/pay", summary="司机支付费用")
async def pay_fee(data: FeePayRequest, db: Session = Depends(get_db)) -> JSONResponse:
    try:
        # 更新费用表
        fee = db.query(Fee).filter_by(fee_id=data.fee_id).first()
        if not fee:
            return not_found_response("费用不存在")

        # 获取客户的账户余额
        account = db.query(Account).filter_by(company_id=fee.company_id).first()
        if not account:
            return not_found_response("账户不存在")

        # 余额不足
        acc_balance = account.company_account_balance
        balance = (
            data.total_price
            + data.carry_fee
            + data.wait_fee
            + data.highway_fee
            + data.parking_fee
        )
        if acc_balance < balance:
            return param_error_response("账户余额不足")

        # 扣除余额
        account.company_account_balance -= balance
        db.add(account)
        db.commit()
        db.refresh(account)

        # 更新费用表
        fee.status = OrderStatusEnum.SETTLED
        fee.updated_at = datetime.utcnow()

        # 司机增加费用
        driver = (
            db.query(Driver).filter_by(driver_account_id=fee.driver_account_id).first()
        )
        if not driver:
            return not_found_response("司机不存在")
        driver.driver_account_balance = driver.driver_account_balance + balance
        db.add(driver)
        db.commit()
        db.refresh(driver)

        # 推送消息给司机端
        push_message = {
            "type": "fee_paid",
            "data": {
                "driver_account_id": driver.driver_account_id,
                "order_id": fee.order_id,
                "path_id": fee.path_id,
                "total_price": data.total_price,
                "carry_fee": data.carry_fee,
                "wait_fee": data.wait_fee,
                "highway_fee": data.highway_fee,
                "parking_fee": data.parking_fee,
                "pay_time": datetime.utcnow().isoformat(),
            },
        }
        await send_message_to_type("driver", push_message)

        return success_response("费用支付成功")

    except Exception as e:
        print(f"支付费用错误: {e}")
        return internal_error_response("支付费用失败")


@router.get(
    "/detail",
    summary="获取支付订单详情",
    description="根据订单号或运单号获取订单详情信息",
)
async def get_order_detail(
    order_id: Optional[str] = Query(None, description="订单号"),
    path_id: Optional[str] = Query(None, description="运单号"),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    司机获取订单详情
    order_id 和 path_id 至少传入一个
    """
    try:
        # 参数验证
        if not order_id and not path_id:
            return param_error_response("订单号和运单号至少传入一个")

        # 查询费用信息
        fee_query = select(Fee)

        # 修改查询条件：同时考虑order_id和path_id（如果都提供了）
        conditions = []
        if order_id:
            conditions.append(Fee.order_id == order_id)
        if path_id:
            conditions.append(Fee.path_id == path_id)

        # 使用and_连接所有条件
        fee_query = (
            fee_query.where(and_(*conditions))
            if len(conditions) > 1
            else fee_query.where(conditions[0])
        )

        fee = db.exec(fee_query).first()
        if not fee:
            return not_found_response("订单不存在")

        # 状态映射：数据库里的"已结算" → 返回前端的"已支付"
        display_status = "已支付" if fee.status == "已结算" else fee.status

        # 查询订单详情
        order_detail = db.exec(
            select(OrderDetail).where(OrderDetail.order_id == fee.order_id)
        ).first()

        # 查询司机信息
        driver = None
        if fee.driver_account_id:
            driver = db.exec(
                select(Driver).where(Driver.driver_account_id == fee.driver_account_id)
            ).first()

        # 构建响应数据（使用映射后的状态）
        response_data = {
            "path_id": fee.path_id,
            "order_id": fee.order_id,
            "status": display_status,  # 使用映射后的状态
            "order_time": fee.order_time.isoformat() if fee.order_time else None,
            "finish_time": (
                order_detail.finish_time.isoformat()
                if order_detail and order_detail.finish_time
                else None
            ),
            "driver_name": driver.driver_name if driver else None,
            "driver_phone": driver.driver_phone if driver else None,
            "car_plate": order_detail.car_plate if order_detail else None,
            "loading_addr": order_detail.loading_addr if order_detail else None,
            "sender_name": order_detail.sender_name if order_detail else None,
            "sender_phone": order_detail.sender_phone if order_detail else None,
            "unloading_addr": order_detail.unloading_addr if order_detail else None,
            "receiver_name": order_detail.receiver_name if order_detail else None,
            "receiver_phone": order_detail.receiver_phone if order_detail else None,
            "goods_volume": order_detail.goods_volume if order_detail else None,
            "goods_num": order_detail.goods_num if order_detail else None,
            "goods_weight": order_detail.goods_weight if order_detail else None,
            "demand_car_type": order_detail.demand_car_type if order_detail else None,
            "is_carpool": order_detail.is_carpool if order_detail else None,
            "need_carry": order_detail.need_carry if order_detail else None,
            "logistics_platform": fee.logistics_platform,
            "other_loading_demand": (
                order_detail.other_loading_demand if order_detail else None
            ),
            "total_distance": order_detail.total_distance if order_detail else None,
            "loading_goods_imgs": (
                order_detail.loading_goods_imgs if order_detail else None
            ),
            "loading_car_imgs": order_detail.loading_car_imgs if order_detail else None,
            "unloading_goods_imgs": (
                order_detail.unloading_goods_imgs if order_detail else None
            ),
            "unloading_car_imgs": (
                order_detail.unloading_car_imgs if order_detail else None
            ),
            "receipt_imgs": fee.receipt_imgs,
            "parking_bill_imgs": fee.parking_bill_imgs,
            "highway_bill_imgs": fee.highway_bill_imgs,
            "total_price": fee.total_price,
            "highway_fee": fee.highway_fee,
            "parking_fee": fee.parking_fee,
            "carry_fee": fee.carry_fee,
            "wait_fee": fee.wait_fee,
        }

        return success_response(data=response_data, message="获取订单详情成功")

    except Exception as e:
        print(f"司机获取订单详情错误: {e}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("获取订单详情失败")
