"""
Configuração do ambiente Alembic para migrações de banco de dados
"""

from logging.config import fileConfig
import sys
import os
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar configurações e modelos
from app.core.config import settings
from app.models.character import Base

# Configuração Alembic
config = context.config

# Interpretar o arquivo de config para logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adicionar MetaData dos modelos para autogeneração
target_metadata = Base.metadata

# Configurar URL do banco
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Executa migrações em modo 'offline'.
    
    Configura o contexto apenas com uma URL
    e não com uma Engine, embora uma Engine também seja aceitável.
    Chamando context.execute() apenas produz SQL na saída.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Executa migrações em modo 'online'.
    
    Neste cenário, precisamos criar uma Engine
    e associar uma conexão com o contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()