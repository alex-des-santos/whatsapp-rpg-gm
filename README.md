# WhatsApp RPG Game Master 🎲

Sistema completo de Game Master automatizado para WhatsApp, desenvolvido com FastAPI e implementando todas as recomendações críticas de arquitetura e segurança.

## 🚀 Funcionalidades Principais

### 🎮 Sistema de RPG Completo
- **Gestão de Personagens**: Criação, edição e gerenciamento de personagens D&D 5e
- **Validação de Duplicidade**: Sistema robusto que previne criação de personagens duplicados
- **Limites por Jogador**: Controle de quantidade máxima de personagens por usuário
- **Sistema de Experiência**: Progressão automática de nível com cálculo de XP

### 📱 Integração WhatsApp
- **Evolution API**: Integração completa com WhatsApp Business API
- **Mensagens Interativas**: Botões, listas e menus para melhor experiência
- **Webhook Seguro**: Processamento de mensagens com validação robusta
- **Comandos RPG**: Interface natural através de comandos de texto

### 🤖 Inteligência Artificial
- **Múltiplos Provedores**: OpenAI, Google AI, Anthropic e LLMs locais
- **Game Master IA**: Narração automática e tomada de decisões
- **Geração de Conteúdo**: Criação de histórias, NPCs e aventuras
- **Processamento de Linguagem Natural**: Compreensão de comandos em português

### 🏗️ Arquitetura Robusta
- **Volumes Docker**: Persistência completa de dados entre reinicializações
- **Health Checks**: Monitoramento abrangente de todos os componentes
- **Testes Automatizados**: Cobertura completa com pytest
- **Validação de Ambiente**: Verificação rigorosa de configurações críticas

## 📋 Requisitos

### Obrigatórios
- **Docker** e **Docker Compose**
- **PostgreSQL** (incluído no compose)
- **Redis** (incluído no compose)
- **Evolution API** (servidor WhatsApp)
- **Chave de IA** (OpenAI, Google AI, Anthropic ou LLM local)

### Opcionais
- **Python 3.11+** (para desenvolvimento local)
- **Nginx** (para proxy reverso em produção)

## ⚡ Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/whatsapp-rpg-gm.git
cd whatsapp-rpg-gm
```

### 2. Configure o Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais
nano .env
```

### 3. Variáveis Obrigatórias
Configure no arquivo `.env`:

```env
# WhatsApp Evolution API
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution_api
INSTANCE_NAME=sua_instancia_whatsapp
VERIFY_TOKEN=seu_token_verificacao_minimo_12_chars

# Segurança
SECRET_KEY=sua_chave_secreta_muito_longa_para_jwt

# IA (configure pelo menos um)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-sua_chave_openai

# Banco de dados (já configurado para Docker)
DATABASE_URL=postgresql://rpg_user:rpg_password@postgres:5432/rpg_db
REDIS_URL=redis://:redis_password@redis:6379/0
```

### 4. Inicie os Serviços
```bash
# Criar diretórios de volumes
mkdir -p volumes/{game_data,logs,sessions,characters,backups,ai_configs,gui_data}

# Iniciar containers
docker-compose up --build -d

# Verificar funcionamento
curl http://localhost:8000/health/detailed
```

### 5. Configure o Webhook
Na sua Evolution API, configure o webhook para:
```
http://seu-servidor:8000/webhook/message
```

## 🔧 Uso

### Comandos WhatsApp

#### Gerenciamento de Personagens
```
/criar personagem
/listar personagens
/ficha [nome]
/editar [nome]
/deletar [nome]
```

#### Sistema RPG
```
/rolar 1d20+5
/rolar 2d6 vantagem
/status [personagem]
/xp adicionar [quantidade]
/descanso [tipo]
```

#### Comandos do GM
```
/aventura criar
/npc gerar
/historia continuar
/ajuda
```

### API REST

#### Personagens
```bash
# Verificar duplicidade
GET /api/character/check_duplicate/{nome}

# Criar personagem
POST /api/character/create_character

# Listar personagens do jogador
GET /api/character/list/{player_id}

# Buscar por ID
GET /api/character/{character_id}

# Atualizar
PUT /api/character/{character_id}

# Deletar
DELETE /api/character/{character_id}
```

#### Health Checks
```bash
# Health check básico
GET /health/

# Verificação detalhada
GET /health/detailed

# Readiness probe (Kubernetes)
GET /health/readiness

# Liveness probe (Kubernetes)
GET /health/liveness

# Métricas básicas
GET /health/metrics
```

### Interface GUI

Acesse a interface Streamlit em:
```
http://localhost:8501
```

Funcionalidades da GUI:
- **Dashboard**: Visão geral do sistema
- **Gerenciamento**: CRUD de personagens
- **Monitoramento**: Health checks e métricas
- **Configurações**: Ajustes de IA e sistema

## 🧪 Testes

### Executar Todos os Testes
```bash
# Via Docker
docker-compose exec whatsapp_rpg_gm pytest -v

# Local (se Python instalado)
pytest -v
```

