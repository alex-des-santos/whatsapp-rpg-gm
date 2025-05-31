#!/usr/bin/env python3
"""
WhatsApp RPG GM - Aplicação Principal
Sistema de Mestre de Jogo automatizado via WhatsApp com IA
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger
from dotenv import load_dotenv

from src.core.config import Settings
from src.core.game_manager import GameManager
from src.whatsapp.evolution_client import EvolutionClient
from src.whatsapp.webhook_handler import WebhookHandler
from src.ai.ai_manager import AIManager
from src.rpg.dice_system import DiceSystem
from src.hitl.hitl_manager import HITLManager

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
settings = Settings()

# Configurar logger
logger.add(
    "logs/rpg_gm_{time}.log",
    rotation="1 day",
    retention="30 days",
    level=settings.log_level
)

# Criar aplicação FastAPI
app = FastAPI(
    title="WhatsApp RPG GM",
    description="Sistema de Mestre de Jogo automatizado via WhatsApp com IA",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes globais
game_manager: GameManager = None
evolution_client: EvolutionClient = None
webhook_handler: WebhookHandler = None
ai_manager: AIManager = None
dice_system: DiceSystem = None
hitl_manager: HITLManager = None


@app.on_event("startup")
async def startup_event():
    """Inicializar componentes na inicialização da aplicação"""
    global game_manager, evolution_client, webhook_handler, ai_manager, dice_system, hitl_manager
    
    logger.info("🚀 Iniciando WhatsApp RPG GM...")
    
    try:
        # Inicializar Game Manager
        game_manager = GameManager(settings)
        await game_manager.initialize()
        logger.info("✅ Game Manager inicializado")
        
        # Inicializar AI Manager
        ai_manager = AIManager(settings)
        await ai_manager.initialize()
        logger.info("✅ AI Manager inicializado")
        
        # Inicializar Dice System
        dice_system = DiceSystem()
        logger.info("✅ Dice System inicializado")
        
        # Inicializar HITL Manager
        hitl_manager = HITLManager(settings)
        await hitl_manager.initialize()
        logger.info("✅ HITL Manager inicializado")
        
        # Inicializar Evolution Client
        evolution_client = EvolutionClient(settings)
        await evolution_client.initialize()
        logger.info("✅ Evolution Client inicializado")
        
        # Inicializar Webhook Handler
        webhook_handler = WebhookHandler(
            game_manager, ai_manager, dice_system, hitl_manager, settings
        )
        logger.info("✅ Webhook Handler inicializado")
        
        logger.info("🎲 Sistema WhatsApp RPG GM iniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup na finalização da aplicação"""
    logger.info("🛑 Finalizando WhatsApp RPG GM...")
    
    if evolution_client:
        await evolution_client.cleanup()
    
    if game_manager:
        await game_manager.cleanup()
    
    logger.info("👋 Sistema finalizado")


@app.get("/")
async def root():
    """Endpoint raiz - informações básicas da API"""
    return {
        "message": "🎲 WhatsApp RPG GM API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "components": {
            "evolution_api": evolution_client.is_connected() if evolution_client else False,
            "ai_manager": ai_manager.is_ready() if ai_manager else False,
            "game_manager": game_manager.is_ready() if game_manager else False,
            "dice_system": dice_system.is_ready() if dice_system else False,
            "hitl_manager": hitl_manager.is_ready() if hitl_manager else False
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": str(asyncio.get_event_loop().time()),
            "components": {
                "evolution_api": "ok" if evolution_client and evolution_client.is_connected() else "error",
                "ai_manager": "ok" if ai_manager and ai_manager.is_ready() else "error",
                "game_manager": "ok" if game_manager and game_manager.is_ready() else "error",
                "dice_system": "ok" if dice_system and dice_system.is_ready() else "error",
                "hitl_manager": "ok" if hitl_manager and hitl_manager.is_ready() else "error"
            }
        }
        
        # Verificar se todos os componentes estão OK
        all_healthy = all(status == "ok" for status in health_status["components"].values())
        if not all_healthy:
            health_status["status"] = "degraded"
            
        return health_status
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """Endpoint para receber webhooks do Evolution API"""
    try:
        if not webhook_handler:
            raise HTTPException(status_code=503, detail="Webhook handler não inicializado")
        
        body = await request.body()
        headers = dict(request.headers)
        
        response = await webhook_handler.handle_webhook(body, headers)
        return response
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/setup/instance")
async def setup_instance():
    """Configurar instância do WhatsApp"""
    try:
        if not evolution_client:
            raise HTTPException(status_code=503, detail="Evolution client não inicializado")
        
        result = await evolution_client.create_instance()
        return result
        
    except Exception as e:
        logger.error(f"Erro ao configurar instância: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/qrcode/{instance_name}")
async def get_qrcode(instance_name: str):
    """Obter QR Code para conectar WhatsApp"""
    try:
        if not evolution_client:
            raise HTTPException(status_code=503, detail="Evolution client não inicializado")
        
        qr_code = await evolution_client.get_qr_code(instance_name)
        return {"qr_code": qr_code}
        
    except Exception as e:
        logger.error(f"Erro ao obter QR Code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-message")
async def send_message(data: dict):
    """Enviar mensagem via WhatsApp"""
    try:
        if not evolution_client:
            raise HTTPException(status_code=503, detail="Evolution client não inicializado")
        
        result = await evolution_client.send_message(
            data.get("number"),
            data.get("message"),
            data.get("instance", settings.evolution_instance_name)
        )
        return result
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/status")
async def get_game_status():
    """Obter status atual do jogo"""
    try:
        if not game_manager:
            raise HTTPException(status_code=503, detail="Game manager não inicializado")
        
        status = await game_manager.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status do jogo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dice/roll")
async def roll_dice(data: dict):
    """Rolar dados"""
    try:
        if not dice_system:
            raise HTTPException(status_code=503, detail="Dice system não inicializado")
        
        result = dice_system.roll(data.get("expression", "1d20"))
        return result
        
    except Exception as e:
        logger.error(f"Erro ao rolar dados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hitl/trigger")
async def trigger_hitl(data: dict):
    """Trigger manual do sistema HITL"""
    try:
        if not hitl_manager:
            raise HTTPException(status_code=503, detail="HITL manager não inicializado")
        
        result = await hitl_manager.trigger_intervention(
            data.get("reason", "Manual trigger"),
            data.get("context", {}),
            data.get("priority", "medium")
        )
        return result
        
    except Exception as e:
        logger.error(f"Erro ao trigger HITL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """Função principal para executar a aplicação"""
    logger.info("🎯 Iniciando servidor FastAPI...")
    
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Aplicação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)