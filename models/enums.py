from enum import Enum


class PositionEnum(str, Enum):
    """
    岗位枚举

    Notes:
        继承str确保序列化兼容性
    """

    CUSTOMER_SERVICE = "1"  # 客服
    LOGISTICS_SPECIALIST = "2"  # 物流专员
    FINANCE = "3"  # 财务
    HR = "4"  # 人事
    ADMINISTRATOR = "5"  # 管理员


class PermissionEnum(str, Enum):
    """
    权限枚举
    """

    ONLINE_ORDER = "1"  # 在线下单
    ORDER_MANAGEMENT = "2"  # 订单管理
    EMPLOYEE_MANAGEMENT = "3"  # 员工管理
    FINANCIAL_MANAGEMENT = "4"  # 财务管理


class OperatorTypeEnum(str, Enum):
    """
    操作员类型枚举
    """

    CLIENT = "CLIENT"  # 用户
    PLATFORM = "PLATFORM"  # 平台


class OrderStatusEnum(str, Enum):
    """
    订单状态枚举
    """

    APPEALING = "申诉中"
    PENDING_PAYMENT = "待支付"
    PENDING_SETTLEMENT = "待结算"
    SETTLED = "已结算"


class RechargeStatusEnum(str, Enum):
    UNDER_REVIEW = "审核中"
    APPROVED = "已通过"
