# Sistema de GM de RPG com IA para WhatsApp

Um aplicativo robusto para WhatsApp que atua como um agente de Mestre de Jogo (GM) de RPG utilizando Inteligência Artificial. O sistema integra múltiplas tecnologias para criar uma experiência imersiva de RPG através do WhatsApp.

## 🎯 Funcionalidades Principais

- **Integração com WhatsApp**: Utiliza a Evolution API para comunicação
- **IA Generativa**: Suporte para múltiplos provedores (OpenAI, Anthropic, Google, Ollama)
- **Sistema de Dados**: Rolagem precisa de dados D&D com dicepy
- **Gestão de Estado**: Persistência de personagens, mundo e narrativa
- **Interface Gráfica**: Dashboard para controle e monitoramento
- **Human-in-the-Loop**: Intervenção humana quando necessário

## 📋 Pré-requisitos

### Sistema
- Python 3.8 ou superior
- Node.js v20.10.0 (para Evolution API)
- PostgreSQL 12+
- Redis 6+

### Serviços Externos
- Conta OpenAI, Anthropic, Google ou servidor Ollama local
- Instância da Evolution API configurada

## 🚀 Instalação

### 1. Configuração da Evolution API

A Evolution API serve como ponte entre seu aplicativo e o WhatsApp.

#### Instalação com Docker (Recomendado)

```bash
# Clone o repositório da Evolution API
git clone -b v2.0.0 https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Crie o arquivo .env
cp .env.example .env

# Configure as variáveis de ambiente básicas
nano .env
```

Configure no `.env` da Evolution API:
```env
# Configurações básicas
SERVER_PORT=8080
SERVER_URL=http://localhost:8080
AUTHENTICATION_API_KEY=sua-chave-secreta-aqui

# Banco de dados PostgreSQL
DATABASE_CONNECTION_URI=postgresql://usuario:senha@localhost:5432/evolution_db

# Redis
REDIS_URI=redis://localhost:6379

# Webhook para integração
WEBHOOK_GLOBAL_URL=http://localhost:3000/webhook
WEBHOOK_GLOBAL_ENABLED=true
```

#### Execute com Docker Compose

```bash
# Inicie os serviços
docker-compose up -d

# Verifique se está funcionando
curl http://localhost:8080
```

### 2. Configuração do Projeto RPG GM

#### Clone e Instale Dependências

```bash
# Clone este repositório
git clone <seu-repositorio>
cd rpg-gm-whatsapp

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

#### Arquivo requirements.txt

```txt
# Integração WhatsApp
evolutionapi==1.0.0
requests==2.31.0

# IA e LLM
instructor[anthropic,openai,google]==1.3.3
llama-index==0.10.57
openai==1.30.5
anthropic==0.25.8

# Dados e RPG
dicepy==2.3.0
dice==4.0.0

# Interface e Web
streamlit==1.28.0
gradio==4.29.0
fastapi==0.104.1
uvicorn==0.24.0

# Banco de dados e estado
sqlalchemy==2.0.23
redis==5.0.1
psycopg2-binary==2.9.9

# Utilitários
pydantic==2.5.0
python-dotenv==1.0.0
pyyaml==6.0.1
websockets==12.0

# Interface gráfica avançada (opcional)
pyqt6==6.6.0
```

### 3. Configuração do Ambiente

Crie um arquivo `.env` no diretório do projeto:

```env
# === CONFIGURAÇÕES GERAIS ===
APP_NAME=RPG_GM_Bot
DEBUG=True
LOG_LEVEL=INFO

# === EVOLUTION API ===
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-secreta-aqui
EVOLUTION_INSTANCE_NAME=rpg-gm-instance

# === BANCO DE DADOS ===
DATABASE_URL=postgresql://usuario:senha@localhost:5432/rpg_gm_db
REDIS_URL=redis://localhost:6379/0

# === INTELIGÊNCIA ARTIFICIAL ===
# OpenAI
OPENAI_API_KEY=sua-chave-openai-aqui
OPENAI_MODEL=gpt-4o-mini

# Anthropic
ANTHROPIC_API_KEY=sua-chave-anthropic-aqui
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Google
GOOGLE_API_KEY=sua-chave-google-aqui
GOOGLE_MODEL=gemini-pro

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Provedor padrão (openai, anthropic, google, ollama)
DEFAULT_LLM_PROVIDER=openai

# === CONFIGURAÇÕES DE RPG ===
RPG_SYSTEM=dnd5e
AUTO_DICE_ROLL=true
DIFFICULTY_LEVEL=medium

# === INTERFACE WEB ===
WEB_PORT=3000
STREAMLIT_PORT=8501
GRADIO_PORT=7860

# === HUMAN-IN-THE-LOOP ===
HITL_ENABLED=true
HITL_WEBHOOK_URL=http://localhost:3000/hitl
GM_NOTIFICATION_EMAIL=gm@exemplo.com

# === WEBHOOKS ===
WEBHOOK_SECRET=sua-chave-webhook-secreta
WEBHOOK_TIMEOUT=30
```

## 🏃‍♂️ Como Executar

### 1. Preparação do Banco de Dados

```bash
# Inicie PostgreSQL e Redis
sudo systemctl start postgresql redis

# Crie o banco de dados
createdb rpg_gm_db

# Execute as migrações (se houver)
python manage.py migrate
```

### 2. Configuração da Instância WhatsApp

```bash
# Execute o script de configuração
python scripts/setup_whatsapp_instance.py
```

Este script irá:
- Criar uma instância no Evolution API
- Configurar webhooks
- Gerar QR Code para conectar ao WhatsApp

### 3. Inicialização dos Serviços

#### Modo Desenvolvimento

```bash
# Terminal 1: Evolution API (se não estiver rodando via Docker)
cd evolution-api
npm run start:prod

