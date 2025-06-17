# 🎯 WhatsApp RPG GM - Setup Reproduzível para Windows 11

## 📋 Visão Geral

Este projeto foi **completamente adaptado** para ser **reproduzível em qualquer configuração** no Windows 11. O script de setup é **interativo e inteligente**, funcionando com:

- ✅ **PostgreSQL**: Local, remoto, Docker ou nuvem (AWS RDS, Azure, etc.)
- ✅ **Redis**: Local, remoto, Docker ou nuvem (ElastiCache, Azure Cache, etc.)  
- ✅ **Python**: Detecta instalações existentes ou instala automaticamente
- ✅ **Qualquer infraestrutura**: Adapta-se à sua configuração específica

## 🚀 Instalação Rápida

### 1. Setup Interativo (Recomendado)

```powershell
# Abrir PowerShell como Administrador
cd z:\Dev\RPG\whatsapp-rpg-gm

# Executar setup interativo
.\setup-windows.ps1
```

**O script irá perguntar sobre sua infraestrutura:**
- 🐍 **Python**: Usar existente ou instalar?
- 🐘 **PostgreSQL**: Local, remoto, Docker ou nuvem?
- 🔴 **Redis**: Local, remoto, Docker ou nuvem?
- 🔗 **Conectividade**: Testa automaticamente todos os serviços
- ⚙️ **Configuração**: Gera .env personalizado

### 2. Opções de Execução

```powershell
# Setup interativo completo
.\setup-windows.ps1

# Setup automático (sem perguntas)
.\setup-windows.ps1 -AutoMode

# Ver exemplos de configuração
.\examples-setup.ps1

# Testar conectividade antes do setup
.\test-connectivity.ps1 -Interactive
```

### 3. Iniciar Aplicação

```powershell
# Iniciar com verificação automática
.\start-windows.ps1

# Verificar status dos serviços
.\start-windows.ps1 -CheckServices
```

## 🏗️ Cenários de Infraestrutura Suportados

### 1. **Tudo Local** (Desenvolvimento)
- PostgreSQL instalado localmente
- Redis instalado localmente
- Setup instala tudo automaticamente

### 2. **Serviços Remotos** (Produção)
- PostgreSQL em servidor dedicado (ex: 192.168.1.100:5432)
- Redis em servidor dedicado (ex: 192.168.1.101:6379)
- Setup conecta e configura automaticamente

### 3. **Docker/Containers**
- PostgreSQL em container Docker
- Redis em container Docker
- Setup configura portas mapeadas

### 4. **Nuvem/Cloud**
- AWS RDS PostgreSQL
- AWS ElastiCache Redis
- Azure Database/Cache
- Google Cloud SQL/Memorystore

### 5. **Híbrido**
- PostgreSQL local + Redis remoto
- PostgreSQL nuvem + Redis local
- Qualquer combinação

## 🛠️ Como Funciona o Setup

### Detecção Automática do Python
```powershell
# O script verifica:
# - Comandos: python, python3, py
# - Locais: C:\Python*, Program Files, AppData
# - Versões: Mostra todas as instalações encontradas
# - Escolha: Permite escolher qual usar ou instalar nova
```

### Configuração Dinâmica do PostgreSQL
```powershell
# Opções detectadas automaticamente:
# 1. Local: Detecta serviço Windows PostgreSQL
# 2. Remoto: Testa conectividade de rede
# 3. Docker: Configura para containers
# 4. Nuvem: Suporte a RDS, Azure, GCP
```

### Configuração Dinâmica do Redis
```powershell
# Opções detectadas automaticamente:
# 1. Local: Detecta serviço Windows Redis
# 2. Remoto: Testa conectividade de rede  
# 3. Docker: Configura para containers
# 4. Nuvem: Suporte a ElastiCache, Azure Cache
```

## 📋 Exemplos de Uso

### Exemplo 1: Desenvolvimento Local
```powershell
.\setup-windows.ps1
# Responder:
# - Python: Usar existente ou instalar
# - PostgreSQL: "local" → Instalar local
# - Redis: "local" → Instalar local
```

### Exemplo 2: Servidor Remoto
```powershell
.\setup-windows.ps1
# Responder:
# - Python: Usar existente
# - PostgreSQL: "remoto" → IP: 192.168.1.100, Porta: 5432
# - Redis: "remoto" → IP: 192.168.1.101, Porta: 6379
```

### Exemplo 3: AWS Cloud
```powershell
.\setup-windows.ps1
# Responder:
# - PostgreSQL: "nuvem" → Host: mydb.xxxxx.us-east-1.rds.amazonaws.com
# - Redis: "nuvem" → Host: myredis.xxxxx.cache.amazonaws.com
```

