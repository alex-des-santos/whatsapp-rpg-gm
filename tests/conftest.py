"""
Configurações de testes compartilhadas para WhatsApp RPG GM
Implementa fixtures e mocks para testes automatizados
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import Mock, patch, AsyncMock

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import fakeredis

# Importações da aplicação
from app.main import app
from app.core.config import Settings
from app.core.database import get_db, Base
from app.models.character import Character, PlayerCharacterCount
from app.services.whatsapp_service import WhatsAppService
from app.services.ai_service import AIService


# ==========================================
# CONFIGURAÇÕES DE TESTE
# ==========================================

# Configurações específicas para teste
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/15"  # DB 15 para testes


class TestSettings(Settings):
    """Configurações específicas para testes"""
    
    # Override de configurações críticas
    ENVIRONMENT: str = "test"
    DEBUG: bool = True
    
    # Database de teste
    DATABASE_URL: str = TEST_DATABASE_URL
    
    # Redis de teste
    REDIS_URL: str = TEST_REDIS_URL
    
    # Chaves de teste (valores seguros para CI/CD)
    VERIFY_TOKEN: str = "test_verify_token_123456"
    SECRET_KEY: str = "test_secret_key_for_testing_purposes_very_long_key_12345"
    
    # Evolution API de teste
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str = "test_evolution_key"
    INSTANCE_NAME: str = "test_instance"
    
    # IA de teste
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = "sk-test_openai_key_for_testing"
    
    # Configurações de teste
    MAX_CHARACTERS_PER_PLAYER: int = 3
    ENABLE_CLASS_RACE_VALIDATION: bool = True
    
    def validate_critical_settings(self) -> None:
        """Override para pular validação crítica em testes"""
        pass


# ==========================================
# FIXTURES DE CONFIGURAÇÃO
# ==========================================

@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para toda a sessão de testes"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Fixture para configurações de teste"""
    return TestSettings()


# ==========================================
# FIXTURES DE BANCO DE DADOS
# ==========================================

@pytest.fixture(scope="session")
def test_engine():
    """Cria engine do banco de dados para testes"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    
    # Remover arquivo de teste se existir
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Cria uma sessão de banco de dados isolada para cada teste
    """
    # Criar nova sessão
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    # Usar transação para rollback após teste
    transaction = session.begin()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override do dependency get_db para usar session de teste"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    return _override_get_db


# ==========================================
# FIXTURES DE APLICAÇÃO
# ==========================================

@pytest.fixture(scope="function")
def test_app(override_get_db) -> FastAPI:
    """
    Cria uma instância da aplicação para testes
    """
    # Override de dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    yield app
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_app) -> TestClient:
    """Cliente de teste para FastAPI"""
    return TestClient(test_app)


