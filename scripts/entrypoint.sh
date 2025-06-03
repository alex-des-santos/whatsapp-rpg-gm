#!/bin/bash
# ===========================================
# Entrypoint script para WhatsApp RPG GM
# Inicialização e configuração do container
# ===========================================

set -e  # Exit on any error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Banner de inicialização
echo -e "${BLUE}"
echo "=========================================="
echo "   WhatsApp RPG Game Master v1.0.0"
echo "=========================================="
echo -e "${NC}"

# Verificar se variáveis críticas estão definidas
log "Verificando variáveis de ambiente críticas..."

required_vars=(
    "VERIFY_TOKEN"
    "SECRET_KEY"
    "DATABASE_URL"
    "REDIS_URL"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    log_error "Variáveis de ambiente obrigatórias não definidas:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

log_success "Variáveis de ambiente verificadas"

# Verificar conectividade com banco de dados
log "Verificando conectividade com banco de dados..."

max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if python -c "
import sys
import psycopg2
from urllib.parse import urlparse
try:
    # Parse DATABASE_URL
    url = urlparse('$DATABASE_URL')
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database=url.path[1:] if url.path else 'postgres'
    )
    conn.close()
    print('✅ Conexão com banco estabelecida')
    sys.exit(0)
except Exception as e:
    print(f'❌ Erro ao conectar: {e}')
    sys.exit(1)
"; then
        log_success "Banco de dados acessível"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            log_error "Não foi possível conectar ao banco após $max_attempts tentativas"
            exit 1
        fi
        
        log_warning "Tentativa $attempt/$max_attempts falhou. Aguardando 2 segundos..."
        sleep 2
        ((attempt++))
    fi
done

# Verificar conectividade com Redis
log "Verificando conectividade com Redis..."

max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if python -c "
import sys
import redis
from urllib.parse import urlparse
try:
    url = urlparse('$REDIS_URL')
    r = redis.Redis.from_url('$REDIS_URL')
    r.ping()
    print('✅ Conexão com Redis estabelecida')
    sys.exit(0)
except Exception as e:
    print(f'❌ Erro ao conectar: {e}')
    sys.exit(1)
"; then
        log_success "Redis acessível"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            log_warning "Redis não acessível após $max_attempts tentativas (continuando...)"
            break
        fi
        
        log_warning "Tentativa $attempt/$max_attempts falhou. Aguardando 1 segundo..."
        sleep 1
        ((attempt++))
    fi
done

# Executar migrações de banco
if [ "${SKIP_MIGRATIONS:-false}" != "true" ]; then
    log "Executando migrações de banco de dados..."
    
    if alembic upgrade head; then
        log_success "Migrações executadas com sucesso"
    else
        log_warning "Falha nas migrações (continuando...)"
    fi
else
    log_warning "Migrações puladas (SKIP_MIGRATIONS=true)"
fi

# Criar diretórios necessários
log "Criando diretórios necessários..."

directories=(
    "/app/data"
    "/app/logs"
    "/app/sessions"
    "/app/characters"
    "/app/backups"
    "/app/ai_configs"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_success "Diretório criado: $dir"
    fi
done

# Ajustar permissões
chmod -R 755 /app/data /app/logs /app/sessions /app/characters /app/backups /app/ai_configs

# Validações específicas de ambiente
log "Validando configurações específicas..."

# Verificar comprimento do VERIFY_TOKEN
if [ ${#VERIFY_TOKEN} -lt 12 ]; then
    log_error "VERIFY_TOKEN deve ter pelo menos 12 caracteres"
    exit 1
fi

# Verificar comprimento da SECRET_KEY
if [ ${#SECRET_KEY} -lt 32 ]; then
    log_error "SECRET_KEY deve ter pelo menos 32 caracteres"
    exit 1
fi

log_success "Validações concluídas"

# Health check inicial
log "Executando health check inicial..."

# Aguardar um momento para o serviço ficar disponível
sleep 2

# Se não for especificado comando, usar o padrão
if [ $# -eq 0 ]; then
    log "Iniciando aplicação FastAPI..."
    log_success "🎮 WhatsApp RPG GM iniciado com sucesso!"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    # Executar comando passado como argumento
    log "Executando comando: $*"
    exec "$@"
fi