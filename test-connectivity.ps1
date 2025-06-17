# ==========================================
# Script de Teste de Conectividade - Serviços Remotos
# Testa conexão com PostgreSQL e Redis remotos
# ==========================================

param(
    [string]$PostgreSQLHost = "",
    [int]$PostgreSQLPort = 5432,
    [string]$RedisHost = "", 
    [int]$RedisPort = 6379,
    [string]$DatabaseName = "whatsapp_rpg_gm",
    [string]$Username = "postgres",
    [switch]$Detailed = $false,
    [switch]$Interactive = $false
)

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

Write-Header "Teste de Conectividade - Serviços"

# Se não foram fornecidos hosts, perguntar ou tentar ler do .env
if ([string]::IsNullOrEmpty($PostgreSQLHost) -or [string]::IsNullOrEmpty($RedisHost)) {
    Write-Info "Hosts não especificados. Tentando ler do arquivo .env..."
    
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        foreach ($line in $envContent) {
            if ($line -match "^DB_HOST=(.+)$" -and [string]::IsNullOrEmpty($PostgreSQLHost)) { 
                $PostgreSQLHost = $matches[1] 
            }
            if ($line -match "^DB_PORT=(\d+)$") { 
                $PostgreSQLPort = [int]$matches[1] 
            }
            if ($line -match "^REDIS_HOST=(.+)$" -and [string]::IsNullOrEmpty($RedisHost)) { 
                $RedisHost = $matches[1] 
            }
            if ($line -match "^REDIS_PORT=(\d+)$") { 
                $RedisPort = [int]$matches[1] 
            }
            if ($line -match "^DB_NAME=(.+)$") { 
                $DatabaseName = $matches[1] 
            }
            if ($line -match "^DB_USER=(.+)$") { 
                $Username = $matches[1] 
            }
        }
        Write-Success "Configurações lidas do arquivo .env"
    }
    
    # Se ainda estão vazios, perguntar
    if ([string]::IsNullOrEmpty($PostgreSQLHost) -and $Interactive) {
        $PostgreSQLHost = Read-Host "Host do PostgreSQL"
    }
    if ([string]::IsNullOrEmpty($RedisHost) -and $Interactive) {
        $RedisHost = Read-Host "Host do Redis"
    }
    
    # Se ainda estão vazios, usar defaults
    if ([string]::IsNullOrEmpty($PostgreSQLHost)) { $PostgreSQLHost = "localhost" }
    if ([string]::IsNullOrEmpty($RedisHost)) { $RedisHost = "localhost" }
}

Write-Info "Testando conectividade com:"
Write-Host "  • PostgreSQL: $PostgreSQLHost`:$PostgreSQLPort" -ForegroundColor Cyan
Write-Host "  • Redis: $RedisHost`:$RedisPort" -ForegroundColor Cyan

# ==========================================
# Teste de conectividade de rede PostgreSQL
# ==========================================

Write-Header "Testando PostgreSQL"

Write-Info "Testando conectividade de rede..."
$pgTest = Test-NetConnection -ComputerName $PostgreSQLHost -Port $PostgreSQLPort -WarningAction SilentlyContinue

if ($pgTest.TcpTestSucceeded) {
    Write-Success "Conectividade de rede PostgreSQL: OK"
    
    if ($Detailed) {
        Write-Info "Detalhes da conexão:"
        Write-Host "  • Tempo de resposta: $($pgTest.PingReplyDetails.RoundtripTime)ms" -ForegroundColor Cyan
        Write-Host "  • Interface local: $($pgTest.SourceAddress.IPAddress)" -ForegroundColor Cyan
    }
    
    # Teste de autenticação PostgreSQL (requer psql)
    $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
    if ($psqlPath) {
        Write-Info "Cliente psql encontrado: $($psqlPath.Source)"
        
        # Ler senha do arquivo .env se existir
        $password = $null
        if (Test-Path ".env") {
            $envContent = Get-Content ".env"
            foreach ($line in $envContent) {
                if ($line -match "^DB_PASSWORD=(.+)$") {
                    $password = $matches[1]
                    Write-Info "Senha encontrada no arquivo .env"
                    break
                }
            }
        }
        
        if (-not $password) {
            $securePassword = Read-Host "Digite a senha do PostgreSQL" -AsSecureString
            $password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
        }
        
        Write-Info "Testando autenticação PostgreSQL..."
        $env:PGPASSWORD = $password
        
        # Teste básico de conexão
        $testQuery = "SELECT version();"
        $result = & psql -h $PostgreSQLHost -p $PostgreSQLPort -U $Username -d postgres -c $testQuery 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Autenticação PostgreSQL: OK"
            if ($Detailed) {
                $version = $result | Select-String 'PostgreSQL'
                Write-Info "Versão PostgreSQL: $version"
            }
            
            # Verificar se o banco existe
            Write-Info "Verificando banco '$DatabaseName'..."
            $dbCheckQuery = "SELECT 1 FROM pg_database WHERE datname='$DatabaseName';"
            $dbResult = & psql -h $PostgreSQLHost -p $PostgreSQLPort -U $Username -d postgres -c $dbCheckQuery 2>&1
            
            if ($dbResult -match "1") {
                Write-Success "Banco '$DatabaseName' existe"
            } else {
                Write-Warning "Banco '$DatabaseName' não existe"
                Write-Info "Será necessário criar o banco durante o setup"
            }
            
            if ($Detailed) {
                # Listar bancos disponíveis
                Write-Info "Bancos disponíveis:"
                $listDbQuery = "\l"
                & psql -h $PostgreSQLHost -p $PostgreSQLPort -U $Username -d postgres -c $listDbQuery
            }
            
        } else {
            Write-Error "Autenticação PostgreSQL: FALHOU"
            Write-Error "Erro: $result"
            Write-Info "Verifique:"
            Write-Info "  • Usuário e senha estão corretos"
            Write-Info "  • PostgreSQL permite conexões remotas"
            Write-Info "  • Arquivo pg_hba.conf está configurado corretamente"
        }
    } else {
        Write-Warning "Cliente PostgreSQL (psql) não encontrado"
        Write-Info "Para teste completo:"
        Write-Info "  • Instale PostgreSQL client: choco install postgresql"
        Write-Info "  • Ou use apenas teste de conectividade de rede"
    }
} else {
    Write-Error "Conectividade de rede PostgreSQL: FALHOU"
    Write-Info "Verifique:"
    Write-Info "  • PostgreSQL está rodando em $PostgreSQLHost`:$PostgreSQLPort"
    Write-Info "  • Firewall permite conexões na porta $PostgreSQLPort"
    Write-Info "  • Endereço IP está correto"
}

