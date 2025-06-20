from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"  # 数据表名规范是复数

    name = Column(
        String(100), nullable=False, comment="企业名称"
    )  # comment是注释补充，增强维护性
    code = Column(String(20), nullable=False, unique=True, comment="企业邀请码")
    admin_name = Column(String(50), nullable=False, comment="管理员姓名")
    admin_phone = Column(String(20), nullable=False, comment="管理员手机号")
    admin_pwd = Column(String(255), nullable=False, comment="管理员密码")

    # 关联
    """
    一个企业有多个员工，一个员工只能属于一个企业

    Args:
        back_populates: 在Employee表中有对应的反向关联字段
    
    use:
        company.employees 访问所有关联员工
    """
    employees = relationship("Employee", back_populates="company")
