from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

from config.settings import settings
from api.router import router, finance_router
from websocket.router import ws_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="物流系统后端API",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 服务器需要使用配置：settings.CORS_ORIGINS
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

# API路由
app.include_router(router, prefix="/api")
finance_app.include_router(finance_router, prefix="/api")
# WebSocket路由
app.include_router(ws_router, prefix="/api")

app.mount("/finance", finance_app)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@finance_app.get("/api/docs", include_in_schema=False)
async def finance_custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/finance/openapi.json",
        title=finance_app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.ENVIRONMENT == "development" else False,
        workers=1 if settings.ENVIRONMENT == "development" else 4,
    )
