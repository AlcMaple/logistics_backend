from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "物流系统后端"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # 数据库配置
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123qweQWE!"
    MYSQL_DATABASE: str = "logistics_db"
    MYSQL_PORT: int = 3306

    # 装饰器啊访问像属性一样访问
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
