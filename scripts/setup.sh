#!/bin/bash
# ===========================================
# Script de setup para WhatsApp RPG GM
# Configura e inicia todos os serviços necessários
# ===========================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parâmetros
SKIP_TESTS=false
FORCE_REBUILD=false
BACKUP=true
DETAILED_OUTPUT=false

# ====================================================
# Funções auxiliares
# ====================================================

# Função para imprimir cabeçalho
print_header() {
    echo -e "\n${BLUE}==================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}==================================================${NC}\n"
}

# Função para imprimir mensagem de sucesso
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Função para imprimir mensagem de erro
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para imprimir mensagem de aviso
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Função para imprimir mensagem de informação
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Função para imprimir progresso
print_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# Função para verificar requisitos
check_requirements() {
    print_header "Verificando requisitos"
    
    # Verificar se Docker está instalado
    if ! command -v docker &> /dev/null; then
        print_error "Docker não encontrado. Por favor, instale o Docker primeiro."
        exit 1
    else
        print_success "Docker encontrado"
    fi
    
    # Verificar se Docker Compose está instalado
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
        exit 1
    else
        print_success "Docker Compose encontrado"
    fi
    
    # Verificar se curl está instalado (para health checks)
    if ! command -v curl &> /dev/null; then
        print_warning "curl não encontrado. Alguns testes podem falhar."
    else
        print_success "curl encontrado"
    fi
    
    # Verificar se arquivo .env existe
    if [ ! -f ".env" ]; then
        print_warning ".env não encontrado. Criando a partir do exemplo..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env criado a partir de .env.example"
            print_warning "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais reais antes de continuar!"
            echo
            echo "Deseja editar o arquivo .env agora? (s/n)"
            read -r response
            if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
                ${EDITOR:-nano} .env
            fi
        else
            print_error ".env.example não encontrado. Não foi possível criar .env."
            exit 1
        fi
    else
        print_success ".env encontrado"
    fi
}

# Função para criar diretórios de volumes
create_volume_dirs() {
    print_header "Criando diretórios de volumes"
    
    # Lista de diretórios
    volume_dirs=(
        "volumes/game_data"
        "volumes/logs"
        "volumes/sessions"
        "volumes/characters"
        "volumes/backups"
        "volumes/ai_configs"
        "volumes/gui_data"
    )
    
    # Criar diretórios
    for dir in "${volume_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Diretório $dir criado"
        else
            print_info "Diretório $dir já existe"
        fi
    done
    
    # Permissões
    chmod -R 755 volumes/
    print_success "Permissões configuradas"
}

# Função para fazer backup
backup_data() {
    if [ "$BACKUP" = true ]; then
        print_header "Fazendo backup dos dados existentes"
        
        # Verificar se existem dados para backup
        if [ -z "$(ls -A volumes/game_data 2>/dev/null)" ] && [ -z "$(ls -A volumes/characters 2>/dev/null)" ]; then
            print_info "Nenhum dado encontrado para backup"
            return
        fi
        
        # Criar diretório de backup
        backup_dir="volumes/backups/backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Backup de diretórios importantes
        for dir in game_data characters sessions; do
            if [ -d "volumes/$dir" ] && [ -n "$(ls -A volumes/$dir 2>/dev/null)" ]; then
                print_step "Fazendo backup de $dir..."
                tar czf "$backup_dir/$dir.tar.gz" -C volumes "$dir"
                print_success "Backup de $dir concluído"
            fi
        done
        
        print_success "Backup completo: $backup_dir"
    else
        print_info "Backup pulado (--skip-backup)"
    fi
}

# Função para parar containers existentes
stop_containers() {
    print_header "Parando containers existentes"
    
    # Verificar se existem containers rodando
    if docker-compose ps | grep -q "Up"; then
        print_step "Parando containers..."
        docker-compose down
        print_success "Containers parados"
    else
        print_info "Nenhum container rodando"
    fi
}

# Função para construir e iniciar containers
start_containers() {
    print_header "Construindo e iniciando containers"
    
    if [ "$FORCE_REBUILD" = true ]; then
        print_step "Forçando rebuild completo..."
        docker-compose build --no-cache
    else
        print_step "Construindo containers (se necessário)..."
        docker-compose build
    fi
    
    print_step "Iniciando containers..."
    docker-compose up -d
    
    print_success "Containers iniciados"
}

