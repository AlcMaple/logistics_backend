from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, func
from datetime import datetime

from models.user import (
    User,
    UserCreate,
    UserResponse,
    UserListRequest,
    UserListResponse,
    UserUpdate,
)
from models.company import Company
from utils.validation import validate_phone
from utils.response import (
    success_response,
    not_found_response,
    param_error_response,
    internal_error_response,
)
from config.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["员工管理"],
)


@router.post(
    "/add",
    summary="添加员工",
    description="根据企业id添加新员工",
    responses={
        200: {
            "description": "添加成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "员工添加成功",
                        "data": {
                            "nick_name": "张三",
                            "phone": "18800001234",
                            "job_number": "00000001",
                            "position": "1（1：客服，2：物流专员，3：财务，4：人事，5：管理员）",
                            "permissions": [
                                "1（在线下单）",
                                "2（订单管理）",
                                "3（员工管理）",
                                "4（财务管理）",
                            ],
                            "registered": False,
                            "company_id": "550e8400-e29b-41d4-a716-446655440000",
                        },
                    }
                }
            },
        },
        400: {
            "description": "参数错误",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "参数错误", "data": None}
                }
            },
        },
        404: {"description": "企业不存在"},
    },
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    添加员工

    Args:
        user_data: 员工信息
        db: 数据库会话
    """
    try:
        # 验证字段
        if not user_data.nick_name.strip():
            return param_error_response("员工姓名不能为空")

        if not user_data.phone.strip():
            return param_error_response("手机号不能为空")

        if not user_data.job_number.strip():
            return param_error_response("工号不能为空")

        if not user_data.company_id.strip():
            return param_error_response("企业ID不能为空")

        if not user_data.position:
            return param_error_response("岗位不能为空")

        # 验证手机号格式
        if not validate_phone(user_data.phone):
            return param_error_response("手机号格式错误")

        # 验证企业是否存在
        company = db.get(Company, user_data.company_id)
        if not company:
            return not_found_response("企业不存在")

        # 检查手机号是否存在
        existing_phone = db.exec(
            select(User).where(User.phone == user_data.phone, User.is_deleted == False)
        ).first()
        if existing_phone:
            return param_error_response("手机号已存在")

        # 检查工号是否存在
        existing_job_number = db.exec(
            select(User).where(
                User.job_number == user_data.job_number, User.is_deleted == False
            )
        ).first()
        if existing_job_number:
            return param_error_response("工号已存在")

        # 创建新员工
        new_user = User(
            nick_name=user_data.nick_name.strip(),
            phone=user_data.phone.strip(),
            job_number=user_data.job_number.strip(),
            position=user_data.position,
            company_id=user_data.company_id,
            registered=False,
            operator_type="CLIENT",
        )

        # 设置权限
        if user_data.permissions:
            new_user.set_permissions(user_data.permissions)

        # 保存到数据库
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 用户数据
        response_data = UserResponse(
            user_id=new_user.user_id,
            nick_name=new_user.nick_name,
            phone=new_user.phone,
            job_number=new_user.job_number,
            position=new_user.position,
            permissions=new_user.get_permissions(),
            registered=new_user.registered,
            operator_type=new_user.operator_type,
            company_id=new_user.company_id,
            created_at=new_user.created_at.isoformat(),
            updated_at=new_user.updated_at.isoformat(),
        )

        return success_response(data=response_data.model_dump(), message="员工添加成功")

    except Exception as e:
        db.rollback()
        print(f"添加员工错误: {e}")
        print(f"错误类型: {type(e)}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("员工添加失败")


@router.post(
    "/list",
    summary="获取员工列表",
    description="根据企业ID获取员工列表，支持分页和搜索",
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "获取员工列表成功",
                        "data": {
                            "items": [
                                {
                                    "user_id": "421c3d5a-a16f-4d9f-8d9f-a7d5a3d1c31c",
                                    "nick_name": "张三",
                                    "phone": "18800001234",
                                    "job_number": "EMP001",
                                    "position": "1（1：客服，2：物流专员，3：财务，4：人事，5：管理员）",
                                    "permissions": ["1（在线下单）", "2（订单管理）"],
                                    "registered": "false（未激活）",
                                    "operator_type": "CLIENT（用户）",
                                    "company_id": "550e8400-e29b-41d4-a716-446655440000",
                                    "created_at": "2025-06-23T09:13:23",
                                    "updated_at": "2025-06-23T09:13:23",
                                }
                            ],
                            "total": 50,
                            "page": 1,
                            "size": 11,
                            "total_pages": 5,
                        },
                    }
                }
            },
        },
        400: {
            "description": "参数错误",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "企业ID不能为空", "data": None}
                }
            },
        },
        404: {
            "description": "企业不存在",
            "content": {
                "application/json": {
                    "example": {"code": 404, "message": "企业不存在", "data": None}
                }
            },
        },
    },
)
async def get_user_list(
    request_data: UserListRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    获取员工列表

    Args:
        request_data: 请求参数
        db: 数据库会话

    Returns:
        JSONResponse: 员工列表
    """
    try:
        # 验证企业ID
        if not request_data.company_id.strip():
            return param_error_response("企业ID不能为空")

        # 验证企业是否存在
        company = db.get(Company, request_data.company_id)
        if not company:
            return not_found_response("企业不存在")

        # 构建查询条件
        query = select(User).where(
            User.company_id == request_data.company_id, User.is_deleted == False
        )

        # 添加搜索条件
        if request_data.search and request_data.search.strip():
            search_term = f"%{request_data.search.strip()}%"
            query = query.where(
                (User.nick_name.like(search_term)) | (User.job_number.like(search_term))
            )

        # 获取总数量
        count_query = select(func.count(User.user_id)).where(
            User.company_id == request_data.company_id, User.is_deleted == False
        )

        # 添加搜索条件到计数查询
        if request_data.search and request_data.search.strip():
            search_term = f"%{request_data.search.strip()}%"
            count_query = count_query.where(
                (User.nick_name.like(search_term)) | (User.job_number.like(search_term))
            )

        total = db.exec(count_query).first()

        # 计算分页
        offset = (request_data.page - 1) * request_data.size
        total_pages = (total + request_data.size - 1) // request_data.size

        # 分页查询
        query = query.offset(offset).limit(request_data.size)
        query = query.order_by(User.created_at.desc())  # 按创建时间倒序

        users = db.exec(query).all()

        # 转换数据
        user_items = []
        for user in users:

            user_response = UserResponse(
                user_id=user.user_id,
                nick_name=user.nick_name,
                phone=user.phone,
                job_number=user.job_number,
                position=user.position,
                permissions=user.get_permissions(),
                registered=user.registered,
                operator_type=user.operator_type,
                company_id=user.company_id,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat(),
            )
            user_items.append(user_response)

        # 构造响应数据
        response_data = UserListResponse(
            items=user_items,
            total=total,
            page=request_data.page,
            size=request_data.size,
            total_pages=total_pages,
        )

        return success_response(
            data=jsonable_encoder(response_data),
            message="获取员工列表成功",
        )

    except Exception as e:
        print(f"获取员工列表错误: {e}")
        print(f"错误类型: {type(e)}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("获取员工列表失败")


@router.put(
    "",
    summary="更新员工信息",
    description="更新员工信息",
    responses={
        200: {
            "description": "更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "员工信息更新成功",
                        "data": {
                            "user_id": "421c3d5a-a16f-4d9f-8d9f-a7d5a3d1c31c",
                            "nick_name": "张三",
                            "phone": "18800001234",
                            "job_number": "00000001",
                            "position": "1",
                            "permissions": ["1", "2"],
                            "registered": False,
                            "operator_type": "CLIENT",
                            "company_id": "550e8400-e29b-41d4-a716-446655440000",
                            "created_at": "2025-06-23T09:13:23",
                            "updated_at": "2025-06-23T09:13:23",
                        },
                    }
                }
            },
        },
        400: {
            "description": "参数错误",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "参数错误", "data": None}
                }
            },
        },
        404: {
            "description": "员工不存在",
            "content": {
                "application/json": {
                    "example": {"code": 404, "message": "员工不存在", "data": None}
                }
            },
        },
    },
)
async def update_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    更新员工信息

    Args:
        user_data: 更新的员工信息
        db: 数据库会话
    """
    try:
        # 验证user_id
        if not user_data.user_id:
            return param_error_response("员工ID不能为空")

        # 验证字段
        if not user_data.nick_name.strip():
            return param_error_response("员工姓名不能为空")

        if not user_data.phone.strip():
            return param_error_response("手机号不能为空")

        if not user_data.job_number.strip():
            return param_error_response("工号不能为空")

        if not user_data.position:
            return param_error_response("岗位不能为空")

        # 验证手机号格式
        if not validate_phone(user_data.phone):
            return param_error_response("手机号格式错误")

        # 查找更新的员工
        user = db.exec(
            select(User).where(
                User.user_id == user_data.user_id, User.is_deleted == False
            )
        ).first()

        if not user:
            return not_found_response("员工不存在")

        # 验证企业是否存在
        company = db.get(Company, user.company_id)
        if not company:
            return not_found_response("所属企业不存在")

        # 检查手机号
        existing_phone = db.exec(
            select(User).where(
                User.phone == user_data.phone.strip(),
                User.user_id != user_data.user_id,  # 排除当前用户
                User.is_deleted == False,
            )
        ).first()
        if existing_phone:
            return param_error_response("手机号已被其他员工使用")

        # 检查工号
        existing_job_number = db.exec(
            select(User).where(
                User.job_number == user_data.job_number.strip(),
                User.user_id != user_data.user_id,
                User.is_deleted == False,
            )
        ).first()
        if existing_job_number:
            return param_error_response("工号已被其他员工使用")

        # 更新员工信息
        user.nick_name = user_data.nick_name.strip()
        user.phone = user_data.phone.strip()
        user.job_number = user_data.job_number.strip()
        user.position = user_data.position

        # 更新权限
        if user_data.permissions:
            user.set_permissions(user_data.permissions)
        else:
            user.set_permissions([])  # 清空权限

        # 保存到数据库
        db.add(user)
        db.commit()
        db.refresh(user)

        # 用户数据
        response_data = UserResponse(
            user_id=user.user_id,
            nick_name=user.nick_name,
            phone=user.phone,
            job_number=user.job_number,
            position=user.position,
            permissions=user.get_permissions(),
            registered=user.registered,
            operator_type=user.operator_type,
            company_id=user.company_id,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

        return success_response(
            data=jsonable_encoder(response_data), message="员工信息更新成功"
        )

    except Exception as e:
        db.rollback()
        print(f"更新员工错误: {e}")
        print(f"错误类型: {type(e)}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("员工信息更新失败")


@router.delete(
    "/{user_id}",
    summary="删除员工",
    description="根据员工ID删除员工",
    responses={
        200: {
            "description": "删除成功",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "员工删除成功", "data": None}
                }
            },
        },
        404: {
            "description": "员工不存在",
            "content": {
                "application/json": {
                    "example": {"code": 404, "message": "员工不存在", "data": None}
                }
            },
        },
    },
)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    逻辑删除员工

    Args:
        user_id: 员工ID
        db: 数据库会话
    """
    try:
        # 查找要删除的员工
        user = db.get(User, user_id)
        if not user:
            return not_found_response("员工不存在")

        # 删除员工
        user.is_deleted = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return success_response(data=None, message="员工删除成功")

    except Exception as e:
        db.rollback()
        print(f"删除员工错误: {e}")
        print(f"错误类型: {type(e)}")
        import traceback

        print(f"完整错误信息: {traceback.format_exc()}")
        return internal_error_response("员工删除失败")
