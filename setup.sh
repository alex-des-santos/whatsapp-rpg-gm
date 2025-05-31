#!/bin/bash

# =============================================================================
# WhatsApp RPG GM - Script de Instalação Automatizada
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções utilitárias
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."

    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não encontrado. Instale Docker primeiro."
        exit 1
    fi

    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não encontrado. Instale Docker Compose primeiro."
        exit 1
    fi

    log_success "Dependências verificadas"
}

# Configurar ambiente
setup_environment() {
    log_info "Configurando ambiente..."

    # Criar .env se não existir
    if [ ! -f .env ]; then
        log_info "Criando arquivo .env..."
        cp .env.example .env

        # Gerar chave secreta
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/sua-chave-secreta-muito-complexa-e-unica-aqui/$SECRET_KEY/" .env

        log_warning "Configure suas chaves de API no arquivo .env antes de continuar!"
        log_info "Principais configurações necessárias:"
        echo "  - EVOLUTION_API_KEY"
        echo "  - WEBHOOK_BASE_URL"
        echo "  - Pelo menos uma chave de IA (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)"

        read -p "Pressione Enter após configurar o .env para continuar..."
    fi

    # Criar diretórios necessários
    mkdir -p logs data/characters data/campaigns data/prompts

    log_success "Ambiente configurado"
}

# Validar configuração
validate_config() {
    log_info "Validando configuração..."

    # Verificar se .env existe
    if [ ! -f .env ]; then
        log_error "Arquivo .env não encontrado!"
        exit 1
    fi

    # Verificar configurações críticas
    source .env

    if [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY não configurada no .env"
        exit 1
    fi

    if [ -z "$EVOLUTION_API_KEY" ]; then
        log_warning "EVOLUTION_API_KEY não configurada"
    fi

    if [ -z "$WEBHOOK_BASE_URL" ]; then
        log_warning "WEBHOOK_BASE_URL não configurada"
    fi

    # Verificar pelo menos um provedor de IA
    if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
        log_warning "Nenhum provedor de IA configurado. Ollama será usado como fallback."
    fi

    log_success "Configuração validada"
}

# Escolher perfil de instalação
choose_profile() {
    log_info "Escolha o perfil de instalação:"
    echo "1) Básico (apenas serviços essenciais)"
    echo "2) Desenvolvimento (com dashboards)"
    echo "3) Produção (com monitoramento)"
    echo "4) Completo (todos os serviços)"

    read -p "Digite sua escolha (1-4): " choice

    case $choice in
        1)
            PROFILE="basic"
            SERVICES="app postgres redis evolution-api"
            ;;
        2)
            PROFILE="development"
            SERVICES="--profile dashboard"
            ;;
        3)
            PROFILE="production"
            SERVICES="--profile production --profile monitoring"
            ;;
        4)
            PROFILE="complete"
            SERVICES="--profile dashboard --profile monitoring --profile production"
            ;;
        *)
            log_warning "Escolha inválida. Usando perfil básico."
            PROFILE="basic"
            SERVICES="app postgres redis evolution-api"
            ;;
    esac

    log_info "Perfil selecionado: $PROFILE"
}

# Iniciar serviços
start_services() {
    log_info "Iniciando serviços Docker..."

    # Build das imagens
    log_info "Construindo imagens..."
    docker-compose build

    # Iniciar serviços
    log_info "Iniciando containers..."
    if [ "$PROFILE" = "basic" ]; then
        docker-compose up -d $SERVICES
    else
        docker-compose $SERVICES up -d
    fi

    # Aguardar serviços ficarem prontos
    log_info "Aguardando serviços ficarem prontos..."
    sleep 30

    log_success "Serviços iniciados"
}

# Verificar saúde dos serviços
check_health() {
    log_info "Verificando saúde dos serviços..."

    # Verificar API principal
    if curl -s http://localhost:3000/health > /dev/null; then
        log_success "API principal: OK"
    else
        log_error "API principal: FALHA"
    fi

    # Verificar PostgreSQL
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        log_success "PostgreSQL: OK"
    else
        log_error "PostgreSQL: FALHA"
    fi

    # Verificar Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: OK"
    else
        log_error "Redis: FALHA"
    fi

    # Verificar Evolution API
    if curl -s http://localhost:8080 > /dev/null; then
        log_success "Evolution API: OK"
    else
        log_warning "Evolution API: Verificar configuração"
    fi
}

# Mostrar informações finais
show_final_info() {
    log_success "Instalação concluída!"
    echo ""
    echo "==============================================================================="
    echo "🎲 WhatsApp RPG GM está rodando!"
    echo "==============================================================================="
    echo ""
    echo "📱 Interfaces disponíveis:"
    echo "  • API Principal: http://localhost:3000"
    echo "  • Documentação: http://localhost:3000/docs"
    echo "  • Evolution API: http://localhost:8080"

    if [ "$PROFILE" != "basic" ]; then
        echo "  • Dashboard Streamlit: http://localhost:8501"
        echo "  • Interface Gradio: http://localhost:7860"
    fi

    if [[ "$SERVICES" == *"monitoring"* ]]; then
        echo "  • Prometheus: http://localhost:9090"
        echo "  • Grafana: http://localhost:3001"
    fi

    echo ""
    echo "🔧 Próximos passos:"
    echo "  1. Configure sua instância WhatsApp em http://localhost:8080"
    echo "  2. Escaneie o QR Code com WhatsApp Business"
    echo "  3. Configure o webhook para: $WEBHOOK_BASE_URL/webhook"
    echo "  4. Teste enviando /start para o bot"
    echo ""
    echo "📊 Comandos úteis:"
    echo "  • Ver logs: docker-compose logs -f"
    echo "  • Parar serviços: docker-compose down"
    echo "  • Reiniciar: docker-compose restart"
    echo ""
    echo "📚 Documentação completa: README.md"
    echo "==============================================================================="
}

# Função principal
main() {
    echo "==============================================================================="
    echo "🎲 WhatsApp RPG GM - Instalação Automatizada"
    echo "==============================================================================="

    check_dependencies
    setup_environment
    validate_config
    choose_profile
    start_services
    check_health
    show_final_info
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
