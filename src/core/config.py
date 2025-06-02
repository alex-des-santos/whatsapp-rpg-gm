"""
Configurações centralizadas do WhatsApp RPG GM
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Configurações básicas
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")

    # API Settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(3000, env="API_PORT")
    API_WORKERS: int = Field(4, env="API_WORKERS")

    # Evolution API
    EVOLUTION_API_URL: str = Field(..., env="EVOLUTION_API_URL")
    EVOLUTION_API_KEY: str = Field(..., env="EVOLUTION_API_KEY")
    EVOLUTION_INSTANCE_NAME: str = Field(..., env="EVOLUTION_INSTANCE_NAME")
    EVOLUTION_WEBHOOK_SECRET: str = Field("", env="EVOLUTION_WEBHOOK_SECRET")
    WEBHOOK_BASE_URL: str = Field(..., env="WEBHOOK_BASE_URL")

    # Base de dados
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # PostgreSQL específico
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("rpg_gm_db", env="POSTGRES_DB")
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("", env="POSTGRES_PASSWORD")

    # Redis específico
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    # Provedores de IA
    DEFAULT_AI_PROVIDER: str = Field("openai", env="DEFAULT_AI_PROVIDER")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(2000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(0.7, env="OPENAI_TEMPERATURE")

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field("claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    ANTHROPIC_MAX_TOKENS: int = Field(2000, env="ANTHROPIC_MAX_TOKENS")

    # Google AI
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    GOOGLE_MODEL: str = Field("gemini-pro", env="GOOGLE_MODEL")

    # Ollama (Local LLM)
    OLLAMA_URL: str = Field("http://localhost:11434", env="OLLAMA_URL")
    OLLAMA_MODEL: str = Field("llama2:13b", env="OLLAMA_MODEL")

    # HITL (Human-in-the-Loop)
    DISCORD_WEBHOOK_URL: Optional[str] = Field(None, env="DISCORD_WEBHOOK_URL")

    # Email SMTP
    SMTP_HOST: Optional[str] = Field(None, env="SMTP_HOST")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(None, env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = Field(None, env="SMTP_FROM_EMAIL")

    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(None, env="TWILIO_PHONE_NUMBER")
    GM_PHONE_NUMBER: Optional[str] = Field(None, env="GM_PHONE_NUMBER")

    # JWT e Segurança
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(1440, env="JWT_EXPIRE_MINUTES")

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(30, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(60, env="RATE_LIMIT_PERIOD")

    # Upload de arquivos
    MAX_FILE_SIZE: int = Field(10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: str = Field("image/jpeg,image/png,image/gif,application/pdf", env="ALLOWED_FILE_TYPES")

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/rpg_gm.log", env="LOG_FILE")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8501", "http://localhost:7860"],
        env="CORS_ORIGINS"
    )

    # Trusted Hosts
    TRUSTED_HOSTS: List[str] = Field(
        ["localhost", "127.0.0.1"],
        env="TRUSTED_HOSTS"
    )

    # Configurações específicas do jogo
    MAX_CONCURRENT_SESSIONS: int = Field(100, env="MAX_CONCURRENT_SESSIONS")
    MAX_PLAYERS_PER_SESSION: int = Field(6, env="MAX_PLAYERS_PER_SESSION")
    SESSION_TIMEOUT_MINUTES: int = Field(30, env="SESSION_TIMEOUT_MINUTES")
    AUTO_BACKUP_INTERVAL_HOURS: int = Field(6, env="AUTO_BACKUP_INTERVAL_HOURS")

    # Interfaces
    STREAMLIT_HOST: str = Field("0.0.0.0", env="STREAMLIT_HOST")
    STREAMLIT_PORT: int = Field(8501, env="STREAMLIT_PORT")
    GRADIO_HOST: str = Field("0.0.0.0", env="GRADIO_HOST")
    GRADIO_PORT: int = Field(7860, env="GRADIO_PORT")

    # Monitoramento
    PROMETHEUS_PORT: int = Field(9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(3001, env="GRAFANA_PORT")
    GRAFANA_ADMIN_PASSWORD: str = Field("admin123", env="GRAFANA_ADMIN_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Criar diretório de logs se não existir
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)

        # Validar configurações críticas
        self._validate_critical_settings()

    def _validate_critical_settings(self):
        """Validar configurações críticas"""
        errors = []

        # Verificar se pelo menos um provedor de IA está configurado
        ai_providers = {
            "openai": self.OPENAI_API_KEY,
            "anthropic": self.ANTHROPIC_API_KEY,
            "google": self.GOOGLE_API_KEY,
            "ollama": True  # Ollama não precisa de API key
        }

        if self.DEFAULT_AI_PROVIDER not in ai_providers:
            errors.append(f"Provedor de IA inválido: {self.DEFAULT_AI_PROVIDER}")

        if self.DEFAULT_AI_PROVIDER != "ollama" and not ai_providers[self.DEFAULT_AI_PROVIDER]:
            errors.append(f"API key não configurada para provedor: {self.DEFAULT_AI_PROVIDER}")

        # Verificar URLs obrigatórias
        if not self.EVOLUTION_API_URL.startswith(("http://", "https://")):
            errors.append("EVOLUTION_API_URL deve ser uma URL válida")

        if not self.WEBHOOK_BASE_URL.startswith(("http://", "https://")):
            errors.append("WEBHOOK_BASE_URL deve ser uma URL válida")

        if errors:
            raise ValueError(f"Configurações inválidas: {'; '.join(errors)}")

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Lista de tipos de arquivo permitidos"""
        return [mime.strip() for mime in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def is_development(self) -> bool:
        """Verificar se está em ambiente de desenvolvimento"""
        return self.ENVIRONMENT == "development" or self.DEBUG

    @property
    def database_url_sync(self) -> str:
        """URL de banco de dados síncrona (para SQLAlchemy)"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

    @property
    def database_url_async(self) -> str:
        """URL de banco de dados assíncrona"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Instância global de configurações
settings = Settings()

# Função para recarregar configurações (útil para testes)
def reload_settings():
    """Recarregar configurações"""
    global settings
    settings = Settings()
    return settings
