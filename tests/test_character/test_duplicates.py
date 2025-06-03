"""
Testes para validação de duplicidade de personagens
Implementa testes para as recomendações críticas
"""

import pytest
from fastapi import status
from sqlalchemy import func

from app.models.character import Character


# ==========================================
# TESTES DE VERIFICAÇÃO DE DUPLICIDADE
# ==========================================

@pytest.mark.unit
def test_check_duplicate_endpoint(client, create_test_character):
    """
    Testa o endpoint de verificação de duplicidade de nome
    Validação prévia de nomes para melhorar UX
    """
    # Criar personagem no banco
    create_test_character(name="Gandalf")
    
    # Verificar nome já existente
    response = client.get("/api/character/check_duplicate/Gandalf")
    assert response.status_code == 200
    data = response.json()
    assert data["is_duplicate"] is True
    assert data["name"] == "Gandalf"
    assert len(data["suggestions"]) > 0
    
    # Verificar nome com capitalização diferente (case-insensitive)
    response = client.get("/api/character/check_duplicate/gandalf")
    assert response.status_code == 200
    data = response.json()
    assert data["is_duplicate"] is True
    assert data["name"] == "gandalf"
    assert len(data["suggestions"]) > 0
    
    # Verificar nome com espaços extras
    response = client.get("/api/character/check_duplicate/ Gandalf ")
    assert response.status_code == 200
    data = response.json()
    assert data["is_duplicate"] is True
    
    # Verificar nome disponível
    response = client.get("/api/character/check_duplicate/Frodo")
    assert response.status_code == 200
    data = response.json()
    assert data["is_duplicate"] is False
    assert data["name"] == "Frodo"
    assert len(data["suggestions"]) == 0


# ==========================================
# TESTES DE DUPLICIDADE NA CRIAÇÃO
# ==========================================

@pytest.mark.unit
def test_create_character_duplicate_name(client, sample_character_data, create_test_character):
    """
    Testa a validação de duplicidade de nome na criação de personagem
    Implementa a recomendação crítica de verificação
    """
    # Criar personagem no banco
    create_test_character(name="Gandalf")
    
    # Tentar criar personagem com mesmo nome
    response = client.post(
        "/api/character/create_character",
        json={**sample_character_data, "name": "Gandalf"}
    )
    
    # Verificar resposta
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "duplicate_name" in data["detail"]["code"]
    
    # Verificar case-insensitivity
    response = client.post(
        "/api/character/create_character",
        json={**sample_character_data, "name": "gandalf"}
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    
    # Verificar sanitização de nome
    response = client.post(
        "/api/character/create_character",
        json={**sample_character_data, "name": " Gandalf "}
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.unit
def test_create_character_duplicate_class_race(client, sample_character_data, create_test_character):
    """
    Testa a validação de duplicidade de classe+raça na criação de personagem
    """
    # Criar personagem Humano Mago
    create_test_character(
        name="Gandalf", 
        player_id="5511999999999",
        race="Humano",
        character_class="Mago"
    )
    
    # Tentar criar outro Humano Mago para o mesmo jogador
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Saruman",  # Nome diferente
            "player_id": "5511999999999",
            "race": "Humano",
            "character_class": "Mago"
        }
    )
    
    # Verificar resposta
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "duplicate_class_race" in data["detail"]["code"]
    
    # Permitir mesma classe mas raça diferente
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Radagast",
            "player_id": "5511999999999",
            "race": "Elfo",  # Raça diferente
            "character_class": "Mago"  # Mesma classe
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Permitir mesma raça mas classe diferente
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Boromir",
            "player_id": "5511999999999",
            "race": "Humano",  # Mesma raça
            "character_class": "Guerreiro"  # Classe diferente
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED


# ==========================================
# TESTES DE LIMITE DE PERSONAGENS
# ==========================================

@pytest.mark.unit
def test_character_limit_validation(client, sample_character_data, create_test_character, create_test_player_count):
    """
    Testa o limite de personagens por jogador
    """
    # Configurar contador de personagens (2 de 3 slots usados)
    create_test_player_count(
        player_id="5511999999999",
        count=2,
        max_allowed=3
    )
    
    # Criar personagens existentes
    create_test_character(
        name="Gandalf", 
        player_id="5511999999999",
        race="Humano",
        character_class="Mago"
    )
    
    create_test_character(
        name="Aragorn", 
        player_id="5511999999999",
        race="Humano",
        character_class="Patrulheiro"
    )
    
    # Tentar criar um personagem válido (3º slot)
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Legolas",
            "player_id": "5511999999999",
            "race": "Elfo",
            "character_class": "Patrulheiro"
        }
    )
    
    # Deve ser permitido (dentro do limite)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Tentar criar um 4º personagem (excedendo limite)
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Gimli",
            "player_id": "5511999999999",
            "race": "Anão",
            "character_class": "Guerreiro"
        }
    )
    
    # Deve ser rejeitado por limite excedido
    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert "character_limit" in data["detail"]["code"]


