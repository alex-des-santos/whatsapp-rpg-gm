# ==========================================
# Script para iniciar WhatsApp RPG GM no Windows 11
# Inicia todos os serviços necessários
# ==========================================

param(
    [switch]$Development = $false,
    [switch]$Production = $false,
    [switch]$CheckServices = $false,
    [switch]$StopServices = $false
)

# Configurar título da janela
$Host.UI.RawUI.WindowTitle = "WhatsApp RPG GM - Executando"

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# ==========================================
# Função para verificar serviços
# ==========================================

function Test-Services {
    Write-Header "Verificando Serviços"
    
    # Verificar PostgreSQL
    $postgresService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($postgresService -and $postgresService.Status -eq "Running") {
        Write-Success "PostgreSQL está rodando"
        
        # Testar conexão        try {
            $env:PGPASSWORD = "rpg_password"
            psql -U postgres -h localhost -d rpg_db -c "SELECT 1;" 2>$null | Out-Null
            Write-Success "Conexão com banco de dados OK"
        } catch {
            Write-Error "Erro ao conectar com PostgreSQL"
        }
    } else {
        Write-Error "PostgreSQL não está rodando"
        Write-Info "Iniciando PostgreSQL..."
        Start-Service postgresql*
    }
    
    # Verificar Redis
    $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
    if ($redisService -and $redisService.Status -eq "Running") {
        Write-Success "Redis está rodando"
        
        # Testar conexão Redis
        try {
            redis-cli ping | Out-Null
            Write-Success "Conexão com Redis OK"
        } catch {
            Write-Error "Erro ao conectar com Redis"
        }
    } else {
        Write-Error "Redis não está rodando"
        Write-Info "Iniciando Redis..."
        Start-Service Redis
    }
}

# ==========================================
# Função para parar serviços
# ==========================================

function Stop-Services {
    Write-Header "Parando Serviços"
    
    Write-Info "Parando aplicação FastAPI..."
    Get-Process -Name "python" | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force
    
    Write-Info "Parando PostgreSQL..."
    Stop-Service postgresql* -Force
    
    Write-Info "Parando Redis..."
    Stop-Service Redis -Force
    
    Write-Success "Serviços parados!"
}

# ==========================================
# Verificar se deve parar serviços
# ==========================================

if ($StopServices) {
    Stop-Services
    Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
    Read-Host
    exit
}

# ==========================================
# Verificar se deve apenas checar serviços
# ==========================================

if ($CheckServices) {
    Test-Services
    Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
    Read-Host
    exit
}

# ==========================================
# Navegar para diretório do projeto
# ==========================================

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# ==========================================
# Verificar se o ambiente virtual existe
# ==========================================

Write-Header "Verificando Ambiente Python"

if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Error "Ambiente virtual não encontrado!"
    Write-Info "Execute primeiro: .\setup-windows.ps1"
    exit 1
}

Write-Success "Ambiente virtual encontrado"

# ==========================================
# Verificar arquivo .env
# ==========================================

if (!(Test-Path ".env")) {
    Write-Error "Arquivo .env não encontrado!"
    Write-Info "Copie o arquivo .env.example para .env e configure-o"
    exit 1
}

Write-Success "Arquivo .env encontrado"

# ==========================================
# Verificar e iniciar serviços
# ==========================================

Test-Services

# ==========================================
# Ativar ambiente virtual
# ==========================================

Write-Header "Iniciando Aplicação"

Write-Info "Ativando ambiente virtual..."
& ".\venv\Scripts\Activate.ps1"

# ==========================================
# Aplicar migrações
# ==========================================

Write-Info "Aplicando migrações do banco de dados..."
try {
    alembic upgrade head
    Write-Success "Migrações aplicadas com sucesso"
} catch {
    Write-Error "Erro ao aplicar migrações: $($_.Exception.Message)"
}

# ==========================================
# Determinar modo de execução
# ==========================================

if ($Development) {
    $mode = "development"
    $reload = "--reload"
    $logLevel = "debug"
} elseif ($Production) {
    $mode = "production"
    $reload = ""
    $logLevel = "info"
} else {
    # Modo padrão - detectar automaticamente
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" | Where-Object { $_ -match "ENVIRONMENT=" }
        if ($envContent -match "production") {
            $mode = "production"
            $reload = ""
            $logLevel = "info"
        } else {
            $mode = "development"
            $reload = "--reload"
            $logLevel = "debug"
        }
    } else {
        $mode = "development"
        $reload = "--reload"
        $logLevel = "debug"
    }
}

Write-Info "Modo de execução: $mode"

# ==========================================
# Iniciar aplicação
# ==========================================

Write-Success "Iniciando WhatsApp RPG GM..."
Write-Info "Acesse: http://localhost:8000"
Write-Info "Documentação da API: http://localhost:8000/docs"
Write-Info "Health Check: http://localhost:8000/health"

Write-Warning "Pressione Ctrl+C para parar a aplicação"

# Iniciar com uvicorn
if ($reload) {
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level $logLevel $reload
} else {
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level $logLevel --workers 4
}
