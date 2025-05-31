"""
Game Manager - Gerenciador central do jogo RPG
Coordena sessões, personagens, IA e estado do mundo
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .database import get_redis, cache_set, cache_get, cache_delete
from .config import settings
from ..ai.ai_coordinator import AICoordinator
from ..rpg.character_manager import CharacterManager
from ..rpg.dice_system import DiceSystem
from ..hitl.hitl_manager import HITLManager
from ..whatsapp.message_handler import MessageHandler

logger = logging.getLogger(__name__)

class SessionState(Enum):
    """Estados possíveis de uma sessão"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    WAITING_GM = "waiting_gm"

@dataclass
class GameSession:
    """Representação de uma sessão de jogo"""
    id: str
    chat_id: str
    gm_phone: Optional[str]
    players: List[str]
    state: SessionState
    current_scene: str
    world_state: Dict[str, Any]
    combat_state: Optional[Dict[str, Any]]
    created_at: datetime
    last_activity: datetime
    settings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            **asdict(self),
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Criar instância a partir de dicionário"""
        data['state'] = SessionState(data['state'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

class GameManager:
    """Gerenciador central do jogo"""

    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.ai_coordinator = AICoordinator()
        self.character_manager = CharacterManager()
        self.dice_system = DiceSystem()
        self.hitl_manager = HITLManager()
        self.message_handler = MessageHandler()

        # Estatísticas
        self.stats = {
            'total_messages': 0,
            'active_sessions': 0,
            'total_characters': 0,
            'dice_rolls': 0,
            'hitl_triggers': 0
        }

        logger.info("🎮 Game Manager inicializado")

    async def process_webhook_message(self, webhook_data: Dict[str, Any]):
        """Processar mensagem recebida via webhook"""
        try:
            # Extrair dados da mensagem
            message_data = self._extract_message_data(webhook_data)
            if not message_data:
                return

            chat_id = message_data['chat_id']
            user_phone = message_data['user_phone']
            message_text = message_data['message_text']
            message_type = message_data.get('message_type', 'text')

            # Atualizar estatísticas
            self.stats['total_messages'] += 1

            # Obter ou criar sessão
            session = await self.get_or_create_session(chat_id)

            # Atualizar atividade da sessão
            await self._update_session_activity(session)

            # Processar comando ou mensagem
            if message_text.startswith('/'):
                await self._process_command(session, user_phone, message_text)
            else:
                await self._process_roleplay_message(session, user_phone, message_text)

            logger.info(f"Mensagem processada: {chat_id} - {user_phone}")

        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            await self.hitl_manager.notify_error(f"Erro no processamento: {e}")

    def _extract_message_data(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrair dados relevantes do webhook"""
        try:
            # Adaptar para diferentes formatos de webhook da Evolution API
            if 'data' in webhook_data:
                data = webhook_data['data']

                return {
                    'chat_id': data.get('key', {}).get('remoteJid'),
                    'user_phone': data.get('key', {}).get('participant', data.get('key', {}).get('remoteJid')),
                    'message_text': data.get('message', {}).get('conversation', ''),
                    'message_type': 'text',
                    'timestamp': data.get('messageTimestamp')
                }

            return None

        except Exception as e:
            logger.error(f"Erro ao extrair dados da mensagem: {e}")
            return None

    async def get_or_create_session(self, chat_id: str) -> GameSession:
        """Obter sessão existente ou criar nova"""
        session_key = f"session:{chat_id}"

        # Tentar obter do cache
        session_data = await cache_get(session_key)
        if session_data:
            session_dict = json.loads(session_data)
            session = GameSession.from_dict(session_dict)
            self.sessions[chat_id] = session
            return session

        # Criar nova sessão
        session = GameSession(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            gm_phone=None,
            players=[],
            state=SessionState.INACTIVE,
            current_scene="Início da aventura",
            world_state={
                'location': 'Taverna do Dragão Dourado',
                'time_of_day': 'tarde',
                'weather': 'ensolarado',
                'npcs_present': ['Bartender Thorek', 'Viajante Misterioso']
            },
            combat_state=None,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            settings={
                'difficulty': 'normal',
                'auto_roll': False,
                'detailed_descriptions': True,
                'language': 'pt-BR'
            }
        )

        # Salvar no cache
        await self._save_session(session)
        self.sessions[chat_id] = session
        self.stats['active_sessions'] += 1

        logger.info(f"Nova sessão criada: {chat_id}")
        return session

    async def _save_session(self, session: GameSession):
        """Salvar sessão no cache"""
        session_key = f"session:{session.chat_id}"
        session_data = json.dumps(session.to_dict(), default=str)
        await cache_set(session_key, session_data, expire=86400)  # 24 horas

    async def _update_session_activity(self, session: GameSession):
        """Atualizar última atividade da sessão"""
        session.last_activity = datetime.now()
        await self._save_session(session)

    async def _process_command(self, session: GameSession, user_phone: str, command: str):
        """Processar comando do usuário"""
        command_parts = command.split()
        base_command = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []

        try:
            if base_command == '/start':
                await self._handle_start_command(session, user_phone)

            elif base_command == '/criar-personagem':
                await self._handle_create_character(session, user_phone, args)

            elif base_command == '/status':
                await self._handle_status_command(session, user_phone)

            elif base_command == '/inventario':
                await self._handle_inventory_command(session, user_phone)

            elif base_command == '/rolar':
                await self._handle_dice_roll(session, user_phone, args)

            elif base_command == '/ataque':
                await self._handle_attack_command(session, user_phone, args)

            elif base_command == '/magia':
                await self._handle_spell_command(session, user_phone, args)

            elif base_command == '/descanso':
                await self._handle_rest_command(session, user_phone, args)

            elif base_command == '/gm' and self._is_gm(session, user_phone):
                await self._handle_gm_command(session, user_phone, args)

            elif base_command == '/help':
                await self._handle_help_command(session, user_phone)

            else:
                await self._send_message(session.chat_id, 
                    f"Comando não reconhecido: {base_command}
"
                    "Digite /help para ver os comandos disponíveis.")

        except Exception as e:
            logger.error(f"Erro ao processar comando {command}: {e}")
            await self._send_message(session.chat_id, 
                "Erro ao processar comando. Tente novamente.")

    async def _handle_start_command(self, session: GameSession, user_phone: str):
        """Processar comando /start"""
        if user_phone not in session.players:
            session.players.append(user_phone)
            await self._save_session(session)

        welcome_message = f"""
🎲 **Bem-vindo ao WhatsApp RPG GM!**

Você entrou na sessão de D&D 5e. Aqui estão os comandos básicos:

**Personagem:**
• /criar-personagem - Criar novo personagem
• /status - Ver status do personagem
• /inventario - Ver inventário

**Jogo:**
• /rolar [dados] - Rolar dados (ex: /rolar 1d20+5)
• /ataque [alvo] - Atacar um inimigo
• /magia [nome] - Lançar magia
• /descanso [curto|longo] - Descansar

**Ajuda:**
• /help - Lista completa de comandos

Para começar a jogar, primeiro crie seu personagem com /criar-personagem
"""

        await self._send_message(session.chat_id, welcome_message)

        if session.state == SessionState.INACTIVE:
            session.state = SessionState.ACTIVE
            await self._save_session(session)

            # Gerar introdução com IA
            intro_prompt = f"""
            Você é um Mestre de Jogo experiente de D&D 5e. Um novo jogador acabou de entrar na sessão.
            Crie uma introdução envolvente para a aventura que está começando.

            Cenário atual: {session.current_scene}
            Localização: {session.world_state.get('location', 'Local desconhecido')}

            Seja criativo e estabeleça o tom da aventura.
            """

            intro_text = await self.ai_coordinator.generate_response(
                prompt=intro_prompt,
                context={'session': session.to_dict()}
            )

            await self._send_message(session.chat_id, f"🎭 **Narrador:** {intro_text}")

    async def _handle_create_character(self, session: GameSession, user_phone: str, args: List[str]):
        """Processar criação de personagem"""
        # Verificar se já tem personagem
        existing_char = await self.character_manager.get_character(user_phone, session.chat_id)
        if existing_char:
            await self._send_message(session.chat_id, 
                "Você já possui um personagem nesta sessão. Use /status para ver detalhes.")
            return

        # Criar personagem com IA ou manual
        if args and args[0].lower() == 'auto':
            character = await self.character_manager.create_random_character(user_phone, session.chat_id)
            char_intro = f"""
🎭 **Personagem criado automaticamente!**

**{character.name}** - {character.race} {character.character_class}
• HP: {character.hp_current}/{character.hp_max}
• CA: {character.armor_class}
• Atributos: FOR {character.strength}, DES {character.dexterity}, CON {character.constitution}, INT {character.intelligence}, SAB {character.wisdom}, CAR {character.charisma}

Use /status para ver detalhes completos.
"""
            await self._send_message(session.chat_id, char_intro)
        else:
            # Iniciar processo interativo de criação
            creation_message = """
🎭 **Criação de Personagem**

Vou te ajudar a criar seu personagem! Escolha uma opção:

1️⃣ Criação automática (rápida)
2️⃣ Criação assistida (com escolhas)
3️⃣ Criação manual (completa)

Responda com o número da opção desejada.
"""
            await self._send_message(session.chat_id, creation_message)

            # Definir estado de criação de personagem
            session.world_state['awaiting_character_creation'] = user_phone
            await self._save_session(session)

    async def _handle_dice_roll(self, session: GameSession, user_phone: str, args: List[str]):
        """Processar rolagem de dados"""
        if not args:
            await self._send_message(session.chat_id, 
                "Uso: /rolar [expressão]
Exemplo: /rolar 1d20+5")
            return

        expression = ' '.join(args)

        try:
            result = self.dice_system.roll(expression)
            self.stats['dice_rolls'] += 1

            # Obter personagem para modifiers
            character = await self.character_manager.get_character(user_phone, session.chat_id)
            char_name = character.name if character else "Jogador"

            roll_message = f"""
🎲 **{char_name}** rolou **{expression}**

**Resultado:** {result.total}
**Dados:** {result.rolls}
{'**CRÍTICO!** 🎯' if result.is_critical else ''}
{'**FALHA CRÍTICA!** 💀' if result.is_fumble else ''}
"""

            await self._send_message(session.chat_id, roll_message)

            # Log da rolagem
            logger.info(f"Rolagem: {user_phone} - {expression} = {result.total}")

        except Exception as e:
            await self._send_message(session.chat_id, 
                f"Erro na rolagem: {str(e)}
Exemplo válido: 1d20+5")

    async def _process_roleplay_message(self, session: GameSession, user_phone: str, message: str):
        """Processar mensagem de roleplay"""
        try:
            # Obter personagem
            character = await self.character_manager.get_character(user_phone, session.chat_id)
            if not character:
                await self._send_message(session.chat_id, 
                    "Você precisa criar um personagem primeiro! Use /criar-personagem")
                return

            # Verificar se precisa de intervenção humana
            needs_hitl = await self.hitl_manager.should_trigger_hitl(message, session.to_dict())
            if needs_hitl:
                await self.hitl_manager.request_intervention(session, user_phone, message)
                await self._send_message(session.chat_id, 
                    "Situação complexa detectada. Aguardando intervenção do Mestre...")
                return

            # Gerar resposta com IA
            ai_prompt = f"""
            Você é um Mestre de Jogo experiente de D&D 5e. Um jogador acabou de realizar uma ação.

            **Personagem:** {character.name} ({character.race} {character.character_class})
            **Ação do jogador:** {message}
            **Localização atual:** {session.world_state.get('location')}
            **Cena atual:** {session.current_scene}
            **Estado da sessão:** {session.state.value}

            Responda como um GM experiente, sendo descritivo e envolvente.
            Se a ação requer testes, sugira as rolagens necessárias.
            """

            gm_response = await self.ai_coordinator.generate_response(
                prompt=ai_prompt,
                context={
                    'session': session.to_dict(),
                    'character': character.to_dict() if hasattr(character, 'to_dict') else str(character),
                    'message': message
                }
            )

            await self._send_message(session.chat_id, f"🎭 **GM:** {gm_response}")

        except Exception as e:
            logger.error(f"Erro ao processar roleplay: {e}")
            await self._send_message(session.chat_id, 
                "Erro ao processar ação. Tente reformular ou use um comando específico.")

    async def _send_message(self, chat_id: str, message: str):
        """Enviar mensagem via WhatsApp"""
        try:
            await self.message_handler.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")

    def _is_gm(self, session: GameSession, user_phone: str) -> bool:
        """Verificar se usuário é GM da sessão"""
        return session.gm_phone == user_phone

    async def get_session_stats(self) -> Dict[str, Any]:
        """Obter estatísticas das sessões"""
        active_sessions = len([s for s in self.sessions.values() if s.state == SessionState.ACTIVE])

        return {
            **self.stats,
            'active_sessions': active_sessions,
            'total_sessions': len(self.sessions),
            'sessions_by_state': {
                state.value: len([s for s in self.sessions.values() if s.state == state])
                for state in SessionState
            }
        }

    async def cleanup_inactive_sessions(self):
        """Limpar sessões inativas"""
        cutoff_time = datetime.now() - timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)

        inactive_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]

        for session_id in inactive_sessions:
            await cache_delete(f"session:{session_id}")
            del self.sessions[session_id]
            logger.info(f"Sessão inativa removida: {session_id}")

        return len(inactive_sessions)
