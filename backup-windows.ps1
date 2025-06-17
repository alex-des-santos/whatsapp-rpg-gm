# ==========================================
# Script de Backup para Windows 11
# Backup automático de dados do RPG GM
# ==========================================

param(
    [switch]$Full = $false,
    [switch]$DatabaseOnly = $false,
    [switch]$Restore = $false,
    [string]$RestoreFile = "",
    [switch]$Schedule = $false
)

# Configurações
$backupDir = "backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Header {
    param([string]$Message)
    Write-Host "`n============================================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "============================================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Criar diretório de backup
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Success "Diretório de backup criado: $backupDir"
}

# ==========================================
# Função de Backup do Banco de Dados
# ==========================================

function Backup-Database {
    param([string]$OutputFile)
    
    Write-Info "Fazendo backup do banco de dados PostgreSQL..."
    
    # Configurar variáveis de ambiente
    $env:PGPASSWORD = "rpg_password"
    
    try {
        # Usar pg_dump para backup
        pg_dump -U postgres -h localhost -d rpg_db -f $OutputFile --verbose
        
        if (Test-Path $OutputFile) {
            $fileSize = (Get-Item $OutputFile).Length
            Write-Success "Backup do banco criado: $OutputFile ($([math]::Round($fileSize/1MB, 2)) MB)"
        } else {
            Write-Error "Falha ao criar backup do banco de dados"
            return $false
        }
    } catch {
        Write-Error "Erro ao fazer backup do banco: $($_.Exception.Message)"
        return $false
    }
    
    return $true
}

# ==========================================
# Função de Backup Completo
# ==========================================

function Backup-Full {
    param([string]$BackupName)
    
    Write-Info "Fazendo backup completo do sistema..."
    
    $fullBackupDir = Join-Path $backupDir $BackupName
    New-Item -ItemType Directory -Path $fullBackupDir -Force | Out-Null
    
    # Backup do banco de dados
    $dbBackupFile = Join-Path $fullBackupDir "database_$timestamp.sql"
    if (!(Backup-Database -OutputFile $dbBackupFile)) {
        return $false
    }
    
    # Backup de arquivos de dados
    $dataDirs = @("data", "logs", "sessions", "characters", "ai_configs")
    
    foreach ($dir in $dataDirs) {
        if (Test-Path $dir) {
            $targetDir = Join-Path $fullBackupDir $dir
            Copy-Item -Path $dir -Destination $targetDir -Recurse -Force
            Write-Success "Backup do diretório $dir concluído"
        }
    }
    
    # Backup de configurações
    $configFiles = @(".env", "alembic.ini")
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $fullBackupDir -Force
            Write-Success "Backup do arquivo $file concluído"
        }
    }
    
    # Criar arquivo de informações do backup
    $infoFile = Join-Path $fullBackupDir "backup_info.txt"
    $info = @"
Backup criado em: $(Get-Date)
Versão do sistema: Windows 11
Usuário: $env:USERNAME
Computador: $env:COMPUTERNAME
Diretório do projeto: $projectDir
Tipo de backup: Completo
"@
    
    $info | Out-File -FilePath $infoFile -Encoding UTF8
    Write-Success "Arquivo de informações criado: backup_info.txt"
    
    # Comprimir backup (opcional)
    try {
        $zipFile = "$fullBackupDir.zip"
        Compress-Archive -Path $fullBackupDir -DestinationPath $zipFile -Force
        Remove-Item -Path $fullBackupDir -Recurse -Force
        Write-Success "Backup comprimido: $zipFile"
    } catch {
        Write-Info "Backup mantido sem compressão: $fullBackupDir"
    }
    
    return $true
}

# ==========================================
# Função de Restauração
# ==========================================

