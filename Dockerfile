# Dockerfile para aplicação principal WhatsApp RPG GM
FROM python:3.11-slim AS base

# Metadados da imagem
LABEL maintainer="WhatsApp RPG GM Team"
LABEL description="Sistema de Game Master automatizado para WhatsApp"
LABEL version="1.0.0"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criação de usuário não-root para segurança
RUN groupadd -r rpguser && useradd -r -g rpguser rpguser

# Diretório de trabalho
WORKDIR /app

# Cópia e instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cópia do código da aplicação
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Criação de diretórios necessários
RUN mkdir -p /app/data \
             /app/logs \
             /app/sessions \
             /app/characters \
             /app/backups \
             /app/ai_configs \
    && chown -R rpguser:rpguser /app

# Mudança para usuário não-root
USER rpguser

# Porta exposta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script de inicialização
COPY --chown=rpguser:rpguser scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando padrão
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]