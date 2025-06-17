# ==========================================
# Setup Script para WhatsApp RPG GM no Windows 11
# Configura ambiente Python e instala dependências
# ==========================================

# Verificar se está executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "⚠️  Este script precisa ser executado como Administrador!" -ForegroundColor Yellow
    Write-Host "Reiniciando como Administrador..." -ForegroundColor Cyan
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

# Configurar cores para output
$Host.UI.RawUI.WindowTitle = "WhatsApp RPG GM - Setup Windows"

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
# Verificações de sistema
# ==========================================

Write-Header "Verificando Sistema Windows 11"

# Verificar versão do Windows
$windowsVersion = (Get-ComputerInfo).WindowsVersion
Write-Info "Versão do Windows: $windowsVersion"

if ($windowsVersion -lt "10.0.22000") {
    Write-Error "Este script foi otimizado para Windows 11 (build 22000+)"
    Write-Warning "O sistema pode funcionar, mas algumas funcionalidades podem não estar disponíveis"
}

# ==========================================
# Instalar Chocolatey (se não estiver instalado)
# ==========================================

Write-Header "Verificando Chocolatey"

if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Info "Instalando Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    Write-Success "Chocolatey instalado com sucesso!"
} else {
    Write-Success "Chocolatey já está instalado"
}

# ==========================================
# Instalar dependências via Chocolatey
# ==========================================

Write-Header "Instalando Dependências"

Write-Info "Instalando Python 3.11..."
choco install python311 -y

Write-Info "Instalando PostgreSQL..."
choco install postgresql --params '/Password:rpg_password' -y

Write-Info "Instalando Redis..."
choco install redis-64 -y

Write-Info "Instalando Git (se necessário)..."
choco install git -y

Write-Info "Instalando Visual Studio Code (opcional)..."
choco install vscode -y

Write-Success "Dependências instaladas!"

# ==========================================
# Configurar variáveis de ambiente
# ==========================================

Write-Header "Configurando Variáveis de Ambiente"

# Adicionar Python ao PATH
$pythonPath = "C:\Python311;C:\Python311\Scripts"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($currentPath -notlike "*$pythonPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pythonPath", "Machine")
    Write-Success "Python adicionado ao PATH"
}

# Recarregar variáveis de ambiente
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# ==========================================
# Configurar serviços Windows
# ==========================================

Write-Header "Configurando Serviços Windows"

# Configurar PostgreSQL
Write-Info "Configurando PostgreSQL..."
Start-Service postgresql*
Set-Service -Name postgresql* -StartupType Automatic
Write-Success "PostgreSQL configurado para iniciar automaticamente"

# Configurar Redis
Write-Info "Configurando Redis..."
Start-Service Redis
Set-Service -Name Redis -StartupType Automatic
Write-Success "Redis configurado para iniciar automaticamente"

# ==========================================
# Configurar Python Virtual Environment
# ==========================================

Write-Header "Configurando Ambiente Python"

# Navegar para diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Info "Criando ambiente virtual Python..."
python -m venv venv

Write-Info "Ativando ambiente virtual..."
& ".\venv\Scripts\Activate.ps1"

Write-Info "Atualizando pip..."
python -m pip install --upgrade pip

Write-Info "Instalando dependências do projeto..."
pip install -r requirements.txt

Write-Success "Ambiente Python configurado!"

# ==========================================
# Configurar banco de dados
# ==========================================

Write-Header "Configurando Banco de Dados"

Write-Info "Criando banco de dados..."
$env:PGPASSWORD = "rpg_password"
createdb -U postgres -h localhost rpg_db

Write-Info "Executando migrações..."
alembic upgrade head

Write-Success "Banco de dados configurado!"

# ==========================================
# Criar arquivos de configuração
# ==========================================

Write-Header "Criando Arquivos de Configuração"

# Criar .env a partir do exemplo
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success "Arquivo .env criado a partir do exemplo"
    Write-Warning "IMPORTANTE: Edite o arquivo .env com suas configurações reais!"
}

# Criar diretórios necessários
$directories = @("data", "logs", "sessions", "characters", "backups", "ai_configs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir
        Write-Success "Diretório $dir criado"
    }
}

# ==========================================
# Configurações de firewall
# ==========================================

Write-Header "Configurando Firewall"

Write-Info "Adicionando regra de firewall para porta 8000..."
New-NetFirewallRule -DisplayName "WhatsApp RPG GM" -Direction Inbound -Port 8000 -Protocol UDP -Action Allow
New-NetFirewallRule -DisplayName "WhatsApp RPG GM" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow

Write-Success "Regras de firewall configuradas!"

# ==========================================
# Finalização
# ==========================================

Write-Header "Setup Concluído!"

Write-Success "WhatsApp RPG GM configurado com sucesso no Windows 11!"
Write-Info "Próximos passos:"
Write-Host "1. Edite o arquivo .env com suas configurações" -ForegroundColor Cyan
Write-Host "2. Execute: .\start-windows.ps1" -ForegroundColor Cyan
Write-Host "3. Acesse: http://localhost:8000" -ForegroundColor Cyan

Write-Warning "Lembre-se de configurar:"
Write-Host "- Evolution API URL e chave" -ForegroundColor Yellow
Write-Host "- Chave da API de IA (OpenAI, Google, etc.)" -ForegroundColor Yellow
Write-Host "- Tokens de segurança únicos" -ForegroundColor Yellow

Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
Read-Host
