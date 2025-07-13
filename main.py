from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import os

from config.settings import settings
from api.router import router, finance_router
from websocket.router import ws_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="物流系统后端API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": 400, "message": "参数错误", "details": exc.errors()},
        )

    return app


app = create_app()
finance_app = create_app()

# 只有当static目录存在时才挂载
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✅ Static files mounted from local directory")
else:
    print("⚠️ Static directory not found, using CDN for docs")

# API路由
app.include_router(router, prefix="/api")
finance_app.include_router(finance_router, prefix="/api")
# WebSocket路由
app.include_router(ws_router, prefix="/api")

# 挂载子应用
app.mount("/finance", finance_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.ENVIRONMENT == "development" else False,
        workers=1 if settings.ENVIRONMENT == "development" else 4,
    )
