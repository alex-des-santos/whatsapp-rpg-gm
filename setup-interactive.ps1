# ==========================================
# Setup Script Interativo para WhatsApp RPG GM
# Script reproduzível que funciona em qualquer configuração
# ==========================================

param(
    [switch]$AutoMode = $false,
    [switch]$SkipQuestions = $false
)

# Verificar se está executando como administrador para instalações
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

# Configurar cores para output
$Host.UI.RawUI.WindowTitle = "WhatsApp RPG GM - Setup Interativo"

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

function Ask-Question {
    param(
        [string]$Question,
        [string]$Default = "",
        [switch]$Required = $false,
        [switch]$Password = $false
    )
    
    if ($AutoMode -and $Default) {
        Write-Info "Modo automático: usando valor padrão '$Default'"
        return $Default
    }
    
    do {
        if ($Password) {
            $response = Read-Host "$Question" -AsSecureString
            $response = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($response))
        } else {
            if ($Default) {
                $response = Read-Host "$Question [$Default]"
                if ([string]::IsNullOrEmpty($response)) { $response = $Default }
            } else {
                $response = Read-Host $Question
            }
        }
        
        if ($Required -and [string]::IsNullOrWhiteSpace($response)) {
            Write-Warning "Esta informação é obrigatória!"
            continue
        }
        
        break
    } while ($true)
    
    return $response
}

function Confirm-Choice {
    param([string]$Question, [string]$Default = "N")
    
    if ($AutoMode) {
        return ($Default -eq "S")
    }
    
    $response = Read-Host "$Question (S/N) [$Default]"
    if ([string]::IsNullOrEmpty($response)) { $response = $Default }
    return ($response.ToUpper() -eq "S")
}

function Test-NetworkConnection {
    param([string]$Host, [int]$Port)
    
    try {
        $test = Test-NetConnection -ComputerName $Host -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        return $test.TcpTestSucceeded
    } catch {
        return $false
    }
}

# Variáveis globais para configurações
$global:Config = @{
    Python = @{}
    PostgreSQL = @{}
    Redis = @{}
}

# ==========================================
# Bem-vindo e verificações iniciais
# ==========================================

Write-Header "WhatsApp RPG Game Master - Setup Interativo"

Write-Info "Este script irá configurar o WhatsApp RPG GM para sua infraestrutura específica."
Write-Info "Ele detectará instalações existentes e perguntará sobre configurações personalizadas."

if (-not $isAdmin -and -not $SkipQuestions) {
    Write-Warning "Script não está rodando como Administrador"
    Write-Info "Algumas instalações automáticas podem falhar"
    
    if (Confirm-Choice "Continuar mesmo assim?" "S") {
        Write-Info "Continuando sem privilégios de administrador..."
    } else {
        Write-Info "Reiniciando como Administrador..."
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        if ($AutoMode) { $arguments += " -AutoMode" }
        Start-Process PowerShell -Verb RunAs $arguments
        exit
    }
}

# Verificar versão do Windows
$windowsVersion = (Get-ComputerInfo).WindowsVersion
Write-Info "Sistema: Windows $windowsVersion"

# ==========================================
# Configuração do Python
# ==========================================

Write-Header "Configuração do Python"

# Detectar instalações existentes do Python
$pythonInstallations = @()

# Verificar comandos comuns
$pythonCommands = @("python", "python3", "py")
foreach ($cmd in $pythonCommands) {
    try {
        $cmdPath = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($cmdPath) {
            $version = & $cmd --version 2>$null
            if ($version -match "Python (\d+\.\d+\.\d+)") {
                $pythonInstallations += @{
                    Command = $cmd
                    Path = $cmdPath.Source
                    Version = $matches[1]
                }
            }
        }
    } catch {
        # Continuar verificando
    }
}

# Verificar instalações em locais comuns
$commonPaths = @(
    "C:\Python*",
    "C:\Program Files\Python*",
    "C:\Program Files (x86)\Python*",
    "$env:LOCALAPPDATA\Programs\Python\Python*",
    "$env:APPDATA\Python\Python*"
)

