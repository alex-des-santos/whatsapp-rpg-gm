"""
Evolution API Client
Cliente para interação com a Evolution API do WhatsApp
"""

import httpx
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from ..core.config import settings

logger = logging.getLogger(__name__)

class EvolutionClient:
    """Cliente para Evolution API"""

    def __init__(self, api_url: str, api_key: str, instance_name: str):
        """
        Inicializar cliente Evolution API

        Args:
            api_url: URL base da Evolution API
            api_key: Chave API para autenticação
            instance_name: Nome da instância WhatsApp
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.client = httpx.AsyncClient(timeout=30.0)
        self.webhook_url = None
        self.is_connected = False
        self.status = {
            'connected': False,
            'qrcode': None,
            'last_check': None,
            'state': 'DISCONNECTED'
        }

        logger.info(f"Evolution API Client inicializado - Instância: {instance_name}")

    async def close(self):
        """Fechar conexões HTTP"""
        await self.client.aclose()
        logger.info("Conexões HTTP fechadas")

    def _build_headers(self) -> Dict[str, str]:
        """Criar headers para requisições"""
        return {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

    def _build_url(self, path: str) -> str:
        """Construir URL completa"""
        return urljoin(self.api_url, path)

    async def check_connection(self) -> bool:
        """Verificar conexão com Evolution API"""
        try:
            url = self._build_url(f"/instance/status/{self.instance_name}")
            response = await self.client.get(url, headers=self._build_headers())

            if response.status_code == 200:
                status_data = response.json()

                # Atualizar status
                self.status = {
                    'connected': status_data.get('status') == 'CONNECTED',
                    'qrcode': status_data.get('qrcode'),
                    'last_check': status_data.get('timestamp'),
                    'state': status_data.get('status', 'UNKNOWN')
                }

                self.is_connected = self.status['connected']

                return self.is_connected

            else:
                logger.warning(f"Erro ao verificar status: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            return False

    async def create_instance(self) -> bool:
        """Criar instância no WhatsApp"""
        try:
            url = self._build_url("/instance/create")

            data = {
                "instanceName": self.instance_name,
                "webhook": self.webhook_url,
                "webhook_by_events": True,
                "events": [
                    "messages.upsert",
                    "qr",
                    "connection.update"
                ]
            }

            response = await self.client.post(
                url, 
                headers=self._build_headers(),
                json=data
            )

            if response.status_code in (200, 201):
                logger.info(f"Instância criada com sucesso: {self.instance_name}")
                return True

            logger.error(f"Erro ao criar instância: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            logger.error(f"Erro ao criar instância: {e}")
            return False

    async def send_text_message(self, to: str, message: str) -> bool:
        """Enviar mensagem de texto"""
        try:
            url = self._build_url(f"/message/text/{self.instance_name}")

            data = {
                "number": to,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": message
                }
            }

            response = await self.client.post(
                url,
                headers=self._build_headers(),
                json=data
            )

            if response.status_code == 201:
                return True

            logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
