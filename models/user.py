from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import json

from .base import BaseModel, generate_uuid
from .enums import PositionEnum, PermissionEnum, OperatorTypeEnum


class User(BaseModel, table=True):
    """
    用户模型
    """

    __tablename__ = "users"

    user_id: str = Field(
        default_factory=generate_uuid, primary_key=True, description="用户ID"
    )
    nick_name: str = Field(max_length=50, description="用户名称")

    phone: str = Field(max_length=20, unique=True, description="手机号")

    job_number: str = Field(max_length=20, unique=True, description="工号")

    position: PositionEnum = Field(description="岗位")

    permissions: str = Field(default="[]", description="权限")

    registered: bool = Field(default=False, description="激活状态")

    operator_type: OperatorTypeEnum = Field(
        default=OperatorTypeEnum.CLIENT, description="操作员类型"
    )

    password: Optional[str] = Field(
        default=None, max_length=255, description="哈希密码"
    )

    salt: Optional[str] = Field(default=None, max_length=32, description="盐值")

    # 外键关联
    company_id: str = Field(
        foreign_key="companies.company_id", description="所属企业ID"
    )

    # 关联关系：一个用户属于一个企业
    company: Optional["Company"] = Relationship(back_populates="users")

    def get_permissions(self) -> List[PermissionEnum]:
        """
        获取用户权限列表

        Returns:
            List[PermissionEnum]: 权限枚举列表
        """
        try:
            permission_values = json.loads(self.permissions)
            return [
                PermissionEnum(p)
                for p in permission_values
                if p in PermissionEnum.__members__.values()
            ]
        except (json.JSONDecodeError, ValueError):
            return []

    def set_permissions(self, permissions: List[PermissionEnum]):
        """
        设置用户权限列表

        Args:
            permissions: 权限枚举列表
        """
        self.permissions = json.dumps([p.value for p in permissions])


class UserCreate(BaseModel):
    """用户创建模型"""

    nick_name: str = Field(max_length=50)
    phone: str = Field(max_length=20)
    job_number: str = Field(max_length=20)
    position: PositionEnum
    permissions: List[PermissionEnum] = Field(default=[])
    company_id: str
    operator_type: OperatorTypeEnum = OperatorTypeEnum.CLIENT


class UserUpdate(BaseModel):
    """用户更新模型"""

    nick_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    job_number: Optional[str] = Field(None, max_length=20)
    position: Optional[PositionEnum] = None
    permissions: Optional[List[PermissionEnum]] = None


class UserResponse(BaseModel):
    """用户响应模型"""

    user_id: str
    nick_name: str
    phone: str
    job_number: str
    position: PositionEnum
    permissions: List[PermissionEnum]
    registered: bool
    operator_type: OperatorTypeEnum
    company_id: str
    created_at: str
    updated_at: str
