"""
Endpoints de health checks para monitoramento
Implementa verificações abrangentes do sistema
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# Configuração de logging
logger = logging.getLogger(__name__)

# Criação do router
router = APIRouter()


# ==========================================
# HEALTH CHECK BÁSICO
# ==========================================

@router.get(
    "/",
    summary="Health check básico",
    description="Verificação básica de funcionamento da aplicação"
)
async def health_check():
    """
    Health check básico - retorna apenas se a aplicação está respondendo
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WhatsApp RPG Game Master",
        "version": settings.VERSION
    }


# ==========================================
# HEALTH CHECK DETALHADO
# ==========================================

@router.get(
    "/detailed",
    summary="Health check detalhado",
    description="Verificação completa de todos os componentes do sistema"
)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Health check detalhado com verificação de todos os serviços
    Implementa monitoramento abrangente
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WhatsApp RPG Game Master",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    overall_healthy = True
    
    # 1. Verificar banco de dados
    db_health = await check_database_health(db)
    health_data["checks"]["database"] = db_health
    if not db_health["healthy"]:
        overall_healthy = False
    
    # 2. Verificar Redis
    redis_health = await check_redis_health()
    health_data["checks"]["redis"] = redis_health
    if not redis_health["healthy"]:
        overall_healthy = False
    
    # 3. Verificar Evolution API
    whatsapp_health = await check_whatsapp_health()
    health_data["checks"]["whatsapp"] = whatsapp_health
    if not whatsapp_health["healthy"]:
        overall_healthy = False
    
    # 4. Verificar serviços de IA
    ai_health = await check_ai_services_health()
    health_data["checks"]["ai_services"] = ai_health
    if not ai_health["healthy"]:
        overall_healthy = False
    
    # 5. Verificar variáveis de ambiente críticas
    env_health = check_environment_health()
    health_data["checks"]["environment"] = env_health
    if not env_health["healthy"]:
        overall_healthy = False
    
    # 6. Verificar recursos do sistema
    system_health = check_system_resources()
    health_data["checks"]["system"] = system_health
    if not system_health["healthy"]:
        overall_healthy = False
    
    # Status final
    health_data["status"] = "healthy" if overall_healthy else "unhealthy"
    
    # Log se houver problemas
    if not overall_healthy:
        logger.warning(f"Health check failed: {health_data}")
    
    # Retornar status HTTP apropriado
    status_code = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    if not overall_healthy:
        raise HTTPException(status_code=status_code, detail=health_data)
    
    return health_data


# ==========================================
# CHECKS INDIVIDUAIS
# ==========================================

