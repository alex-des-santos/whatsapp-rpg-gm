# Criando a estrutura completa do projeto FastAPI integrado com o frontend
import os

# Criar estrutura de diretórios
project_structure = """
whatsapp-rpg-gm/
├── main.py                     # Aplicação FastAPI principal
├── requirements.txt            # Dependências
├── .env.example               # Variáveis de ambiente exemplo
├── Dockerfile                 # Container Docker
├── docker-compose.yml         # Orquestração
├── README.md                  # Documentação
├── static/                    # Arquivos estáticos (frontend)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data.json
├── src/                       # Código fonte Python
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── game_manager.py
│   │   └── database.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py
│   │   │   ├── whatsapp.py
│   │   │   ├── game_state.py
│   │   │   ├── ai_module.py
│   │   │   ├── dice_system.py
│   │   │   └── hitl.py
│   │   └── dependencies.py
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   ├── evolution_client.py
│   │   ├── message_handler.py
│   │   └── webhook.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── llm_manager.py
│   │   ├── prompt_engine.py
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── openai_provider.py
│   │       ├── anthropic_provider.py
│   │       └── local_provider.py
│   ├── rpg/
│   │   ├── __init__.py
│   │   ├── dice_roller.py
│   │   ├── character_manager.py
│   │   ├── world_state.py
│   │   └── rules_engine.py
│   └── hitl/
│       ├── __init__.py
│       ├── intervention_detector.py
│       └── notification_system.py
└── tests/
    ├── __init__.py
    ├── test_api/
    ├── test_whatsapp/
    └── test_rpg/
"""

print("Estrutura do projeto WhatsApp RPG GM:")
print(project_structure)