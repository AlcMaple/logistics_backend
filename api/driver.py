from fastapi import FastAPI, Request, status, APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlmodel import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from utils.response import (
    success_response,
    not_found_response,
    param_error_response,
    internal_error_response,
)
from models.fee import Fee

router = APIRouter(
    prefix="/driver",
    tags=["司机管理"],
)


class DriverSubmitRequest(BaseModel):
    driver_id: str = Field(
        ..., description="司机ID", example=""
    )  # 使用example来兼容交互式文档
    order_id: str = Field(..., description="订单ID", example="")
    path_id: str = Field(..., description="运单ID", example="")
    highway_fee: int = Field(..., description="高速费（分）")
    parking_fee: int = Field(..., description="停车费（分）")
    carry_fee: int = Field(..., description="搬运费（分）")
    wait_fee: int = Field(..., description="逾时等候费（分）")
    highway_bill_imgs: Optional[str] = Field(
        "", description="高速费图片路径"
    )  # 默认值为空，兼容交互式文档
    parking_bill_imgs: Optional[str] = Field("", description="停车费图片路径")


class DriverResponse(BaseModel):
    highway_fee: int
    parking_fee: int
    carry_fee: int
    wait_fee: int
    highway_bill_imgs: Optional[str]
    parking_bill_imgs: Optional[str]
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

        return success_response(message="司机提交费用成功", data=new_fee.model_dump())

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
    return success_response("费用确认成功")
