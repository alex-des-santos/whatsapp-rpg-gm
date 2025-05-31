"""
WhatsApp RPG GM - Aplicação Principal
Mestre de Jogo de RPG com Inteligência Artificial para WhatsApp
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.database import init_db
from src.core.game_manager import GameManager
from src.whatsapp.evolution_client import EvolutionClient
from src.interfaces.api_routes import router as api_router
from src.interfaces.websocket_handler import router as ws_router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Variáveis globais para gerenciadores
game_manager = None
evolution_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    global game_manager, evolution_client

    logger.info("🚀 Iniciando WhatsApp RPG GM...")

    try:
        # Inicializar base de dados
        await init_db()
        logger.info("✅ Base de dados inicializada")

        # Inicializar Game Manager
        game_manager = GameManager()
        app.state.game_manager = game_manager
        logger.info("✅ Game Manager inicializado")

        # Inicializar Evolution Client
        evolution_client = EvolutionClient(
            api_url=settings.EVOLUTION_API_URL,
            api_key=settings.EVOLUTION_API_KEY,
            instance_name=settings.EVOLUTION_INSTANCE_NAME
        )
        app.state.evolution_client = evolution_client

        # Verificar conexão com Evolution API
        if await evolution_client.check_connection():
            logger.info("✅ Conexão com Evolution API estabelecida")
        else:
            logger.warning("⚠️ Não foi possível conectar com Evolution API")

        logger.info("🎮 WhatsApp RPG GM iniciado com sucesso!")

        yield

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar aplicação: {e}")
        raise

    finally:
        logger.info("🛑 Encerrando WhatsApp RPG GM...")
        if evolution_client:
            await evolution_client.close()

# Criar aplicação FastAPI
app = FastAPI(
    title="WhatsApp RPG GM",
    description="Mestre de Jogo de RPG com IA para WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>WhatsApp RPG GM</title></head>
            <body>
                <h1>🎲 WhatsApp RPG GM</h1>
                <p>Sistema inicializado com sucesso!</p>
                <ul>
                    <li><a href="/docs">Documentação da API</a></li>
                    <li><a href="/api/health">Status de Saúde</a></li>
                    <li><a href="/api/stats">Estatísticas</a></li>
                </ul>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        status = {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "api": "online",
                "database": "checking...",
                "redis": "checking...",
                "evolution_api": "checking..."
            }
        }

        # Verificar serviços se disponíveis
        if hasattr(app.state, 'game_manager'):
            status["services"]["database"] = "online"
            status["services"]["redis"] = "online"

        if hasattr(app.state, 'evolution_client'):
            evolution_status = await app.state.evolution_client.check_connection()
            status["services"]["evolution_api"] = "online" if evolution_status else "offline"

        return status

    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        raise HTTPException(status_code=500, detail="Sistema não saudável")

@app.get("/webhook")
async def webhook_validation(hub_challenge: str = None):
    """Validação de webhook para Evolution API"""
    if hub_challenge:
        return {"hub.challenge": hub_challenge}
    return {"status": "webhook_ready"}

@app.post("/webhook")
async def webhook_handler(request):
    """Processar mensagens recebidas via webhook"""
    try:
        if not hasattr(app.state, 'game_manager'):
            raise HTTPException(status_code=503, detail="Game Manager não disponível")

        # Processar mensagem via Game Manager
        await app.state.game_manager.process_webhook_message(request)

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Erro no processamento do webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro no processamento")

if __name__ == "__main__":
    logger.info("🎮 Iniciando WhatsApp RPG GM...")

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=1,  # Para desenvolvimento
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