foreach ($pathPattern in $commonPaths) {
    $paths = Get-ChildItem $pathPattern -Directory -ErrorAction SilentlyContinue
    foreach ($path in $paths) {
        $pythonExe = Join-Path $path.FullName "python.exe"
        if (Test-Path $pythonExe) {
            try {
                $version = & $pythonExe --version 2>$null
                if ($version -match "Python (\d+\.\d+\.\d+)") {
                    $pythonInstallations += @{
                        Command = $pythonExe
                        Path = $pythonExe
                        Version = $matches[1]
                    }
                }
            } catch {
                # Continuar verificando
            }
        }
    }
}

# Remover duplicatas
$pythonInstallations = $pythonInstallations | Sort-Object Version -Unique

if ($pythonInstallations.Count -gt 0) {
    Write-Success "Encontradas $($pythonInstallations.Count) instalação(ões) do Python:"
    for ($i = 0; $i -lt $pythonInstallations.Count; $i++) {
        $python = $pythonInstallations[$i]
        Write-Host "  [$($i + 1)] Python $($python.Version) - $($python.Path)" -ForegroundColor Cyan
    }
    
    if (Confirm-Choice "Usar uma instalação existente do Python?" "S") {
        if ($pythonInstallations.Count -eq 1) {
            $selectedPython = $pythonInstallations[0]
            Write-Success "Usando Python $($selectedPython.Version)"
        } else {
            do {
                $selection = Ask-Question "Escolha uma instalação (1-$($pythonInstallations.Count))" -Required
                $index = [int]$selection - 1
            } while ($index -lt 0 -or $index -ge $pythonInstallations.Count)
            
            $selectedPython = $pythonInstallations[$index]
            Write-Success "Usando Python $($selectedPython.Version) - $($selectedPython.Path)"
        }
        
        $global:Config.Python.Path = $selectedPython.Path
        $global:Config.Python.Version = $selectedPython.Version
        $global:Config.Python.Install = $false
    } else {
        $global:Config.Python.Install = $true
    }
} else {
    Write-Warning "Nenhuma instalação do Python encontrada"
    $global:Config.Python.Install = $true
}

if ($global:Config.Python.Install) {
    Write-Info "Será necessário instalar o Python"
    
    if ($isAdmin) {
        $installPython = Confirm-Choice "Instalar Python 3.11 automaticamente?" "S"
        $global:Config.Python.AutoInstall = $installPython
        
        if (-not $installPython) {
            $global:Config.Python.ManualPath = Ask-Question "Caminho para o executável do Python" -Required
        }
    } else {
        Write-Warning "Sem privilégios de administrador, instalação manual necessária"
        Write-Info "Opções:"
        Write-Info "1. Baixar de: https://www.python.org/downloads/"
        Write-Info "2. Instalar via Microsoft Store"
        Write-Info "3. Instalar via Chocolatey: choco install python"
        
        $global:Config.Python.ManualPath = Ask-Question "Caminho para o executável do Python (após instalação)" -Required
    }
}

# ==========================================
# Configuração do PostgreSQL
# ==========================================

Write-Header "Configuração do PostgreSQL"

Write-Info "O sistema precisa de um banco PostgreSQL para funcionar."
Write-Info "Você pode usar:"
Write-Info "1. PostgreSQL local (instalado nesta máquina)"
Write-Info "2. PostgreSQL remoto (outro servidor)"
Write-Info "3. PostgreSQL em container Docker"
Write-Info "4. Serviço PostgreSQL na nuvem (AWS RDS, Azure, etc.)"

$pgChoice = Ask-Question "Que tipo de PostgreSQL você quer usar? (local/remoto/docker/nuvem)" "local"

