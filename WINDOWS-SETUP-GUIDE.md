# 🎯 Guia Completo: WhatsApp RPG GM no Windows 11

## 📋 Resumo das Alterações

Este projeto foi adaptado para rodar **nativamente no Windows 11** sem necessidade de Docker ou WSL. As principais alterações incluem:

### ✅ Arquivos Criados

1. **`setup-windows.ps1`** - Script de instalação automática
2. **`start-windows.ps1`** - Script para iniciar a aplicação
3. **`start-quick.bat`** - Alternativa simples em Batch
4. **`backup-windows.ps1`** - Sistema de backup para Windows
5. **`.env.windows`** - Configurações específicas para Windows
6. **`requirements-windows.txt`** - Dependências otimizadas
7. **`README-WINDOWS.md`** - Documentação específica para Windows

### 🔧 Arquivos Modificados

1. **`app/core/config.py`** - Detecção automática de Windows e otimizações
2. **`app/core/database.py`** - Configurações de banco otimizadas para Windows
3. **`alembic.ini`** - URL do banco configurada para Windows local

## 🚀 Instalação Rápida

### Opção 1: Instalação Automática (Recomendada)

```powershell
# 1. Abrir PowerShell como Administrador
# 2. Navegar para o diretório do projeto
cd z:\Dev\RPG\whatsapp-rpg-gm

# 3. Executar setup automático
.\setup-windows.ps1

# 4. Iniciar aplicação
.\start-windows.ps1
```

### Opção 2: Início Rápido (Se já tiver Python)

```batch
# Usar o script batch simples
start-quick.bat
```

## ⚙️ Configurações Importantes

### 1. Banco de Dados
- **PostgreSQL** instalado como serviço Windows
- **Porta**: 5432
- **Usuário**: postgres
- **Senha**: rpg_password (configurável)
- **Banco**: rpg_db

### 2. Redis
- **Redis para Windows** instalado como serviço
- **Porta**: 6379
- **Sem senha por padrão** (configurável)

### 3. Python
- **Versão**: 3.11+
- **Ambiente virtual**: `venv/`
- **Dependências**: Via `requirements-windows.txt`

## 🔧 Scripts PowerShell Disponíveis

### Setup Inicial
```powershell
.\setup-windows.ps1
```
- Instala todas as dependências
- Configura serviços Windows
- Cria ambiente virtual
- Configura banco de dados

### Iniciar Aplicação
```powershell
# Modo desenvolvimento (padrão)
.\start-windows.ps1

# Modo desenvolvimento explícito
.\start-windows.ps1 -Development

# Modo produção
.\start-windows.ps1 -Production

# Verificar serviços
.\start-windows.ps1 -CheckServices

# Parar serviços
.\start-windows.ps1 -StopServices
```

### Sistema de Backup
```powershell
# Backup completo
.\backup-windows.ps1 -Full

# Backup apenas do banco
.\backup-windows.ps1 -DatabaseOnly

# Restaurar backup
.\backup-windows.ps1 -Restore -RestoreFile "backup.zip"

# Agendar backup automático
.\backup-windows.ps1 -Schedule
```

## 📁 Estrutura de Diretórios (Windows)

```
whatsapp-rpg-gm/
├── app/                    # Código da aplicação
├── alembic/               # Migrações do banco
├── venv/                  # Ambiente virtual Python
├── data/                  # Dados do jogo
├── logs/                  # Logs da aplicação
├── sessions/              # Sessões do WhatsApp
├── characters/            # Personagens salvos
├── backups/              # Backups automáticos
├── ai_configs/           # Configurações de IA
├── setup-windows.ps1     # Setup automático
├── start-windows.ps1     # Iniciar aplicação
├── start-quick.bat       # Início rápido
├── backup-windows.ps1    # Sistema de backup
├── .env.windows          # Configurações Windows
└── requirements-windows.txt # Dependências Windows
```

## 🔍 Verificações de Sistema

