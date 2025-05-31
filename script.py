# Vou criar a estrutura de arquivos necessária para o protótipo funcional

import os
import json
from typing import Dict, List, Any

# Criar estrutura de diretórios
directories = [
    "whatsapp-rpg-gm-prototype",
    "whatsapp-rpg-gm-prototype/src",
    "whatsapp-rpg-gm-prototype/src/core", 
    "whatsapp-rpg-gm-prototype/src/whatsapp",
    "whatsapp-rpg-gm-prototype/src/ai",
    "whatsapp-rpg-gm-prototype/src/rpg",
    "whatsapp-rpg-gm-prototype/src/hitl",
    "whatsapp-rpg-gm-prototype/src/interfaces",
    "whatsapp-rpg-gm-prototype/config",
    "whatsapp-rpg-gm-prototype/data",
    "whatsapp-rpg-gm-prototype/tests"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

print("\nStructure created successfully!")