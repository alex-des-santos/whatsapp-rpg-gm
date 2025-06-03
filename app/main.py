"""
Aplicação principal do WhatsApp RPG Game Master
Implementa um sistema completo de Game Master automatizado para WhatsApp
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Importações internas
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging
from app.core.exceptions import AppException, handle_app_exception
from app.api.endpoints import character, health, webhook
from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService
from app.services.game_state_service import GameStateService

# Setup de logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    logger.info("🚀 Iniciando WhatsApp RPG Game Master...")
    
    try:
        # Validação de configurações críticas
        settings.validate_critical_settings()
        logger.info("✅ Configurações validadas com sucesso")
        
        # Inicialização do banco de dados
        await init_db()
        logger.info("✅ Banco de dados inicializado")
        
        # Inicialização dos serviços
        ai_service = AIService()
        await ai_service.initialize()
        app.state.ai_service = ai_service
        logger.info("✅ Serviço de IA inicializado")
        
        whatsapp_service = WhatsAppService()
        await whatsapp_service.initialize()
        app.state.whatsapp_service = whatsapp_service
        logger.info("✅ Serviço WhatsApp inicializado")
        
        game_state_service = GameStateService()
        await game_state_service.initialize()
        app.state.game_state_service = game_state_service
        logger.info("✅ Serviço de estado do jogo inicializado")
        
        logger.info("🎮 WhatsApp RPG GM iniciado com sucesso!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erro durante inicialização: {str(e)}")
        raise
    
    finally:
        # Cleanup durante shutdown
        logger.info("🔄 Encerrando WhatsApp RPG Game Master...")
        
        # Cleanup dos serviços
        if hasattr(app.state, 'ai_service'):
            await app.state.ai_service.cleanup()
            logger.info("✅ Serviço de IA encerrado")
            
        if hasattr(app.state, 'whatsapp_service'):
            await app.state.whatsapp_service.cleanup()
            logger.info("✅ Serviço WhatsApp encerrado")
            
        if hasattr(app.state, 'game_state_service'):
            await app.state.game_state_service.cleanup()
            logger.info("✅ Serviço de estado encerrado")
        
        logger.info("👋 WhatsApp RPG GM encerrado com sucesso!")


# Criação da aplicação FastAPI
app = FastAPI(
    title="WhatsApp RPG Game Master",
    description="""
    Sistema completo de Game Master automatizado para WhatsApp
    
    ## Funcionalidades Principais
    
    * **Gestão de Personagens**: Criação, edição e gerenciamento de personagens D&D 5e
    * **Integração WhatsApp**: Comunicação através da Evolution API
    * **IA Avançada**: Game Master inteligente com múltiplos provedores de IA
    * **Sistema de RPG**: Rolagem de dados, combate e progressão
    * **Estado Persistente**: Manutenção do mundo e sessões de jogo
    
    ## Endpoints Principais
    
    * `/api/character/` - Gerenciamento de personagens
    * `/webhook/` - Integração WhatsApp
    * `/health/` - Monitoramento e saúde do sistema
    """,
    version="1.0.0",
    contact={
        "name": "WhatsApp RPG GM Team",
        "email": "contato@whatsapprpg.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# ==========================================
# MIDDLEWARE
# ==========================================

# CORS middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Trusted host middleware para segurança
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de requests
    """
    start_time = time.time()
    
    # Log da request
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Processar request
    response = await call_next(request)
    
    # Log da response
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """
    Middleware para adicionar headers de segurança
    """
    response = await call_next(request)
    
    # Headers de segurança
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


# ==========================================
# EXCEPTION HANDLERS
# ==========================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handler para exceções customizadas da aplicação
    """
    return await handle_app_exception(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler para exceções HTTP
    """
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} - "
        f"Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """
    Handler para erros internos do servidor
    """
    logger.error(
        f"Internal Server Error: {str(exc)} - Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "Um erro interno ocorreu. Tente novamente mais tarde.",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


# ==========================================
# ROUTERS
# ==========================================

# Inclusão dos routers
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Checks"]
)

app.include_router(
    character.router,
    prefix="/api/character",
    tags=["Character Management"]
)

app.include_router(
    webhook.router,
    prefix="/webhook",
    tags=["WhatsApp Integration"]
)


# ==========================================
# STATIC FILES
# ==========================================

# Servir arquivos estáticos se existirem
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================================
# ROOT ENDPOINTS
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz com informações da aplicação
    """
    return {
        "message": "WhatsApp RPG Game Master API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
        "health": "/health",
        "status": "operational"
    }


@app.get("/info", tags=["Root"])
async def app_info():
    """
    Informações detalhadas da aplicação
    """
    return {
        "name": "WhatsApp RPG Game Master",
        "version": "1.0.0",
        "description": "Sistema de Game Master automatizado para WhatsApp",
        "environment": settings.ENVIRONMENT,
        "features": {
            "character_management": True,
            "whatsapp_integration": True,
            "ai_game_master": True,
            "dice_rolling": True,
            "persistent_game_state": True
        },
        "apis": {
            "character": "/api/character/",
            "webhook": "/webhook/",
            "health": "/health/"
        },
        "documentation": {
            "openapi": "/docs" if settings.ENVIRONMENT != "production" else None,
            "redoc": "/redoc" if settings.ENVIRONMENT != "production" else None
        }
    }


# ==========================================
# STARTUP VALIDATION
# ==========================================

def validate_startup_requirements():
    """
    Valida requisitos obrigatórios para inicialização
    """
    try:
        # Verificar variáveis críticas
        if not settings.VERIFY_TOKEN or len(settings.VERIFY_TOKEN) < 12:
            raise ValueError("VERIFY_TOKEN deve ter pelo menos 12 caracteres")
        
        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        
        # Verificar pelo menos um provedor de IA
        ai_providers = [
            settings.OPENAI_API_KEY,
            settings.GOOGLE_API_KEY,
            settings.ANTHROPIC_API_KEY
        ]
        
        if not any(ai_providers):
            raise ValueError("Pelo menos um provedor de IA deve ser configurado")
        
        logger.info("✅ Validação de startup concluída com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na validação de startup: {str(e)}")
        sys.exit(1)


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    # Validar requisitos antes de iniciar
    validate_startup_requirements()
    
    # Configuração do uvicorn
    uvicorn_config = {
        "app": "app.main:app",
        "host": settings.APP_HOST,
        "port": settings.APP_PORT,
        "log_level": settings.LOG_LEVEL.lower(),
        "reload": settings.AUTO_RELOAD and settings.ENVIRONMENT == "development",
        "workers": 1 if settings.ENVIRONMENT == "development" else 4,
    }
    
    logger.info(f"🚀 Iniciando servidor em {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"📊 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    
    uvicorn.run(**uvicorn_config)