switch ($pgChoice.ToLower()) {
    "local" {
        # Verificar instalação local
        $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
        $pgInstalled = $false
        
        if ($pgService) {
            Write-Success "Serviço PostgreSQL encontrado: $($pgService.Name)"
            $pgInstalled = $true
        }
        
        # Verificar executáveis
        $pgPaths = @(
            "C:\Program Files\PostgreSQL\*\bin\psql.exe",
            "C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe"
        )
        
        $psqlPath = $null
        foreach ($pathPattern in $pgPaths) {
            $found = Get-ChildItem $pathPattern -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $psqlPath = $found.FullName
                $pgInstalled = $true
                break
            }
        }
        
        if ($pgInstalled) {
            Write-Success "PostgreSQL local detectado"
            if (Confirm-Choice "Usar PostgreSQL local existente?" "S") {
                $global:Config.PostgreSQL.Type = "local"
                $global:Config.PostgreSQL.Host = "localhost"
                $global:Config.PostgreSQL.Port = Ask-Question "Porta do PostgreSQL" "5432"
                $global:Config.PostgreSQL.User = Ask-Question "Usuário PostgreSQL" "postgres"
                $global:Config.PostgreSQL.Password = Ask-Question "Senha do PostgreSQL" -Password -Required
                $global:Config.PostgreSQL.Database = Ask-Question "Nome do banco de dados" "whatsapp_rpg_gm"
                
                if ($psqlPath) {
                    $global:Config.PostgreSQL.BinPath = Split-Path $psqlPath
                }
            } else {
                Write-Info "Configurando para PostgreSQL remoto..."
                $pgChoice = "remoto"
            }
        } else {
            Write-Warning "PostgreSQL local não encontrado"
            if ($isAdmin -and (Confirm-Choice "Instalar PostgreSQL local?" "S")) {
                $global:Config.PostgreSQL.Type = "local"
                $global:Config.PostgreSQL.Install = $true
                $global:Config.PostgreSQL.Host = "localhost"
                $global:Config.PostgreSQL.Port = "5432"
                $global:Config.PostgreSQL.User = "postgres"
                $global:Config.PostgreSQL.Password = Ask-Question "Senha para o usuário postgres" -Password -Required
                $global:Config.PostgreSQL.Database = Ask-Question "Nome do banco de dados" "whatsapp_rpg_gm"
            } else {
                Write-Info "Configurando para PostgreSQL remoto..."
                $pgChoice = "remoto"
            }
        }
    }
    
    "remoto" {
        Write-Info "Configurando PostgreSQL remoto..."
        $global:Config.PostgreSQL.Type = "remote"
        $global:Config.PostgreSQL.Host = Ask-Question "Endereço do servidor PostgreSQL (IP ou hostname)" -Required
        $global:Config.PostgreSQL.Port = Ask-Question "Porta do PostgreSQL" "5432"
        $global:Config.PostgreSQL.User = Ask-Question "Usuário PostgreSQL" "postgres"
        $global:Config.PostgreSQL.Password = Ask-Question "Senha do PostgreSQL" -Password -Required
        $global:Config.PostgreSQL.Database = Ask-Question "Nome do banco de dados" "whatsapp_rpg_gm"
        
        # Testar conectividade
        Write-Info "Testando conectividade com $($global:Config.PostgreSQL.Host):$($global:Config.PostgreSQL.Port)..."
        if (Test-NetworkConnection $global:Config.PostgreSQL.Host ([int]$global:Config.PostgreSQL.Port)) {
            Write-Success "Conectividade OK"
        } else {
            Write-Error "Não foi possível conectar ao servidor PostgreSQL"
            Write-Warning "Verifique se o servidor está rodando e acessível"
            
            if (-not (Confirm-Choice "Continuar mesmo assim?" "N")) {
                exit 1
            }
        }
    }
    
    "docker" {
        Write-Info "Configurando PostgreSQL em Docker..."
        $global:Config.PostgreSQL.Type = "docker"
        $global:Config.PostgreSQL.Host = Ask-Question "Host do container PostgreSQL" "localhost"
        $global:Config.PostgreSQL.Port = Ask-Question "Porta mapeada do container" "5432"
        $global:Config.PostgreSQL.User = Ask-Question "Usuário PostgreSQL" "postgres"
        $global:Config.PostgreSQL.Password = Ask-Question "Senha do PostgreSQL" -Password -Required
        $global:Config.PostgreSQL.Database = Ask-Question "Nome do banco de dados" "whatsapp_rpg_gm"
        $global:Config.PostgreSQL.ContainerName = Ask-Question "Nome do container (opcional)"
    }
    
    "nuvem" {
        Write-Info "Configurando PostgreSQL na nuvem..."
        $global:Config.PostgreSQL.Type = "cloud"
        Write-Info "Exemplos de hosts:"
        Write-Info "  • AWS RDS: mydb.xxxxxxxxx.us-east-1.rds.amazonaws.com"
        Write-Info "  • Azure: myserver.postgres.database.azure.com"
        Write-Info "  • Google Cloud: xxx.xxx.xxx.xxx (IP público)"
        
        $global:Config.PostgreSQL.Host = Ask-Question "Host do PostgreSQL na nuvem" -Required
        $global:Config.PostgreSQL.Port = Ask-Question "Porta do PostgreSQL" "5432"
        $global:Config.PostgreSQL.User = Ask-Question "Usuário PostgreSQL" -Required
        $global:Config.PostgreSQL.Password = Ask-Question "Senha do PostgreSQL" -Password -Required
        $global:Config.PostgreSQL.Database = Ask-Question "Nome do banco de dados" "whatsapp_rpg_gm"
        
        # Verificar se precisa de SSL
        $global:Config.PostgreSQL.RequireSSL = Confirm-Choice "Requer SSL?" "S"
    }
}