function Restore-Backup {
    param([string]$BackupPath)
    
    Write-Header "Restaurando Backup"
    
    if (!(Test-Path $BackupPath)) {
        Write-Error "Arquivo de backup não encontrado: $BackupPath"
        return $false
    }
    
    # Confirmar restauração
    Write-Warning "ATENÇÃO: Esta operação irá substituir os dados atuais!"
    $confirm = Read-Host "Digite 'CONFIRMAR' para prosseguir"
    
    if ($confirm -ne "CONFIRMAR") {
        Write-Info "Restauração cancelada pelo usuário"
        return $false
    }
    
    Write-Info "Iniciando restauração de $BackupPath..."
    
    # Parar aplicação se estiver rodando
    Write-Info "Parando aplicação..."
    Get-Process -Name "python" | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force
    
    # Restaurar banco de dados
    if ($BackupPath.EndsWith(".sql")) {
        # Backup apenas do banco
        Write-Info "Restaurando banco de dados..."
        $env:PGPASSWORD = "rpg_password"
        
        # Recriar banco
        dropdb -U postgres -h localhost rpg_db --if-exists
        createdb -U postgres -h localhost rpg_db
        
        # Restaurar dados
        psql -U postgres -h localhost -d rpg_db -f $BackupPath
        Write-Success "Banco de dados restaurado"
    } else {
        # Backup completo
        Write-Info "Extraindo backup completo..."
        
        # Extrair se for ZIP
        if ($BackupPath.EndsWith(".zip")) {
            $tempDir = Join-Path $env:TEMP "rpg_restore_$timestamp"
            Expand-Archive -Path $BackupPath -DestinationPath $tempDir -Force
            $extractedPath = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
            $BackupPath = $extractedPath.FullName
        }
        
        # Restaurar banco de dados
        $dbFile = Get-ChildItem -Path $BackupPath -Filter "database_*.sql" | Select-Object -First 1
        if ($dbFile) {
            Write-Info "Restaurando banco de dados..."
            $env:PGPASSWORD = "rpg_password"
            dropdb -U postgres -h localhost rpg_db --if-exists
            createdb -U postgres -h localhost rpg_db
            psql -U postgres -h localhost -d rpg_db -f $dbFile.FullName
            Write-Success "Banco de dados restaurado"
        }
        
        # Restaurar arquivos de dados
        $dataDirs = @("data", "logs", "sessions", "characters", "ai_configs")
        foreach ($dir in $dataDirs) {
            $sourceDir = Join-Path $BackupPath $dir
            if (Test-Path $sourceDir) {
                if (Test-Path $dir) {
                    Remove-Item -Path $dir -Recurse -Force
                }
                Copy-Item -Path $sourceDir -Destination $dir -Recurse -Force
                Write-Success "Diretório $dir restaurado"
            }
        }
        
        # Restaurar configurações (com cuidado)
        $envBackup = Join-Path $BackupPath ".env"
        if (Test-Path $envBackup) {
            $restoreEnv = Read-Host "Restaurar arquivo .env? (s/n)"
            if ($restoreEnv -eq "s") {
                Copy-Item -Path $envBackup -Destination ".env" -Force
                Write-Success "Arquivo .env restaurado"
            }
        }
    }
    
    Write-Success "Restauração concluída!"
    return $true
}

# ==========================================
# Função para Agendar Backup
# ==========================================

function Schedule-Backup {
    Write-Header "Agendando Backup Automático"
    
    $taskName = "WhatsApp_RPG_GM_Backup"
    $scriptPath = $MyInvocation.MyCommand.Path
    
    # Verificar se tarefa já existe
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Warning "Tarefa de backup já existe. Removendo..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    # Criar nova tarefa
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$scriptPath`" -Full"
    $trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    $principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal
    
    Write-Success "Backup automático agendado para executar diariamente às 2:00 AM"
    Write-Info "Para remover: Unregister-ScheduledTask -TaskName '$taskName'"
}

# ==========================================
# Lógica Principal
# ==========================================

Set-Location $projectDir

if ($Schedule) {
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "Permissões de administrador necessárias para agendar tarefas"
        exit 1
    }
    Schedule-Backup
} elseif ($Restore) {
    if ($RestoreFile -eq "") {
        Write-Error "Especifique o arquivo de backup com -RestoreFile"
        exit 1
    }
    Restore-Backup -BackupPath $RestoreFile
} elseif ($DatabaseOnly) {
    Write-Header "Backup do Banco de Dados"
    $dbBackupFile = Join-Path $backupDir "database_$timestamp.sql"
    Backup-Database -OutputFile $dbBackupFile
} elseif ($Full) {
    Write-Header "Backup Completo"
    $backupName = "full_backup_$timestamp"
    Backup-Full -BackupName $backupName
} else {
    Write-Header "WhatsApp RPG GM - Backup Windows"
    Write-Info "Uso:"
    Write-Host "  .\backup-windows.ps1 -Full          # Backup completo" -ForegroundColor Yellow
    Write-Host "  .\backup-windows.ps1 -DatabaseOnly  # Apenas banco de dados" -ForegroundColor Yellow
    Write-Host "  .\backup-windows.ps1 -Restore -RestoreFile 'backup.zip'  # Restaurar" -ForegroundColor Yellow
    Write-Host "  .\backup-windows.ps1 -Schedule      # Agendar backup automático" -ForegroundColor Yellow
}

Write-Host "`nPressione Enter para sair..." -ForegroundColor Green
Read-Host
