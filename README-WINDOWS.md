# WhatsApp RPG Game Master - Windows 11 🎲🪟

Guia completo para executar o WhatsApp RPG Game Master no Windows 11 **sem Docker e WSL**.

## 🚀 Instalação Rápida no Windows 11

### Opção 1: Setup Automático Inteligente (Recomendado)

O script de setup agora detecta automaticamente instalações existentes e serviços remotos:

```powershell
# 1. Testar conectividade com seus serviços remotos
.\test-connectivity.ps1

# 2. Executar setup inteligente (como Administrador)
.\setup-windows.ps1

# 3. Para setup totalmente automático
.\setup-windows.ps1 -AutoMode

# 4. Para pular componentes específicos
.\setup-windows.ps1 -SkipPython -SkipPostgreSQL
```

O script irá:
- ✅ Detectar Python existente ou instalar Python 3.11
- ✅ Configurar PostgreSQL remoto (192.168.22.111:5432) ou local
- ✅ Configurar Redis remoto (192.168.22.111:6379) ou local
- ✅ Testar conectividade com os serviços
- ✅ Criar ambiente virtual Python
- ✅ Gerar arquivo .env com configurações detectadas
- ✅ Instalar dependências
- ✅ Configurar banco de dados

### Opção 2: Configuração Manual com Serviços Remotos

Se você já tem PostgreSQL e Redis rodando em `192.168.22.111`:

```powershell
# 1. Testar conectividade primeiro
.\test-connectivity.ps1 -PostgreSQLHost "192.168.22.111" -RedisHost "192.168.22.111" -Detailed

# 2. Configurar apenas Python e dependências
.\setup-windows.ps1 -SkipPostgreSQL -SkipRedis

# 3. Editar .env com suas credenciais
# 4. Iniciar aplicação
.\start-windows.ps1
```

## ⚙️ Configuração Manual (Alternativa)

Se preferir instalação manual:

### 1. Instalar Dependências

#### Via Chocolatey (Recomendado)
```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Instalar dependências
choco install python311 postgresql redis-64 git -y
```

#### Via Downloads Manuais
- [Python 3.11](https://www.python.org/downloads/windows/)
- [PostgreSQL](https://www.postgresql.org/download/windows/)
- [Redis para Windows](https://github.com/tporadowski/redis/releases)

### 2. Configurar Serviços

```powershell
# Iniciar e configurar PostgreSQL
Start-Service postgresql*
Set-Service -Name postgresql* -StartupType Automatic

# Iniciar e configurar Redis
Start-Service Redis
Set-Service -Name Redis -StartupType Automatic
```

### 3. Configurar Projeto

```powershell
# Clonar repositório
git clone https://github.com/seu-usuario/whatsapp-rpg-gm.git
cd whatsapp-rpg-gm

# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements-windows.txt

# Configurar banco
createdb -U postgres -h localhost rpg_db
alembic upgrade head
```

## 📝 Configuração do .env

Copie `.env.windows` para `.env` e configure:

```env
# WhatsApp Evolution API
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution_api
INSTANCE_NAME=sua_instancia_whatsapp

# IA (escolha um)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-sua_chave_openai

# Banco (configuração Windows)
DATABASE_URL=postgresql://postgres:rpg_password@localhost:5432/rpg_db

# Redis (configuração Windows)
REDIS_URL=redis://localhost:6379/0

# Segurança
VERIFY_TOKEN=seu_token_muito_seguro_12345
SECRET_KEY=sua_chave_secreta_muito_longa_e_segura_12345
```

## 🔧 Scripts Disponíveis

### PowerShell Scripts

```powershell
# Setup completo (executar como Admin)
.\setup-windows.ps1

# Iniciar aplicação
.\start-windows.ps1

# Iniciar em modo desenvolvimento
.\start-windows.ps1 -Development

# Iniciar em modo produção
.\start-windows.ps1 -Production

# Verificar serviços
.\start-windows.ps1 -CheckServices

# Parar todos os serviços
.\start-windows.ps1 -StopServices
```

### Batch Scripts (Alternativa Simples)

```batch
REM Início rápido
start-quick.bat
```

## 🐛 Resolução de Problemas

### PostgreSQL não inicia
```powershell
# Verificar status
Get-Service postgresql*

# Reiniciar serviço
Restart-Service postgresql*

# Verificar logs
Get-EventLog -LogName Application -Source PostgreSQL
```

### Redis não conecta
```powershell
# Verificar status
Get-Service Redis

# Testar conexão
redis-cli ping

# Reinstalar se necessário
choco uninstall redis-64 -y
choco install redis-64 -y
```

### Erro de permissão no PowerShell
```powershell
# Ajustar política de execução
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problemas com Python/pip
```powershell
# Verificar versão
python --version
pip --version

# Atualizar pip
python -m pip install --upgrade pip

# Reinstalar em ambiente limpo
Remove-Item venv -Recurse -Force
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt
```

## 📊 Monitoramento

### Verificar Status dos Serviços
```powershell
# Status completo
.\start-windows.ps1 -CheckServices

# PostgreSQL
Get-Service postgresql*

# Redis  
Get-Service Redis

# Aplicação Python
Get-Process python | Where-Object {$_.CommandLine -like "*uvicorn*"}
```

### Logs da Aplicação
```powershell
# Ver logs em tempo real
Get-Content logs\app.log -Wait

# Logs do PostgreSQL
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50
```

## 🔒 Segurança no Windows

### Firewall
O script de setup configura automaticamente:
- Porta 8000 (HTTP)
- Porta 5432 (PostgreSQL - apenas local)
- Porta 6379 (Redis - apenas local)

### Serviços Windows
- PostgreSQL configurado para iniciar automaticamente
- Redis configurado para iniciar automaticamente
- Aplicação pode ser configurada como serviço Windows (opcional)

## 🚀 Performance no Windows

### Otimizações Aplicadas
- Pool de conexões ajustado para Windows
- Timeouts otimizados
- Configurações específicas do PostgreSQL para Windows
- Uso de workers limitado (adequado para desenvolvimento)

### Para Produção
```powershell
# Iniciar com mais workers
.\start-windows.ps1 -Production
```

## 📱 Diferenças do Modo Docker

| Aspecto | Docker | Windows Nativo |
|---------|--------|----------------|
| PostgreSQL | Container | Serviço Windows |
| Redis | Container | Serviço Windows |
| Volumes | Docker volumes | Diretórios locais |
| Logs | Docker logs | Arquivos locais |
| Backup | Volume backup | Scripts PowerShell |
| Atualização | Rebuild image | pip upgrade |

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs**: `logs\app.log`
2. **Teste os serviços**: `.\start-windows.ps1 -CheckServices`
3. **Consulte a documentação**: http://localhost:8000/docs
4. **Issues no GitHub**: [Link do repositório]

## 📈 Próximos Passos

Após a instalação:

1. Configure o arquivo `.env` com suas chaves reais
2. Configure a Evolution API
3. Teste a integração com WhatsApp
4. Configure backup automático
5. Configure monitoramento (opcional)

---

**💡 Dica**: Para desenvolvimento, use o modo desenvolvimento. Para produção, configure um serviço Windows ou use IIS como proxy reverso.
