"""
Character Manager - Gerenciamento de personagens D&D 5e
Sistema completo de criação, modificação e persistência de personagens
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

from .dice_system import DiceSystem, get_modifier, get_proficiency_bonus
from ..core.database import cache_get, cache_set, cache_delete

logger = logging.getLogger(__name__)

class CharacterClass(Enum):
    """Classes de personagem D&D 5e"""
    BARBARIAN = "barbaro"
    BARD = "bardo"
    CLERIC = "clerigo"
    DRUID = "druida"
    FIGHTER = "guerreiro"
    MONK = "monge"
    PALADIN = "paladino"
    RANGER = "batedor"
    ROGUE = "ladino"
    SORCERER = "feiticeiro"
    WARLOCK = "bruxo"
    WIZARD = "mago"

class Race(Enum):
    """Raças de personagem D&D 5e"""
    HUMAN = "humano"
    ELF = "elfo"
    DWARF = "anao"
    HALFLING = "halfling"
    DRAGONBORN = "draconato"
    GNOME = "gnomo"
    HALF_ELF = "meio_elfo"
    HALF_ORC = "meio_orc"
    TIEFLING = "tiefling"

@dataclass
class Equipment:
    """Equipamento do personagem"""
    name: str
    type: str  # weapon, armor, item, etc.
    equipped: bool = False
    quantity: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Spell:
    """Magia conhecida"""
    name: str
    level: int
    school: str
    prepared: bool = False
    description: str = ""

@dataclass
class Character:
    """Personagem de D&D 5e"""
    # Identificação
    player_id: str
    session_id: str
    name: str

    # Características básicas
    race: Race
    character_class: CharacterClass
    level: int = 1

    # Atributos
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Combate
    hp_max: int = 8
    hp_current: int = 8
    armor_class: int = 10

    # Proficiências
    proficiencies: List[str] = field(default_factory=list)

    # Equipamentos
    equipment: List[Equipment] = field(default_factory=list)
    gold: int = 0

    # Magias (se aplicável)
    spells_known: List[Spell] = field(default_factory=list)
    spell_slots: Dict[int, int] = field(default_factory=dict)
    spell_slots_used: Dict[int, int] = field(default_factory=dict)

    # Progressão
    experience: int = 0

    # Características de roleplay
    background: str = ""
    alignment: str = "Neutro"

    # Metadados
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        data = asdict(self)
        data['race'] = self.race.value
        data['character_class'] = self.character_class.value
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Criar instância a partir de dicionário"""
        data['race'] = Race(data['race'])
        data['character_class'] = CharacterClass(data['character_class'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])

        # Converter equipment de dict para Equipment objects
        if 'equipment' in data:
            data['equipment'] = [Equipment(**eq) for eq in data['equipment']]

        # Converter spells de dict para Spell objects
        if 'spells_known' in data:
            data['spells_known'] = [Spell(**spell) for spell in data['spells_known']]

        return cls(**data)

    @property
    def strength_modifier(self) -> int:
        return get_modifier(self.strength)

    @property
    def dexterity_modifier(self) -> int:
        return get_modifier(self.dexterity)

    @property
    def constitution_modifier(self) -> int:
        return get_modifier(self.constitution)

    @property
    def intelligence_modifier(self) -> int:
        return get_modifier(self.intelligence)

    @property
    def wisdom_modifier(self) -> int:
        return get_modifier(self.wisdom)

    @property
    def charisma_modifier(self) -> int:
        return get_modifier(self.charisma)

    @property
    def proficiency_bonus(self) -> int:
        return get_proficiency_bonus(self.level)

    @property
    def is_spellcaster(self) -> bool:
        """Verificar se a classe é conjuradora"""
        spellcasting_classes = {
            CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID,
            CharacterClass.PALADIN, CharacterClass.RANGER, CharacterClass.SORCERER,
            CharacterClass.WARLOCK, CharacterClass.WIZARD
        }
        return self.character_class in spellcasting_classes