# ==========================================
# Configuração do Redis
# ==========================================

Write-Header "Configuração do Redis"

Write-Info "O sistema precisa de um servidor Redis para cache e sessões."
Write-Info "Você pode usar:"
Write-Info "1. Redis local (instalado nesta máquina)"
Write-Info "2. Redis remoto (outro servidor)"
Write-Info "3. Redis em container Docker"
Write-Info "4. Serviço Redis na nuvem (AWS ElastiCache, Azure Cache, etc.)"

$redisChoice = Ask-Question "Que tipo de Redis você quer usar? (local/remoto/docker/nuvem)" "local"

switch ($redisChoice.ToLower()) {
    "local" {
        # Verificar instalação local
        $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
        $redisInstalled = $false
        
        if ($redisService) {
            Write-Success "Serviço Redis encontrado: $($redisService.Name)"
            $redisInstalled = $true
        }
        
        # Verificar executáveis
        $redisCliPath = Get-Command redis-cli -ErrorAction SilentlyContinue
        if ($redisCliPath) {
            $redisInstalled = $true
        }
        
        if ($redisInstalled) {
            Write-Success "Redis local detectado"
            if (Confirm-Choice "Usar Redis local existente?" "S") {
                $global:Config.Redis.Type = "local"
                $global:Config.Redis.Host = "localhost"
                $global:Config.Redis.Port = Ask-Question "Porta do Redis" "6379"
                $global:Config.Redis.Database = Ask-Question "Número do banco Redis (0-15)" "0"
                
                if (Confirm-Choice "O Redis tem senha configurada?" "N") {
                    $global:Config.Redis.Password = Ask-Question "Senha do Redis" -Password
                } else {
                    $global:Config.Redis.Password = ""
                }
            } else {
                Write-Info "Configurando para Redis remoto..."
                $redisChoice = "remoto"
            }
        } else {
            Write-Warning "Redis local não encontrado"
            if ($isAdmin -and (Confirm-Choice "Instalar Redis local?" "S")) {
                $global:Config.Redis.Type = "local"
                $global:Config.Redis.Install = $true
                $global:Config.Redis.Host = "localhost"
                $global:Config.Redis.Port = "6379"
                $global:Config.Redis.Database = "0"
                $global:Config.Redis.Password = ""
            } else {
                Write-Info "Configurando para Redis remoto..."
                $redisChoice = "remoto"
            }
        }
    }
    
    "remoto" {
        Write-Info "Configurando Redis remoto..."
        $global:Config.Redis.Type = "remote"
        $global:Config.Redis.Host = Ask-Question "Endereço do servidor Redis (IP ou hostname)" -Required
        $global:Config.Redis.Port = Ask-Question "Porta do Redis" "6379"
        $global:Config.Redis.Database = Ask-Question "Número do banco Redis (0-15)" "0"
        
        if (Confirm-Choice "O Redis tem senha configurada?" "N") {
            $global:Config.Redis.Password = Ask-Question "Senha do Redis" -Password
        } else {
            $global:Config.Redis.Password = ""
        }
        
        # Testar conectividade
        Write-Info "Testando conectividade com $($global:Config.Redis.Host):$($global:Config.Redis.Port)..."
        if (Test-NetworkConnection $global:Config.Redis.Host ([int]$global:Config.Redis.Port)) {
            Write-Success "Conectividade OK"
        } else {
            Write-Error "Não foi possível conectar ao servidor Redis"
            Write-Warning "Verifique se o servidor está rodando e acessível"
            
            if (-not (Confirm-Choice "Continuar mesmo assim?" "N")) {
                exit 1
            }
        }
    }
    
    "docker" {
        Write-Info "Configurando Redis em Docker..."
        $global:Config.Redis.Type = "docker"
        $global:Config.Redis.Host = Ask-Question "Host do container Redis" "localhost"
        $global:Config.Redis.Port = Ask-Question "Porta mapeada do container" "6379"
        $global:Config.Redis.Database = Ask-Question "Número do banco Redis (0-15)" "0"
        
        if (Confirm-Choice "O Redis tem senha configurada?" "N") {
            $global:Config.Redis.Password = Ask-Question "Senha do Redis" -Password
        } else {
            $global:Config.Redis.Password = ""
        }
        
        $global:Config.Redis.ContainerName = Ask-Question "Nome do container (opcional)"
    }
    
    "nuvem" {
        Write-Info "Configurando Redis na nuvem..."
        $global:Config.Redis.Type = "cloud"
        Write-Info "Exemplos de hosts:"
        Write-Info "  • AWS ElastiCache: myredis.xxxxxx.cache.amazonaws.com"
        Write-Info "  • Azure Cache: myredis.redis.cache.windows.net"
        Write-Info "  • Google Cloud: xxx.xxx.xxx.xxx (IP público)"
        
        $global:Config.Redis.Host = Ask-Question "Host do Redis na nuvem" -Required
        $global:Config.Redis.Port = Ask-Question "Porta do Redis" "6379"
        $global:Config.Redis.Database = Ask-Question "Número do banco Redis (0-15)" "0"
        $global:Config.Redis.Password = Ask-Question "Senha/Token do Redis" -Password -Required
        
        # Verificar se precisa de SSL
        $global:Config.Redis.RequireSSL = Confirm-Choice "Requer SSL/TLS?" "S"
    }
}