# ==========================================
# TESTES DE DUPLICIDADE NA ATUALIZAÇÃO
# ==========================================

@pytest.mark.unit
def test_update_character_duplicate_validation(client, create_test_character):
    """
    Testa a validação de duplicidade na atualização de personagem
    """
    # Criar dois personagens
    char1 = create_test_character(
        name="Gandalf", 
        player_id="5511999999999",
        race="Humano",
        character_class="Mago"
    )
    
    char2 = create_test_character(
        name="Aragorn", 
        player_id="5511999999999",
        race="Humano",
        character_class="Patrulheiro"
    )
    
    # Tentar renomear char2 para o nome de char1
    response = client.put(
        f"/api/character/{char2.id}",
        json={"name": "Gandalf"}
    )
    
    # Deve ser rejeitado (nome duplicado)
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "duplicate_name" in data["detail"]["code"]
    
    # Tentar alterar classe e raça para combinação existente
    response = client.put(
        f"/api/character/{char2.id}",
        json={
            "character_class": "Mago",
            "race": "Humano"
        }
    )
    
    # Deve ser rejeitado (combinação classe+raça duplicada)
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "duplicate_class_race" in data["detail"]["code"]
    
    # Atualização válida (sem duplicidade)
    response = client.put(
        f"/api/character/{char2.id}",
        json={
            "name": "Aragorn Strider",
            "character_class": "Patrulheiro",
            "strength": 18
        }
    )
    
    # Deve ser permitido
    assert response.status_code == status.HTTP_200_OK


# ==========================================
# TESTES DE PERSISTÊNCIA E INTEGRIDADE
# ==========================================

@pytest.mark.unit
def test_character_persistence_with_duplicates(db_session, create_test_character):
    """
    Testa a persistência correta de personagens com constraints de duplicidade
    """
    # Criar personagem
    char1 = create_test_character(
        name="Gandalf", 
        player_id="5511999999999",
        race="Humano",
        character_class="Mago"
    )
    
    # Verificar se foi criado corretamente
    assert char1.id is not None
    assert char1.name == "Gandalf"
    
    # Tentar criar personagem com mesmo nome diretamente no banco (bypassing API)
    char2 = Character(
        name="Gandalf",  # Nome duplicado
        player_id="5522888888888",  # Jogador diferente
        race="Elfo",
        character_class="Mago",
        max_hit_points=10,
        current_hit_points=10,
        armor_class=12
    )
    
    db_session.add(char2)
    
    # Deve lançar exceção ao tentar commit (constraint violation)
    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    
    # Verificar que constraint impediu
    assert "ix_character_name_lower" in str(excinfo.value) or "UNIQUE constraint failed" in str(excinfo.value)
    
    # Rollback para limpar sessão
    db_session.rollback()


@pytest.mark.integration
def test_character_player_count_update(client, sample_character_data, db_session):
    """
    Testa a atualização automática da contagem de personagens
    """
    # Verificar que não existe contador inicial
    player_count = db_session.query(PlayerCharacterCount).filter_by(
        player_id="5511999999999"
    ).first()
    
    assert player_count is None
    
    # Criar primeiro personagem
    response = client.post(
        "/api/character/create_character",
        json=sample_character_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verificar que contador foi criado
    player_count = db_session.query(PlayerCharacterCount).filter_by(
        player_id="5511999999999"
    ).first()
    
    assert player_count is not None
    assert player_count.character_count == 1
    assert player_count.max_allowed == 3
    
    # Criar segundo personagem
    response = client.post(
        "/api/character/create_character",
        json={
            **sample_character_data,
            "name": "Aragorn",
            "character_class": "Patrulheiro",
            "race": "Humano"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verificar que contador foi atualizado
    db_session.refresh(player_count)
    assert player_count.character_count == 2
    
    # Excluir um personagem
    characters = db_session.query(Character).filter_by(
        player_id="5511999999999"
    ).all()
    
    assert len(characters) == 2
    
    response = client.delete(f"/api/character/{characters[0].id}?soft_delete=false")
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar que contador foi decrementado
    db_session.refresh(player_count)
    assert player_count.character_count == 1