"""
Endpoints para gerenciamento de personagens com validação de duplicidade
Implementa as recomendações críticas de validação
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text

from app.core.config import settings
from app.core.database import get_db
from app.models.character import Character, PlayerCharacterCount
from app.schemas.character import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    CharacterListResponse, DuplicateCheckResponse
)
from app.utils.validation import sanitize_name

# Configuração de logging
logger = logging.getLogger(__name__)

# Criação do router
router = APIRouter()


# ==========================================
# VALIDAÇÕES DE DUPLICIDADE
# ==========================================

async def check_character_name_duplicate(
    name: str, 
    db: Session,
    exclude_id: Optional[int] = None
) -> bool:
    """
    Verifica se já existe personagem com este nome (case-insensitive)
    Implementa a validação de duplicidade recomendada
    """
    sanitized_name = sanitize_name(name)
    
    # Query base com filtro case-insensitive
    query = db.query(Character).filter(
        func.lower(Character.name) == func.lower(sanitized_name)
    )
    
    # Se tiver ID para excluir (em caso de update)
    if exclude_id:
        query = query.filter(Character.id != exclude_id)
    
    # Verificar se existe
    return query.first() is not None


async def check_player_character_limit(
    player_id: str,
    db: Session
) -> tuple[bool, int]:
    """
    Verifica se o jogador atingiu o limite de personagens
    Parte da validação de duplicidade
    """
    # Buscar contador do jogador
    player_count = db.query(PlayerCharacterCount).filter(
        PlayerCharacterCount.player_id == player_id
    ).first()
    
    # Se não existir, criar
    if not player_count:
        player_count = PlayerCharacterCount(
            player_id=player_id,
            character_count=0,
            max_allowed=settings.MAX_CHARACTERS_PER_PLAYER
        )
        db.add(player_count)
        db.commit()
        db.refresh(player_count)
    
    # Verificar se pode criar mais
    can_create = player_count.can_create_character
    remaining = player_count.remaining_slots
    
    return can_create, remaining


async def check_class_race_duplicate(
    player_id: str,
    character_class: str,
    race: str,
    db: Session,
    exclude_id: Optional[int] = None
) -> bool:
    """
    Verifica se o jogador já tem personagem desta classe e raça
    Validação adicional de duplicidade
    """
    # Skip se não for ativar esta validação
    if not settings.ENABLE_CLASS_RACE_VALIDATION:
        return False
    
    # Query base
    query = db.query(Character).filter(
        Character.player_id == player_id,
        func.lower(Character.character_class) == func.lower(character_class),
        func.lower(Character.race) == func.lower(race)
    )
    
    # Se tiver ID para excluir
    if exclude_id:
        query = query.filter(Character.id != exclude_id)
    
    # Verificar se existe
    return query.first() is not None


# ==========================================
# ENDPOINT: VERIFICAÇÃO DE DUPLICIDADE
# ==========================================

@router.get(
    "/check_duplicate/{name}",
    response_model=DuplicateCheckResponse,
    summary="Verifica duplicidade de nome de personagem",
    description="Verifica se um nome de personagem já está em uso"
)
async def check_character_duplicate(
    name: str = Path(..., description="Nome do personagem a verificar"),
    db: Session = Depends(get_db)
):
    """
    Endpoint específico para verificar duplicidade de nome de personagem
    Facilita validação no frontend antes de tentar criar
    """
    # Sanitizar e verificar
    sanitized_name = sanitize_name(name)
    is_duplicate = await check_character_name_duplicate(sanitized_name, db)
    
    # Sugestões se for duplicado
    suggestions = []
    if is_duplicate:
        # Criar algumas sugestões com números
        for i in range(2, 6):
            suggestions.append(f"{sanitized_name} {i}")
        
        # Sugestões com adjetivos
        adjectives = ["Heroico", "Valente", "Místico", "Selvagem", "Audaz"]
        for adj in adjectives:
            suggestions.append(f"{sanitized_name}, o {adj}")
    
    return {
        "name": sanitized_name,
        "is_duplicate": is_duplicate,
        "suggestions": suggestions if is_duplicate else []
    }


# ==========================================
# ENDPOINT: CRIAÇÃO DE PERSONAGEM
# ==========================================

@router.post(
    "/create_character",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo personagem",
    description="Cria um novo personagem com validação completa de duplicidade"
)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo personagem com verificações robustas de duplicidade
    Implementa as recomendações críticas
    """
    # Sanitizar nome
    character_data.name = sanitize_name(character_data.name)
    
    try:
        # 1. Validar duplicidade de nome (case-insensitive)
        name_exists = await check_character_name_duplicate(character_data.name, db)
        if name_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Personagem com este nome já existe",
                    "field": "name",
                    "code": "duplicate_name"
                }
            )
        
        # 2. Validar limite de personagens por jogador
        can_create, remaining = await check_player_character_limit(character_data.player_id, db)
        if not can_create:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"Limite de personagens atingido (máximo: {settings.MAX_CHARACTERS_PER_PLAYER})",
                    "field": "player_id",
                    "code": "character_limit"
                }
            )
        
        # 3. Validar duplicidade de classe + raça (se configurado)
        if settings.ENABLE_CLASS_RACE_VALIDATION:
            class_race_exists = await check_class_race_duplicate(
                character_data.player_id,
                character_data.character_class,
                character_data.race,
                db
            )
            
            if class_race_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": f"Você já possui um personagem {character_data.race} {character_data.character_class}",
                        "field": "character_class",
                        "code": "duplicate_class_race"
                    }
                )
        
        # Criar o personagem com dados validados
        new_character = Character(**character_data.dict())
        
        # Cálculos automáticos
        if not new_character.max_hit_points:
            # Calcula HP baseado na classe
            hp_by_class = {
                "Bárbaro": 12 + new_character.constitution_modifier,
                "Guerreiro": 10 + new_character.constitution_modifier,
                "Paladino": 10 + new_character.constitution_modifier,
                "Patrulheiro": 10 + new_character.constitution_modifier,
                "Monge": 8 + new_character.constitution_modifier,
                "Druida": 8 + new_character.constitution_modifier,
                "Clérico": 8 + new_character.constitution_modifier,
                "Ladino": 8 + new_character.constitution_modifier,
                "Bardo": 8 + new_character.constitution_modifier,
                "Bruxo": 8 + new_character.constitution_modifier,
                "Feiticeiro": 6 + new_character.constitution_modifier,
                "Mago": 6 + new_character.constitution_modifier,
            }
            
            new_character.max_hit_points = hp_by_class.get(
                new_character.character_class, 
                8 + new_character.constitution_modifier
            )
            
            # Garante HP mínimo de 1
            new_character.max_hit_points = max(1, new_character.max_hit_points)
        
        # Define HP atual como máximo se não especificado
        if not new_character.current_hit_points:
            new_character.current_hit_points = new_character.max_hit_points
        
        # Adicionar ao banco
        db.add(new_character)
        
        # Atualizar contador de personagens do jogador
        player_count = db.query(PlayerCharacterCount).filter(
            PlayerCharacterCount.player_id == character_data.player_id
        ).first()
        
        if player_count:
            player_count.character_count += 1
        else:
            player_count = PlayerCharacterCount(
                player_id=character_data.player_id,
                character_count=1,
                max_allowed=settings.MAX_CHARACTERS_PER_PLAYER
            )
            db.add(player_count)
        
        # Salvar alterações
        db.commit()
        db.refresh(new_character)
        
        # Log de sucesso
        logger.info(
            f"Personagem criado: {new_character.name} (ID: {new_character.id}) "
            f"para jogador {new_character.player_id}"
        )
        
        return CharacterResponse(
            success=True,
            message="Personagem criado com sucesso",
            character=new_character.to_dict()
        )
        
    except HTTPException:
        # Repassar exceções HTTP
        raise
        
    except IntegrityError as e:
        # Tratar violações de constraints SQL
        db.rollback()
        error_message = str(e)
        
        if "uq_player_class_race" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": f"Você já possui um personagem {character_data.race} {character_data.character_class}",
                    "field": "character_class",
                    "code": "duplicate_class_race"
                }
            )
        
        if "ix_character_name_lower" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Personagem com este nome já existe",
                    "field": "name",
                    "code": "duplicate_name"
                }
            )
        
        # Erro genérico de integridade
        logger.error(f"Erro de integridade: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Erro de validação de dados",
                "field": "unknown",
                "code": "integrity_error"
            }
        )
        
    except Exception as e:
        # Erros gerais
        db.rollback()
        logger.error(f"Erro ao criar personagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro ao criar personagem",
                "message": str(e),
                "code": "internal_error"
            }
        )