# ==========================================
# Teste de conectividade Redis
# ==========================================

Write-Header "Testando Redis"

Write-Info "Testando conectividade de rede..."
$redisTest = Test-NetConnection -ComputerName $RedisHost -Port $RedisPort -WarningAction SilentlyContinue

if ($redisTest.TcpTestSucceeded) {
    Write-Success "Conectividade de rede Redis: OK"
    
    if ($Detailed) {
        Write-Info "Detalhes da conexão:"
        Write-Host "  • Tempo de resposta: $($redisTest.PingReplyDetails.RoundtripTime)ms" -ForegroundColor Cyan
        Write-Host "  • Interface local: $($redisTest.SourceAddress.IPAddress)" -ForegroundColor Cyan
    }
    
    # Teste de comando Redis (requer redis-cli)
    $redisCliPath = Get-Command redis-cli -ErrorAction SilentlyContinue
    if ($redisCliPath) {
        Write-Info "Cliente redis-cli encontrado: $($redisCliPath.Source)"
        
        # Ler senha do Redis do arquivo .env se existir
        $redisPassword = ""
        if (Test-Path ".env") {
            $envContent = Get-Content ".env"
            foreach ($line in $envContent) {
                if ($line -match "^REDIS_PASSWORD=(.+)$") {
                    $redisPassword = $matches[1]
                    Write-Info "Senha Redis encontrada no arquivo .env"
                    break
                }
            }
        }
        
        Write-Info "Testando comando PING..."
        
        if ([string]::IsNullOrEmpty($redisPassword)) {
            $pingResult = & redis-cli -h $RedisHost -p $RedisPort ping 2>&1
        } else {
            $pingResult = & redis-cli -h $RedisHost -p $RedisPort -a $redisPassword ping 2>&1
        }
        
        if ($pingResult -match "PONG") {
            Write-Success "Comando Redis PING: OK"
            
            if ($Detailed) {
                # Informações do servidor Redis
                Write-Info "Informações do servidor Redis:"
                if ([string]::IsNullOrEmpty($redisPassword)) {
                    $infoResult = & redis-cli -h $RedisHost -p $RedisPort info server
                } else {
                    $infoResult = & redis-cli -h $RedisHost -p $RedisPort -a $redisPassword info server
                }
                
                $redisVersion = $infoResult | Select-String "redis_version"
                if ($redisVersion) {
                    Write-Host "  • $redisVersion" -ForegroundColor Cyan
                }
                
                $redisMode = $infoResult | Select-String "redis_mode"
                if ($redisMode) {
                    Write-Host "  • $redisMode" -ForegroundColor Cyan
                }
            }
            
        } else {
            Write-Error "Comando Redis PING: FALHOU"
            Write-Error "Resposta: $pingResult"
            Write-Info "Verifique:"
            Write-Info "  • Redis aceita conexões remotas"
            Write-Info "  • Senha do Redis está correta (se configurada)"
            Write-Info "  • Configuração bind no redis.conf"
        }
    } else {
        Write-Warning "Cliente Redis (redis-cli) não encontrado"
        Write-Info "Para teste completo:"
        Write-Info "  • Instale Redis client: choco install redis-64"
        Write-Info "  • Ou use apenas teste de conectividade de rede"
    }
} else {
    Write-Error "Conectividade de rede Redis: FALHOU"
    Write-Info "Verifique:"
    Write-Info "  • Redis está rodando em $RedisHost`:$RedisPort"
    Write-Info "  • Firewall permite conexões na porta $RedisPort"
    Write-Info "  • Endereço IP está correto"
}

# ==========================================
# Resumo final
# ==========================================

Write-Header "Resumo do Teste"

$pgStatus = if ($pgTest.TcpTestSucceeded) { "✅ OK" } else { "❌ FALHA" }
$redisStatus = if ($redisTest.TcpTestSucceeded) { "✅ OK" } else { "❌ FALHA" }

Write-Host "PostgreSQL ($PostgreSQLHost`:$PostgreSQLPort): $pgStatus" -ForegroundColor $(if ($pgTest.TcpTestSucceeded) { "Green" } else { "Red" })
Write-Host "Redis ($RedisHost`:$RedisPort): $redisStatus" -ForegroundColor $(if ($redisTest.TcpTestSucceeded) { "Green" } else { "Red" })

if ($pgTest.TcpTestSucceeded -and $redisTest.TcpTestSucceeded) {
    Write-Success "Todos os serviços estão acessíveis!"
    Write-Info "Você pode prosseguir com o setup: .\setup-windows.ps1"
} else {
    Write-Warning "Alguns serviços não estão acessíveis"
    Write-Info "Resolva os problemas antes de executar o setup"
}

Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
Read-Host
