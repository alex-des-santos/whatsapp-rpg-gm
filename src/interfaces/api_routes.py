"""
API Routes - Rotas da API REST
Endpoints para gerenciamento do sistema RPG
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ..core.database import get_async_session, get_redis
from ..core.game_manager import GameManager
from ..rpg.dice_system import DiceSystem, AdvantageType

logger = logging.getLogger(__name__)

router = APIRouter()

# Models para requests
class DiceRollRequest(BaseModel):
    expression: str
    advantage: str = "normal"

class MessageRequest(BaseModel):
    chat_id: str
    message: str

class CharacterCreateRequest(BaseModel):
    name: str
    race: str
    character_class: str
    player_id: str
    session_id: str

# =============================================================================
# Health Check
# =============================================================================
@router.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/status")
async def system_status():
    """Status detalhado do sistema"""
    try:
        # Aqui você verificaria o status real dos serviços
        return {
            "api": "online",
            "database": "online", 
            "redis": "online",
            "evolution_api": "checking...",
            "active_sessions": 0,
            "total_players": 0
        }
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

# =============================================================================
# Statistics
# =============================================================================
@router.get("/stats")
async def get_statistics():
    """Obter estatísticas do sistema"""
    try:
        # Mock data - em produção, viria do GameManager
        return {
            "active_sessions": 3,
            "total_players": 8,
            "dice_rolls": 127,
            "messages_today": 245,
            "characters_created": 12,
            "hitl_triggers": 2
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas")

# =============================================================================
# Dice Rolling
# =============================================================================
@router.post("/dice/roll")
async def roll_dice(request: DiceRollRequest):
    """Rolar dados"""
    try:
        dice_system = DiceSystem()

        # Converter string de vantagem para enum
        advantage_map = {
            "normal": AdvantageType.NORMAL,
            "advantage": AdvantageType.ADVANTAGE,
            "disadvantage": AdvantageType.DISADVANTAGE
        }

        advantage = advantage_map.get(request.advantage, AdvantageType.NORMAL)
        result = dice_system.roll(request.expression, advantage)

        return {
            "expression": result.expression,
            "total": result.total,
            "rolls": result.rolls,
            "modifiers": result.modifiers,
            "is_critical": result.is_critical,
            "is_fumble": result.is_fumble,
            "advantage_type": result.advantage_type.value
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na rolagem: {e}")
        raise HTTPException(status_code=500, detail="Erro na rolagem de dados")

@router.get("/dice/presets")
async def get_dice_presets():
    """Obter presets de dados"""
    return {
        "basic": ["1d4", "1d6", "1d8", "1d10", "1d12", "1d20", "1d100"],
        "combat": ["1d20", "1d8+3", "2d6", "1d4+1"],
        "abilities": ["4d6k3", "3d6", "2d6+6"],
        "saves": ["1d20+2", "1d20+5", "1d20+8"]
    }

# =============================================================================
# Sessions Management
# =============================================================================
@router.get("/sessions")
async def get_sessions():
    """Obter lista de sessões"""
    try:
        # Mock data - em produção, viria do GameManager
        return [
            {
                "id": "session_001",
                "name": "A Maldição de Strahd",
                "state": "active",
                "players": ["player1", "player2", "player3"],
                "current_scene": "Vila de Barovia",
                "last_activity": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "id": "session_002", 
                "name": "Waterdeep: Heist do Dragão",
                "state": "paused",
                "players": ["player4", "player5"],
                "current_scene": "Taverna Yawning Portal",
                "last_activity": "2024-01-01T11:30:00Z",
                "created_at": "2024-01-01T09:00:00Z"
            }
        ]
    except Exception as e:
        logger.error(f"Erro ao obter sessões: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter sessões")

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Obter detalhes de uma sessão"""
    try:
        # Mock data
        return {
            "id": session_id,
            "name": "Sessão de Exemplo",
            "state": "active",
            "players": ["player1", "player2"],
            "current_scene": "Floresta Sombria",
            "world_state": {
                "location": "Estrada do Norte",
                "weather": "chuva leve",
                "time_of_day": "noite"
            },
            "combat_state": None,
            "last_activity": "2024-01-01T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Erro ao obter sessão: {e}")
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

# =============================================================================
# Characters Management
# =============================================================================
@router.get("/characters")
async def get_characters():
    """Obter lista de personagens"""
    try:
        # Mock data
        return [
            {
                "player_id": "player1",
                "session_id": "session_001",
                "name": "Thorin Machado de Ferro",
                "race": "anao",
                "character_class": "guerreiro", 
                "level": 3,
                "hp_current": 28,
                "hp_max": 32,
                "armor_class": 16,
                "strength": 16,
                "dexterity": 12,
                "constitution": 15,
                "intelligence": 10,
                "wisdom": 13,
                "charisma": 8
            },
            {
                "player_id": "player2",
                "session_id": "session_001",
                "name": "Luna Luaverde",
                "race": "elfo",
                "character_class": "mago",
                "level": 3,
                "hp_current": 18,
                "hp_max": 18,
                "armor_class": 12,
                "strength": 8,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 17,
                "wisdom": 15,
                "charisma": 11
            }
        ]
    except Exception as e:
        logger.error(f"Erro ao obter personagens: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter personagens")