### Testes Específicos
```bash
# Apenas testes de duplicidade
pytest tests/test_character/test_duplicates.py -v

# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Com cobertura de código
pytest --cov=app --cov-report=html
```

### Markers Disponíveis
- `unit`: Testes unitários
- `integration`: Testes de integração
- `api`: Testes de API
- `character`: Testes de personagens
- `whatsapp`: Testes WhatsApp
- `slow`: Testes demorados

## 📊 Monitoramento

### Health Checks
```bash
# Verificação completa
curl http://localhost:8000/health/detailed

# Apenas banco de dados
curl http://localhost:8000/health/readiness

# Status básico
curl http://localhost:8000/health/
```

### Logs
```bash
# Logs da aplicação
docker-compose logs -f whatsapp_rpg_gm

# Logs do banco
docker-compose logs -f postgres

# Logs específicos
docker-compose logs --tail=100 whatsapp_rpg_gm
```

### Métricas
- **Prometheus**: `http://localhost:9090/metrics`
- **Aplicação**: `http://localhost:8000/health/metrics`
- **GUI**: `http://localhost:8501`

## 🔒 Segurança

### Validações Implementadas
- ✅ **VERIFY_TOKEN**: Mínimo 12 caracteres, sem valores padrão
- ✅ **SECRET_KEY**: Mínimo 32 caracteres, verificação de força
- ✅ **API Keys**: Validação de formato específico por provedor
- ✅ **URLs**: Verificação de formato e segurança
- ✅ **Duplicidade**: Prevenção robusta de dados duplicados

### Boas Práticas
- **Containers não-root**: Usuários dedicados em todos os containers
- **Health checks**: Monitoramento contínuo de componentes
- **Logs estruturados**: Rastreabilidade completa de operações
- **Validação de entrada**: Sanitização rigorosa de dados

## 🐳 Docker

### Volumes Persistentes
```yaml
volumes/
├── game_data/     # Estado do jogo e campanhas
├── logs/          # Logs da aplicação
├── sessions/      # Sessões WhatsApp
├── characters/    # Dados de personagens
├── backups/       # Backups automáticos
├── ai_configs/    # Configurações de IA
└── gui_data/      # Dados da interface
```

### Comandos Úteis
```bash
# Rebuild completo
docker-compose down && docker-compose up --build -d

# Backup de volumes
docker run --rm -v whatsapp-rpg-gm_game_data:/source:ro -v $(pwd)/backup:/backup alpine tar czf /backup/game_data.tar.gz -C /source .

# Restore de backup
docker run --rm -v whatsapp-rpg-gm_game_data:/target -v $(pwd)/backup:/backup alpine tar xzf /backup/game_data.tar.gz -C /target

# Logs em tempo real
docker-compose logs -f

# Entrar no container
docker-compose exec whatsapp_rpg_gm bash
```

## 🔄 Atualizações

### Processo Seguro
1. **Backup**: Sempre faça backup antes de atualizar
2. **Teste**: Execute em ambiente de staging primeiro
3. **Blue-Green**: Use deploy blue-green para zero downtime
4. **Rollback**: Mantenha capacidade de rollback rápido

```bash
# Backup automático
./scripts/backup.sh

# Atualizar código
git pull origin main

# Rebuild com novo código
docker-compose up --build -d

# Verificar funcionamento
curl http://localhost:8000/health/detailed
```

## 🤝 Contribuição

### Ambiente de Desenvolvimento
```bash
# Clone e setup
git clone https://github.com/seu-usuario/whatsapp-rpg-gm.git
cd whatsapp-rpg-gm

# Instalar dependências locais
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Executar localmente
uvicorn app.main:app --reload
```

### Padrões de Código
- **Black**: Formatação automática
- **isort**: Organização de imports
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testes com 80%+ cobertura

### Pull Requests
1. Fork o repositório
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Comuns

#### Erro de Conexão com Banco
```bash
# Verificar se containers estão rodando
docker-compose ps

# Verificar logs do banco
docker-compose logs postgres

# Resetar banco (CUIDADO!)
docker-compose down -v
docker-compose up -d
```

#### Erro de Evolution API
```bash
# Verificar configuração
curl -H "apikey: $EVOLUTION_API_KEY" $EVOLUTION_API_URL/instance/connectionState/$INSTANCE_NAME

# Verificar webhook
curl -X POST -H "Content-Type: application/json" -d '{"test": true}' http://localhost:8000/webhook/message
```

#### Problemas de IA
```bash
# Verificar chaves de API
curl http://localhost:8000/health/detailed | jq '.checks.ai_services'

# Testar provedor específico
python -c "import openai; print(openai.Model.list())"
```

### Documentação
- **API**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health**: `http://localhost:8000/health/detailed`

### Contato
- **Email**: contato@whatsapprpg.com
- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions

---

**Desenvolvido com ❤️ para a comunidade RPG** 🎲