@pytest.fixture(scope="function")
async def async_client(test_app) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Cliente assíncrono para testes"""
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


# ==========================================
# FIXTURES DE MOCKS
# ==========================================

@pytest.fixture(scope="function")
def mock_redis():
    """Mock do Redis usando fakeredis"""
    fake_redis = fakeredis.FakeRedis()
    
    with patch('app.core.redis.redis_client', fake_redis):
        yield fake_redis


@pytest.fixture(scope="function")
def mock_whatsapp_service():
    """Mock do serviço WhatsApp"""
    mock_service = Mock(spec=WhatsAppService)
    
    # Configurar métodos mock
    mock_service.send_message = AsyncMock(return_value={
        "success": True,
        "message_id": "test_message_123",
        "status": "sent"
    })
    
    mock_service.send_interactive_message = AsyncMock(return_value={
        "success": True,
        "message_id": "test_interactive_123",
        "status": "sent"
    })
    
    mock_service.get_profile = AsyncMock(return_value={
        "name": "Test User",
        "phone": "5511999999999",
        "photo": None
    })
    
    mock_service.is_connected = AsyncMock(return_value=True)
    
    return mock_service


@pytest.fixture(scope="function")
def mock_ai_service():
    """Mock do serviço de IA"""
    mock_service = Mock(spec=AIService)
    
    # Respostas mock para diferentes tipos de prompt
    mock_service.generate_response = AsyncMock(return_value={
        "response": "Esta é uma resposta mock do Game Master",
        "usage": {"tokens": 50},
        "model": "gpt-3.5-turbo"
    })
    
    mock_service.generate_character_backstory = AsyncMock(return_value={
        "backstory": "Um herói corajoso com passado misterioso...",
        "personality_traits": "Corajoso e leal",
        "ideals": "Proteger os inocentes",
        "bonds": "Família perdida",
        "flaws": "Muito confiante"
    })
    
    mock_service.roll_dice = AsyncMock(return_value={
        "roll": "1d20+5",
        "result": 15,
        "details": [10],
        "modifier": 5,
        "description": "Teste de Atletismo"
    })
    
    return mock_service


@pytest.fixture(scope="function")
def mock_evolution_api():
    """Mock para requests à Evolution API"""
    with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_client:
        # Mock de resposta bem-sucedida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "messageId": "test_msg_123",
                "status": "sent"
            }
        }
        
        # Configurar o client mock
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        yield mock_client


@pytest.fixture(scope="function")
def mock_openai_api():
    """Mock para chamadas à OpenAI API"""
    with patch('app.services.ai_service.openai.ChatCompletion.acreate') as mock_create:
        mock_create.return_value = {
            "choices": [{
                "message": {
                    "content": "Esta é uma resposta mock da OpenAI"
                }
            }],
            "usage": {
                "total_tokens": 50,
                "prompt_tokens": 30,
                "completion_tokens": 20
            }
        }
        
        yield mock_create


# ==========================================
# FIXTURES DE DADOS DE TESTE
# ==========================================

@pytest.fixture
def sample_character_data():
    """Dados de exemplo para criação de personagem"""
    return {
        "name": "Gandalf",
        "player_id": "5511999999999",
        "race": "Humano",
        "character_class": "Mago",
        "level": 1,
        "alignment": "Neutro e Bom",
        "background": "Eremita",
        "strength": 8,
        "dexterity": 14,
        "constitution": 12,
        "intelligence": 18,
        "wisdom": 16,
        "charisma": 10,
        "max_hit_points": 7,
        "current_hit_points": 7,
        "armor_class": 12,
        "experience_points": 0,
        "skills": {
            "arcana": True,
            "history": True,
            "investigation": True,
            "religion": True
        },
        "equipment": [
            {"name": "Adaga", "quantity": 1, "type": "weapon"},
            {"name": "Grimório", "quantity": 1, "type": "spellbook"},
            {"name": "Roupas de Viajante", "quantity": 1, "type": "clothing"}
        ],
        "spells": {
            "cantrips": ["Luzes Dançantes", "Mãos Mágicas", "Prestidigitação"],
            "level_1": ["Mísseis Mágicos", "Escudo"]
        }
    }


@pytest.fixture
def sample_characters_batch():
    """Conjunto de personagens para testes em lote"""
    return [
        {
            "name": "Aragorn",
            "player_id": "5511999999999",
            "race": "Humano",
            "character_class": "Patrulheiro",
            "level": 5
        },
        {
            "name": "Legolas",
            "player_id": "5511999999999",
            "race": "Elfo",
            "character_class": "Patrulheiro",
            "level": 5
        },
        {
            "name": "Gimli",
            "player_id": "5511888888888",
            "race": "Anão",
            "character_class": "Guerreiro",
            "level": 5
        }
    ]


@pytest.fixture
def sample_webhook_message():
    """Mensagem de webhook do WhatsApp para testes"""
    return {
        "instanceId": "test_instance",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "test_message_id_123"
            },
            "messageTimestamp": 1640995200,
            "message": {
                "conversation": "/criar personagem"
            },
            "pushName": "Test User",
            "participant": "5511999999999@s.whatsapp.net"
        }
    }


# ==========================================
# FIXTURES DE HELPERS
# ==========================================

@pytest.fixture
def create_test_character(db_session):
    """Helper para criar personagens de teste"""
    def _create_character(**kwargs):
        default_data = {
            "name": "Test Character",
            "player_id": "5511999999999",
            "race": "Humano",
            "character_class": "Guerreiro",
            "level": 1,
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
            "max_hit_points": 11,
            "current_hit_points": 11,
            "armor_class": 16,
            "experience_points": 0
        }
        
        # Override com kwargs
        default_data.update(kwargs)
        
        # Criar personagem
        character = Character(**default_data)
        db_session.add(character)
        db_session.commit()
        db_session.refresh(character)
        
        return character
    
    return _create_character


@pytest.fixture
def create_test_player_count(db_session):
    """Helper para criar contadores de jogador"""
    def _create_player_count(player_id: str, count: int = 0, max_allowed: int = 3):
        player_count = PlayerCharacterCount(
            player_id=player_id,
            character_count=count,
            max_allowed=max_allowed
        )
        db_session.add(player_count)
        db_session.commit()
        db_session.refresh(player_count)
        
        return player_count
    
    return _create_player_count


# ==========================================
# FIXTURES DE CLEANUP
# ==========================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup automático de arquivos de teste"""
    yield
    
    # Limpar arquivos temporários
    test_files = ["test.db", "test.db-journal"]
    for file in test_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass


# ==========================================
# MARKERS PERSONALIZADOS
# ==========================================

# Marker para testes que precisam de rede
pytest.mark.requires_internet = pytest.mark.skipif(
    os.getenv("SKIP_INTERNET_TESTS", "false").lower() == "true",
    reason="Testes que precisam de internet foram desabilitados"
)

# Marker para testes que precisam de chaves de API
pytest.mark.requires_api_keys = pytest.mark.skipif(
    os.getenv("SKIP_API_TESTS", "false").lower() == "true",
    reason="Testes que precisam de API keys foram desabilitados"
)

# Marker para testes lentos
pytest.mark.slow = pytest.mark.skipif(
    os.getenv("SKIP_SLOW_TESTS", "false").lower() == "true",
    reason="Testes lentos foram desabilitados"
)


# ==========================================
# UTILIDADES DE TESTE
# ==========================================

def assert_character_equal(char1: Character, char2: Character, ignore_fields: list = None):
    """
    Utility para comparar personagens em testes
    """
    ignore_fields = ignore_fields or ["id", "created_at", "updated_at"]
    
    for attr in Character.__table__.columns.keys():
        if attr not in ignore_fields:
            assert getattr(char1, attr) == getattr(char2, attr), f"Field {attr} differs"


def create_mock_response(status_code: int = 200, json_data: dict = None):
    """
    Utility para criar mock responses HTTP
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


# ==========================================
# CONFIGURAÇÕES PYTEST
# ==========================================

# Configurar asyncio para testes
pytest_asyncio.asyncio_mode = "auto"