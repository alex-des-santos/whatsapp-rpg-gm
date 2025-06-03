"""
Modelo de personagem D&D 5e com validação de duplicidade
Implementa todas as funcionalidades de RPG necessárias
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, JSON, Text,
    ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class CharacterRace(str, Enum):
    """Raças disponíveis em D&D 5e"""
    HUMAN = "Humano"
    ELF = "Elfo"
    DWARF = "Anão"
    HALFLING = "Halfling"
    DRAGONBORN = "Draconato"
    GNOME = "Gnomo"
    HALF_ELF = "Meio-elfo"
    HALF_ORC = "Meio-orc"
    TIEFLING = "Tiefling"


class CharacterClass(str, Enum):
    """Classes disponíveis em D&D 5e"""
    BARBARIAN = "Bárbaro"
    BARD = "Bardo"
    CLERIC = "Clérico"
    DRUID = "Druida"
    FIGHTER = "Guerreiro"
    MONK = "Monge"
    PALADIN = "Paladino"
    RANGER = "Patrulheiro"
    ROGUE = "Ladino"
    SORCERER = "Feiticeiro"
    WARLOCK = "Bruxo"
    WIZARD = "Mago"


class CharacterAlignment(str, Enum):
    """Tendências disponíveis em D&D 5e"""
    LAWFUL_GOOD = "Leal e Bom"
    NEUTRAL_GOOD = "Neutro e Bom"
    CHAOTIC_GOOD = "Caótico e Bom"
    LAWFUL_NEUTRAL = "Leal e Neutro"
    TRUE_NEUTRAL = "Neutro"
    CHAOTIC_NEUTRAL = "Caótico e Neutro"
    LAWFUL_EVIL = "Leal e Mau"
    NEUTRAL_EVIL = "Neutro e Mau"
    CHAOTIC_EVIL = "Caótico e Mau"


class Character(Base):
    """
    Modelo de personagem D&D 5e com validação de duplicidade
    """
    __tablename__ = "characters"
    
    # ==========================================
    # CAMPOS BÁSICOS
    # ==========================================
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas do personagem
    name = Column(String(100), nullable=False, index=True)
    player_id = Column(String(50), nullable=False, index=True)  # WhatsApp number
    race = Column(String(20), nullable=False)
    character_class = Column(String(20), nullable=False)
    level = Column(Integer, default=1, nullable=False)
    alignment = Column(String(30), nullable=True)
    background = Column(String(50), nullable=True)
    
    # ==========================================
    # ATRIBUTOS PRINCIPAIS (D&D 5e)
    # ==========================================
    
    strength = Column(Integer, default=10, nullable=False)
    dexterity = Column(Integer, default=10, nullable=False)
    constitution = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    charisma = Column(Integer, default=10, nullable=False)
    
    # ==========================================
    # PONTOS DE VIDA E DEFESA
    # ==========================================
    
    max_hit_points = Column(Integer, nullable=False)
    current_hit_points = Column(Integer, nullable=False)
    temporary_hit_points = Column(Integer, default=0)
    armor_class = Column(Integer, default=10, nullable=False)
    
    # ==========================================
    # EXPERIÊNCIA E PROGRESSÃO
    # ==========================================
    
    experience_points = Column(Integer, default=0, nullable=False)
    proficiency_bonus = Column(Integer, default=2, nullable=False)
    
    # ==========================================
    # PERÍCIAS E PROFICIÊNCIAS
    # ==========================================
    
    # Perícias (JSON com skill_name: is_proficient)
    skills = Column(JSON, default=dict)
    
    # Proficiências com armas e armaduras
    weapon_proficiencies = Column(JSON, default=list)
    armor_proficiencies = Column(JSON, default=list)
    
    # Idiomas
    languages = Column(JSON, default=list)
    
    # ==========================================
    # EQUIPAMENTOS E INVENTÁRIO
    # ==========================================
    
    # Equipamentos (JSON com detalhes)
    equipment = Column(JSON, default=list)
    
    # Moedas
    gold_pieces = Column(Integer, default=0)
    silver_pieces = Column(Integer, default=0)
    copper_pieces = Column(Integer, default=0)
    
    # ==========================================
    # CARACTERÍSTICAS ESPECIAIS
    # ==========================================
    
    # Características raciais
    racial_traits = Column(JSON, default=list)
    
    # Características de classe
    class_features = Column(JSON, default=list)
    
    # Magias (se aplicável)
    spells = Column(JSON, default=dict)
    spell_slots = Column(JSON, default=dict)
    
    # ==========================================
    # INFORMAÇÕES NARRATIVAS
    # ==========================================
    
    # História do personagem
    backstory = Column(Text, nullable=True)
    personality_traits = Column(Text, nullable=True)
    ideals = Column(Text, nullable=True)
    bonds = Column(Text, nullable=True)
    flaws = Column(Text, nullable=True)
    
    # ==========================================
    # METADADOS E CONTROLE
    # ==========================================
    
    # Status do personagem
    is_active = Column(Boolean, default=True, nullable=False)
    is_dead = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_played = Column(DateTime(timezone=True), nullable=True)
    
    # Sessão/campanha atual
    current_session = Column(String(100), nullable=True)
    campaign_id = Column(String(50), nullable=True)
    
    # ==========================================
    # CONSTRAINTS E ÍNDICES
    # ==========================================
    
    __table_args__ = (
        # Constraint para evitar nomes duplicados (case-insensitive)
        Index('ix_character_name_lower', func.lower(name), unique=True),
        
        # Constraint para limitar personagens por jogador + classe + raça
        UniqueConstraint(
            'player_id', 'character_class', 'race',
            name='uq_player_class_race'
        ),
        
        # Constraints de validação
        CheckConstraint('level >= 1 AND level <= 20', name='valid_level'),
        CheckConstraint('strength >= 1 AND strength <= 30', name='valid_strength'),
        CheckConstraint('dexterity >= 1 AND dexterity <= 30', name='valid_dexterity'),
        CheckConstraint('constitution >= 1 AND constitution <= 30', name='valid_constitution'),
        CheckConstraint('intelligence >= 1 AND intelligence <= 30', name='valid_intelligence'),
        CheckConstraint('wisdom >= 1 AND wisdom <= 30', name='valid_wisdom'),
        CheckConstraint('charisma >= 1 AND charisma <= 30', name='valid_charisma'),
        CheckConstraint('current_hit_points >= 0', name='valid_current_hp'),
        CheckConstraint('max_hit_points >= 1', name='valid_max_hp'),
        CheckConstraint('armor_class >= 1', name='valid_armor_class'),
        CheckConstraint('experience_points >= 0', name='valid_experience'),
        
        # Índices para performance
        Index('ix_character_player_active', 'player_id', 'is_active'),
        Index('ix_character_class_level', 'character_class', 'level'),
        Index('ix_character_campaign', 'campaign_id', 'is_active'),
    )
    
    # ==========================================
    # MÉTODOS DE VALIDAÇÃO
    # ==========================================
    
    def validate_race(self) -> bool:
        """Valida se a raça é válida"""
        try:
            CharacterRace(self.race)
            return True
        except ValueError:
            return False
    
    def validate_class(self) -> bool:
        """Valida se a classe é válida"""
        try:
            CharacterClass(self.character_class)
            return True
        except ValueError:
            return False
    
    def validate_alignment(self) -> bool:
        """Valida se a tendência é válida"""
        if not self.alignment:
            return True  # Alignment é opcional
        try:
            CharacterAlignment(self.alignment)
            return True
        except ValueError:
            return False
    
    def validate_attributes(self) -> bool:
        """Valida se todos os atributos estão em range válido"""
        attributes = [
            self.strength, self.dexterity, self.constitution,
            self.intelligence, self.wisdom, self.charisma
        ]
        return all(1 <= attr <= 30 for attr in attributes)
    
    # ==========================================
    # MÉTODOS DE CÁLCULO D&D 5e
    # ==========================================
    
    def get_ability_modifier(self, ability_score: int) -> int:
        """Calcula o modificador de atributo"""
        return (ability_score - 10) // 2
    
    @property
    def strength_modifier(self) -> int:
        return self.get_ability_modifier(self.strength)
    
    @property
    def dexterity_modifier(self) -> int:
        return self.get_ability_modifier(self.dexterity)
    
    @property
    def constitution_modifier(self) -> int:
        return self.get_ability_modifier(self.constitution)
    
    @property
    def intelligence_modifier(self) -> int:
        return self.get_ability_modifier(self.intelligence)
    
    @property
    def wisdom_modifier(self) -> int:
        return self.get_ability_modifier(self.wisdom)
    
    @property
    def charisma_modifier(self) -> int:
        return self.get_ability_modifier(self.charisma)
    
    def get_skill_modifier(self, skill_name: str) -> int:
        """
        Calcula o modificador de perícia
        """
        # Mapeamento de perícias para atributos
        skill_abilities = {
            "acrobatics": self.dexterity_modifier,
            "animal_handling": self.wisdom_modifier,
            "arcana": self.intelligence_modifier,
            "athletics": self.strength_modifier,
            "deception": self.charisma_modifier,
            "history": self.intelligence_modifier,
            "insight": self.wisdom_modifier,
            "intimidation": self.charisma_modifier,
            "investigation": self.intelligence_modifier,
            "medicine": self.wisdom_modifier,
            "nature": self.intelligence_modifier,
            "perception": self.wisdom_modifier,
            "performance": self.charisma_modifier,
            "persuasion": self.charisma_modifier,
            "religion": self.intelligence_modifier,
            "sleight_of_hand": self.dexterity_modifier,
            "stealth": self.dexterity_modifier,
            "survival": self.wisdom_modifier,
        }
        
        base_modifier = skill_abilities.get(skill_name, 0)
        
        # Adicionar bônus de proficiência se proficiente
        if self.skills and self.skills.get(skill_name, False):
            base_modifier += self.proficiency_bonus
        
        return base_modifier
    
    @property
    def is_alive(self) -> bool:
        """Verifica se o personagem está vivo"""
        return not self.is_dead and self.current_hit_points > 0
    
    @property
    def is_unconscious(self) -> bool:
        """Verifica se o personagem está inconsciente"""
        return self.current_hit_points <= 0 and not self.is_dead
    
    @property
    def hit_point_percentage(self) -> float:
        """Retorna a porcentagem de HP atual"""
        if self.max_hit_points <= 0:
            return 0.0
        return (self.current_hit_points / self.max_hit_points) * 100
    
    @property
    def health_status(self) -> str:
        """Retorna o status de saúde do personagem"""
        if self.is_dead:
            return "Morto"
        elif self.is_unconscious:
            return "Inconsciente"
        elif self.hit_point_percentage >= 75:
            return "Saudável"
        elif self.hit_point_percentage >= 50:
            return "Ferido"
        elif self.hit_point_percentage >= 25:
            return "Gravemente Ferido"
        else:
            return "Crítico"
    
    # ==========================================
    # MÉTODOS DE EXPERIÊNCIA E NÍVEL
    # ==========================================
    
    def experience_needed_for_next_level(self) -> int:
        """Calcula XP necessário para o próximo nível"""
        xp_table = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        
        if self.level >= 20:
            return 0  # Nível máximo atingido
        
        return xp_table.get(self.level + 1, 0) - self.experience_points
    
    def can_level_up(self) -> bool:
        """Verifica se o personagem pode subir de nível"""
        return self.experience_needed_for_next_level() <= 0 and self.level < 20
    
    def add_experience(self, xp: int) -> bool:
        """Adiciona experiência e verifica level up"""
        self.experience_points += xp
        
        level_up_occurred = False
        while self.can_level_up():
            self.level += 1
            self.proficiency_bonus = 2 + ((self.level - 1) // 4)
            level_up_occurred = True
        
        return level_up_occurred
    
    # ==========================================
    # MÉTODOS DE CONVERSÃO E SERIALIZAÇÃO
    # ==========================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o personagem para dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "player_id": self.player_id,
            "race": self.race,
            "character_class": self.character_class,
            "level": self.level,
            "alignment": self.alignment,
            "background": self.background,
            "attributes": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma,
            },
            "modifiers": {
                "strength": self.strength_modifier,
                "dexterity": self.dexterity_modifier,
                "constitution": self.constitution_modifier,
                "intelligence": self.intelligence_modifier,
                "wisdom": self.wisdom_modifier,
                "charisma": self.charisma_modifier,
            },
            "hit_points": {
                "current": self.current_hit_points,
                "max": self.max_hit_points,
                "temporary": self.temporary_hit_points,
                "percentage": self.hit_point_percentage,
                "status": self.health_status,
            },
            "armor_class": self.armor_class,
            "experience": {
                "current": self.experience_points,
                "needed_for_next": self.experience_needed_for_next_level(),
                "can_level_up": self.can_level_up(),
            },
            "proficiency_bonus": self.proficiency_bonus,
            "skills": self.skills,
            "equipment": self.equipment,
            "money": {
                "gold": self.gold_pieces,
                "silver": self.silver_pieces,
                "copper": self.copper_pieces,
            },
            "spells": self.spells,
            "is_active": self.is_active,
            "is_alive": self.is_alive,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_played": self.last_played.isoformat() if self.last_played else None,
        }
    
    def to_whatsapp_card(self) -> str:
        """
        Gera uma ficha resumida para WhatsApp
        """
        card = f"""