# ==========================================
# Instalações necessárias
# ==========================================

Write-Header "Executando Instalações"

# Instalar Python se necessário
if ($global:Config.Python.Install -and $global:Config.Python.AutoInstall) {
    Write-Info "Instalando Python 3.11..."
    
    # Verificar se Chocolatey está instalado
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Info "Instalando Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        Write-Success "Chocolatey instalado!"
    }
    
    choco install python311 -y
    
    # Atualizar PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    
    # Verificar instalação
    try {
        $newVersion = python --version
        Write-Success "Python instalado: $newVersion"
        $global:Config.Python.Path = (Get-Command python).Source
    } catch {
        Write-Error "Erro ao verificar instalação do Python"
    }
}

# Instalar PostgreSQL se necessário
if ($global:Config.PostgreSQL.Install) {
    Write-Info "Instalando PostgreSQL..."
    choco install postgresql -y --params "/Password:$($global:Config.PostgreSQL.Password)"
    
    # Aguardar serviço iniciar
    Start-Sleep 10
    Start-Service postgresql*
}

# Instalar Redis se necessário
if ($global:Config.Redis.Install) {
    Write-Info "Instalando Redis..."
    choco install redis-64 -y
    
    # Aguardar serviço iniciar
    Start-Sleep 5
    Start-Service Redis
}

# ==========================================
# Configurar ambiente Python
# ==========================================

Write-Header "Configurando Ambiente Python"

