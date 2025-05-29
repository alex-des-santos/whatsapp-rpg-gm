from pydantic import BaseModel
from typing import Dict, List, Optional

class Character(BaseModel):
    name: str = "Aventureiro"
    hp: int = 100
    max_hp: int = 100
    level: int = 1
    xp: int = 0
    inventory: List[str] = []
    location: str = "Floresta Encantada"
    attributes: Dict[str, int] = {
        "força": 10,
        "destreza": 10,
        "constituição": 10,
        "inteligência": 10,
        "sabedoria": 10,
        "carisma": 10
    }

class WorldState(BaseModel):
    locations: Dict[str, str] = {}
    npcs: Dict[str, Dict] = {}
    quests: Dict[str, Dict] = {}
    relations: Dict[str, Dict] = {}

class GameState(BaseModel):
    characters: Dict[str, Character] = {}
    world: WorldState = WorldState()
    history: List[Dict] = []
    rules: Dict[str, str] = {}