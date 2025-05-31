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

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

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