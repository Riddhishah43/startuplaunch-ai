from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Startup Idea Validator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
