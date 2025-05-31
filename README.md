# 🎲 WhatsApp RPG GM

Sistema completo de Mestre de Jogo com Inteligência Artificial para WhatsApp, especializado em D&D 5e.

## 🎯 Visão Geral

O WhatsApp RPG GM é uma aplicação robusta que atua como um Mestre de Jogo automatizado para sessões de RPG via WhatsApp. Utiliza Inteligência Artificial para gerar narrativas, gerenciar personagens, processar rolagens de dados e coordenar sessões completas de D&D 5e.

### ✨ Características Principais

- **🤖 IA Avançada**: Múltiplos provedores (OpenAI, Anthropic, Google, Ollama)
- **🎮 Sistema Completo D&D 5e**: Personagens, dados, combate, magia
- **📱 Integração WhatsApp**: Via Evolution API
- **👨‍🏫 Human-in-the-Loop**: Intervenção humana quando necessário
- **🔧 Modular e Escalável**: Arquitetura preparada para expansão
- **📊 Dashboard Web**: Interface completa de gerenciamento
- **🐳 Docker Ready**: Containerização completa

## 🚀 Instalação Rápida

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento)
- Evolution API configurada
- Pelo menos um provedor de IA configurado

### 1. Clone e Configure

```bash
git clone https://github.com/seu-usuario/whatsapp-rpg-gm.git
cd whatsapp-rpg-gm

# Copie e configure as variáveis de ambiente
cp .env.example .env
nano .env  # Configure suas chaves de API
```

### 2. Configure Variáveis Essenciais

No arquivo `.env`, configure pelo menos:

```bash
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-evolution-api
EVOLUTION_INSTANCE_NAME=rpg-gm-bot
WEBHOOK_BASE_URL=https://seudominio.com

# IA (pelo menos uma)
OPENAI_API_KEY=sk-sua-chave-openai
# ou
ANTHROPIC_API_KEY=sk-ant-sua-chave-anthropic

# Segurança
SECRET_KEY=sua-chave-secreta-complexa

# Base de dados (as padrão funcionam para desenvolvimento)
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/rpg_gm_db
REDIS_URL=redis://redis:6379/0
```

### 3. Inicie os Serviços

```bash
# Apenas serviços essenciais
docker-compose up -d app postgres redis evolution-api

# Com dashboard (recomendado)
docker-compose --profile dashboard up -d

# Completo com monitoramento
docker-compose --profile dashboard --profile monitoring up -d
```

### 4. Acesse as Interfaces

- **API Principal**: http://localhost:3000
- **Documentação**: http://localhost:3000/docs
- **Dashboard**: http://localhost:8501 (Streamlit)
- **Interface Gradio**: http://localhost:7860
- **Evolution API**: http://localhost:8080

## 📋 Comandos WhatsApp

### Comandos Básicos

- `/start` - Iniciar o jogo
- `/help` - Mostrar ajuda
- `/status` - Ver status do personagem
- `/inventario` - Ver inventário

### Criação de Personagem

- `/criar-personagem` - Criação interativa
- `/criar-personagem auto` - Criação automática

### Sistema de Dados

- `/rolar 1d20+5` - Rolar dados com modificador
- `/rolar vantagem` - Rolar com vantagem
- `/rolar desvantagem` - Rolar com desvantagem
- `/rolar atributos` - Rolar novos atributos

### Combate

- `/ataque [alvo]` - Atacar inimigo
- `/magia [nome]` - Lançar magia
- `/defesa` - Ação de defesa
- `/iniciativa` - Rolar iniciativa

### Comandos GM

- `/gm pausar` - Pausar sessão
- `/gm anuncio [mensagem]` - Anúncio global
- `/gm backup` - Criar backup
- `/gm stats` - Estatísticas

## 🏗️ Arquitetura

```
whatsapp-rpg-gm/
├── src/
│   ├── core/           # Núcleo (config, database, game_manager)
│   ├── whatsapp/       # Integração Evolution API
│   ├── ai/             # Sistema de IA
│   ├── rpg/            # Mecânicas D&D 5e
│   ├── hitl/           # Human-in-the-Loop
│   └── interfaces/     # APIs e WebSocket
├── frontend/           # Interface web
├── config/             # Configurações
├── data/               # Dados do jogo
└── docs/               # Documentação
```

### Componentes Principais

#### 🎮 Game Manager
Coordena todas as operações de jogo:
- Gerenciamento de sessões
- Estado dos personagens
- Integração com IA
- Processamento de comandos

#### 🤖 AI Coordinator
Sistema de IA com múltiplos provedores:
- **OpenAI GPT-4**: Narrativas principais
- **Anthropic Claude**: Diálogos de NPCs
- **Google Gemini**: Descrições de ambiente
- **Ollama**: LLM local para backup

#### 🎲 Dice System
Sistema completo de dados D&D 5e:
- Suporte a todas as expressões (1d20+5, 2d6, etc.)
- Vantagem/Desvantagem
- Críticos e falhas críticas
- Testes de resistência

#### 👨‍🏫 HITL Manager
Human-in-the-Loop para situações complexas:
- Detecção automática de situações críticas
- Notificações via Discord/Email/SMS
- Interface para GM humano intervir

## 🔧 Configuração Avançada

### Provedores de IA

Configure múltiplos provedores para redundância:

