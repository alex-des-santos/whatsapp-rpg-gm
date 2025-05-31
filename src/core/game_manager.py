"""
Game Manager - Núcleo do sistema de RPG
Gerencia estado do jogo, personagens e narrativa
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Character:
    """Modelo de personagem D&D"""
    name: str
    char_class: str
    level: int
    hp_current: int
    hp_max: int
    stats: Dict[str, int]  # STR, DEX, CON, INT, WIS, CHA
    location: str
    inventory: List[str]
    status: str
    player_id: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def get_modifier(self, stat: str) -> int:
        """Calcula modificador de atributo D&D"""
        return (self.stats.get(stat, 10) - 10) // 2
    
    def is_alive(self) -> bool:
        """Verifica se personagem está vivo"""
        return self.hp_current > 0
    
    def take_damage(self, damage: int) -> bool:
        """Aplica dano ao personagem"""
        self.hp_current = max(0, self.hp_current - damage)
        return self.is_alive()
    
    def heal(self, healing: int):
        """Cura personagem"""
        self.hp_current = min(self.hp_max, self.hp_current + healing)


@dataclass
class NPC:
    """Modelo de NPC"""
    name: str
    disposition: str  # friendly, neutral, hostile
    knows: str
    location: str
    description: str = ""
    dialogue_history: List[str] = None
    
    def __post_init__(self):
        if self.dialogue_history is None:
            self.dialogue_history = []


@dataclass
class WorldState:
    """Estado atual do mundo"""
    current_scene: str
    active_quest: str
    location: str
    time: str
    weather: str
    mood: str
    npcs_present: List[NPC]
    recent_events: List[str]
    session_id: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class GameManager:
    """Gerenciador principal do estado do jogo"""
    
    def __init__(self, settings):
        self.settings = settings
        self.characters: Dict[str, Character] = {}
        self.world_state: Optional[WorldState] = None
        self.active_sessions: Dict[str, str] = {}  # player_id -> session_id
        self.session_history: Dict[str, List[Dict]] = {}
        self._initialized = False
        
        # Cache em memória para desenvolvimento
        self._character_cache = {}
        self._world_cache = {}
        
    async def initialize(self):
        """Inicializar Game Manager"""
        try:
            logger.info("Inicializando Game Manager...")
            
            # Carregar dados de exemplo
            await self._load_sample_data()
            
            # Em produção, aqui conectaríamos com PostgreSQL
            # await self._connect_database()
            
            self._initialized = True
            logger.info("Game Manager inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Game Manager: {e}")
            raise
    
    async def cleanup(self):
        """Limpeza na finalização"""
        logger.info("Finalizando Game Manager...")
        self._initialized = False
    
    def is_ready(self) -> bool:
        """Verifica se o Game Manager está pronto"""
        return self._initialized
    
    async def _load_sample_data(self):
        """Carregar dados de exemplo"""
        # Personagens de exemplo
        sample_characters = [
            Character(
                name="Aria Nightwhisper",
                char_class="Ranger",
                level=5,
                hp_current=45,
                hp_max=45,
                stats={
                    "strength": 14,
                    "dexterity": 18,
                    "constitution": 16,
                    "intelligence": 12,
                    "wisdom": 15,
                    "charisma": 10
                },
                location="Floresta Sombria",
                inventory=["Arco Élfico", "Aljava com 30 flechas", "Armadura de Couro"],
                status="healthy",
                player_id="player_1"
            ),
            Character(
                name="Thorin Barbaferro",
                char_class="Fighter",
                level=4,
                hp_current=38,
                hp_max=42,
                stats={
                    "strength": 17,
                    "dexterity": 13,
                    "constitution": 15,
                    "intelligence": 10,
                    "wisdom": 12,
                    "charisma": 14
                },
                location="Taverna do Dragão",
                inventory=["Machado de Batalha", "Escudo", "Armadura de Placas"],
                status="slightly_wounded",
                player_id="player_2"
            )
        ]
        
        for char in sample_characters:
            self.characters[char.player_id] = char
        
        # Estado do mundo de exemplo
        self.world_state = WorldState(
            current_scene="Investigação na Taverna",
            active_quest="O Mistério dos Comerciantes Desaparecidos",
            location="Taverna do Dragão Dourado",
            time="Final da tarde",
            weather="Chuva leve",
            mood="tenso, suspeitas no ar",
            npcs_present=[
                NPC(
                    name="Bartender Willem",
                    disposition="friendly",
                    knows="informações sobre comerciantes",
                    location="Taverna do Dragão Dourado",
                    description="Um homem robusto com barba grisalha"
                ),
                NPC(
                    name="Comerciante Suspeito",
                    disposition="nervous",
                    knows="pistas sobre o desaparecimento",
                    location="Taverna do Dragão Dourado",
                    description="Um homem encapuzado no canto da taverna"
                )
            ],
            recent_events=[
                "Personagens chegaram à taverna",
                "Ouviram rumores sobre comerciantes desaparecidos",
                "Notaram comportamento suspeito de um cliente"
            ],
            session_id="default_session"
        )
    
    async def get_character(self, player_id: str) -> Optional[Character]:
        """Obter personagem do jogador"""
        return self.characters.get(player_id)
    
    async def create_character(self, player_id: str, character_data: Dict) -> Character:
        """Criar novo personagem"""
        try:
            character = Character(
                name=character_data.get("name", "Aventureiro"),
                char_class=character_data.get("class", "Fighter"),
                level=character_data.get("level", 1),
                hp_current=character_data.get("hp", 10),
                hp_max=character_data.get("hp", 10),
                stats=character_data.get("stats", {
                    "strength": 13,
                    "dexterity": 14,
                    "constitution": 13,
                    "intelligence": 12,
                    "wisdom": 15,
                    "charisma": 12
                }),
                location=character_data.get("location", "Vila Inicial"),
                inventory=character_data.get("inventory", ["Espada", "Escudo"]),
                status="healthy",
                player_id=player_id
            )
            
            self.characters[player_id] = character
            logger.info(f"Personagem criado: {character.name} para jogador {player_id}")
            
            return character
            
        except Exception as e:
            logger.error(f"Erro ao criar personagem: {e}")
            raise
    
    async def update_character(self, player_id: str, updates: Dict):
        """Atualizar personagem"""
        character = await self.get_character(player_id)
        if not character:
            raise ValueError(f"Personagem não encontrado para jogador {player_id}")
        
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        logger.info(f"Personagem atualizado: {character.name}")
    
    async def get_world_state(self) -> WorldState:
        """Obter estado atual do mundo"""
        return self.world_state
    
    async def update_world_state(self, updates: Dict):
        """Atualizar estado do mundo"""
        if not self.world_state:
            raise ValueError("Estado do mundo não inicializado")
        
        for key, value in updates.items():
            if hasattr(self.world_state, key):
                setattr(self.world_state, key, value)
        
        logger.info("Estado do mundo atualizado")
    
    async def add_event_to_history(self, event: str, player_id: str = None):
        """Adicionar evento ao histórico"""
        if self.world_state:
            self.world_state.recent_events.append(f"[{datetime.now().strftime('%H:%M')}] {event}")
            
            # Manter apenas os 10 eventos mais recentes
            if len(self.world_state.recent_events) > 10:
                self.world_state.recent_events = self.world_state.recent_events[-10:]
        
        # Adicionar ao histórico da sessão
        if player_id:
            session_id = self.active_sessions.get(player_id, "default")
            if session_id not in self.session_history:
                self.session_history[session_id] = []
            
            self.session_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "player_id": player_id,
                "event": event,
                "type": "game_event"
            })
    
    async def get_session_context(self, player_id: str) -> Dict:
        """Obter contexto da sessão para IA"""
        character = await self.get_character(player_id)
        world_state = await self.get_world_state()
        
        session_id = self.active_sessions.get(player_id, "default")
        history = self.session_history.get(session_id, [])
        
        context = {
            "character": asdict(character) if character else None,
            "world_state": asdict(world_state) if world_state else None,
            "recent_history": history[-10:] if history else [],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return context
    
    async def process_player_action(self, player_id: str, action: str, action_type: str = "general") -> Dict:
        """Processar ação do jogador"""
        try:
            # Registrar ação no histórico
            await self.add_event_to_history(f"PLAYER({player_id}): {action}", player_id)
            
            # Obter contexto
            context = await self.get_session_context(player_id)
            
            # Determinar tipo de ação e processar
            if action_type == "combat":
                return await self._process_combat_action(player_id, action, context)
            elif action_type == "skill_check":
                return await self._process_skill_check(player_id, action, context)
            elif action_type == "dialogue":
                return await self._process_dialogue(player_id, action, context)
            else:
                return await self._process_general_action(player_id, action, context)
        
        except Exception as e:
            logger.error(f"Erro ao processar ação do jogador: {e}")
            raise
    
    async def _process_combat_action(self, player_id: str, action: str, context: Dict) -> Dict:
        """Processar ação de combate"""
        return {
            "type": "combat",
            "action": action,
            "requires_dice": True,
            "dice_expression": "1d20+5",
            "context": context,
            "message": f"Processando ação de combate: {action}"
        }
    
    async def _process_skill_check(self, player_id: str, action: str, context: Dict) -> Dict:
        """Processar teste de habilidade"""
        return {
            "type": "skill_check",
            "action": action,
            "requires_dice": True,
            "dice_expression": "1d20",
            "context": context,
            "message": f"Processando teste de habilidade: {action}"
        }
    
    async def _process_dialogue(self, player_id: str, action: str, context: Dict) -> Dict:
        """Processar diálogo com NPC"""
        return {
            "type": "dialogue",
            "action": action,
            "requires_dice": False,
            "context": context,
            "message": f"Processando diálogo: {action}"
        }
    
    async def _process_general_action(self, player_id: str, action: str, context: Dict) -> Dict:
        """Processar ação geral"""
        return {
            "type": "general",
            "action": action,
            "requires_dice": False,
            "context": context,
            "message": f"Processando ação: {action}"
        }
    
    async def get_status(self) -> Dict:
        """Obter status geral do sistema"""
        return {
            "initialized": self._initialized,
            "total_characters": len(self.characters),
            "active_sessions": len(self.active_sessions),
            "world_state": asdict(self.world_state) if self.world_state else None,
            "characters": [
                {
                    "name": char.name,
                    "level": char.level,
                    "status": char.status,
                    "location": char.location
                }
                for char in self.characters.values()
            ]
        }