🎭 **{self.name}**
📊 **Nível {self.level} {self.race} {self.character_class}**

⚔️ **Atributos:**
💪 FOR: {self.strength} ({self.strength_modifier:+d})
🏃 DES: {self.dexterity} ({self.dexterity_modifier:+d})
🛡️ CON: {self.constitution} ({self.constitution_modifier:+d})
🧠 INT: {self.intelligence} ({self.intelligence_modifier:+d})
🦉 SAB: {self.wisdom} ({self.wisdom_modifier:+d})
💬 CAR: {self.charisma} ({self.charisma_modifier:+d})

❤️ **HP:** {self.current_hit_points}/{self.max_hit_points} ({self.health_status})
🛡️ **CA:** {self.armor_class}
⭐ **XP:** {self.experience_points} ({self.experience_needed_for_next_level()} para próximo nível)

🎯 **Bônus de Proficiência:** +{self.proficiency_bonus}
        """.strip()
        
        return card
    
    # ==========================================
    # MÉTODOS ESPECIAIS
    # ==========================================
    
    def __repr__(self) -> str:
        return f"<Character(id={self.id}, name='{self.name}', level={self.level}, class='{self.character_class}')>"
    
    def __str__(self) -> str:
        return f"{self.name} - Nível {self.level} {self.race} {self.character_class}"


# ==========================================
# MODELO DE CONTADOR DE PERSONAGENS
# ==========================================

class PlayerCharacterCount(Base):
    """
    Tabela auxiliar para controlar limite de personagens por jogador
    """
    __tablename__ = "player_character_counts"
    
    player_id = Column(String(50), primary_key=True)
    character_count = Column(Integer, default=0, nullable=False)
    max_allowed = Column(Integer, default=3, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('character_count >= 0', name='valid_character_count'),
        CheckConstraint('max_allowed >= 1', name='valid_max_allowed'),
    )
    
    @property
    def can_create_character(self) -> bool:
        """Verifica se o jogador pode criar mais personagens"""
        return self.character_count < self.max_allowed
    
    @property
    def remaining_slots(self) -> int:
        """Retorna quantos personagens ainda podem ser criados"""
        return max(0, self.max_allowed - self.character_count)