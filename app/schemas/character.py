"""
Schemas de validação para personagens
Implementa validação robusta de dados de entrada/saída
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import conint

# Enumerations
from app.models.character import CharacterRace, CharacterClass, CharacterAlignment


# ==========================================
# SCHEMAS DE ENTRADA
# ==========================================

class CharacterBase(BaseModel):
    """Schema base para personagens"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do personagem")
    player_id: str = Field(..., min_length=8, description="ID do jogador (número WhatsApp)")
    race: str = Field(..., description="Raça do personagem")
    character_class: str = Field(..., description="Classe do personagem")
    level: conint(ge=1, le=20) = Field(1, description="Nível do personagem")
    alignment: Optional[str] = Field(None, description="Tendência do personagem")
    background: Optional[str] = Field(None, description="Antecedente do personagem")
    
    # Atributos
    strength: conint(ge=1, le=30) = Field(10, description="Força")
    dexterity: conint(ge=1, le=30) = Field(10, description="Destreza")
    constitution: conint(ge=1, le=30) = Field(10, description="Constituição")
    intelligence: conint(ge=1, le=30) = Field(10, description="Inteligência")
    wisdom: conint(ge=1, le=30) = Field(10, description="Sabedoria")
    charisma: conint(ge=1, le=30) = Field(10, description="Carisma")
    
    # Pontos de vida
    max_hit_points: Optional[conint(ge=1)] = Field(None, description="Pontos de vida máximos")
    current_hit_points: Optional[conint(ge=0)] = Field(None, description="Pontos de vida atuais")
    temporary_hit_points: conint(ge=0) = Field(0, description="Pontos de vida temporários")
    
    # Defesa
    armor_class: conint(ge=1, le=30) = Field(10, description="Classe de armadura")
    
    # Experiência
    experience_points: conint(ge=0) = Field(0, description="Pontos de experiência")
    
    # Extras
    skills: Optional[Dict[str, bool]] = Field(None, description="Perícias")
    equipment: Optional[List[Dict[str, Any]]] = Field(None, description="Equipamentos")
    gold_pieces: conint(ge=0) = Field(0, description="Moedas de ouro")
    silver_pieces: conint(ge=0) = Field(0, description="Moedas de prata")
    copper_pieces: conint(ge=0) = Field(0, description="Moedas de cobre")
    racial_traits: Optional[List[str]] = Field(None, description="Características raciais")
    class_features: Optional[List[str]] = Field(None, description="Características de classe")
    spells: Optional[Dict[str, List[str]]] = Field(None, description="Magias")
    backstory: Optional[str] = Field(None, description="História do personagem")
    personality_traits: Optional[str] = Field(None, description="Traços de personalidade")
    ideals: Optional[str] = Field(None, description="Ideais")
    bonds: Optional[str] = Field(None, description="Vínculos")
    flaws: Optional[str] = Field(None, description="Fraquezas")
    
    # Validadores
    @validator('race')
    def validate_race(cls, v):
        """Valida se a raça é válida"""
        try:
            CharacterRace(v)
            return v
        except ValueError:
            raise ValueError(f"Raça inválida. Opções válidas: {[r.value for r in CharacterRace]}")
    
    @validator('character_class')
    def validate_class(cls, v):
        """Valida se a classe é válida"""
        try:
            CharacterClass(v)
            return v
        except ValueError:
            raise ValueError(f"Classe inválida. Opções válidas: {[c.value for c in CharacterClass]}")
    
    @validator('alignment')
    def validate_alignment(cls, v):
        """Valida se a tendência é válida"""
        if v is None:
            return v
        try:
            CharacterAlignment(v)
            return v
        except ValueError:
            raise ValueError(f"Tendência inválida. Opções válidas: {[a.value for a in CharacterAlignment]}")
    
    @validator('name')
    def sanitize_name(cls, v):
        """Sanitiza o nome do personagem"""
        if not v:
            raise ValueError("Nome não pode estar vazio")
        
        # Remover espaços extras e normalizar
        v = v.strip()
        
        # Verificar comprimento após sanitização
        if len(v) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        return v
    
    @validator('player_id')
    def validate_player_id(cls, v):
        """Valida o ID do jogador (número WhatsApp)"""
        # Remover caracteres não numéricos
        v = ''.join(c for c in v if c.isdigit())
        
        if len(v) < 8:
            raise ValueError("ID do jogador deve ter pelo menos 8 dígitos")
        
        return v
    
    @root_validator
    def validate_hit_points(cls, values):
        """Valida coerência entre HP máximo e atual"""
        max_hp = values.get("max_hit_points")
        current_hp = values.get("current_hit_points")
        
        # Se max_hp for definido, mas current_hp não, define current_hp = max_hp
        if max_hp is not None and current_hp is None:
            values["current_hp"] = max_hp
        
        # Se current_hp for definido, mas max_hp não, isso é um erro
        if max_hp is None and current_hp is not None:
            raise ValueError("Não é possível definir HP atual sem definir HP máximo")
        
        return values