### Verificar Serviços
```powershell
# PostgreSQL
Get-Service postgresql*

# Redis
Get-Service Redis

# Status completo
.\start-windows.ps1 -CheckServices
```

### Verificar Conectividade
```powershell
# Testar PostgreSQL
psql -U postgres -h localhost -d rpg_db -c "SELECT 1;"

# Testar Redis
redis-cli ping

# Testar aplicação
curl http://localhost:8000/health
```

## 🐛 Solução de Problemas Comuns

### 1. PowerShell não executa scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. PostgreSQL não inicia
```powershell
# Verificar e reiniciar
Get-Service postgresql*
Restart-Service postgresql*

# Verificar logs
Get-EventLog -LogName Application -Source PostgreSQL
```

### 3. Redis não conecta
```powershell
# Status do serviço
Get-Service Redis

# Reinstalar se necessário
choco uninstall redis-64 -y
choco install redis-64 -y
```

### 4. Erro de permissão no diretório
- Execute PowerShell como Administrador
- Verifique permissões do diretório do projeto

### 5. Problemas com ambiente virtual
```powershell
# Recriar ambiente virtual
Remove-Item venv -Recurse -Force
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt
```

## 🎯 Configuração do .env

### Arquivo .env Principal
```env
# Evolution API (OBRIGATÓRIO)
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution_api
INSTANCE_NAME=sua_instancia

# IA (OBRIGATÓRIO - escolha um)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-sua_chave_openai

# Banco Windows (CONFIGURADO AUTOMATICAMENTE)
DATABASE_URL=postgresql://postgres:rpg_password@localhost:5432/rpg_db
REDIS_URL=redis://localhost:6379/0

# Segurança (GERAR TOKENS ÚNICOS)
VERIFY_TOKEN=seu_token_muito_seguro_12345
SECRET_KEY=sua_chave_secreta_muito_longa_e_segura_12345
```

## 🚀 Performance no Windows

### Otimizações Aplicadas
- **Workers limitados**: 1 worker por padrão no Windows
- **Pool de conexões menor**: 5 conexões máximo
- **Timeouts ajustados**: 15 segundos em vez de 30
- **Configurações específicas do PostgreSQL** para Windows

### Para Produção
```powershell
# Usar modo produção
.\start-windows.ps1 -Production

# Ou configurar como serviço Windows
# (instruções avançadas no README-WINDOWS.md)
```

## 📊 Monitoramento

### URLs Importantes
- **Aplicação**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Métricas**: http://localhost:8000/metrics

### Logs
```powershell
# Logs da aplicação
Get-Content logs\app.log -Wait

# Logs do PostgreSQL
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50
```

## 🔄 Atualizações

### Atualizar Código
```powershell
git pull origin main
pip install -r requirements-windows.txt
alembic upgrade head
```

### Atualizar Dependências
```powershell
pip install --upgrade -r requirements-windows.txt
```

## 🆘 Suporte e Troubleshooting

### 1. Verificar Status Geral
```powershell
.\start-windows.ps1 -CheckServices
```

### 2. Logs Detalhados
```powershell
# Habilitar debug no .env
DEBUG=true
LOG_LEVEL=DEBUG

# Reiniciar aplicação
.\start-windows.ps1
```

### 3. Reset Completo
```powershell
# Parar tudo
.\start-windows.ps1 -StopServices

# Limpar dados (CUIDADO!)
Remove-Item data, logs, sessions -Recurse -Force

# Reconfigurar
.\setup-windows.ps1
```

## 📈 Próximos Passos

Após a instalação bem-sucedida:

1. **Configure as chaves de API** no arquivo `.env`
2. **Teste a integração** com WhatsApp via Evolution API
3. **Configure backup automático** com `.\backup-windows.ps1 -Schedule`
4. **Monitore logs** regularmente
5. **Considere configurar como serviço Windows** para produção

---

**🎮 Divirta-se com seu RPG Game Master automatizado no Windows 11!**