# Função para verificar saúde do sistema
check_health() {
    print_header "Verificando saúde do sistema"
    
    print_step "Aguardando inicialização completa..."
    sleep 10
    
    # Verificar health check básico
    print_step "Verificando health check básico..."
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Health check básico OK"
    else
        print_error "Health check básico falhou"
        print_warning "Verifique os logs para mais detalhes: docker-compose logs whatsapp_rpg_gm"
        return 1
    fi
    
    # Verificar health check detalhado
    if [ "$DETAILED_OUTPUT" = true ]; then
        print_step "Verificando health check detalhado..."
        
        health_output=$(curl -s http://localhost:8000/health/detailed)
        
        if echo "$health_output" | grep -q "healthy"; then
            print_success "Health check detalhado OK"
            echo
            echo "$health_output" | grep -A 1 "status"
        else
            print_error "Health check detalhado falhou"
            echo
            echo "$health_output" | grep -A 5 "error"
            return 1
        fi
    fi
    
    return 0
}

# Função para executar testes
run_tests() {
    if [ "$SKIP_TESTS" = false ]; then
        print_header "Executando testes"
        
        print_step "Executando testes unitários..."
        if docker-compose exec -T whatsapp_rpg_gm pytest -m unit; then
            print_success "Testes unitários OK"
        else
            print_error "Testes unitários falharam"
            return 1
        fi
        
        print_step "Executando testes de duplicidade..."
        if docker-compose exec -T whatsapp_rpg_gm pytest tests/test_character/test_duplicates.py; then
            print_success "Testes de duplicidade OK"
        else
            print_error "Testes de duplicidade falharam"
            return 1
        fi
        
        print_success "Todos os testes passaram!"
    else
        print_info "Testes pulados (--skip-tests)"
    fi
    
    return 0
}

# Função para mostrar informações finais
show_final_info() {
    print_header "🎮 WhatsApp RPG Game Master Pronto!"
    
    echo -e "📊 ${CYAN}Dashboard:${NC} http://localhost:8501"
    echo -e "📝 ${CYAN}API Docs:${NC} http://localhost:8000/docs"
    echo -e "🩺 ${CYAN}Health Check:${NC} http://localhost:8000/health/detailed"
    echo
    echo -e "${YELLOW}Para configurar o webhook do WhatsApp, use:${NC}"
    echo -e "  URL: http://seu-servidor:8000/webhook/message"
    echo
    echo -e "${GREEN}Para verificar logs:${NC}"
    echo -e "  docker-compose logs -f whatsapp_rpg_gm"
    echo
    echo -e "${BLUE}Para mais informações, consulte o README.md${NC}"
}

# Função para parsing de argumentos
parse_args() {
    for arg in "$@"; do
        case $arg in
            --skip-tests)
                SKIP_TESTS=true
                ;;
            --force-rebuild)
                FORCE_REBUILD=true
                ;;
            --skip-backup)
                BACKUP=false
                ;;
            --detailed)
                DETAILED_OUTPUT=true
                ;;
            --help)
                echo "Uso: ./setup.sh [opções]"
                echo
                echo "Opções:"
                echo "  --skip-tests      Pula execução de testes"
                echo "  --force-rebuild   Força rebuild de todos os containers"
                echo "  --skip-backup     Pula backup de dados existentes"
                echo "  --detailed        Mostra saída detalhada"
                echo "  --help            Mostra esta ajuda"
                echo
                exit 0
                ;;
        esac
    done
}

# ====================================================
# Fluxo principal
# ====================================================

# Parse argumentos
parse_args "$@"

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml não encontrado. Execute este script do diretório raiz do projeto."
    exit 1
fi

# Mostrar cabeçalho
clear
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}         WhatsApp RPG Game Master Setup           ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo
echo -e "${CYAN}Este script configurará e iniciará o ambiente completo.${NC}"
echo

# Verificar requisitos
check_requirements

# Criar diretórios de volumes
create_volume_dirs

# Fazer backup se necessário
backup_data

# Parar containers existentes
stop_containers

# Construir e iniciar containers
start_containers

# Verificar saúde do sistema
if ! check_health; then
    print_warning "Houve problemas na verificação de saúde. O sistema pode não estar funcionando corretamente."
    
    echo
    echo "Deseja ver os logs para diagnóstico? (s/n)"
    read -r response
    if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        docker-compose logs whatsapp_rpg_gm
    fi
    
    echo
    echo "Deseja continuar mesmo assim? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        print_error "Setup interrompido."
        exit 1
    fi
fi

# Executar testes
if ! run_tests; then
    print_warning "Alguns testes falharam. O sistema pode não estar funcionando corretamente."
    
    echo
    echo "Deseja continuar mesmo assim? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        print_error "Setup interrompido."
        exit 1
    fi
fi

# Mostrar informações finais
show_final_info

exit 0