async def check_database_health(db: Session) -> Dict[str, Any]:
    """
    Verifica saúde do banco de dados
    """
    try:
        # Teste de conectividade
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        # Teste de escrita (se possível)
        try:
            db.execute(text("SELECT COUNT(*) FROM characters"))
            can_read_tables = True
        except Exception:
            can_read_tables = False
        
        return {
            "healthy": True,
            "connection": "ok",
            "can_read_tables": can_read_tables,
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "connection": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_redis_health() -> Dict[str, Any]:
    """
    Verifica saúde do Redis
    """
    try:
        # Conectar ao Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # Teste de ping
        pong = redis_client.ping()
        
        # Teste de escrita/leitura
        test_key = "health_check_test"
        redis_client.set(test_key, "test_value", ex=10)
        value = redis_client.get(test_key)
        redis_client.delete(test_key)
        
        can_write = value == b"test_value"
        
        # Informações do servidor
        info = redis_client.info()
        
        return {
            "healthy": True,
            "ping": pong,
            "can_write": can_write,
            "version": info.get("redis_version", "unknown"),
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "ping": False,
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_whatsapp_health() -> Dict[str, Any]:
    """
    Verifica saúde da Evolution API (WhatsApp)
    """
    try:
        # Timeout para requests
        timeout = httpx.Timeout(10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # URL de status da Evolution API
            status_url = f"{settings.EVOLUTION_API_URL}/instance/connectionState/{settings.INSTANCE_NAME}"
            
            headers = {
                "apikey": settings.EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = await client.get(status_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "healthy": True,
                    "connection_state": data.get("instance", {}).get("state", "unknown"),
                    "status_code": response.status_code,
                    "api_url": settings.EVOLUTION_API_URL,
                    "instance": settings.INSTANCE_NAME,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "healthy": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}",
                    "api_url": settings.EVOLUTION_API_URL,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
    except Exception as e:
        logger.error(f"WhatsApp health check failed: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "api_url": settings.EVOLUTION_API_URL,
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_ai_services_health() -> Dict[str, Any]:
    """
    Verifica saúde dos serviços de IA
    """
    ai_checks = {}
    overall_healthy = False
    
    # Verificar provedor principal
    main_provider = settings.AI_PROVIDER
    
    # OpenAI
    if settings.OPENAI_API_KEY:
        ai_checks["openai"] = await check_openai_health()
        if main_provider == "openai":
            overall_healthy = ai_checks["openai"]["healthy"]
    
    # Google AI
    if settings.GOOGLE_API_KEY:
        ai_checks["google"] = await check_google_ai_health()
        if main_provider == "google":
            overall_healthy = ai_checks["google"]["healthy"]
    
    # Anthropic
    if settings.ANTHROPIC_API_KEY:
        ai_checks["anthropic"] = await check_anthropic_health()
        if main_provider == "anthropic":
            overall_healthy = ai_checks["anthropic"]["healthy"]
    
    # Local LLM
    if settings.LOCAL_LLM_URL:
        ai_checks["local"] = await check_local_llm_health()
        if main_provider == "local":
            overall_healthy = ai_checks["local"]["healthy"]
    
    return {
        "healthy": overall_healthy,
        "main_provider": main_provider,
        "providers": ai_checks,
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_openai_health() -> Dict[str, Any]:
    """Verifica saúde da OpenAI API"""
    try:
        timeout = httpx.Timeout(10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Endpoint de models da OpenAI
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers=headers
            )
            
            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_google_ai_health() -> Dict[str, Any]:
    """Verifica saúde da Google AI API"""
    try:
        # Verificação básica da chave
        return {
            "healthy": bool(settings.GOOGLE_API_KEY),
            "configured": bool(settings.GOOGLE_API_KEY),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_anthropic_health() -> Dict[str, Any]:
    """Verifica saúde da Anthropic API"""
    try:
        # Verificação básica da chave
        return {
            "healthy": bool(settings.ANTHROPIC_API_KEY),
            "configured": bool(settings.ANTHROPIC_API_KEY),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def check_local_llm_health() -> Dict[str, Any]:
    """Verifica saúde do LLM local"""
    try:
        if not settings.LOCAL_LLM_URL:
            return {
                "healthy": False,
                "error": "Local LLM URL not configured",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        timeout = httpx.Timeout(10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Verificar endpoint de saúde do Ollama ou similar
            response = await client.get(f"{settings.LOCAL_LLM_URL}/api/tags")
            
            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "url": settings.LOCAL_LLM_URL,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "url": settings.LOCAL_LLM_URL,
            "timestamp": datetime.utcnow().isoformat()
        }


def check_environment_health() -> Dict[str, Any]:
    """
    Verifica variáveis de ambiente críticas
    """
    try:
        issues = []
        
        # Verificar variáveis obrigatórias
        required_vars = {
            "VERIFY_TOKEN": settings.VERIFY_TOKEN,
            "SECRET_KEY": settings.SECRET_KEY,
            "EVOLUTION_API_URL": settings.EVOLUTION_API_URL,
            "EVOLUTION_API_KEY": settings.EVOLUTION_API_KEY,
            "DATABASE_URL": settings.DATABASE_URL,
            "REDIS_URL": settings.REDIS_URL,
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                issues.append(f"{var_name} not set")
        
        # Verificar comprimentos mínimos
        if len(settings.VERIFY_TOKEN) < 12:
            issues.append("VERIFY_TOKEN too short")
        
        if len(settings.SECRET_KEY) < 32:
            issues.append("SECRET_KEY too short")
        
        # Verificar pelo menos um provedor de IA
        ai_providers = [
            settings.OPENAI_API_KEY,
            settings.GOOGLE_API_KEY,
            settings.ANTHROPIC_API_KEY,
            settings.LOCAL_LLM_URL
        ]
        
        if not any(ai_providers):
            issues.append("No AI provider configured")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def check_system_resources() -> Dict[str, Any]:
    """
    Verifica recursos do sistema
    """
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Determinar se está saudável
        healthy = (
            cpu_percent < 90 and
            memory.percent < 90 and
            disk.percent < 90
        )
        
        return {
            "healthy": healthy,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ImportError:
        # psutil não disponível
        return {
            "healthy": True,
            "note": "psutil not available for system monitoring",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ==========================================
# READINESS E LIVENESS PROBES
# ==========================================

@router.get(
    "/readiness",
    summary="Readiness probe para Kubernetes",
    description="Verifica se a aplicação está pronta para receber tráfego"
)
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Readiness probe - verifica se a aplicação está pronta para servir requests
    """
    try:
        # Verificar apenas componentes críticos para servir requests
        
        # 1. Banco de dados deve estar acessível
        db_result = await check_database_health(db)
        if not db_result["healthy"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not ready"
            )
        
        # 2. Variáveis de ambiente críticas devem estar configuradas
        env_result = check_environment_health()
        if not env_result["healthy"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Environment not ready"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Not ready: {str(e)}"
        )


@router.get(
    "/liveness",
    summary="Liveness probe para Kubernetes",
    description="Verifica se a aplicação está viva e funcionando"
)
async def liveness_probe():
    """
    Liveness probe - verifica se a aplicação está viva
    """
    try:
        # Verificação muito básica - apenas se o processo está respondendo
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": "unknown"  # Poderia calcular uptime se necessário
        }
        
    except Exception as e:
        logger.error(f"Liveness probe failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Not alive: {str(e)}"
        )


# ==========================================
# MÉTRICAS BÁSICAS
# ==========================================

@router.get(
    "/metrics",
    summary="Métricas básicas da aplicação",
    description="Retorna métricas básicas para monitoramento"
)
async def basic_metrics(db: Session = Depends(get_db)):
    """
    Métricas básicas da aplicação
    """
    try:
        # Contar personagens ativos
        active_characters = db.execute(
            text("SELECT COUNT(*) FROM characters WHERE is_active = true")
        ).scalar()
        
        # Contar jogadores únicos
        unique_players = db.execute(
            text("SELECT COUNT(DISTINCT player_id) FROM characters")
        ).scalar()
        
        # Estatísticas por classe
        class_stats = db.execute(
            text("""
                SELECT character_class, COUNT(*) as count 
                FROM characters 
                WHERE is_active = true 
                GROUP BY character_class 
                ORDER BY count DESC
            """)
        ).fetchall()
        
        return {
            "active_characters": active_characters,
            "unique_players": unique_players,
            "characters_by_class": [
                {"class": row[0], "count": row[1]} 
                for row in class_stats
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
        )