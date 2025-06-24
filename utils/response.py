from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """
    API响应

    Attributes:
        code: 状态码
        message: 响应消息
        data: 响应数据
    """

    code: int
    message: str
    data: Optional[Any] = None


class ResponseCode:
    """
    响应状态码常量
    """

    # 成功
    SUCCESS = 200

    # 客户端错误
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

    # 服务器错误
    INTERNAL_ERROR = 500


def success_response(
    data: Any = None, message: str = "操作成功", http_status: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    成功响应

    Args:
        data: 响应数据
        message: 成功消息
        http_status: HTTP状态码
    """
    response = ApiResponse(code=ResponseCode.SUCCESS, message=message, data=data)
    return JSONResponse(status_code=http_status, content=response.model_dump())


def error_response(
    message: str,
    code: int = ResponseCode.BAD_REQUEST,
    http_status: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None,
) -> JSONResponse:
    """
    错误响应

    Args:
        message: 错误消息
        code: 业务错误码
        http_status: HTTP状态码
        data: 错误详情数据
    """
    response = ApiResponse(code=code, message=message, data=data)
    return JSONResponse(status_code=http_status, content=response.model_dump())


def param_error_response(message: str = "参数错误") -> JSONResponse:
    """参数错误响应"""
    return error_response(
        message=message,
        code=ResponseCode.BAD_REQUEST,
        http_status=status.HTTP_400_BAD_REQUEST,
    )


def unauthorized_response(message: str = "认证失败，请登录") -> JSONResponse:
    """认证失败响应"""
    return error_response(
        message=message,
        code=ResponseCode.UNAUTHORIZED,
        http_status=status.HTTP_401_UNAUTHORIZED,
    )


def forbidden_response(message: str = "权限不足") -> JSONResponse:
    """权限不足响应"""
    return error_response(
        message=message,
        code=ResponseCode.FORBIDDEN,
        http_status=status.HTTP_403_FORBIDDEN,
    )


def not_found_response(message: str = "资源不存在") -> JSONResponse:
    """错误响应"""
    return error_response(
        message=message,
        code=ResponseCode.NOT_FOUND,
        http_status=status.HTTP_404_NOT_FOUND,
    )


def internal_error_response(message: str = "服务器内部错误") -> JSONResponse:
    """服务器错误响应"""
    return error_response(
        message=message,
        code=ResponseCode.INTERNAL_ERROR,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
