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
    
    $allOk = $true
    
    # Ler configurações do .env
    $envFile = ".env"
    $dbHost = "localhost"
    $dbPort = 5432
    $redisHost = "localhost"
    $redisPort = 6379
    
    if (Test-Path $envFile) {
        $envContent = Get-Content $envFile
        foreach ($line in $envContent) {
            if ($line -match "^DB_HOST=(.+)$") { $dbHost = $matches[1] }
            if ($line -match "^DB_PORT=(\d+)$") { $dbPort = [int]$matches[1] }
            if ($line -match "^REDIS_HOST=(.+)$") { $redisHost = $matches[1] }
            if ($line -match "^REDIS_PORT=(\d+)$") { $redisPort = [int]$matches[1] }
        }
    }
    
    # Verificar PostgreSQL
    Write-Info "Testando PostgreSQL ($dbHost`:$dbPort)..."
    $postgresTest = Test-NetConnection -ComputerName $dbHost -Port $dbPort -WarningAction SilentlyContinue
    if ($postgresTest.TcpTestSucceeded) {
        Write-Success "PostgreSQL ($dbHost`:$dbPort) está acessível"
        
        # Testar conexão se psql estiver disponível
        $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
        if ($psqlPath) {
            try {
                $testQuery = & psql -h $dbHost -p $dbPort -U postgres -d postgres -c "SELECT 1;" 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Conexão com PostgreSQL: OK"
                } else {
                    Write-Warning "PostgreSQL acessível mas falha na autenticação"
                    Write-Info "Verifique as credenciais no arquivo .env"
                }
            } catch {
                Write-Warning "Erro ao testar conexão PostgreSQL: $($_.Exception.Message)"
            }
        }
    } else {
        Write-Error "PostgreSQL ($dbHost`:$dbPort) não está acessível"
        $allOk = $false
        
        if ($dbHost -ne "localhost") {
            Write-Info "Verifique se:"
            Write-Info "  1. PostgreSQL está rodando em $dbHost`:$dbPort"
            Write-Info "  2. Firewall permite conexões na porta $dbPort"
            Write-Info "  3. PostgreSQL aceita conexões remotas"
        } else {
            # Tentar iniciar serviço local
            $postgresService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
            if ($postgresService) {
                Write-Info "Iniciando PostgreSQL local..."
                Start-Service postgresql*
            }
        }
    }
    
    # Verificar Redis
    Write-Info "Testando Redis ($redisHost`:$redisPort)..."
    $redisTest = Test-NetConnection -ComputerName $redisHost -Port $redisPort -WarningAction SilentlyContinue
    if ($redisTest.TcpTestSucceeded) {
        Write-Success "Redis ($redisHost`:$redisPort) está acessível"
        
        # Testar conexão se redis-cli estiver disponível
        $redisCliPath = Get-Command redis-cli -ErrorAction SilentlyContinue
        if ($redisCliPath) {
            try {
                $pingResult = & redis-cli -h $redisHost -p $redisPort ping 2>&1
                if ($pingResult -match "PONG") {
                    Write-Success "Conexão com Redis: OK"
                } else {
                    Write-Warning "Redis acessível mas falha no ping: $pingResult"
                }
            } catch {
                Write-Warning "Erro ao testar conexão Redis: $($_.Exception.Message)"
            }
        }
    } else {
        Write-Error "Redis ($redisHost`:$redisPort) não está acessível"
        $allOk = $false
        
        if ($redisHost -ne "localhost") {
            Write-Info "Verifique se:"
            Write-Info "  1. Redis está rodando em $redisHost`:$redisPort"
            Write-Info "  2. Firewall permite conexões na porta $redisPort"
            Write-Info "  3. Redis aceita conexões remotas"
        } else {
            # Tentar iniciar serviço local
            $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
            if ($redisService) {
                Write-Info "Iniciando Redis local..."
                Start-Service Redis
            }
        }
    }
    
    return $allOk
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
