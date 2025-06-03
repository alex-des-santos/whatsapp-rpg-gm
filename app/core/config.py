"""
Configurações da aplicação WhatsApp RPG Game Master
Implementa validação robusta de variáveis de ambiente
"""

import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

from pydantic import BaseSettings, Field, validator, AnyUrl
from pydantic.env_settings import SettingsSourceCallable


class Settings(BaseSettings):
    """
    Configurações da aplicação com validação robusta
    Implementa todas as recomendações de verificação de variáveis de ambiente
    """
    
    # ==========================================
    # CONFIGURAÇÕES BÁSICAS
    # ==========================================
    
    APP_NAME: str = "WhatsApp RPG Game Master"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema de Game Master automatizado para WhatsApp"
    
    # Ambiente de execução
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Configurações de servidor
    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")
    AUTO_RELOAD: bool = Field(default=True, env="AUTO_RELOAD")
    
    # ==========================================
    # SEGURANÇA - VALIDAÇÃO CRÍTICA
    # ==========================================
    
    # Token de verificação do WhatsApp (CRÍTICO)
    VERIFY_TOKEN: str = Field(min_length=12, env="VERIFY_TOKEN")
    
    # Chave secreta para JWT (CRÍTICA)
    SECRET_KEY: str = Field(min_length=32, env="SECRET_KEY")
    
    # Algoritmo de hash para senhas
    PASSWORD_HASH_ALGORITHM: str = Field(default="bcrypt", env="PASSWORD_HASH_ALGORITHM")
    PASSWORD_SALT_ROUNDS: int = Field(default=12, env="PASSWORD_SALT_ROUNDS")
    
    # JWT settings
    JWT_EXPIRATION_MINUTES: int = Field(default=1440, env="JWT_EXPIRATION_MINUTES")
    
    @validator('VERIFY_TOKEN')
    def validate_verify_token(cls, v):
        """Validação específica do VERIFY_TOKEN"""
        if not v or len(v.strip()) < 12:
            raise ValueError("VERIFY_TOKEN deve ter pelo menos 12 caracteres para segurança adequada")
        
        # Verificar se não é um valor padrão inseguro
        insecure_defaults = [
            "123456789012", "verify_token_12", "default_token_", 
            "whatsapp_token", "rpg_token_123"
        ]
        
        if v.lower() in [token.lower() for token in insecure_defaults]:
            raise ValueError("VERIFY_TOKEN não pode usar valores padrão inseguros")
        
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validação específica da SECRET_KEY"""
        if not v or len(v.strip()) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        
        # Verificar se não é um valor padrão inseguro
        insecure_keys = [
            "your_secret_key_here", "secret_key_12345", "default_secret",
            "mysecretkey", "secretkey123"
        ]
        
        if v.lower() in [key.lower() for key in insecure_keys]:
            raise ValueError("SECRET_KEY não pode usar valores padrão inseguros")
        
        return v
    
    # ==========================================
    # WHATSAPP EVOLUTION API - VALIDAÇÃO CRÍTICA
    # ==========================================
    
    # URLs e credenciais da Evolution API
    EVOLUTION_API_URL: AnyUrl = Field(env="EVOLUTION_API_URL")
    EVOLUTION_API_KEY: str = Field(min_length=10, env="EVOLUTION_API_KEY")
    INSTANCE_NAME: str = Field(min_length=3, env="INSTANCE_NAME")
    
    # Configurações de webhook
    WEBHOOK_URL: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    WEBHOOK_RETRY_ATTEMPTS: int = Field(default=3, env="WEBHOOK_RETRY_ATTEMPTS")
    
    @validator('EVOLUTION_API_URL')
    def validate_evolution_api_url(cls, v):
        """Validação da URL da Evolution API"""
        if not v:
            raise ValueError("EVOLUTION_API_URL é obrigatória")
        
        url_str = str(v)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError("EVOLUTION_API_URL deve começar com http:// ou https://")
        
        # Verificar se não é uma URL de exemplo
        example_urls = [
            "https://sua-evolution-api.com",
            "http://localhost:8080",
            "https://example.com"
        ]
        
        if url_str in example_urls:
            raise ValueError("EVOLUTION_API_URL não pode usar URLs de exemplo")
        
        return v
    
    @validator('EVOLUTION_API_KEY')
    def validate_evolution_api_key(cls, v):
        """Validação da chave da Evolution API"""
        if not v or len(v.strip()) < 10:
            raise ValueError("EVOLUTION_API_KEY deve ter pelo menos 10 caracteres")
        
        # Verificar valores de exemplo
        example_keys = [
            "sua_chave_evolution_api", "api_key_example", "evolution_key_123"
        ]
        
        if v in example_keys:
            raise ValueError("EVOLUTION_API_KEY não pode usar valores de exemplo")
        
        return v
    
    # ==========================================
    # INTELIGÊNCIA ARTIFICIAL - VALIDAÇÃO POR PROVEDOR
    # ==========================================
    
    # Provedor principal de IA
    AI_PROVIDER: str = Field(default="openai", env="AI_PROVIDER")
    
    # Chaves de API para diferentes provedores
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Configurações para IA local
    LOCAL_LLM_URL: Optional[str] = Field(default=None, env="LOCAL_LLM_URL")
    LOCAL_LLM_MODEL: str = Field(default="llama2", env="LOCAL_LLM_MODEL")
    
    # Parâmetros de IA
    AI_MAX_TOKENS: int = Field(default=2000, env="AI_MAX_TOKENS")
    AI_TEMPERATURE: float = Field(default=0.7, env="AI_TEMPERATURE")
    AI_TOP_P: float = Field(default=0.9, env="AI_TOP_P")
    
    @validator('AI_PROVIDER')
    def validate_ai_provider(cls, v):
        """Validação do provedor de IA"""
        valid_providers = ["openai", "google", "anthropic", "local"]
        if v not in valid_providers:
            raise ValueError(f"AI_PROVIDER deve ser um de: {', '.join(valid_providers)}")
        return v
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v, values):
        """Validação da chave OpenAI"""
        if values.get('AI_PROVIDER') == 'openai' and not v:
            raise ValueError("OPENAI_API_KEY é obrigatória quando AI_PROVIDER=openai")
        
        if v and not v.startswith('sk-'):
            raise ValueError("OPENAI_API_KEY deve começar com 'sk-'")
        
        if v and v == "sk-sua_chave_openai":
            raise ValueError("OPENAI_API_KEY não pode usar valor de exemplo")
        
        return v
    
    @validator('GOOGLE_API_KEY')
    def validate_google_key(cls, v, values):
        """Validação da chave Google AI"""
        if values.get('AI_PROVIDER') == 'google' and not v:
            raise ValueError("GOOGLE_API_KEY é obrigatória quando AI_PROVIDER=google")
        
        if v and v == "sua_chave_google_ai":
            raise ValueError("GOOGLE_API_KEY não pode usar valor de exemplo")
        
        return v
    
    @validator('ANTHROPIC_API_KEY')
    def validate_anthropic_key(cls, v, values):
        """Validação da chave Anthropic"""
        if values.get('AI_PROVIDER') == 'anthropic' and not v:
            raise ValueError("ANTHROPIC_API_KEY é obrigatória quando AI_PROVIDER=anthropic")
        
        if v and not v.startswith('sk-ant-'):
            raise ValueError("ANTHROPIC_API_KEY deve começar com 'sk-ant-'")
        
        if v and v == "sk-ant-sua_chave_anthropic":
            raise ValueError("ANTHROPIC_API_KEY não pode usar valor de exemplo")
        
        return v
    
    # ==========================================
    # BANCO DE DADOS - VALIDAÇÃO CRÍTICA
    # ==========================================
    
    # URL completa do banco
    DATABASE_URL: str = Field(env="DATABASE_URL")
    
    # Configurações individuais (para referência)
    DB_HOST: str = Field(default="postgres", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_NAME: str = Field(default="rpg_db", env="DB_NAME")
    DB_USER: str = Field(default="rpg_user", env="DB_USER")
    DB_PASSWORD: str = Field(min_length=8, env="DB_PASSWORD")
    
    # Pool de conexões
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validação da URL do banco de dados"""
        if not v:
            raise ValueError("DATABASE_URL é obrigatória")
        
        if not v.startswith(('postgresql://', 'postgres://', 'sqlite:///')):
            raise ValueError("DATABASE_URL deve usar PostgreSQL ou SQLite")
        
        # Verificar se não é URL de exemplo
        if "rpg_password" in v and "postgres:5432" in v:
            raise ValueError("Configure DATABASE_URL com credenciais reais")
        
        return v
    
    # ==========================================
    # REDIS - VALIDAÇÃO DE CACHE
    # ==========================================
    
    # URL do Redis
    REDIS_URL: str = Field(env="REDIS_URL")
    
    # Configurações individuais
    REDIS_HOST: str = Field(default="redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_TTL: int = Field(default=3600, env="REDIS_TTL")
    
    @validator('REDIS_URL')
    def validate_redis_url(cls, v):
        """Validação da URL do Redis"""
        if not v:
            raise ValueError("REDIS_URL é obrigatória")
        
        if not v.startswith('redis://'):
            raise ValueError("REDIS_URL deve começar com 'redis://'")
        
        return v
    
    # ==========================================
    # LOGGING E MONITORAMENTO
    # ==========================================
    
    # Configurações de log
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_MAX_SIZE: int = Field(default=10, env="LOG_MAX_SIZE")  # MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Monitoramento
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    ENABLE_DETAILED_HEALTH_CHECKS: bool = Field(default=True, env="ENABLE_DETAILED_HEALTH_CHECKS")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validação do nível de log"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL deve ser um de: {', '.join(valid_levels)}")
        return v.upper()
    
    # ==========================================
    # RPG ESPECÍFICO
    # ==========================================
    
    # Sistema de RPG
    DEFAULT_RPG_SYSTEM: str = Field(default="dnd5e", env="DEFAULT_RPG_SYSTEM")
    MAX_CHARACTERS_PER_PLAYER: int = Field(default=3, env="MAX_CHARACTERS_PER_PLAYER")
    MAX_CHARACTER_LEVEL: int = Field(default=20, env="MAX_CHARACTER_LEVEL")
    AUTO_XP_PER_SESSION: int = Field(default=100, env="AUTO_XP_PER_SESSION")
    ALLOW_CUSTOM_CHARACTERS: bool = Field(default=True, env="ALLOW_CUSTOM_CHARACTERS")
    
    # ==========================================
    # BACKUP E STORAGE
    # ==========================================
    
    # Configurações de backup
    ENABLE_AUTO_BACKUP: bool = Field(default=True, env="ENABLE_AUTO_BACKUP")
    BACKUP_INTERVAL_HOURS: int = Field(default=24, env="BACKUP_INTERVAL_HOURS")
    MAX_BACKUP_FILES: int = Field(default=7, env="MAX_BACKUP_FILES")
    BACKUP_COMPRESSION: str = Field(default="gzip", env="BACKUP_COMPRESSION")
    
    # ==========================================
    # CORS E SEGURANÇA WEB
    # ==========================================
    
    # CORS
    ENABLE_CORS: bool = Field(default=True, env="ENABLE_CORS")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Hosts permitidos
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS"
    )
    
    # ==========================================
    # CONFIGURAÇÕES REGIONAIS
    # ==========================================
    
    # Timezone e idioma
    TIMEZONE: str = Field(default="America/Sao_Paulo", env="TIMEZONE")
    DEFAULT_LANGUAGE: str = Field(default="pt-BR", env="DEFAULT_LANGUAGE")
    DATE_FORMAT: str = Field(default="%d/%m/%Y %H:%M:%S", env="DATE_FORMAT")
    
    # ==========================================
    # UPLOAD E ARQUIVOS
    # ==========================================
    
    # Configurações de upload
    MAX_UPLOAD_SIZE: int = Field(default=10, env="MAX_UPLOAD_SIZE")  # MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".png", ".jpg", ".jpeg", ".gif", ".pdf", ".txt"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # ==========================================
    # VALIDAÇÃO GERAL DA APLICAÇÃO
    # ==========================================
    
    def validate_critical_settings(self) -> None:
        """
        Validação crítica de todas as configurações obrigatórias
        Chamada durante a inicialização da aplicação
        """
        errors = []
        
        # Verificar se pelo menos um provedor de IA está configurado
        ai_providers_configured = any([
            self.OPENAI_API_KEY,
            self.GOOGLE_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.LOCAL_LLM_URL
        ])
        
        if not ai_providers_configured:
            errors.append("Pelo menos um provedor de IA deve ser configurado")
        
        # Verificar consistência do provedor selecionado
        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY é obrigatória quando AI_PROVIDER=openai")
        elif self.AI_PROVIDER == "google" and not self.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY é obrigatória quando AI_PROVIDER=google")
        elif self.AI_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY é obrigatória quando AI_PROVIDER=anthropic")
        elif self.AI_PROVIDER == "local" and not self.LOCAL_LLM_URL:
            errors.append("LOCAL_LLM_URL é obrigatória quando AI_PROVIDER=local")
        
        # Verificar configurações de produção
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                errors.append("DEBUG deve ser False em produção")
            
            if self.AUTO_RELOAD:
                errors.append("AUTO_RELOAD deve ser False em produção")
            
            if "localhost" in str(self.EVOLUTION_API_URL):
                errors.append("EVOLUTION_API_URL não deve usar localhost em produção")
        
        # Se houver erros, interromper a aplicação
        if errors:
            error_msg = "❌ Erros críticos de configuração:\n" + "\n".join(f"  • {error}" for error in errors)
            print(error_msg)
            sys.exit(1)
    
    # ==========================================
    # CONFIGURAÇÃO DO PYDANTIC
    # ==========================================
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
        extra = "forbid"  # Não permitir campos extras
        
        # Fonte customizada para variáveis de ambiente
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