class CharacterCreate(CharacterBase):
    """Schema para criação de personagem"""
    pass


class CharacterUpdate(BaseModel):
    """
    Schema para atualização de personagem
    Todos os campos são opcionais para permitir atualização parcial
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do personagem")
    race: Optional[str] = Field(None, description="Raça do personagem")
    character_class: Optional[str] = Field(None, description="Classe do personagem")
    level: Optional[conint(ge=1, le=20)] = Field(None, description="Nível do personagem")
    alignment: Optional[str] = Field(None, description="Tendência do personagem")
    background: Optional[str] = Field(None, description="Antecedente do personagem")
    
    # Atributos
    strength: Optional[conint(ge=1, le=30)] = Field(None, description="Força")
    dexterity: Optional[conint(ge=1, le=30)] = Field(None, description="Destreza")
    constitution: Optional[conint(ge=1, le=30)] = Field(None, description="Constituição")
    intelligence: Optional[conint(ge=1, le=30)] = Field(None, description="Inteligência")
    wisdom: Optional[conint(ge=1, le=30)] = Field(None, description="Sabedoria")
    charisma: Optional[conint(ge=1, le=30)] = Field(None, description="Carisma")
    
    # Pontos de vida
    max_hit_points: Optional[conint(ge=1)] = Field(None, description="Pontos de vida máximos")
    current_hit_points: Optional[conint(ge=0)] = Field(None, description="Pontos de vida atuais")
    temporary_hit_points: Optional[conint(ge=0)] = Field(None, description="Pontos de vida temporários")
    
    # Defesa
    armor_class: Optional[conint(ge=1, le=30)] = Field(None, description="Classe de armadura")
    
    # Experiência
    experience_points: Optional[conint(ge=0)] = Field(None, description="Pontos de experiência")
    
    # Extras
    skills: Optional[Dict[str, bool]] = Field(None, description="Perícias")
    equipment: Optional[List[Dict[str, Any]]] = Field(None, description="Equipamentos")
    gold_pieces: Optional[conint(ge=0)] = Field(None, description="Moedas de ouro")
    silver_pieces: Optional[conint(ge=0)] = Field(None, description="Moedas de prata")
    copper_pieces: Optional[conint(ge=0)] = Field(None, description="Moedas de cobre")
    racial_traits: Optional[List[str]] = Field(None, description="Características raciais")
    class_features: Optional[List[str]] = Field(None, description="Características de classe")
    spells: Optional[Dict[str, List[str]]] = Field(None, description="Magias")
    backstory: Optional[str] = Field(None, description="História do personagem")
    personality_traits: Optional[str] = Field(None, description="Traços de personalidade")
    ideals: Optional[str] = Field(None, description="Ideais")
    bonds: Optional[str] = Field(None, description="Vínculos")
    flaws: Optional[str] = Field(None, description="Fraquezas")
    is_active: Optional[bool] = Field(None, description="Se o personagem está ativo")
    
    # Validadores
    @validator('race')
    def validate_race(cls, v):
        """Valida se a raça é válida"""
        if v is None:
            return v
        try:
            CharacterRace(v)
            return v
        except ValueError:
            raise ValueError(f"Raça inválida. Opções válidas: {[r.value for r in CharacterRace]}")
    
    @validator('character_class')
    def validate_class(cls, v):
        """Valida se a classe é válida"""
        if v is None:
            return v
        try:
            CharacterClass(v)
            return v
        except ValueError:
            raise ValueError(f"Classe inválida. Opções válidas: {[c.value for c in CharacterClass]}")
    
    @validator('alignment')
    def validate_alignment(cls, v):
        """Valida se a tendência é válida"""
        if v is None:
            return v
        try:
            CharacterAlignment(v)
            return v
        except ValueError:
            raise ValueError(f"Tendência inválida. Opções válidas: {[a.value for a in CharacterAlignment]}")
    
    @validator('name')
    def sanitize_name(cls, v):
        """Sanitiza o nome do personagem"""
        if v is None:
            return v
        
        # Remover espaços extras e normalizar
        v = v.strip()
        
        # Verificar comprimento após sanitização
        if len(v) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        return v
    
    class Config:
        # Aceitar atualização parcial
        extra = "forbid"
        validate_assignment = True


# ==========================================
# SCHEMAS DE RESPOSTA
# ==========================================

class CharacterResponse(BaseModel):
    """Schema para resposta de operações com personagem"""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva")
    character: Optional[Dict[str, Any]] = Field(None, description="Dados do personagem")


class CharacterListResponse(BaseModel):
    """Schema para listagem de personagens"""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    count: int = Field(..., description="Quantidade de personagens")
    characters: List[Dict[str, Any]] = Field(..., description="Lista de personagens")
    player_id: str = Field(..., description="ID do jogador")
    remaining_slots: int = Field(..., description="Slots de personagem restantes")
    max_characters: int = Field(..., description="Máximo de personagens permitidos")


class DuplicateCheckResponse(BaseModel):
    """Schema para verificação de duplicidade de nome"""
    name: str = Field(..., description="Nome verificado")
    is_duplicate: bool = Field(..., description="Indica se o nome já existe")
    suggestions: List[str] = Field(..., description="Sugestões de nomes alternativos")


# ==========================================
# SCHEMAS RELACIONADOS A EXCEÇÕES
# ==========================================

class ErrorDetail(BaseModel):
    """Schema para detalhes de erro"""
    error: str = Field(..., description="Mensagem de erro")
    field: Optional[str] = Field(None, description="Campo com erro")
    code: str = Field(..., description="Código de erro")


class ErrorResponse(BaseModel):
    """Schema para resposta de erro"""
    detail: Union[str, ErrorDetail] = Field(..., description="Detalhes do erro")


# ==========================================
# SCHEMAS DE WEBHOOK
# ==========================================

class WebhookMessageKey(BaseModel):
    """Schema para chave da mensagem de webhook"""
    remoteJid: str = Field(..., description="ID do remetente")
    fromMe: bool = Field(..., description="Indica se a mensagem é minha")
    id: str = Field(..., description="ID da mensagem")


class WebhookMessage(BaseModel):
    """Schema para mensagem do webhook"""
    conversation: Optional[str] = Field(None, description="Texto da mensagem")
    extendedTextMessage: Optional[Dict[str, Any]] = Field(None, description="Mensagem de texto estendida")
    imageMessage: Optional[Dict[str, Any]] = Field(None, description="Mensagem com imagem")
    audioMessage: Optional[Dict[str, Any]] = Field(None, description="Mensagem com áudio")
    videoMessage: Optional[Dict[str, Any]] = Field(None, description="Mensagem com vídeo")
    documentMessage: Optional[Dict[str, Any]] = Field(None, description="Mensagem com documento")
    buttonsResponseMessage: Optional[Dict[str, Any]] = Field(None, description="Resposta de botões")
    listResponseMessage: Optional[Dict[str, Any]] = Field(None, description="Resposta de lista")


class WebhookData(BaseModel):
    """Schema para dados do webhook"""
    key: WebhookMessageKey = Field(..., description="Chave da mensagem")
    messageTimestamp: int = Field(..., description="Timestamp da mensagem")
    message: Optional[WebhookMessage] = Field(None, description="Conteúdo da mensagem")
    pushName: Optional[str] = Field(None, description="Nome do remetente")
    participant: Optional[str] = Field(None, description="Participante (para grupos)")


class WebhookRequest(BaseModel):
    """Schema para requisição de webhook"""
    instanceId: str = Field(..., description="ID da instância")
    data: WebhookData = Field(..., description="Dados da mensagem")


class WebhookResponse(BaseModel):
    """Schema para resposta de webhook"""
    success: bool = Field(..., description="Indica se o processamento foi bem-sucedido")
    message: str = Field(..., description="Mensagem descritiva")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")