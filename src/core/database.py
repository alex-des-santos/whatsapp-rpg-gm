"""
Configuração e gerenciamento da base de dados
"""

import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis.asyncio as redis
from typing import AsyncGenerator, Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Metadata para migrations
metadata = MetaData()

# Engines de banco de dados
sync_engine = None
async_engine = None

# Session makers
AsyncSessionLocal = None
SessionLocal = None

# Redis client
redis_client = None

async def init_db():
    """Inicializar conexões com base de dados"""
    global sync_engine, async_engine, AsyncSessionLocal, SessionLocal, redis_client

    try:
        # Criar engines
        sync_engine = create_engine(
            settings.database_url_sync,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.is_development
        )

        async_engine = create_async_engine(
            settings.database_url_async,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.is_development
        )

        # Criar session makers
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        SessionLocal = sessionmaker(
            sync_engine,
            autocommit=False,
            autoflush=False
        )

        # Conectar ao Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

        # Testar conexões
        await test_connections()

        logger.info("✅ Conexões com base de dados inicializadas")

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar base de dados: {e}")
        raise

async def test_connections():
    """Testar conectividade com base de dados"""
    try:
        # Testar PostgreSQL
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Conexão PostgreSQL OK")

        # Testar Redis
        await redis_client.ping()
        logger.info("✅ Conexão Redis OK")

    except Exception as e:
        logger.error(f"❌ Erro nos testes de conexão: {e}")
        raise

async def close_db():
    """Fechar conexões com base de dados"""
    global sync_engine, async_engine, redis_client

    if async_engine:
        await async_engine.dispose()
        logger.info("Conexão async PostgreSQL fechada")

    if sync_engine:
        sync_engine.dispose()
        logger.info("Conexão sync PostgreSQL fechada")

    if redis_client:
        await redis_client.close()
        logger.info("Conexão Redis fechada")

# Dependency para FastAPI - Sessão assíncrona
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obter sessão assíncrona do banco"""
    if not AsyncSessionLocal:
        raise RuntimeError("Base de dados não inicializada")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Erro na sessão de banco: {e}")
            raise
        finally:
            await session.close()

# Dependency para operações síncronas
def get_sync_session() -> Generator[Session, None, None]:
    """Dependency para obter sessão síncrona do banco"""
    if not SessionLocal:
        raise RuntimeError("Base de dados não inicializada")

    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Erro na sessão síncrona: {e}")
        raise
    finally:
        session.close()

# Dependency para Redis
async def get_redis() -> redis.Redis:
    """Dependency para obter cliente Redis"""
    if not redis_client:
        raise RuntimeError("Redis não inicializado")
    return redis_client

# Utility functions para cache
async def cache_set(key: str, value: str, expire: int = 3600):
    """Definir valor no cache"""
    if redis_client:
        await redis_client.setex(key, expire, value)

async def cache_get(key: str) -> str | None:
    """Obter valor do cache"""
    if redis_client:
        return await redis_client.get(key)
    return None

async def cache_delete(key: str):
    """Deletar chave do cache"""
    if redis_client:
        await redis_client.delete(key)

async def cache_exists(key: str) -> bool:
    """Verificar se chave existe no cache"""
    if redis_client:
        return await redis_client.exists(key) > 0
    return False

# Context manager para transações
class DatabaseTransaction:
    """Context manager para transações de banco"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            logger.error(f"Transação revertida devido a erro: {exc_val}")
        else:
            await self.session.commit()

# Utility para paginação
class Pagination:
    """Helper para paginação de resultados"""

    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = max(1, page)
        self.per_page = min(100, max(1, per_page))  # Máximo 100 itens por página

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page

    def paginate_query(self, query):
        """Aplicar paginação a uma query"""
        return query.offset(self.offset).limit(self.limit)
