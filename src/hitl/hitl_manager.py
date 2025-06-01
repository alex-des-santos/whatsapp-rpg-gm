"""
HITL Manager - Human-in-the-Loop
Sistema para detectar situações que requerem intervenção humana
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any # Optional removed
from enum import Enum
import smtplib # Moved import here
from email.mime.text import MIMEText # Added for EmailNotifier
from email.mime.multipart import MIMEMultipart # Added for EmailNotifier

from ..core.config import settings
from ..core.database import cache_set, cache_get

logger = logging.getLogger(__name__)


class HITLTrigger(Enum):
    """Tipos de gatilhos para intervenção humana"""

    COMPLEX_SITUATION = "complex_situation"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    RULES_DISPUTE = "rules_dispute"
    PLAYER_CONFLICT = "player_conflict"
    TECHNICAL_ERROR = "technical_error"
    CUSTOM_REQUEST = "custom_request"
    AI_UNCERTAINTY = "ai_uncertainty"


class HITLManager:
    """Gerenciador Human-in-the-Loop"""

    def __init__(self):
        self.trigger_keywords = self._load_trigger_keywords()
        self.notification_channels = self._initialize_channels()
        self.pending_interventions = {}

        logger.info("HITL Manager inicializado")

    def _load_trigger_keywords(self) -> Dict[HITLTrigger, List[str]]:
        """Carregar palavras-chave que disparam intervenção"""
        return {
            HITLTrigger.INAPPROPRIATE_CONTENT: [
                "inadequado",
                "ofensivo",
                "impróprio",
                "inapropriado",
                "violento",
                "sexual",
                "discriminação",
                "preconceito",
            ],
            HITLTrigger.RULES_DISPUTE: [
                "regra",
                "não funciona assim",
                "está errado",
                "disputo",
                "discordo",
                "regras oficiais",
                "manual",
                "errata",
            ],
            HITLTrigger.PLAYER_CONFLICT: [
                "não gostei",
                "injusto",
                "favorecimento",
                "parcial",
                "trapaça",
                "batota",
                "conflito",
                "discussão",
            ],
            HITLTrigger.COMPLEX_SITUATION: [
                "não entendo",
                "complicado",
                "confuso",
                "ajuda",
                "gm humano",
                "mestre real",
                "intervenção",
            ],
            HITLTrigger.CUSTOM_REQUEST: [
                "gm",
                "mestre",
                "admin",
                "moderador",
                "suporte",
            ],
        }

    def _initialize_channels(self) -> Dict[str, Any]:
        """Inicializar canais de notificação"""
        channels = {}

        # Discord
        if settings.DISCORD_WEBHOOK_URL:
            channels["discord"] = DiscordNotifier(settings.DISCORD_WEBHOOK_URL)

        # Email
        if all([settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
            channels["email"] = EmailNotifier(
                host=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                from_email=settings.SMTP_FROM_EMAIL,
            )

        # SMS via Twilio
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
            channels["sms"] = SMSNotifier(
                account_sid=settings.TWILIO_ACCOUNT_SID,
                auth_token=settings.TWILIO_AUTH_TOKEN,
                from_number=settings.TWILIO_PHONE_NUMBER,
                to_number=settings.GM_PHONE_NUMBER,
            )

        return channels

    async def should_trigger_hitl(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Verificar se uma situação requer intervenção humana

        Args:
            message: Mensagem do jogador
            context: Contexto da sessão

        Returns:
            bool: True se requer intervenção
        """
        message_lower = message.lower()

        # Verificar palavras-chave
        for trigger_type, keywords in self.trigger_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    logger.info(
                        f"HITL trigger detectado: {trigger_type.value} - palavra: {keyword}"
                    )
                    return True

        # Verificar complexidade da situação
        if self._is_complex_situation(message, context):
            logger.info("HITL trigger: situação complexa detectada")
            return True

        # Verificar se IA está incerta
        if self._ai_seems_uncertain(context):
            logger.info("HITL trigger: IA incerta")
            return True

        return False

    def _is_complex_situation(self, message: str, context: Dict[str, Any]) -> bool:
        """Detectar se a situação é muito complexa para IA"""
        complexity_indicators = [
            len(message.split()) > 50,  # Mensagem muito longa
            message.count("?") > 2,  # Muitas perguntas
            "multi" in message.lower(),  # Ações múltiplas
            "simultâneo" in message.lower(),
            "ao mesmo tempo" in message.lower(),
        ]

        return sum(complexity_indicators) >= 2

    def _ai_seems_uncertain(self, context: Dict[str, Any]) -> bool:
        """Verificar se IA demonstra incerteza"""
        # Implementar lógica para detectar incerteza da IA
        # Por enquanto, retorna False
        return False

    async def request_intervention(
        self,
        session: Dict[str, Any],
        player_id: str,
        message: str,
        trigger_type: HITLTrigger = HITLTrigger.CUSTOM_REQUEST,
    ) -> str:
        """
        Solicitar intervenção humana

        Args:
            session: Dados da sessão
            player_id: ID do jogador
            message: Mensagem que gerou a solicitação
            trigger_type: Tipo de gatilho

        Returns:
            str: ID da intervenção criada
        """
        intervention_id = (
            f"hitl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{player_id[:8]}"
        )

        intervention_data = {
            "id": intervention_id,
            "session_id": session["id"],
            "player_id": player_id,
            "message": message,
            "trigger_type": trigger_type.value,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "context": {
                "current_scene": session.get("current_scene"),
                "location": session.get("world_state", {}).get("location"),
                "session_state": session.get("state"),
                "players_count": len(session.get("players", [])),
            },
        }

        # Salvar no cache
        await cache_set(
            f"hitl_intervention:{intervention_id}",
            json.dumps(intervention_data),
            expire=86400,
        )

        self.pending_interventions[intervention_id] = intervention_data

        # Enviar notificações
        await self._send_notifications(intervention_data)

        logger.info(f"Intervenção HITL criada: {intervention_id}")
        return intervention_id

    async def _send_notifications(self, intervention: Dict[str, Any]):
        """Enviar notificações para todos os canais configurados"""
        notification_text = self._format_notification(intervention)

        for channel_name, notifier in self.notification_channels.items():
            try:
                await notifier.send(notification_text)
                logger.info(f"Notificação HITL enviada via {channel_name}")
            except Exception as e:
                logger.error(f"Erro ao enviar notificação via {channel_name}: {e}")

    def _format_notification(self, intervention: Dict[str, Any]) -> str:
        """Formatar texto da notificação"""
        return f"""
🚨 **INTERVENÇÃO HITL NECESSÁRIA**

**ID:** {intervention['id']}
**Tipo:** {intervention['trigger_type']}
**Sessão:** {intervention['session_id'][:8]}...
**Jogador:** {intervention['player_id']}
**Horário:** {intervention['timestamp']}

**Contexto:**
- Cena: {intervention['context']['current_scene']}
- Local: {intervention['context']['location']}
- Estado: {intervention['context']['session_state']}

**Mensagem do Jogador:**
{intervention['message']}

Para responder, acesse o dashboard de GM.
"""

    async def resolve_intervention(
        self, intervention_id: str, gm_response: str, gm_id: str
    ) -> bool:
        """
        Resolver intervenção com resposta do GM

        Args:
            intervention_id: ID da intervenção
            gm_response: Resposta do GM humano
            gm_id: ID do GM que respondeu

        Returns:
            bool: True se resolvido com sucesso
        """
        try:
            intervention_key = f"hitl_intervention:{intervention_id}"
            intervention_data = await cache_get(intervention_key)

            if not intervention_data:
                logger.error(f"Intervenção não encontrada: {intervention_id}")
                return False

            intervention = json.loads(intervention_data)
            intervention["status"] = "resolved"
            intervention["gm_response"] = gm_response
            intervention["gm_id"] = gm_id
            intervention["resolved_at"] = datetime.now().isoformat()

            # Atualizar no cache
            await cache_set(intervention_key, json.dumps(intervention), expire=86400)

            # Remover dos pendentes
            if intervention_id in self.pending_interventions:
                del self.pending_interventions[intervention_id]

            logger.info(f"Intervenção resolvida: {intervention_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao resolver intervenção: {e}")
            return False

    async def get_pending_interventions(self) -> List[Dict[str, Any]]:
        """Obter lista de intervenções pendentes"""
        return list(self.pending_interventions.values())

    async def notify_error(self, error_message: str, context: Dict[str, Any] = None):
        """Notificar erro técnico"""
        notification = f"""
⚠️ **ERRO TÉCNICO DETECTADO**

**Erro:** {error_message}
**Horário:** {datetime.now().isoformat()}

**Contexto:** {json.dumps(context, indent=2) if context else 'N/A'}

Verificar logs do sistema para mais detalhes.
"""

        for channel_name, notifier in self.notification_channels.items():
            try:
                await notifier.send(notification)
            except Exception as e:
                logger.error(
                    f"Erro ao enviar notificação de erro via {channel_name}: {e}"
                )


