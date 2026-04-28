from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    mongodb_uri: str = Field(default="", validation_alias="MONGODB_URI")

    @field_validator("mongodb_uri", mode="before")
    @classmethod
    def _strip_mongo_uri(cls, v: object) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        if len(s) >= 2 and s[0] in "\"'" and s[0] == s[-1]:
            s = s[1:-1].strip()
        return s
    mongodb_db_name: str = Field(
        default="tienda_coleccionables",
        validation_alias="MONGODB_DB_NAME",
    )
    cors_origins: str = Field(default="*", validation_alias="CORS_ORIGINS")

    @property
    def cors_origin_list(self) -> List[str]:
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