class CharacterManager:
    """Gerenciador de personagens"""

    def __init__(self):
        self.dice_system = DiceSystem()

        # Dados base para criação de personagens
        self.class_data = self._load_class_data()
        self.race_data = self._load_race_data()
        self.equipment_data = self._load_equipment_data()

        logger.info("Character Manager inicializado")

    async def get_character(self, player_id: str, session_id: str) -> Optional[Character]:
        """Obter personagem do cache"""
        cache_key = f"character:{session_id}:{player_id}"

        try:
            character_data = await cache_get(cache_key)
            if character_data:
                character_dict = json.loads(character_data)
                return Character.from_dict(character_dict)
            return None
        except Exception as e:
            logger.error(f"Erro ao obter personagem: {e}")
            return None

    async def save_character(self, character: Character) -> bool:
        """Salvar personagem no cache"""
        cache_key = f"character:{character.session_id}:{character.player_id}"

        try:
            character.last_updated = datetime.now()
            character_data = json.dumps(character.to_dict(), default=str)
            await cache_set(cache_key, character_data, expire=86400)  # 24 horas
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar personagem: {e}")
            return False

    async def create_random_character(self, player_id: str, session_id: str) -> Character:
        """Criar personagem aleatório"""
        # Escolher raça e classe aleatórias
        race = random.choice(list(Race))
        char_class = random.choice(list(CharacterClass))

        # Rolar atributos
        ability_scores = self.dice_system.roll_ability_scores()

        # Aplicar modificadores raciais
        self._apply_racial_bonuses(ability_scores, race)

        # Criar personagem
        character = Character(
            player_id=player_id,
            session_id=session_id,
            name=self._generate_random_name(race),
            race=race,
            character_class=char_class,
            **ability_scores
        )

        # Configurar HP
        hit_die = self.class_data[char_class]['hit_die']
        character.hp_max = hit_die + character.constitution_modifier
        character.hp_current = character.hp_max

        # Configurar AC base
        character.armor_class = 10 + character.dexterity_modifier

        # Adicionar proficiências
        character.proficiencies = self.class_data[char_class]['proficiencies'].copy()

        # Adicionar equipamento inicial
        self._add_starting_equipment(character)

        # Configurar magias se aplicável
        if character.is_spellcaster:
            self._setup_spellcasting(character)

        # Salvar personagem
        await self.save_character(character)

        logger.info(f"Personagem criado: {character.name} ({race.value} {char_class.value})")
        return character

    async def create_custom_character(self, player_id: str, session_id: str, 
                                    name: str, race: Race, char_class: CharacterClass,
                                    ability_scores: Dict[str, int]) -> Character:
        """Criar personagem customizado"""
        # Aplicar modificadores raciais
        self._apply_racial_bonuses(ability_scores, race)

        # Criar personagem
        character = Character(
            player_id=player_id,
            session_id=session_id,
            name=name,
            race=race,
            character_class=char_class,
            **ability_scores
        )

        # Configurações iniciais
        hit_die = self.class_data[char_class]['hit_die']
        character.hp_max = hit_die + character.constitution_modifier
        character.hp_current = character.hp_max
        character.armor_class = 10 + character.dexterity_modifier
        character.proficiencies = self.class_data[char_class]['proficiencies'].copy()

        # Equipamento e magias
        self._add_starting_equipment(character)
        if character.is_spellcaster:
            self._setup_spellcasting(character)

        await self.save_character(character)
        return character

    def _apply_racial_bonuses(self, ability_scores: Dict[str, int], race: Race):
        """Aplicar bônus raciais aos atributos"""
        bonuses = self.race_data[race]['ability_bonuses']
        for ability, bonus in bonuses.items():
            ability_scores[ability] += bonus

    def _add_starting_equipment(self, character: Character):
        """Adicionar equipamento inicial"""
        class_equipment = self.class_data[character.character_class]['starting_equipment']

        for item_name in class_equipment:
            if item_name in self.equipment_data:
                item_data = self.equipment_data[item_name]
                equipment = Equipment(
                    name=item_name,
                    type=item_data['type'],
                    equipped=item_data.get('auto_equip', False),
                    properties=item_data.get('properties', {})
                )
                character.equipment.append(equipment)

        # Ouro inicial
        character.gold = random.randint(50, 200)

    def _setup_spellcasting(self, character: Character):
        """Configurar sistema de magias"""
        class_spells = self.class_data[character.character_class].get('spellcasting', {})

        if class_spells:
            # Espaços de magia nível 1
            character.spell_slots = {1: class_spells.get('level_1_slots', 1)}
            character.spell_slots_used = {1: 0}

            # Magias conhecidas iniciais
            cantrips = class_spells.get('cantrips', [])
            level_1_spells = class_spells.get('level_1_spells', [])

            for cantrip in cantrips[:2]:  # 2 cantrips iniciais
                spell = Spell(name=cantrip, level=0, school="Universal", prepared=True)
                character.spells_known.append(spell)

            for spell in level_1_spells[:2]:  # 2 magias nível 1
                spell_obj = Spell(name=spell, level=1, school="Universal", prepared=True)
                character.spells_known.append(spell_obj)

    def _generate_random_name(self, race: Race) -> str:
        """Gerar nome aleatório baseado na raça"""
        names_by_race = {
            Race.HUMAN: ["Aelar", "Beiro", "Carric", "Drannor", "Enna", "Fodel", "Galar", "Halimath"],
            Race.ELF: ["Adran", "Aelar", "Aramil", "Aranea", "Berrian", "Dayereth", "Enna", "Galinndan"],
            Race.DWARF: ["Adrik", "Alberich", "Baern", "Balin", "Beira", "Darrak", "Delg", "Eberk"],
            Race.HALFLING: ["Alton", "Ander", "Cade", "Corrin", "Eldon", "Errich", "Finnan", "Garret"],
            Race.DRAGONBORN: ["Arjhan", "Balasar", "Bharash", "Donaar", "Ghesh", "Heskan", "Kriv", "Medrash"],
            Race.GNOME: ["Alston", "Alvyn", "Boddynock", "Brocc", "Burgell", "Dimble", "Eldon", "Erky"],
            Race.HALF_ELF: ["Aerdyl", "Ahvak", "Aramil", "Aranea", "Berrian", "Caelynn", "Carric", "Dayereth"],
            Race.HALF_ORC: ["Dench", "Feng", "Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"],
            Race.TIEFLING: ["Akmenos", "Amnon", "Barakas", "Damakos", "Ekemon", "Iados", "Kairon", "Leucis"]
        }

        return random.choice(names_by_race.get(race, ["Aventureiro"]))

    def _load_class_data(self) -> Dict[CharacterClass, Dict[str, Any]]:
        """Carregar dados das classes"""
        return {
            CharacterClass.FIGHTER: {
                'hit_die': 10,
                'proficiencies': ['athletics', 'intimidation'],
                'starting_equipment': ['leather_armor', 'longsword', 'shield', 'javelin'],
                'features': ['fighting_style', 'second_wind']
            },
            CharacterClass.WIZARD: {
                'hit_die': 6,
                'proficiencies': ['arcana', 'investigation'],
                'starting_equipment': ['quarterstaff', 'light_crossbow', 'spellbook'],
                'spellcasting': {
                    'level_1_slots': 2,
                    'cantrips': ['mage_hand', 'prestidigitation', 'ray_of_frost'],
                    'level_1_spells': ['magic_missile', 'shield', 'detect_magic']
                }
            },
            CharacterClass.ROGUE: {
                'hit_die': 8,
                'proficiencies': ['stealth', 'sleight_of_hand', 'thieves_tools'],
                'starting_equipment': ['leather_armor', 'shortsword', 'thieves_tools', 'dagger'],
                'features': ['sneak_attack', 'thieves_cant']
            },
            # Adicionar outras classes...
        }

    def _load_race_data(self) -> Dict[Race, Dict[str, Any]]:
        """Carregar dados das raças"""
        return {
            Race.HUMAN: {
                'ability_bonuses': {
                    'strength': 1, 'dexterity': 1, 'constitution': 1,
                    'intelligence': 1, 'wisdom': 1, 'charisma': 1
                },
                'features': ['extra_skill', 'extra_feat']
            },
            Race.ELF: {
                'ability_bonuses': {'dexterity': 2},
                'features': ['darkvision', 'keen_senses', 'fey_ancestry', 'trance']
            },
            Race.DWARF: {
                'ability_bonuses': {'constitution': 2},
                'features': ['darkvision', 'dwarven_resilience', 'stonecunning']
            },
            # Adicionar outras raças...
        }

    def _load_equipment_data(self) -> Dict[str, Dict[str, Any]]:
        """Carregar dados de equipamentos"""
        return {
            'leather_armor': {
                'type': 'armor',
                'auto_equip': True,
                'properties': {'armor_class': 11, 'armor_type': 'light'}
            },
            'longsword': {
                'type': 'weapon',
                'auto_equip': True,
                'properties': {'damage': '1d8', 'damage_type': 'slashing'}
            },
            'shield': {
                'type': 'armor',
                'auto_equip': True,
                'properties': {'armor_class': 2, 'armor_type': 'shield'}
            },
            # Adicionar outros equipamentos...
        }
