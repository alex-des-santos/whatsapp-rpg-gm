# Dockerfile para WhatsApp RPG GM
FROM python:3.11-slim

WORKDIR /app

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar e ativar ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs data

# Expor portas
EXPOSE 3000 8501 7860

# Comando para iniciar o servidor (com privilégios reduzidos)
CMD ["python", "main.py"]