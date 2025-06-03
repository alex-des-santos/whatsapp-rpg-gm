"""
Configuração de banco de dados com SQLAlchemy
Implementa conexão e sessões para persistência de dados
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings, get_database_url

# Configuração de logging
logger = logging.getLogger(__name__)

# Base para modelos ORM
Base = declarative_base()

# URL do banco de dados
DATABASE_URL = get_database_url()

# Opções de engine
engine_options = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "pool_size": settings.DB_POOL_SIZE,
    "max_overflow": settings.DB_MAX_OVERFLOW,
    "poolclass": QueuePool,
    "connect_args": {
        # Para PostgreSQL: keepalives
        "keepalives": 1,
        "keepalives_idle": 60,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
}

# Ajustes para SQLite
if DATABASE_URL.startswith("sqlite"):
    engine_options.pop("pool_size", None)
    engine_options.pop("max_overflow", None)
    engine_options.pop("poolclass", None)
    engine_options["connect_args"] = {"check_same_thread": False}

# Criar engine do SQLAlchemy
try:
    engine = create_engine(DATABASE_URL, **engine_options)
    logger.info(f"✅ Banco de dados inicializado: {DATABASE_URL.split('@')[0]}****")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
    raise

# Criar sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency para injeção de sessão de banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """
    Inicializa o banco de dados (criação de tabelas se necessário)
    """
    try:
        # Verificar se pode criar tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas verificadas/criadas com sucesso")
        
        # Verificar conexão
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            logger.info("✅ Conexão com banco de dados testada com sucesso")
            
    except Exception as e:
        logger.error(f"❌ Erro durante inicialização do banco: {str(e)}")
        raise


async def check_db_connection() -> bool:
    """
    Verifica conexão com o banco de dados
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao verificar conexão com banco: {str(e)}")
        return False


def create_tables() -> None:
    """
    Cria todas as tabelas definidas
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        raise


def drop_tables() -> None:
    """
    Remove todas as tabelas (CUIDADO!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ Todas as tabelas foram removidas")
    except Exception as e:
        logger.error(f"❌ Erro ao remover tabelas: {str(e)}")
        raise


# Função para criar tabelas específicas
def create_specific_tables(table_classes: list) -> None:
    """
    Cria tabelas específicas
    
    Args:
        table_classes: Lista de classes de tabelas a serem criadas
    """
    try:
        for table_class in table_classes:
            table_class.__table__.create(bind=engine, checkfirst=True)
            logger.info(f"✅ Tabela {table_class.__tablename__} criada/verificada")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas específicas: {str(e)}")
        raise


# Exportar apenas o necessário
__all__ = [
    "Base", 
    "get_db", 
    "init_db", 
    "create_tables", 
    "drop_tables",
    "create_specific_tables",
    "check_db_connection"
]