### Exemplo 4: Docker
```powershell
.\setup-windows.ps1
# Responder:
# - PostgreSQL: "docker" → Host: localhost, Porta: 5432
# - Redis: "docker" → Host: localhost, Porta: 6379
```

## 🔧 Scripts Disponíveis

### Setup e Configuração
```powershell
.\setup-windows.ps1          # Setup interativo completo
.\setup-windows.ps1 -AutoMode # Setup automático
.\examples-setup.ps1          # Exemplos de configuração
```

### Teste e Diagnóstico
```powershell
.\test-connectivity.ps1 -Interactive          # Teste interativo
.\test-connectivity.ps1 -PostgreSQLHost "IP"  # Teste específico
.\test-connectivity.ps1 -Detailed             # Teste detalhado
```

### Execução
```powershell
.\start-windows.ps1              # Iniciar aplicação
.\start-windows.ps1 -CheckServices # Verificar serviços
.\start-windows.ps1 -StopServices  # Parar serviços
```

### Backup
```powershell
.\backup-windows.ps1 -Full       # Backup completo
.\backup-windows.ps1 -Schedule   # Agendar backup
```

## 📁 Estrutura Resultante

Após o setup, você terá:

```
whatsapp-rpg-gm/
├── .env                     # Configurações da SUA infraestrutura
├── venv/                    # Ambiente virtual Python
├── data/                    # Dados da aplicação
├── logs/                    # Logs da aplicação
├── sessions/                # Sessões WhatsApp
├── characters/              # Personagens salvos
├── backups/                 # Backups automáticos
└── ai_configs/              # Configurações de IA
```

## ⚙️ Arquivo .env Gerado

O setup gera automaticamente um `.env` com suas configurações específicas:

```env
# Exemplo para servidor remoto
DATABASE_URL=postgresql://postgres:senha@192.168.1.100:5432/whatsapp_rpg_gm
REDIS_URL=redis://192.168.1.101:6379/0

# Exemplo para nuvem AWS
DATABASE_URL=postgresql://user:pass@mydb.xxxxx.rds.amazonaws.com:5432/rpgdb
REDIS_URL=redis://myredis.xxxxx.cache.amazonaws.com:6379/0

# Configurações detectadas automaticamente
PYTHON_PATH=C:\Python311\python.exe
POSTGRESQL_TYPE=remote
REDIS_TYPE=remote
```

## 🔍 Resolução de Problemas

### 1. Teste de Conectividade
```powershell
# Diagnosticar problemas de rede
.\test-connectivity.ps1 -PostgreSQLHost "SEU_IP" -RedisHost "SEU_IP" -Detailed
```

### 2. Verificar Configurações
```powershell
# Ver configurações atuais
.\start-windows.ps1 -CheckServices
```

### 3. Reconfigurar
```powershell
# Executar setup novamente
.\setup-windows.ps1
# (Irá detectar configurações existentes)
```

### 4. Problemas Comuns

#### PowerShell não executa scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Erro de conectividade
```powershell
# Verificar firewall
# Verificar se serviços estão rodando
# Verificar credenciais no .env
```

#### Python não encontrado
```powershell
# O setup detecta automaticamente
# Ou permite especificar caminho manualmente
```

## 🎯 Vantagens da Nova Abordagem

### ✅ **Reproduzível**
- Funciona em qualquer configuração
- Não assume IPs ou configurações específicas
- Detecta ambiente existente

### ✅ **Flexível**
- Suporta qualquer infraestrutura
- Local, remoto, Docker, nuvem
- Configuração híbrida

### ✅ **Inteligente**
- Detecta instalações existentes
- Testa conectividade automaticamente
- Gera configurações personalizadas

### ✅ **Fácil de Usar**
- Interface interativa clara
- Validação em tempo real
- Documentação integrada

## 🚀 Próximos Passos

Após o setup bem-sucedido:

1. **Configure as chaves de API** no arquivo `.env`:
   - Evolution API URL e chave
   - Chave da API de IA (OpenAI, Google, Anthropic)
   - Tokens de segurança únicos

2. **Inicie a aplicação**:
   ```powershell
   .\start-windows.ps1
   ```

3. **Acesse a documentação**:
   - http://localhost:8000/docs

4. **Configure backup automático** (opcional):
   ```powershell
   .\backup-windows.ps1 -Schedule
   ```

---

**🎮 Agora seu WhatsApp RPG GM está configurado para SUA infraestrutura específica!**
