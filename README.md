<<<<<<< HEAD
# 🎲 WhatsApp RPG GM - Protótipo

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema de Mestre de Jogo (Game Master) automatizado via WhatsApp com Inteligência Artificial, integrado com Evolution API.

## 📋 Visão Geral

Este protótipo implementa um sistema que permite jogar RPG via WhatsApp, usando IA como Mestre de Jogo, com as seguintes funcionalidades:

- **Integração WhatsApp**: Conecta-se ao WhatsApp via [Evolution API](https://github.com/EvolutionAPI/evolution-api)
- **Inteligência Artificial**: Utiliza LLMs como GM, com opção de múltiplos provedores
- **Sistema de Dados**: Implementa rolagem de dados para D&D 5e
- **Sistema HITL**: Human-in-the-Loop para intervenção humana quando necessário
- **Interfaces Web**: Dashboard Streamlit e interface Gradio para administração

## 🏗️ Arquitetura

O sistema foi projetado com a seguinte arquitetura modular:

```
whatsapp-rpg-gm/
├── src/
│   ├── core/           # Núcleo do sistema
│   ├── whatsapp/       # Integração Evolution API
│   ├── ai/             # Módulos de IA
│   ├── rpg/            # Sistema de RPG e dados
│   ├── hitl/           # Human-in-the-Loop
│   └── interfaces/     # Interfaces web
├── config/             # Configurações
├── data/               # Dados do jogo
├── tests/              # Testes
├── main.py             # Aplicação principal
├── requirements.txt    # Dependências
├── Dockerfile          # Configuração Docker
├── docker-compose.yml  # Docker Compose
└── README.md           # Esta documentação
```

## 🚀 Executando o Protótipo

### Pré-requisitos

- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/) (recomendado)
- [Evolution API](https://github.com/EvolutionAPI/evolution-api) instalada e configurada
- URL pública para webhooks (ngrok, servidor próprio)

### 🐳 Instalação com Docker (Recomendado)

1. **Clone o repositório**
   ```bash
   git clone https://github.com/alex-des-santos/whatsapp-rpg-gm.git
   cd whatsapp-rpg-gm
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

3. **Inicie os contêineres**
   ```bash
   docker-compose up -d
   ```

4. **Verifique os logs**
   ```bash
   docker-compose logs -f
   ```

5. **Acesse as interfaces**
   - API principal: http://localhost:3000
   - Documentação API: http://localhost:3000/docs
   - Dashboard Streamlit: http://localhost:8501
   - Interface Gradio: http://localhost:7860

### 🔧 Instalação Manual

1. **Clone o repositório**
   ```bash
   git clone https://github.com/alex-des-santos/whatsapp-rpg-gm.git
   cd whatsapp-rpg-gm
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```
=======
# 🎮 Sistema de GM de RPG com IA para WhatsApp
## Integração com Evolution API

[![Evolution API](https://img.shields.io/badge/Evolution%20API-v2.0.0-blue)](https://github.com/EvolutionAPI/evolution-api)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
>>>>>>> d469bc5e6a9d6cfd7632791a4e19ddc9d6eb2f01

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

<<<<<<< HEAD
4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

## 🌐 Configurando a Evolution API

1. **Instale a Evolution API** seguindo as instruções em [Evolution API GitHub](https://github.com/EvolutionAPI/evolution-api)

2. **Configure uma instância** na Evolution API

3. **Configure a URL do webhook** para apontar para sua aplicação WhatsApp RPG GM:
   ```
   https://sua-url-publica.com/webhook
   ```

4. **Configure as variáveis de ambiente** no arquivo `.env`:
   ```
   EVOLUTION_API_URL=http://localhost:8080
   EVOLUTION_API_KEY=sua-chave-api-evolution
   EVOLUTION_INSTANCE_NAME=rpg-gm-bot
   ```

## 📱 Uso do Sistema

### Comandos WhatsApp

Os seguintes comandos estão disponíveis via WhatsApp:

- `/start` - Iniciar o jogo
- `/criar-personagem` - Criar novo personagem
- `/status` - Ver status do personagem
- `/inventario` - Ver inventário
- `/rolar [expressão]` - Rolar dados (ex: `/rolar 2d6+3`)
- `/help` - Mostrar ajuda

Além dos comandos, os jogadores podem simplesmente enviar mensagens descrevendo o que seus personagens fazem, e o sistema responderá apropriadamente.

### Interfaces Web

#### Dashboard Streamlit (http://localhost:8501)

- Monitoramento em tempo real
- Gerenciamento de personagens e sessões
- Configuração de parâmetros de IA
- Visualização de logs e estado do jogo

#### Interface Gradio (http://localhost:7860)

- Teste de prompts de IA
- Simulação de conversas
- Debug do sistema

## 🔧 Desenvolvimento

### Estrutura de Módulos

- **Core**: Gerencia o estado do jogo, personagens e narrativa
- **WhatsApp**: Integração com Evolution API, gestão de webhooks
- **AI**: Gerenciamento de modelos LLM, geração de narrativas
- **RPG**: Sistema de dados, mecânicas de jogo
- **HITL**: Detecção e gestão de intervenções humanas
- **Interfaces**: Dashboards e interfaces de administração

### Configurações

O arquivo `.env` contém todas as configurações necessárias, incluindo:

- Conexão com Evolution API
- Chaves de API para provedores LLM
- Configuração de banco de dados
- Configurações de notificação HITL
- Parâmetros do servidor

## 🧪 Testes

Execute os testes com:

```bash
pytest
```

Ou para testes específicos:

```bash
pytest tests/test_whatsapp_integration.py
```

## 📈 Roadmap

- [x] Protótipo inicial com integração WhatsApp
- [x] Sistema de dados para D&D 5e
- [x] Integração com IA para narrativas
- [x] Sistema básico HITL
- [ ] Integração completa com banco de dados
- [ ] Suporte a múltiplos sistemas de RPG
- [ ] Interface avançada para GM humano
- [ ] Geração de imagens para cenas

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## ⚠️ Limitações do Protótipo

Este é um protótipo funcional com algumas limitações:

- Sistema de persistência simplificado (sem banco de dados completo)
- Integração com Evolution API básica
- Suporte apenas para D&D 5e básico
- Respostas de IA simuladas em modo desenvolvimento

## 📞 Contato

Para questões e suporte, abra uma issue no GitHub ou entre em contato com os mantenedores.
=======
## ⚠️ **STATUS ATUAL DO PROJETO**

### 🔴 **ATENÇÃO: REESTRUTURAÇÃO NECESSÁRIA**

O projeto atual em `https://github.com/alex-des-santos/whatsapp-rpg-gm` é **APENAS** um protótipo frontend que simula funcionalidades. **NÃO HÁ** integração real com:

- ❌ WhatsApp (simulado)
- ❌ Evolution API (não implementado)
- ❌ APIs de IA (simulado)
- ❌ Backend Python (inexistente)
- ❌ Base de dados (simulado)

### ✅ **SOLUÇÃO IMPLEMENTADA**

Este repositório contém a **reestruturação completa** necessária para integrar com a [Evolution API](https://github.com/EvolutionAPI/evolution-api) e criar um sistema funcional.

---

## 📋 **Comparação: Antes vs Depois**

| Aspecto | Projeto Original | Este Projeto (Reestruturado) |
|---------|------------------|-------------------------------|
| **WhatsApp** | 🔴 Simulado | ✅ Evolution API Real |
| **Backend** | ❌ Inexistente | ✅ FastAPI + Python |
| **IA/LLM** | 🔴 Simulado | ✅ OpenAI, Anthropic, Google |
| **Base de Dados** | ❌ Inexistente | ✅ PostgreSQL + Redis |
| **RPG System** | 🔴 Mock Data | ✅ D&D 5e Real + dicepy |
| **HITL** | 🔴 Simulado | ✅ Discord, Email, SMS |
| **Deploy** | ❌ Estático | ✅ Docker + Docker Compose |

---

## 🏗️ **Arquitetura do Sistema**

```mermaid
graph TB
    WA[WhatsApp] --> EA[Evolution API]
    EA --> WH[Webhook Server]
    WH --> MH[Message Handler]
    MH --> GM[Game Manager]
    MH --> AI[AI Manager]
    
    GM --> DB[(PostgreSQL)]
    GM --> RD[(Redis)]
    
    AI --> OAI[OpenAI]
    AI --> ANT[Anthropic]
    AI --> GOO[Google AI]
    
    MH --> DS[Dice System]
    MH --> CS[Combat System]
    
    GM --> HITL[HITL System]
    HITL --> DC[Discord]
    HITL --> EM[Email]
    
    subgraph "Interfaces"
        ST[Streamlit Dashboard]
        GR[Gradio Interface]
    end
    
    DB --> ST
    RD --> ST
    GM --> ST
```

---

## 🚀 **Instalação e Configuração**

### Pré-requisitos

- 🐳 **Docker & Docker Compose** (Recomendado)
- 🐍 **Python 3.8+** (Para desenvolvimento local)
- 🔗 **Evolution API** rodando
- 🌐 **URL pública** (ngrok, servidor próprio)

### 🐳 **Instalação com Docker (Recomendado)**

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/whatsapp-rpg-gm-evolution
cd whatsapp-rpg-gm-evolution

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Verifique se tudo está funcionando
docker-compose ps
docker-compose logs -f
```

### 🔧 **Configuração Manual**

```bash
# 1. Clone e instale dependências
git clone https://github.com/seu-usuario/whatsapp-rpg-gm-evolution
cd whatsapp-rpg-gm-evolution
pip install -r requirements.txt

# 2. Configure PostgreSQL
createdb rpg_gm_db

# 3. Configure Redis
redis-server

# 4. Configure Evolution API
# Siga: https://doc.evolution-api.com

# 5. Configure variáveis de ambiente
cp .env.example .env
# Edite com suas configurações

# 6. Execute migrações
python -m alembic upgrade head

# 7. Inicie a aplicação
python main.py
```

---

## ⚙️ **Configuração Essencial**

### 🔑 **Variáveis Obrigatórias (.env)**

```env
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-api-evolution

# Base de Dados
DATABASE_URL=postgresql://user:pass@localhost:5432/rpg_gm_db

# IA (pelo menos uma)
OPENAI_API_KEY=sk-sua-chave-openai

# Webhook (URL pública)
WEBHOOK_URL=https://seu-dominio.com/webhook

# Segurança
SECRET_KEY=chave-secreta-muito-segura
```

### 🌐 **Configuração de URL Pública**

Para desenvolvimento local, use **ngrok**:

```bash
# Instale ngrok
npm install -g ngrok

# Exponha sua aplicação
ngrok http 3000

# Use a URL gerada no .env
WEBHOOK_URL=https://abc123.ngrok.io/webhook
```

---

## 📚 **Uso do Sistema**

### 1️⃣ **Configurar Instância WhatsApp**

```bash
# Via API
curl -X POST http://localhost:3000/setup/instance

# Ou via Evolution API Manager
http://localhost:8080/manager
```

### 2️⃣ **Conectar WhatsApp**

```bash
# Obter QR Code
curl http://localhost:3000/qrcode/rpg-gm-bot

# Escanear com WhatsApp
# Aguardar conexão
```

### 3️⃣ **Testar Sistema**

Envie uma mensagem para o número conectado:
```
/start
```

### 4️⃣ **Comandos Disponíveis**

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/start` | Iniciar sessão RPG | `/start` |
| `/criar-personagem` | Criar novo personagem | `/criar-personagem` |
| `/rolar` | Rolar dados | `/rolar 1d20+5` |
| `/status` | Ver status do personagem | `/status` |
| `/inventario` | Ver inventário | `/inventario` |
| `/help` | Ajuda | `/help` |

---

## 🎛️ **Interfaces de Gestão**

### 📊 **Streamlit Dashboard**
- **URL**: http://localhost:8501
- **Funcionalidades**:
  - Monitoramento em tempo real
  - Gestão de personagens
  - Configuração de IA
  - Logs de sessão
  - Estatísticas de uso

### 🎮 **Gradio Interface**
- **URL**: http://localhost:7860
- **Funcionalidades**:
  - Teste de prompts
  - Simulação de conversas
  - Debug de IA

---

## 🔧 **Desenvolvimento**

### 📁 **Estrutura do Projeto**

```
whatsapp-rpg-gm-evolution/
├── src/
│   ├── core/              # Núcleo do sistema
│   ├── whatsapp/          # Integração Evolution API
│   ├── ai/                # Módulos de IA
│   ├── rpg/               # Sistema de RPG
│   ├── hitl/              # Human-in-the-Loop
│   └── interfaces/        # Interfaces web
├── config/                # Configurações
├── data/                  # Dados do jogo
├── docker/                # Docker configs
├── scripts/               # Scripts utilitários
├── tests/                 # Testes
├── main.py                # Aplicação principal
├── requirements.txt       # Dependências
├── .env.example          # Exemplo de configuração
├── docker-compose.yml    # Docker Compose
└── README.md             # Este arquivo
```

### 🧪 **Executar Testes**

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_evolution_client.py

# Com cobertura
pytest --cov=src
```

### 📝 **Contribuir**

1. Fork o projeto
2. Crie uma branch feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 🌐 **URLs de Acesso**

Após instalação completa:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **RPG GM App** | http://localhost:3000 | API principal |
| **Evolution API** | http://localhost:8080 | WhatsApp API |
| **Streamlit Dashboard** | http://localhost:8501 | Dashboard de gestão |
| **Gradio Interface** | http://localhost:7860 | Interface de teste |
| **PgAdmin** | http://localhost:5050 | Admin PostgreSQL |
| **Redis Commander** | http://localhost:8081 | Admin Redis |
| **API Docs** | http://localhost:3000/docs | Documentação API |

---

## 🔍 **Troubleshooting**

### ❌ **Problemas Comuns**

#### 1. Evolution API não conecta
```bash
# Verificar se Evolution API está rodando
curl http://localhost:8080

# Verificar logs
docker-compose logs evolution-api
```

#### 2. Webhook não recebe mensagens
```bash
# Verificar configuração do webhook
curl -X GET http://localhost:8080/webhook/instance/rpg-gm-bot

# Testar URL pública
curl https://sua-url-publica.com/webhook
```

#### 3. Base de dados não conecta
```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Testar conexão
psql postgresql://rpg_user:senha@localhost:5432/rpg_gm_db
```

#### 4. IA não responde
```bash
# Verificar logs da aplicação
docker-compose logs rpg-gm-app

# Testar chaves de API
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

---

## 📈 **Roadmap**

### ✅ **Fase 1: Infraestrutura (Completa)**
- [x] Integração Evolution API
- [x] Sistema de webhook
- [x] Base de dados PostgreSQL
- [x] Cache Redis
- [x] Docker Compose

### ✅ **Fase 2: Core RPG (Completa)**
- [x] Sistema de dados (dicepy)
- [x] Mecânicas D&D 5e
- [x] Gestão de personagens
- [x] Estado do mundo
- [x] Sistema de combate

### ✅ **Fase 3: IA (Completa)**
- [x] Múltiplos provedores LLM
- [x] Sistema RAG
- [x] Prompts avançados
- [x] Geração narrativa

### 🔄 **Fase 4: HITL (Em Desenvolvimento)**
- [x] Detector de intervenção
- [x] Notificações Discord/Email
- [ ] Interface GM humano
- [ ] Handoff automático

### 📅 **Fase 5: Interfaces (Planejada)**
- [ ] Dashboard Streamlit completo
- [ ] Interface mobile
- [ ] APIs REST públicas
- [ ] Métricas avançadas

### 🔮 **Fase 6: Expansão (Futuro)**
- [ ] Suporte Instagram/Messenger
- [ ] Múltiplos sistemas RPG
- [ ] IA de voz
- [ ] Geração de imagens

---

## 🤝 **Comunidade e Suporte**

### 📞 **Canais de Comunicação**
- **Discord**: [Link do Discord]
- **Telegram**: [Link do Telegram]
- **GitHub Issues**: Para bugs e features
- **Discussions**: Para dúvidas gerais

### 🆘 **Suporte Técnico**
- **Documentação**: https://doc.evolution-api.com
- **Wiki do Projeto**: [Link da Wiki]
- **FAQ**: [Link do FAQ]

---

## 📄 **Licença**

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### ⚖️ **Licenças de Dependências**
- **Evolution API**: Apache 2.0
- **FastAPI**: MIT
- **D&D 5e**: Fair Use (mecânicas não proprietárias)

---

## 🙏 **Agradecimentos**

- **Evolution API Team** - Pela excelente API de WhatsApp
- **OpenAI** - Pelos modelos de IA
- **Comunidade D&D** - Pelas mecânicas e inspiração
- **Contribuidores** - Por tornarem este projeto possível

---

## 🎯 **Call to Action**

### 🚀 **Para Usuários**
1. ⭐ **Star** o repositório
2. 🍴 **Fork** para seus projetos
3. 🐛 **Reporte bugs** via Issues
4. 💡 **Sugira features** via Discussions

### 👨‍💻 **Para Desenvolvedores**
1. 📖 Leia a documentação completa
2. 🧪 Execute os testes
3. 💼 Contribua com código
4. 📚 Melhore a documentação

### 🎮 **Para GMs e Jogadores**
1. 🎲 Teste o sistema
2. 📝 Compartilhe feedback
3. 🌟 Avalie o projeto
4. 📢 Divulgue para a comunidade

---

**🎲 Que as aventuras épicas comecem! 🐉**

---

## 📊 **Estatísticas do Projeto**

![GitHub stars](https://img.shields.io/github/stars/seu-usuario/whatsapp-rpg-gm-evolution)
![GitHub forks](https://img.shields.io/github/forks/seu-usuario/whatsapp-rpg-gm-evolution)
![GitHub issues](https://img.shields.io/github/issues/seu-usuario/whatsapp-rpg-gm-evolution)
![GitHub pull requests](https://img.shields.io/github/issues-pr/seu-usuario/whatsapp-rpg-gm-evolution)

---

*Última atualização: Dezembro 2024*
>>>>>>> d469bc5e6a9d6cfd7632791a4e19ddc9d6eb2f01
