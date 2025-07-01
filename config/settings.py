from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "物流系统后端"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # 生产环境：production

    # # 服务器配置
    # HOST: str = "0.0.0.0"
    # PORT: int = 8001

    # # CORS配置
    # CORS_ORIGINS: List[str] = ["*"]

    # 数据库配置
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123qweQWE!"  # 服务器数据库密码：Yunhai2025!
    MYSQL_DATABASE: str = "logistics_db"
    MYSQL_PORT: int = 3306

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # @property
    # def is_development(self) -> bool:
    #     return self.ENVIRONMENT == "development"

    # @property
    # def is_production(self) -> bool:
    #     return self.ENVIRONMENT == "production"

settings = Settings()
