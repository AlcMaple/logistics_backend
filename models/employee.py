from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Employee(BaseModel):
    __tablename__ = "employees"

    name = Column(String(50), nullable=False, comment="员工姓名")
    employee_id = Column(String(20), unique=True, nullable=False, comment="员工工号")
    position = Column(String(50), nullable=False, comment="职位")
    phone = Column(String(20), nullable=False, comment="手机号")
    permissions = Column(Text, nullable=False, default="[]", comment="权限")
    is_active = Column(Boolean, default=False, comment="状态")

    company_id = Column(
        Integer, ForeignKey("companies.id"), nullable=False, comment="企业ID"
    )
    company = relationship("Company", back_populates="employees")
