# Vou analisar a estrutura dos arquivos anexados para entender o frontend
import json

# Dados do sistema anexado
rpg_data = {
    "system_architecture": {
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
        }
    }
}

print("Estrutura dos módulos do sistema:")
for module_name, module_info in rpg_data["system_architecture"]["modules"].items():
    print(f"\n{module_name}:")
    print(f"  - Descrição: {module_info['description']}")
    print(f"  - Componentes: {', '.join(module_info['components'])}")
    if 'dependencies' in module_info:
        print(f"  - Dependências: {', '.join(module_info['dependencies'])}")
    if 'framework' in module_info:
        print(f"  - Framework: {module_info['framework']}")