# Navegar para diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Determinar comando Python a usar
$pythonCmd = "python"
if ($global:Config.Python.Path) {
    $pythonCmd = $global:Config.Python.Path
} elseif ($global:Config.Python.ManualPath) {
    $pythonCmd = $global:Config.Python.ManualPath
}

Write-Info "Usando Python: $pythonCmd"

Write-Info "Criando ambiente virtual..."
& $pythonCmd -m venv venv

Write-Info "Ativando ambiente virtual..."
& ".\venv\Scripts\Activate.ps1"

Write-Info "Atualizando pip..."
& $pythonCmd -m pip install --upgrade pip

Write-Info "Instalando dependências..."
if (Test-Path "requirements-windows.txt") {
    & $pythonCmd -m pip install -r requirements-windows.txt
} else {
    & $pythonCmd -m pip install -r requirements.txt
}

Write-Success "Ambiente Python configurado!"

# ==========================================
# Configurar banco de dados
# ==========================================

Write-Header "Configurando Banco de Dados"

# Configurar variável de ambiente para senha
$env:PGPASSWORD = $global:Config.PostgreSQL.Password

# Verificar se psql está disponível
$psqlCmd = "psql"
if ($global:Config.PostgreSQL.BinPath) {
    $psqlCmd = Join-Path $global:Config.PostgreSQL.BinPath "psql.exe"
}

try {
    # Verificar se o banco existe
    Write-Info "Verificando banco '$($global:Config.PostgreSQL.Database)'..."
    $dbExists = & $psqlCmd -h $global:Config.PostgreSQL.Host -p $global:Config.PostgreSQL.Port -U $global:Config.PostgreSQL.User -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$($global:Config.PostgreSQL.Database)';" 2>&1
    
    if ($dbExists -match "1") {
        Write-Success "Banco '$($global:Config.PostgreSQL.Database)' já existe"
    } else {
        Write-Info "Criando banco '$($global:Config.PostgreSQL.Database)'..."
        $createdbCmd = "createdb"
        if ($global:Config.PostgreSQL.BinPath) {
            $createdbCmd = Join-Path $global:Config.PostgreSQL.BinPath "createdb.exe"
        }
        & $createdbCmd -h $global:Config.PostgreSQL.Host -p $global:Config.PostgreSQL.Port -U $global:Config.PostgreSQL.User $global:Config.PostgreSQL.Database
        Write-Success "Banco '$($global:Config.PostgreSQL.Database)' criado!"
    }
    
    Write-Info "Executando migrações..."
    alembic upgrade head
    Write-Success "Migrações aplicadas!"
    
} catch {
    Write-Warning "Erro ao configurar banco: $($_.Exception.Message)"
    Write-Info "Você pode configurar o banco manualmente após o setup"
}

# ==========================================
# Gerar arquivo .env
# ==========================================

Write-Header "Gerando Arquivo de Configuração"

# Construir URL do PostgreSQL
$pgUrl = "postgresql://$($global:Config.PostgreSQL.User):$($global:Config.PostgreSQL.Password)@$($global:Config.PostgreSQL.Host):$($global:Config.PostgreSQL.Port)/$($global:Config.PostgreSQL.Database)"

# Construir URL do Redis
if ($global:Config.Redis.Password) {
    $redisUrl = "redis://:$($global:Config.Redis.Password)@$($global:Config.Redis.Host):$($global:Config.Redis.Port)/$($global:Config.Redis.Database)"
} else {
    $redisUrl = "redis://$($global:Config.Redis.Host):$($global:Config.Redis.Port)/$($global:Config.Redis.Database)"
}

# Conteúdo do .env
$envContent = @"
# ==========================================
# CONFIGURAÇÕES GERADAS AUTOMATICAMENTE
# Gerado em: $(Get-Date)
# ==========================================

# ==========================================
# WHATSAPP EVOLUTION API (CONFIGURE SUAS CHAVES)
# ==========================================
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution_api
INSTANCE_NAME=sua_instancia_whatsapp
VERIFY_TOKEN=seu_token_verificacao_muito_seguro_12345

