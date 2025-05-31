# Primeiro, vou criar uma estrutura de dados que representa o sistema de RPG com IA
# Vou definir as classes e componentes principais do sistema

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

# Dados de exemplo para demonstrar o sistema
system_architecture = {
    "modules": {
        "whatsapp_integration": {
            "description": "Módulo de integração com WhatsApp Business API",
            "components": ["message_handler", "webhook_processor", "interactive_buttons"],
            "dependencies": ["whatsapp-api-client-python", "flask", "requests"]
        },
        "game_state_manager": {
            "description": "Gestor de estado do jogo para manter persistência",
            "components": ["character_manager", "world_state", "narrative_tracker"],
            "data_categories": ["personagens", "estado_mundo", "regras_mecanicas"]
        },
        "ai_module": {
            "description": "Módulo de IA com múltiplos provedores LLM",
            "components": ["llm_router", "prompt_engine", "narrative_generator"],
            "supported_providers": ["openai", "anthropic", "google", "openrouter", "local_ollama"]
        },
        "dice_system": {
            "description": "Sistema de rolagem de dados para D&D",
            "components": ["dice_roller", "skill_calculator", "combat_resolver"],
            "dependencies": ["dicepy", "numpy"]
        },
        "hitl_system": {
            "description": "Sistema humano-no-ciclo para intervenções do GM",
            "components": ["intervention_detector", "notification_sender", "transcription_manager"],
            "triggers": ["conflito_regras", "decisao_critica", "narrativa_complexa"]
        },
        "gui_interface": {
            "description": "Interface gráfica para controle do sistema",
            "framework": "streamlit",
            "features": ["real_time_monitoring", "ai_parameter_tuning", "manual_intervention"]
        }
    },
    "integrations": {
        "llamaindex": {
            "purpose": "Fundamentação de lore e regras de D&D",
            "features": ["knowledge_retrieval", "rule_lookup", "lore_expansion"]
        },
        "multi_llm": {
            "primary": "OpenAI GPT-4",
            "fallback": ["Anthropic Claude", "Google Gemini"],
            "local": "Ollama Llama3"
        }
    }
}

# Dados de exemplo de personagens
sample_characters = [
    {
        "name": "Aria Nightwhisper",
        "class": "Ranger",
        "level": 5,
        "hp": {"current": 45, "max": 45},
        "stats": {
            "strength": 14,
            "dexterity": 18,
            "constitution": 16,
            "intelligence": 12,
            "wisdom": 15,
            "charisma": 10
        },
        "location": "Floresta Sombria",
        "inventory": ["Arco Élfico", "Aljava com 30 flechas", "Armadura de Couro", "Kit de Sobrevivência"],
        "status": "healthy"
    },
    {
        "name": "Thorin Barbaferro",
        "class": "Fighter",
        "level": 4,
        "hp": {"current": 38, "max": 42},
        "stats": {
            "strength": 17,
            "dexterity": 13,
            "constitution": 15,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 14
        },
        "location": "Taverna do Dragão",
        "inventory": ["Machado de Batalha", "Escudo", "Armadura de Placas", "Poção de Cura"],
        "status": "slightly_wounded"
    }
]

# Estado atual do mundo
world_state = {
    "current_scene": "Investigação na Taverna",
    "active_quest": "O Mistério dos Comerciantes Desaparecidos",
    "npcs_present": [
        {"name": "Bartender Willem", "disposition": "friendly", "knows": "informações sobre comerciantes"},
        {"name": "Comerciante Suspeito", "disposition": "nervous", "knows": "pistas sobre o desaparecimento"}
    ],
    "environment": {
        "location": "Taverna do Dragão Dourado",
        "time": "Final da tarde",
        "weather": "Chuva leve",
        "mood": "tenso, suspeitas no ar"
    },
    "recent_events": [
        "Personagens chegaram à taverna",
        "Ouviram rumores sobre comerciantes desaparecidos",
        "Notaram comportamento suspeito de um cliente"
    ]
}

# Exemplos de prompts para diferentes técnicas
prompt_examples = {
    "chain_of_thought": """
    Como Mestre de Jogo experiente, analyze a situação atual e responda seguindo estes passos:
    1. Avalie o contexto atual da aventura
    2. Considere as ações dos jogadores
    3. Determine as consequências narrativas
    4. Calcule qualquer mecânica necessária
    5. Descreva a resposta de forma imersiva
    
    Situação: {situation}
    Ação do jogador: {player_action}
    """,
    "tree_of_thought": """
    Você é um GM de D&D. Explore múltiplas possibilidades narrativas:
    
    Ramificação A: Resposta direta à ação
    Ramificação B: Complicação inesperada  
    Ramificação C: Oportunidade para desenvolvimento de personagem
    
    Avalie cada ramificação e escolha a que melhor serve a narrativa.
    """,
    "lore_integration": """
    Consulte o conhecimento de D&D para responder. Use informações sobre:
    - Regras oficiais de D&D 5e
    - Lore estabelecido de Forgotten Realms
    - Mecânicas de combate e habilidades
    
    Pergunta: {query}
    """
}

# Configurações de exemplo para diferentes LLMs
llm_configs = {
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "use_case": "Narrativa principal e diálogos complexos"
    },
    "anthropic": {
        "model": "claude-3-sonnet",
        "temperature": 0.6,
        "max_tokens": 1000,
        "use_case": "Análise de regras e decisões éticas"
    },
    "google": {
        "model": "gemini-pro",
        "temperature": 0.8,
        "max_tokens": 800,
        "use_case": "Geração criativa e descrições ambientais"
    },
    "local": {
        "model": "llama3:8b",
        "temperature": 0.5,
        "max_tokens": 600,
        "use_case": "Backup offline e operações simples"
    }
}

# Salvar dados em JSON para uso no aplicativo
app_data = {
    "system_architecture": system_architecture,
    "characters": sample_characters,
    "world_state": world_state,
    "prompt_examples": prompt_examples,
    "llm_configs": llm_configs,
    "features": {
        "whatsapp_integration": True,
        "multi_llm_support": True,
        "dice_rolling": True,
        "state_persistence": True,
        "human_intervention": True,
        "gui_interface": True,
        "llamaindex_integration": True
    }
}

# Salvar como JSON
with open('rpg_ai_system_data.json', 'w', encoding='utf-8') as f:
    json.dump(app_data, f, indent=2, ensure_ascii=False)

print("Dados do sistema preparados com sucesso!")
print(f"Módulos do sistema: {list(system_architecture['modules'].keys())}")
print(f"Personagens de exemplo: {len(sample_characters)}")
print(f"Configurações LLM: {list(llm_configs.keys())}")