```bash
# OpenAI (recomendado para narrativas)
OPENAI_API_KEY=sk-sua-chave
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Anthropic (excelente para diálogos)
ANTHROPIC_API_KEY=sk-ant-sua-chave
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Google (bom custo-benefício)
GOOGLE_API_KEY=sua-chave-google
GOOGLE_MODEL=gemini-pro

# Ollama (local, sem custos)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b
```

### Evolution API

1. Instale a Evolution API:
```bash
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
docker-compose up -d
```

2. Configure no `.env`:
```bash
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=sua-chave
EVOLUTION_INSTANCE_NAME=rpg-gm-bot
```

3. Configure webhook:
- Acesse http://localhost:8080
- Crie instância "rpg-gm-bot"
- Configure webhook: `https://seudominio.com/webhook`

### HITL Notifications

Configure notificações para intervenção humana:

```bash
# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/seu-webhook

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=seuemail@gmail.com
SMTP_PASSWORD=sua-senha

# SMS via Twilio
TWILIO_ACCOUNT_SID=seu-sid
TWILIO_AUTH_TOKEN=seu-token
TWILIO_PHONE_NUMBER=+5511999999999
```

## 📊 Monitoramento

### Métricas Disponíveis

- Sessões ativas
- Total de jogadores
- Rolagens de dados
- Mensagens processadas
- Tempo de resposta da IA
- Status da Evolution API
- Triggers HITL

### Interfaces de Monitoramento

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Logs**: http://localhost:3000/api/logs

## 🛠️ Desenvolvimento

### Configuração Local

```bash
# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependências
pip install -r requirements.txt

# Executar localmente
python main.py
```

### Estrutura de Dados

#### Personagem
```python
{
    "name": "Thorin Machado de Ferro",
    "race": "anao",
    "character_class": "guerreiro",
    "level": 3,
    "hp_current": 28,
    "hp_max": 32,
    "armor_class": 16,
    "attributes": {
        "strength": 16,
        "dexterity": 12,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 13,
        "charisma": 8
    }
}
```

#### Sessão
```python
{
    "id": "session_001",
    "state": "active",
    "players": ["player1", "player2"],
    "current_scene": "Taverna do Dragão",
    "world_state": {
        "location": "Vila de Pedravale",
        "time_of_day": "tarde",
        "weather": "ensolarado"
    }
}
```

### Extensibilidade

O sistema foi projetado para fácil extensão:

#### Adicionar Nova Classe de Personagem
```python
# src/rpg/character_manager.py
CharacterClass.ARTIFICER = "artificer"

class_data[CharacterClass.ARTIFICER] = {
    'hit_die': 8,
    'proficiencies': ['arcana', 'investigation'],
    'starting_equipment': ['light_crossbow', 'thieves_tools'],
    'features': ['magical_tinkering', 'infuse_item']
}
```

#### Adicionar Novo Provedor de IA
```python
# src/ai/ai_coordinator.py
class CustomAIProvider(BaseAIProvider):
    async def generate(self, prompt: str) -> str:
        # Implementar integração
        pass
```

## 🚨 Troubleshooting

### Problemas Comuns

#### Evolution API não conecta
```bash
# Verificar logs
docker-compose logs evolution-api

# Recriar instância
curl -X DELETE http://localhost:8080/instance/delete/rpg-gm-bot
curl -X POST http://localhost:8080/instance/create -d '{"instanceName":"rpg-gm-bot"}'
```

#### IA não responde
```bash
# Verificar configuração
curl http://localhost:3000/api/status

# Testar provedor
curl -X POST http://localhost:3000/api/dice/roll -d '{"expression":"1d20"}'
```

#### Banco de dados
```bash
# Acessar PostgreSQL
docker-compose exec postgres psql -U postgres -d rpg_gm_db

# Reset do Redis
docker-compose exec redis redis-cli FLUSHALL
```

### Logs Úteis

```bash
# Todos os logs
docker-compose logs -f

# Apenas aplicação
docker-compose logs -f app

# Com filtro
docker-compose logs app | grep ERROR
```

## 🔒 Segurança

### Configurações Recomendadas

```bash
# Chaves fortes
SECRET_KEY=$(openssl rand -hex 32)
EVOLUTION_WEBHOOK_SECRET=$(openssl rand -hex 16)

# CORS restritivo
CORS_ORIGINS=https://seudominio.com,https://admin.seudominio.com

# Rate limiting
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_PERIOD=60
```

### Backup

```bash
# Backup automático
docker-compose exec postgres pg_dump -U postgres rpg_gm_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U postgres rpg_gm_db < backup_20240101.sql
```

## 📈 Performance

### Recomendações de Hardware

- **Mínimo**: 2 CPU, 4GB RAM, 20GB disco
- **Recomendado**: 4 CPU, 8GB RAM, 50GB disco
- **Produção**: 8 CPU, 16GB RAM, 100GB disco SSD

### Otimizações

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🤝 Contribuição

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Diretrizes

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Documente APIs e funções importantes
- Mantenha compatibilidade com versões anteriores

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Evolution API** - Integração WhatsApp
- **FastAPI** - Framework web moderno
- **D&D 5e** - Sistema de RPG base
- **OpenAI/Anthropic/Google** - Provedores de IA
- **Comunidade RPG** - Feedback e sugestões

## 📞 Suporte

- **Issues**: https://github.com/seu-usuario/whatsapp-rpg-gm/issues
- **Discord**: https://discord.gg/seu-servidor
- **Email**: suporte@seudominio.com

---

*Desenvolvido com ❤️ para a comunidade RPG brasileira*
