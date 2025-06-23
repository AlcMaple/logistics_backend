from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import json

from .base import BaseModel, generate_uuid
from .enums import OperatorTypeEnum


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

    position: str = Field(description="岗位")

    permissions: str = Field(default="[]", description="权限")

    registered: bool = Field(default=False, description="激活状态")

    operator_type: OperatorTypeEnum = Field(
        default=OperatorTypeEnum.CLIENT, description="操作员类型"
    )

    password: Optional[str] = Field(
        default=None, max_length=255, description="哈希密码"
    )

    salt: Optional[str] = Field(default=None, max_length=32, description="盐值")

    is_deleted: bool = Field(default=False, description="是否已删除")

    # 外键关联
    company_id: str = Field(
        foreign_key="companies.company_id", description="所属企业ID"
    )

    # 关联关系
    company: Optional["Company"] = Relationship(back_populates="users")

    def get_permissions(self) -> List[str]:
        """
        获取用户权限列表 - 返回字符串列表

        Returns:
            List[str]: 权限字符串列表
        """
        try:
            permission_values = json.loads(self.permissions)
            return [str(p) for p in permission_values]
        except (json.JSONDecodeError, ValueError):
            return []

    def set_permissions(self, permissions: List[str]):
        """
        设置用户权限列表

        Args:
            permissions: 权限字符串列表
        """
        self.permissions = json.dumps(permissions)


class UserCreate(BaseModel):
    """用户创建模型"""

    nick_name: str = Field(max_length=50, min_length=1, description="员工姓名")
    phone: str = Field(max_length=20, min_length=11, description="手机号")
    job_number: str = Field(max_length=20, min_length=1, description="工号")
    position: str = Field(description="岗位")
    permissions: List[str] = Field(default=[], description="权限列表")
    company_id: str = Field(description="所属企业ID")


class UserResponse(BaseModel):
    """用户响应模型"""

    user_id: str
    nick_name: str
    phone: str
    job_number: str
    position: str
    permissions: List[str]
    registered: bool
    operator_type: OperatorTypeEnum
    company_id: str
    created_at: str
    updated_at: str


class UserListRequest(BaseModel):
    """员工列表请求模型"""

    company_id: str = Field(description="企业ID")
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    size: int = Field(default=10, ge=1, le=100, description="每页数量，最大100")
    search: Optional[str] = Field(default=None, description="搜索关键词（姓名或工号）")


class UserListResponse(BaseModel):
    """员工列表响应模型"""

    items: List[UserResponse] = Field(description="员工列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class UserUpdate(BaseModel):
    """用户更新模型"""

    user_id: str = Field(description="员工ID")
    nick_name: str = Field(max_length=50, min_length=1, description="员工姓名")
    phone: str = Field(max_length=20, min_length=11, description="手机号")
    job_number: str = Field(max_length=20, min_length=1, description="工号")
    position: str = Field(description="岗位")
    permissions: List[str] = Field(description="权限列表")