# ==========================================
# INTELIGÊNCIA ARTIFICIAL (CONFIGURE SUA CHAVE)
# ==========================================
AI_PROVIDER=openai
OPENAI_API_KEY=sk-sua_chave_openai
GOOGLE_API_KEY=sua_chave_google_ai
ANTHROPIC_API_KEY=sk-ant-sua_chave_anthropic

# ==========================================
# BANCO DE DADOS POSTGRESQL
# Configurado para: $($global:Config.PostgreSQL.Type)
# ==========================================
DATABASE_URL=$pgUrl
DB_HOST=$($global:Config.PostgreSQL.Host)
DB_PORT=$($global:Config.PostgreSQL.Port)
DB_NAME=$($global:Config.PostgreSQL.Database)
DB_USER=$($global:Config.PostgreSQL.User)
DB_PASSWORD=$($global:Config.PostgreSQL.Password)

# ==========================================
# CACHE REDIS
# Configurado para: $($global:Config.Redis.Type)
# ==========================================
REDIS_URL=$redisUrl
REDIS_HOST=$($global:Config.Redis.Host)
REDIS_PORT=$($global:Config.Redis.Port)
REDIS_PASSWORD=$($global:Config.Redis.Password)
REDIS_DB=$($global:Config.Redis.Database)

# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ==========================================
SECRET_KEY=sua_chave_secreta_jwt_muito_longa_e_segura_123456789
PASSWORD_HASH_ALGORITHM=bcrypt
JWT_EXPIRATION_MINUTES=1440
PASSWORD_SALT_ROUNDS=12

# ==========================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ==========================================
ENVIRONMENT=development
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000
AUTO_RELOAD=true
DEBUG=true
WORKERS=1

# ==========================================
# CONFIGURAÇÕES DETECTADAS
# ==========================================
PYTHON_PATH=$($global:Config.Python.Path)
POSTGRESQL_TYPE=$($global:Config.PostgreSQL.Type)
REDIS_TYPE=$($global:Config.Redis.Type)
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Success "Arquivo .env criado!"

# Criar diretórios necessários
$directories = @("data", "logs", "sessions", "characters", "backups", "ai_configs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Success "Diretório '$dir' criado"
    }
}

# ==========================================
# Configuração do firewall
# ==========================================

Write-Header "Configurando Firewall"

if ($isAdmin) {
    try {
        Write-Info "Adicionando regra de firewall para porta 8000..."
        New-NetFirewallRule -DisplayName "WhatsApp RPG GM" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
        Write-Success "Regra de firewall criada!"
    } catch {
        Write-Warning "Não foi possível configurar firewall automaticamente"
    }
} else {
    Write-Warning "Configure manualmente o firewall para permitir porta 8000"
}

# ==========================================
# Finalização
# ==========================================

Write-Header "Setup Concluído!"

Write-Success "WhatsApp RPG GM configurado com sucesso!"

Write-Info "Configurações aplicadas:"
Write-Host "  • Python: $($global:Config.Python.Path)" -ForegroundColor Cyan
Write-Host "  • PostgreSQL: $($global:Config.PostgreSQL.Host):$($global:Config.PostgreSQL.Port) ($($global:Config.PostgreSQL.Type))" -ForegroundColor Cyan
Write-Host "  • Redis: $($global:Config.Redis.Host):$($global:Config.Redis.Port) ($($global:Config.Redis.Type))" -ForegroundColor Cyan

Write-Info "Próximos passos:"
Write-Host "1. Configure no arquivo .env:" -ForegroundColor Yellow
Write-Host "   - Evolution API URL e chave" -ForegroundColor Yellow
Write-Host "   - Chave da API de IA (OpenAI, Google, Anthropic)" -ForegroundColor Yellow
Write-Host "   - Token de verificação e chave secreta únicos" -ForegroundColor Yellow
Write-Host "2. Execute: .\start-windows.ps1" -ForegroundColor Cyan
Write-Host "3. Acesse: http://localhost:8000/docs" -ForegroundColor Cyan

if (-not $AutoMode) {
    Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
    Read-Host
}
