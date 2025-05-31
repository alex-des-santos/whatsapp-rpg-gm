# 🎮 Sistema de GM de RPG com IA para WhatsApp
## Integração com Evolution API

[![Evolution API](https://img.shields.io/badge/Evolution%20API-v2.0.0-blue)](https://github.com/EvolutionAPI/evolution-api)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

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
