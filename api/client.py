from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlmodel import Session, select, func, or_
from typing import Optional
from datetime import datetime
from fastapi import Query
from enum import Enum
import json

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
    FeeRejectRequest,
    FeeSettlementRequest,
)
from models.account import (
    Account,
    AccountRecharge,
    AccountResponse,
    PaginatedAccountResponse,
    BalanceWarningUpdateRequest,
)
from models.driver import Driver
from websocket.manager import send_message_to_type
from models.enums import OrderStatusEnum, RechargeStatusEnum
from models.order_detail import OrderDetail, OrderDetailResponse
from models.driver import Driver

router = APIRouter(
    prefix="/client",
    tags=["客户管理"],
)


class SettlementStatusEnum(str, Enum):
    """
    结算状态枚举
    """

    PENDING_SETTLEMENT = "待结算"
    SETTLED = "已结算"


@router.get(
    "/fee/list",
    summary="分页查询结算列表",
    description="分页查询结算信息，支持派单渠道、订单状态、运单号、订单号和时间范围筛选",
)
async def get_settlement_list(
    page: int = Query(1, description="当前页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1),
    dispatch_channel: Optional[str] = Query(None, description="派单渠道（可选）"),
    status: Optional[SettlementStatusEnum] = Query(
        None, description="状态（可选，待结算/已结算）"
    ),
    path_id: Optional[str] = Query(None, description="运单号搜索（可选）"),
    order_id: Optional[str] = Query(None, description="订单号搜索（可选）"),
    start_time: Optional[str] = Query(None, description="开始时间（格式：YYYY-MM-DD）"),
    end_time: Optional[str] = Query(None, description="结束时间（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    分页查询结算列表
    """
    try:
        # 基础查询构建
        query = select(Fee)

        # **状态筛选逻辑**
        if status:
            if status == SettlementStatusEnum.PENDING_SETTLEMENT:
                # 如果前端传的是 PENDING_SETTLEMENT，实际查询 PENDING_PAYMENT
                query = query.where(Fee.status == OrderStatusEnum.PENDING_PAYMENT)
            else:
                # 其他状态（如 SETTLED）直接查询
                query = query.where(Fee.status == status)
        else:
            # 如果未指定状态，查询待支付和已结算两种状态
            query = query.where(
                or_(
                    Fee.status == OrderStatusEnum.PENDING_PAYMENT,
                    Fee.status == OrderStatusEnum.SETTLED,
                )
            )

        # 派单渠道筛选
        if dispatch_channel and dispatch_channel.strip():
            query = query.where(Fee.dispatch_channel == dispatch_channel.strip())

        # 运单号筛选
        if path_id and path_id.strip():
            search_term = f"%{path_id.strip()}%"
            query = query.where(Fee.path_id.like(search_term))

        # 订单号筛选
        if order_id and order_id.strip():
            search_term = f"%{order_id.strip()}%"
            query = query.where(Fee.order_id.like(search_term))

        # 时间范围筛选
        if start_time and end_time:
            try:
                start_date = datetime.strptime(start_time, "%Y-%m-%d")
                end_date = datetime.strptime(end_time, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.where(
                    Fee.order_time >= start_date, Fee.order_time <= end_date
                )
            except ValueError:
                return param_error_response("时间格式不正确，请使用YYYY-MM-DD格式")

        # **计算总数（同样应用状态映射逻辑）**
        count_query = select(func.count(Fee.fee_id))

        if status:
            if status == SettlementStatusEnum.PENDING_SETTLEMENT:
                count_query = count_query.where(
                    Fee.status == OrderStatusEnum.PENDING_PAYMENT
                )
            else:
                count_query = count_query.where(Fee.status == status)
        else:
            count_query = count_query.where(
                or_(
                    Fee.status == OrderStatusEnum.PENDING_PAYMENT,
                    Fee.status == OrderStatusEnum.SETTLED,
                )
            )

        # 应用其他筛选条件
        if dispatch_channel and dispatch_channel.strip():
            count_query = count_query.where(
                Fee.dispatch_channel == dispatch_channel.strip()
            )
        if path_id and path_id.strip():
            search_term = f"%{path_id.strip()}%"
            count_query = count_query.where(Fee.path_id.like(search_term))
        if order_id and order_id.strip():
            search_term = f"%{order_id.strip()}%"
            count_query = count_query.where(Fee.order_id.like(search_term))
        if start_time and end_time:
            try:
                start_date = datetime.strptime(start_time, "%Y-%m-%d")
                end_date = datetime.strptime(end_time, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
                count_query = count_query.where(
                    Fee.order_time >= start_date, Fee.order_time <= end_date
                )
            except ValueError:
                pass  # 前面已经处理过错误

        total = db.exec(count_query).first()

        # 分页处理
        offset = (page - 1) * size
        total_pages = (total + size - 1) // size

        query = query.offset(offset).limit(size)
        query = query.order_by(Fee.order_time.desc())

        fees = db.exec(query).all()

        # **构建响应数据（将 PENDING_PAYMENT 映射回 PENDING_SETTLEMENT）**
        fee_items = []
        for fee in fees:
            # 如果状态是 PENDING_PAYMENT，返回给前端时改成 PENDING_SETTLEMENT
            display_status = (
                SettlementStatusEnum.PENDING_SETTLEMENT
                if fee.status == OrderStatusEnum.PENDING_PAYMENT
                else fee.status
            )

            fee_items.append(
                FeeResponse(
                    fee_id=fee.fee_id,
                    path_id=fee.path_id,
                    order_id=fee.order_id,
                    status=display_status,  # 映射后的状态
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
                    driver_account_id=fee.driver_account_id,
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
            message="获取结算列表成功",
        )

    except Exception as e:
        return internal_error_response("获取结算列表失败")


@router.patch("/reject", summary="驳回支付")
async def reject_fee(
    data: FeeRejectRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    驳回支付
    - 驳回类型为bill时: 需要填写驳回金额和原因
    - 驳回类型为receipt时: 只需要填写驳回原因
    """
    try:
        # 查询费用记录
        fee = db.exec(select(Fee).where(Fee.fee_id == data.fee_id)).first()
        if not fee:
            return not_found_response("费用记录不存在")

        print("当前支付状态：", fee.status)

        # 检查状态是否允许驳回
        if fee.status not in [
            OrderStatusEnum.PENDING_PAYMENT,
            OrderStatusEnum.APPEALING,
        ]:
            return param_error_response("当前状态不允许驳回")

        # 更新费用记录
        if data.reject_type == "bill":
            # 费用驳回
            fee.bill_reject_reason = data.reject_reason
            if data.reject_highway_fee is not None:
                fee.highway_fee = max(0, fee.highway_fee - data.reject_highway_fee)
            if data.reject_parking_fee is not None:
                fee.parking_fee = max(0, fee.parking_fee - data.reject_parking_fee)

        else:
            # 回单驳回
            fee.receipt_reject_reason = data.reject_reason

        # 更新状态为已结算
        fee.status = OrderStatusEnum.SETTLED
        fee.updated_at = datetime.utcnow()

        db.add(fee)
        db.commit()
        db.refresh(fee)

        push_message = {
            "type": "reject_fee",
            "fee_id": fee.fee_id,
            "status": fee.status,
            "reject_reason": data.reject_reason,
            "reject_highway_fee": data.reject_highway_fee,
            "reject_parking_fee": data.reject_parking_fee,
        }

        # 推送消息给司机端
        await send_message_to_type("driver", push_message)

        return success_response(
            data={"fee_id": fee.fee_id, "status": fee.status}, message="驳回成功"
        )

    except Exception as e:
        return internal_error_response("驳回支付失败")


@router.patch("/pay", summary="结算")
async def pay_fee(
    data: FeeSettlementRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    结算
    """
    try:
        # 查询费用记录
        fee = db.exec(select(Fee).where(Fee.fee_id == data.fee_id)).first()
        if not fee:
            return not_found_response("费用记录不存在")

        # 更新费用表发起结算操作为True
        fee.settlement_enable = True
        fee.updated_at = datetime.utcnow()

        db.add(fee)
        db.commit()
        db.refresh(fee)

        # 推送消息给平台端
        push_message = {
            "type": "pay_fee",
            "fee_id": fee.fee_id,
            "status": fee.status,
        }
        await send_message_to_type("platform", push_message)

        return success_response(
            data={"fee_id": fee.fee_id, "status": fee.status}, message="已发起结算"
        )

    except Exception as e:
        return internal_error_response("发起结算失败")


@router.patch("/recharge", summary="充值")
async def recharge_fee(
    data: AccountRecharge, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    充值
    """
    try:
        # 查询账户记录
        account = db.exec(
            select(Account).where(Account.company_account_id == data.company_account_id)
        ).first()
        if not account:
            return not_found_response("账户记录不存在")

        # 更新账户充值状态为审核中
        account.recharge_status = RechargeStatusEnum.UNDER_REVIEW
        account.updated_at = datetime.utcnow()
        account.recharge_time = datetime.utcnow()
        account.recharge_amount = data.recharge_amount
        account.recharge_name = data.recharge_name
        account.recharge_phone = data.recharge_phone

        db.add(account)
        db.commit()
        db.refresh(account)

        return success_response(
            data={
                "company_account_id": account.company_account_id,
                "recharge_status": account.recharge_status,
            },
            message="充值成功",
        )

    except Exception as e:
        return internal_error_response("充值失败")


@router.get(
    "/list",
    summary="分页查询账户列表",
    description="分页查询所有账户信息",
    response_model=PaginatedAccountResponse,
)
async def get_account_list(
    page: int = Query(1, description="当前页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    分页查询账户列表
    """
    try:
        # 基础查询
        query = select(Account)

        # 总数查询
        count_query = select(func.count(Account.company_account_id))

        # 获取总数
        total = db.exec(count_query).one()

        # 计算分页参数
        offset = (page - 1) * size
        total_pages = (total + size - 1) // size

        # 应用分页和排序
        query = query.offset(offset).limit(size).order_by(Account.created_at.desc())

        # 执行查询
        accounts = db.exec(query).all()

        # 转换为响应模型
        account_items = [
            AccountResponse(
                company_account_id=account.company_account_id,
                company_id=account.company_id,
                created_at=account.created_at,
                updated_at=account.updated_at,
                company_account_updatetime=account.company_account_updatetime,
                company_account_balance=account.company_account_balance,
                company_account_balance_warning_val=account.company_account_balance_warning_val,
                company_account_balance_warning_phone=account.company_account_balance_warning_phone,
                company_account_balance_warning_enable=account.company_account_balance_warning_enable,
                recharge_status=account.recharge_status,
                recharge_time=account.recharge_time,
                recharge_name=account.recharge_name,
                recharge_phone=account.recharge_phone,
                recharge_amount=account.recharge_amount,
                received_amount=account.received_amount,
            )
            for account in accounts
        ]

        # 构建响应
        response_data = PaginatedAccountResponse(
            items=account_items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

        return response_data

    except Exception as e:
        return internal_error_response("获取账户列表失败")


@router.patch(
    "/accounts/{company_account_id}/approve-recharge",
    summary="审核通过充值申请",
    description="平台端审核通过充值申请，客户账户余额加上到账金额",
    response_model=AccountResponse,
)
async def approve_recharge(
    company_account_id: str,
    db: Session = Depends(get_db),
):
    """
    审核通过充值申请
    """
    try:
        # 查询账户
        account = db.exec(
            select(Account).where(Account.company_account_id == company_account_id)
        ).first()

        if not account:
            return not_found_response("账户记录不存在")

        if account.recharge_status != RechargeStatusEnum.UNDER_REVIEW:
            return param_error_response("充值状态不正确")

        # 更新账户余额
        account.company_account_balance += account.received_amount

        # 更新充值状态和时间
        account.recharge_status = RechargeStatusEnum.APPROVED
        account.recharge_time = datetime.utcnow()
        account.updated_at = datetime.utcnow()
        account.company_account_updatetime = datetime.utcnow()

        # 提交到数据库
        db.add(account)
        db.commit()
        db.refresh(account)

        # 返回更新后的账户信息
        return AccountResponse(
            company_account_id=account.company_account_id,
            company_id=account.company_id,
            created_at=account.created_at,
            updated_at=account.updated_at,
            company_account_updatetime=account.company_account_updatetime,
            company_account_balance=account.company_account_balance,
            company_account_balance_warning_val=account.company_account_balance_warning_val,
            company_account_balance_warning_phone=account.company_account_balance_warning_phone,
            company_account_balance_warning_enable=account.company_account_balance_warning_enable,
            recharge_status=account.recharge_status,
            recharge_time=account.recharge_time,
            recharge_name=account.recharge_name,
            recharge_phone=account.recharge_phone,
            recharge_amount=account.recharge_amount,
            received_amount=account.received_amount,
        )
    except Exception as e:
        return internal_error_response("审核通过充值申请失败")


@router.patch(
    "/balance-warning",
    summary="更新余额预警设置",
    description="接收平台端余额预警设置，更新余额预警值和预警手机号、启动字段",
    response_model=AccountResponse,
)
async def update_balance_warning(
    request: BalanceWarningUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    更新余额预警设置
    """
    try:
        # 查询账户
        account = db.exec(
            select(Account).where(
                Account.company_account_id == request.company_account_id
            )
        ).first()

        if not account:
            return not_found_response("账户记录不存在")

        # 更新预警设置
        account.company_account_balance_warning_val = (
            request.company_account_balance_warning_val
        )
        account.company_account_balance_warning_phone = (
            request.company_account_balance_warning_phone
        )
        account.company_account_balance_warning_enable = (
            request.company_account_balance_warning_enable
        )
        account.updated_at = datetime.utcnow()
        account.company_account_updatetime = datetime.utcnow()

        # 提交到数据库
        db.add(account)
        db.commit()
        db.refresh(account)

        # 返回更新后的账户信息
        return AccountResponse(
            company_account_id=account.company_account_id,
            company_id=account.company_id,
            created_at=account.created_at,
            updated_at=account.updated_at,
            company_account_updatetime=account.company_account_updatetime,
            company_account_balance=account.company_account_balance,
            company_account_balance_warning_val=account.company_account_balance_warning_val,
            company_account_balance_warning_phone=account.company_account_balance_warning_phone,
            company_account_balance_warning_enable=account.company_account_balance_warning_enable,
            recharge_status=account.recharge_status.value,
            recharge_time=account.recharge_time,
            recharge_name=account.recharge_name,
            recharge_phone=account.recharge_phone,
            recharge_amount=account.recharge_amount,
            received_amount=account.received_amount,
        )
    except Exception as e:
        return internal_error_response("更新余额预警设置失败")


@router.get(
    "/detail",
    summary="获取结算订单详情",
    description="根据订单号或运单号获取订单详情信息",
)
async def get_order_detail(
    order_id: Optional[str] = Query(None, description="订单号"),
    path_id: Optional[str] = Query(None, description="运单号"),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    获取订单详情
    order_id 和 path_id 至少传入一个
    """
    try:
        # 参数验证
        if not order_id and not path_id:
            return param_error_response("订单号和运单号至少传入一个")

        # 查询费用信息
        fee_query = select(Fee)
        if order_id:
            fee_query = fee_query.where(Fee.order_id == order_id)
        else:
            fee_query = fee_query.where(Fee.path_id == path_id)

        fee = db.exec(fee_query).first()
        if not fee:
            return not_found_response("订单不存在")

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

        # 构建响应数据
        response_data = {
            "path_id": fee.path_id,
            "order_id": fee.order_id,
            "status": fee.status,
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
        print(f"获取订单详情错误: {e}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("获取订单详情失败")