# ==========================================
# ENDPOINT: LISTAR PERSONAGENS
# ==========================================

@router.get(
    "/list/{player_id}",
    response_model=CharacterListResponse,
    summary="Lista personagens do jogador",
    description="Retorna todos os personagens ativos de um jogador"
)
async def list_characters(
    player_id: str = Path(..., description="ID do jogador (número WhatsApp)"),
    active_only: bool = Query(True, description="Retornar apenas personagens ativos"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os personagens de um jogador
    """
    try:
        # Query base
        query = db.query(Character).filter(Character.player_id == player_id)
        
        # Filtrar ativos se solicitado
        if active_only:
            query = query.filter(Character.is_active == True)
        
        # Ordenar por nome
        query = query.order_by(Character.name)
        
        # Executar query
        characters = query.all()
        
        # Verificar limite do jogador
        _, remaining_slots = await check_player_character_limit(player_id, db)
        
        # Converter para dicionário
        character_list = [char.to_dict() for char in characters]
        
        return {
            "success": True,
            "count": len(character_list),
            "characters": character_list,
            "player_id": player_id,
            "remaining_slots": remaining_slots,
            "max_characters": settings.MAX_CHARACTERS_PER_PLAYER
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar personagens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro ao listar personagens",
                "message": str(e),
                "code": "internal_error"
            }
        )


# ==========================================
# ENDPOINT: BUSCAR PERSONAGEM POR ID
# ==========================================

@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Busca personagem por ID",
    description="Retorna os detalhes de um personagem específico"
)
async def get_character(
    character_id: int = Path(..., description="ID do personagem"),
    db: Session = Depends(get_db)
):
    """
    Busca um personagem pelo ID
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Personagem não encontrado",
                "field": "character_id",
                "code": "not_found"
            }
        )
    
    return {
        "success": True,
        "message": "Personagem encontrado",
        "character": character.to_dict()
    }