# Terminal 2: Aplicação principal
python main.py

# Terminal 3: Interface Streamlit (opcional)
streamlit run dashboard/app.py --port 8501

# Terminal 4: Interface Gradio (opcional)
python interfaces/gradio_app.py
```

#### Modo Produção

```bash
# Use PM2 para gerenciar os processos
npm install -g pm2

# Inicie o aplicativo principal
pm2 start ecosystem.config.js

# Monitore os logs
pm2 logs
```

### Arquivo ecosystem.config.js

```javascript
module.exports = {
  apps: [
    {
      name: 'rpg-gm-main',
      script: 'python',
      args: 'main.py',
      interpreter: './venv/bin/python',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'rpg-gm-dashboard',
      script: 'streamlit',
      args: 'run dashboard/app.py --port 8501',
      interpreter: './venv/bin/streamlit'
    }
  ]
};
```

## 📁 Estrutura do Projeto

```
rpg-gm-whatsapp/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                     # Aplicação principal
├── ecosystem.config.js         # Configuração PM2
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── game_state.py      # Gestor de estado do jogo
│   │   ├── character_manager.py
│   │   ├── world_state.py
│   │   └── narrative_tracker.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── llm_manager.py     # Gerenciador de LLMs
│   │   ├── prompt_templates.py
│   │   ├── rag_system.py      # Sistema RAG com LlamaIndex
│   │   └── reasoning.py       # Chain/Tree of thought
│   │
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   ├── evolution_client.py # Cliente Evolution API
│   │   ├── message_handler.py
│   │   ├── webhook_server.py
│   │   └── interactive_messages.py
│   │
│   ├── rpg/
│   │   ├── __init__.py
│   │   ├── dice_system.py     # Sistema de dados
│   │   ├── rules_engine.py    # Motor de regras D&D
│   │   ├── combat_manager.py
│   │   └── spell_system.py
│   │
│   ├── hitl/
│   │   ├── __init__.py
│   │   ├── intervention_detector.py
│   │   ├── notification_system.py
│   │   └── handoff_manager.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       └── validation.py
│
├── interfaces/
│   ├── streamlit_dashboard.py  # Dashboard Streamlit
│   ├── gradio_app.py          # Interface Gradio
│   └── web_interface.py       # Interface FastAPI
│
├── data/
│   ├── rules/                 # Regras D&D e RPG
│   ├── lore/                  # Lore e worldbuilding
│   └── characters/            # Templates de personagens
│
├── scripts/
│   ├── setup_whatsapp_instance.py
│   ├── migrate_database.py
│   └── backup_game_state.py
│
└── tests/
    ├── test_ai/
    ├── test_whatsapp/
    ├── test_rpg/
    └── test_integration/
```

## 🔧 Configuração Avançada

### Configuração de Múltiplos LLMs

```python
# src/ai/llm_manager.py
LLM_CONFIGS = {
    'openai': {
        'model': 'gpt-4o-mini',
        'max_tokens': 1000,
        'temperature': 0.7
    },
    'anthropic': {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 1000,
        'temperature': 0.7
    },
    'local': {
        'model': 'llama3',
        'base_url': 'http://localhost:11434'
    }
}
```

### Configuração de Sistema RAG

```python
# src/ai/rag_system.py
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def setup_rag_system():
    # Carrega documentos de regras D&D
    documents = SimpleDirectoryReader("./data/rules").load_data()
    
    # Cria índice vetorial
    index = VectorStoreIndex.from_documents(documents)
    
    # Configura query engine
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="tree_summarize"
    )
    
    return query_engine
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Evolution API não conecta**
   ```bash
   # Verifique se o serviço está rodando
   curl http://localhost:8080
   
   # Verifique os logs
   docker logs evolution_api
   ```

2. **Erro de conexão com banco de dados**
   ```bash
   # Teste a conexão
   psql -h localhost -U usuario -d rpg_gm_db
   ```

3. **WhatsApp não recebe mensagens**
   - Verifique se a instância está conectada
   - Confirme se o webhook está configurado corretamente
   - Teste o endpoint webhook manualmente

### Logs e Monitoramento

```bash
# Logs da aplicação principal
tail -f logs/rpg_gm.log

# Logs da Evolution API
docker logs -f evolution_api

# Monitoramento com PM2
pm2 monit
```

## 📖 Uso Básico

### 1. Conectar ao WhatsApp

1. Execute a aplicação
2. Acesse o dashboard em `http://localhost:8501`
3. Escaneie o QR Code com seu WhatsApp
4. Aguarde a confirmação de conexão

### 2. Iniciar uma Sessão de RPG

```
Usuário: /iniciar campanha
Bot: 🎲 Bem-vindo à aventura! Vou ser seu Mestre de Jogo.
     Que tipo de personagem você gostaria de criar?
     
     [Guerreiro] [Mago] [Ladino] [Paladino]
```

### 3. Comandos Disponíveis

- `/rolar d20` - Rola dados
- `/status` - Mostra status do personagem
- `/inventario` - Lista itens
- `/ajuda` - Lista comandos
- `/gm <mensagem>` - Contata GM humano

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Avisos Importantes

- **Evolution API**: Respeite os termos de uso da Evolution API
- **WhatsApp**: Use conforme as políticas do WhatsApp Business
- **LLMs**: Monitore uso e custos das APIs de IA
- **Dados**: Implemente backup regular do estado do jogo

## 📞 Suporte

- **Issues**: [GitHub Issues](link-para-issues)
- **Documentação**: [Wiki do Projeto](link-para-wiki)
- **Comunidade**: [Discord/Telegram](link-para-comunidade)

---

Desenvolvido com ❤️ para a comunidade de RPG