@router.get("/characters/{player_id}/{session_id}")
async def get_character(player_id: str, session_id: str):
    """Obter detalhes de um personagem"""
    try:
        # Mock data
        return {
            "player_id": player_id,
            "session_id": session_id,
            "name": "Personagem de Exemplo",
            "race": "humano",
            "character_class": "guerreiro",
            "level": 1,
            "hp_current": 12,
            "hp_max": 12,
            "armor_class": 14,
            "equipment": [
                {"name": "Espada Longa", "type": "weapon", "equipped": True},
                {"name": "Armadura de Couro", "type": "armor", "equipped": True}
            ],
            "spells_known": [],
            "proficiencies": ["athletics", "intimidation"]
        }
    except Exception as e:
        logger.error(f"Erro ao obter personagem: {e}")
        raise HTTPException(status_code=404, detail="Personagem não encontrado")

# =============================================================================
# Activity & Logs
# =============================================================================
@router.get("/activity/recent")
async def get_recent_activity():
    """Obter atividade recente"""
    try:
        return [
            {
                "type": "dice_roll",
                "title": "João rolou 1d20+5 = 18",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "type": "character_created",
                "title": "Maria criou novo personagem: Elara",
                "timestamp": "2024-01-01T11:45:00Z"
            },
            {
                "type": "session_started",
                "title": "Nova sessão iniciada: A Tumba da Aniquilação",
                "timestamp": "2024-01-01T11:30:00Z"
            }
        ]
    except Exception as e:
        logger.error(f"Erro ao obter atividade: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter atividade")

@router.get("/logs")
async def get_logs(level: str = "all", limit: int = 100):
    """Obter logs do sistema"""
    try:
        # Mock data
        logs = [
            {
                "level": "info",
                "message": "Sistema iniciado com sucesso",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "level": "info", 
                "message": "Nova sessão criada: session_001",
                "timestamp": "2024-01-01T10:05:00Z"
            },
            {
                "level": "warning",
                "message": "Conexão com Evolution API instável",
                "timestamp": "2024-01-01T11:00:00Z"
            },
            {
                "level": "error",
                "message": "Falha ao processar mensagem do usuário player3",
                "timestamp": "2024-01-01T11:30:00Z"
            }
        ]

        # Filtrar por nível se especificado
        if level != "all":
            logs = [log for log in logs if log["level"] == level]

        return logs[:limit]

    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter logs")

# =============================================================================
# GM Commands
# =============================================================================
@router.post("/gm/announce")
async def send_global_announcement(request: MessageRequest):
    """Enviar anúncio global"""
    try:
        # Aqui você enviaria a mensagem para todas as sessões ativas
        logger.info(f"Anúncio global enviado: {request.message}")
        return {"status": "sent", "message": "Anúncio enviado com sucesso"}

    except Exception as e:
        logger.error(f"Erro ao enviar anúncio: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar anúncio")

@router.post("/gm/pause-all")
async def pause_all_sessions():
    """Pausar todas as sessões"""
    try:
        # Aqui você pausaria todas as sessões ativas
        logger.info("Todas as sessões foram pausadas")
        return {"status": "paused", "sessions_affected": 3}

    except Exception as e:
        logger.error(f"Erro ao pausar sessões: {e}")
        raise HTTPException(status_code=500, detail="Erro ao pausar sessões")

@router.post("/gm/backup")
async def create_backup(background_tasks: BackgroundTasks):
    """Criar backup do sistema"""
    try:
        # Agendar backup em background
        background_tasks.add_task(perform_backup)
        return {"status": "started", "message": "Backup iniciado"}

    except Exception as e:
        logger.error(f"Erro ao iniciar backup: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar backup")

async def perform_backup():
    """Executar backup em background"""
    try:
        # Implementar lógica de backup real
        logger.info("Backup concluído com sucesso")
    except Exception as e:
        logger.error(f"Erro no backup: {e}")

# =============================================================================
# HITL Management
# =============================================================================
@router.get("/hitl/interventions")
async def get_pending_interventions():
    """Obter intervenções HITL pendentes"""
    try:
        # Mock data
        return [
            {
                "id": "hitl_20240101_120000_player1",
                "session_id": "session_001",
                "player_id": "player1",
                "message": "Quero fazer algo que não está nas regras",
                "trigger_type": "rules_dispute",
                "timestamp": "2024-01-01T12:00:00Z",
                "status": "pending"
            }
        ]
    except Exception as e:
        logger.error(f"Erro ao obter intervenções: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter intervenções")

@router.post("/hitl/resolve/{intervention_id}")
async def resolve_intervention(intervention_id: str, response: str):
    """Resolver intervenção HITL"""
    try:
        # Aqui você resolveria a intervenção com a resposta do GM
        logger.info(f"Intervenção resolvida: {intervention_id}")
        return {"status": "resolved", "intervention_id": intervention_id}

    except Exception as e:
        logger.error(f"Erro ao resolver intervenção: {e}")
        raise HTTPException(status_code=500, detail="Erro ao resolver intervenção")

# =============================================================================
# Evolution API Integration
# =============================================================================
@router.get("/whatsapp/status")
async def get_whatsapp_status():
    """Obter status da conexão WhatsApp"""
    try:
        # Mock data - em produção, verificaria o Evolution API
        return {
            "connected": True,
            "instance_name": "rpg-gm-bot",
            "qr_code": None,
            "last_check": "2024-01-01T12:00:00Z",
            "state": "CONNECTED"
        }
    except Exception as e:
        logger.error(f"Erro ao obter status WhatsApp: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter status WhatsApp")

@router.get("/whatsapp/qr")
async def get_qr_code():
    """Obter QR Code para conexão"""
    try:
        # Mock response
        return {
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
            "expires_in": 300
        }
    except Exception as e:
        logger.error(f"Erro ao obter QR Code: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter QR Code")