# Notificadores específicos
class DiscordNotifier:
    """Notificador via Discord Webhook"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, message: str):
        """Enviar mensagem via Discord"""
        import httpx

        payload = {
            "content": message,
            "username": "WhatsApp RPG GM",
            "avatar_url": "https://cdn.iconscout.com/icon/free/png-256/discord-3-569463.png",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload)

            if response.status_code != 204:
                raise Exception(f"Discord webhook failed: {response.status_code}")


class EmailNotifier:
    """Notificador via Email"""

    def __init__(
        self, host: str, port: int, username: str, password: str, from_email: str
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email

    async def send(self, message: str):
        """Enviar email"""
        # import smtplib # Moved to top
        # from email.mime.text import MIMEText # Moved to top
        # from email.mime.multipart import MIMEMultipart # Moved to top

        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = self.username  # Enviar para si mesmo
        msg["Subject"] = "WhatsApp RPG GM - Intervenção HITL"

        msg.attach(MIMEText(message, "plain"))

        # Enviar em thread separada para não bloquear
        await asyncio.to_thread(self._send_sync, msg)

    def _send_sync(self, msg):
        """Enviar email de forma síncrona"""
        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class SMSNotifier:
    """Notificador via SMS (Twilio)"""

    def __init__(
        self, account_sid: str, auth_token: str, from_number: str, to_number: str
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number

    async def send(self, message: str):
        """Enviar SMS"""
        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)

            # Truncar mensagem para limites SMS
            if len(message) > 1600:
                message = message[:1597] + "..."

            await asyncio.to_thread(
                client.messages.create,
                body=message,
                from_=self.from_number,
                to=self.to_number,
            )

        except ImportError:
            logger.error("twilio package not installed")
            raise Exception("Twilio not available")
