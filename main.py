from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings
from api.router import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="物流系统后端API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许的域名
        allow_credentials=True,  # 允许跨域请求携带凭据（如 cookies、HTTP认证等）
        allow_methods=["*"],  # 允许所有方法（GET, POST, PUT, DELETE等）
        allow_headers=["*"],  # 允许所有头部
    )

    # API路由
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.ENVIRONMENT == "development" else False,
        workers=1 if settings.ENVIRONMENT == "development" else 4,  # 线程数
    )