# ==========================================
# ENDPOINT: ATUALIZAR PERSONAGEM
# ==========================================

@router.put(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Atualiza personagem",
    description="Atualiza os dados de um personagem existente"
)
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de um personagem com validação de duplicidade
    """
    # Buscar personagem
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Personagem não encontrado",
                "field": "character_id",
                "code": "not_found"
            }
        )
    
    try:
        # Verificar alteração de nome
        if character_data.name and character_data.name != character.name:
            # Sanitizar nome
            character_data.name = sanitize_name(character_data.name)
            
            # Verificar duplicidade
            name_exists = await check_character_name_duplicate(
                character_data.name, 
                db, 
                exclude_id=character_id
            )
            
            if name_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Personagem com este nome já existe",
                        "field": "name",
                        "code": "duplicate_name"
                    }
                )
        
        # Verificar alteração de classe ou raça
        if ((character_data.character_class and character_data.character_class != character.character_class) or
            (character_data.race and character_data.race != character.race)):
            
            new_class = character_data.character_class or character.character_class
            new_race = character_data.race or character.race
            
            # Verificar duplicidade de classe + raça
            if settings.ENABLE_CLASS_RACE_VALIDATION:
                class_race_exists = await check_class_race_duplicate(
                    character.player_id,
                    new_class,
                    new_race,
                    db,
                    exclude_id=character_id
                )
                
                if class_race_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "error": f"Você já possui um personagem {new_race} {new_class}",
                            "field": "character_class",
                            "code": "duplicate_class_race"
                        }
                    )
        
        # Atualizar campos
        update_data = character_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(character, key, value)
        
        # Salvar alterações
        db.commit()
        db.refresh(character)
        
        logger.info(f"Personagem atualizado: {character.name} (ID: {character.id})")
        
        return {
            "success": True,
            "message": "Personagem atualizado com sucesso",
            "character": character.to_dict()
        }
        
    except HTTPException:
        # Repassar exceções HTTP
        raise
        
    except IntegrityError as e:
        # Tratar violações de constraints SQL
        db.rollback()
        error_message = str(e)
        
        if "uq_player_class_race" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Você já possui um personagem desta classe e raça",
                    "field": "character_class",
                    "code": "duplicate_class_race"
                }
            )
        
        if "ix_character_name_lower" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Personagem com este nome já existe",
                    "field": "name",
                    "code": "duplicate_name"
                }
            )
        
        # Erro genérico de integridade
        logger.error(f"Erro de integridade: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Erro de validação de dados",
                "field": "unknown",
                "code": "integrity_error"
            }
        )
        
    except Exception as e:
        # Erros gerais
        db.rollback()
        logger.error(f"Erro ao atualizar personagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro ao atualizar personagem",
                "message": str(e),
                "code": "internal_error"
            }
        )


# ==========================================
# ENDPOINT: DELETAR PERSONAGEM
# ==========================================

@router.delete(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Deleta personagem",
    description="Deleta ou inativa um personagem existente"
)
async def delete_character(
    character_id: int,
    soft_delete: bool = Query(True, description="Exclusão lógica (inativação) em vez de física"),
    db: Session = Depends(get_db)
):
    """
    Deleta ou inativa um personagem
    """
    # Buscar personagem
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Personagem não encontrado",
                "field": "character_id",
                "code": "not_found"
            }
        )
    
    try:
        if soft_delete:
            # Exclusão lógica (apenas inativa)
            character.is_active = False
            db.commit()
            
            logger.info(f"Personagem inativado: {character.name} (ID: {character.id})")
            
            return {
                "success": True,
                "message": "Personagem inativado com sucesso",
                "character": character.to_dict()
            }
        else:
            # Exclusão física (remove do banco)
            player_id = character.player_id
            char_name = character.name
            char_id = character.id
            
            # Remover personagem
            db.delete(character)
            
            # Atualizar contador de personagens do jogador
            player_count = db.query(PlayerCharacterCount).filter(
                PlayerCharacterCount.player_id == player_id
            ).first()
            
            if player_count and player_count.character_count > 0:
                player_count.character_count -= 1
                
            # Salvar alterações
            db.commit()
            
            logger.info(f"Personagem deletado: {char_name} (ID: {char_id})")
            
            return {
                "success": True,
                "message": "Personagem deletado permanentemente",
                "character": None
            }
            
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar personagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro ao deletar personagem",
                "message": str(e),
                "code": "internal_error"
            }
        )