# ==========================================
# INSTÂNCIA GLOBAL DE CONFIGURAÇÕES
# ==========================================

# Criar instância global das configurações
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Erro ao carregar configurações: {str(e)}")
    print("💡 Verifique se o arquivo .env está configurado corretamente")
    print("📖 Consulte o arquivo .env.example para referência")
    sys.exit(1)


# ==========================================
# FUNÇÕES UTILITÁRIAS
# ==========================================

def get_database_url() -> str:
    """Retorna a URL do banco de dados"""
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Retorna a URL do Redis"""
    return settings.REDIS_URL


def is_development() -> bool:
    """Verifica se está em ambiente de desenvolvimento"""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Verifica se está em ambiente de produção"""
    return settings.ENVIRONMENT == "production"


def get_ai_config() -> Dict[str, Any]:
    """Retorna configuração do provedor de IA ativo"""
    config = {
        "provider": settings.AI_PROVIDER,
        "max_tokens": settings.AI_MAX_TOKENS,
        "temperature": settings.AI_TEMPERATURE,
        "top_p": settings.AI_TOP_P,
    }
    
    if settings.AI_PROVIDER == "openai":
        config["api_key"] = settings.OPENAI_API_KEY
    elif settings.AI_PROVIDER == "google":
        config["api_key"] = settings.GOOGLE_API_KEY
    elif settings.AI_PROVIDER == "anthropic":
        config["api_key"] = settings.ANTHROPIC_API_KEY
    elif settings.AI_PROVIDER == "local":
        config["url"] = settings.LOCAL_LLM_URL
        config["model"] = settings.LOCAL_LLM_MODEL
    
    return config


def get_log_config() -> Dict[str, Any]:
    """Retorna configuração de logging"""
    return {
        "level": settings.LOG_LEVEL,
        "max_size": settings.LOG_MAX_SIZE,
        "backup_count": settings.LOG_BACKUP_COUNT,
    }