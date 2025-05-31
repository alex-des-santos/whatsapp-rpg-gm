"""
Cliente para integração com Evolution API
Gerencia conexão WhatsApp e envio/recebimento de mensagens
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
import httpx
from loguru import logger


class EvolutionClient:
    """Cliente para Evolution API"""
    
    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.evolution_api_url
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name
        self.webhook_url = settings.webhook_url
        
        self._connected = False
        self._instance_created = False
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def initialize(self):
        """Inicializar cliente Evolution API"""
        try:
            logger.info("Inicializando Evolution API Client...")
            
            # Verificar se API está disponível
            await self._check_api_health()
            
            # Verificar/criar instância
            await self._ensure_instance_exists()
            
            # Configurar webhook
            await self._configure_webhook()
            
            self._connected = True
            logger.info("✅ Evolution API Client inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Evolution API: {e}")
            # Em desenvolvimento, continuar mesmo com erro
            if self.settings.debug:
                logger.warning("Modo debug: continuando sem Evolution API")
                self._connected = False
            else:
                raise
    
    async def cleanup(self):
        """Limpeza na finalização"""
        logger.info("Finalizando Evolution API Client...")
        self._connected = False
    
    def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self._connected
    
    async def _check_api_health(self):
        """Verificar se Evolution API está funcionando"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Evolution API ativa - versão: {data.get('version', 'unknown')}")
                else:
                    raise Exception(f"API não disponível - status: {response.status_code}")
                    
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão com Evolution API: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar health da API: {e}")
            raise
    
    async def _ensure_instance_exists(self):
        """Verificar se instância existe, criar se necessário"""
        try:
            # Verificar se instância já existe
            existing_instances = await self._get_instances()
            
            instance_exists = any(
                instance.get("instanceName") == self.instance_name 
                for instance in existing_instances
            )
            
            if not instance_exists:
                logger.info(f"Criando nova instância: {self.instance_name}")
                await self.create_instance()
            else:
                logger.info(f"Instância já existe: {self.instance_name}")
                self._instance_created = True
                
        except Exception as e:
            logger.error(f"Erro ao verificar/criar instância: {e}")
            raise
    
    async def _get_instances(self) -> List[Dict]:
        """Obter lista de instâncias"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/instance/fetchInstances",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Não foi possível obter instâncias: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao obter instâncias: {e}")
            return []
    
    async def create_instance(self) -> Dict:
        """Criar nova instância WhatsApp"""
        try:
            instance_data = {
                "instanceName": self.instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS",
                "rejectCall": True,
                "msgCall": "Chamadas não são aceitas por este bot",
                "groupsIgnore": False,
                "alwaysOnline": True,
                "readMessages": True,
                "readStatus": False,
                "syncFullHistory": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/instance/create",
                    headers=self.headers,
                    json=instance_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self._instance_created = True
                    logger.info(f"Instância criada com sucesso: {self.instance_name}")
                    return result
                else:
                    error_msg = f"Erro ao criar instância: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Erro ao criar instância: {e}")
            raise
    
    async def _configure_webhook(self):
        """Configurar webhook para receber mensagens"""
        if not self.webhook_url:
            logger.warning("Webhook URL não configurada")
            return
            
        try:
            webhook_data = {
                "url": self.webhook_url,
                "byEvents": True,
                "base64": False,
                "events": [
                    "messages.upsert",
                    "messages.update",
                    "messages.delete",
                    "send.message",
                    "groups.upsert",
                    "groups.update", 
                    "groups.delete",
                    "group-participants.update",
                    "contacts.upsert",
                    "contacts.update",
                    "contacts.delete",
                    "presence.update",
                    "chats.upsert",
                    "chats.update",
                    "chats.delete",
                    "connection.update",
                    "call",
                    "typebot.start",
                    "typebot.change-status"
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/webhook/set/{self.instance_name}",
                    headers=self.headers,
                    json=webhook_data
                )
                
                if response.status_code in [200, 201]:
                    logger.info("Webhook configurado com sucesso")
                else:
                    logger.warning(f"Erro ao configurar webhook: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
    
    async def get_qr_code(self, instance_name: Optional[str] = None) -> str:
        """Obter QR Code para conectar WhatsApp"""
        instance = instance_name or self.instance_name
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/instance/connect/{instance}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    qr_code = data.get("base64", data.get("code", ""))
                    logger.info("QR Code obtido com sucesso")
                    return qr_code
                else:
                    error_msg = f"Erro ao obter QR Code: {response.status_code}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Erro ao obter QR Code: {e}")
            raise
    
    async def send_message(self, number: str, message: str, instance: Optional[str] = None) -> Dict:
        """Enviar mensagem de texto"""
        instance = instance or self.instance_name
        
        try:
            # Limpar e formatar número
            clean_number = self._clean_phone_number(number)
            
            message_data = {
                "number": clean_number,
                "text": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{instance}",
                    headers=self.headers,
                    json=message_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"Mensagem enviada para {clean_number}")
                    return result
                else:
                    error_msg = f"Erro ao enviar mensagem: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    async def send_interactive_message(self, number: str, message: str, buttons: List[Dict], 
                                     instance: Optional[str] = None) -> Dict:
        """Enviar mensagem com botões interativos"""
        instance = instance or self.instance_name
        
        try:
            clean_number = self._clean_phone_number(number)
            
            message_data = {
                "number": clean_number,
                "text": message,
                "buttons": buttons
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/sendButtons/{instance}",
                    headers=self.headers,
                    json=message_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"Mensagem interativa enviada para {clean_number}")
                    return result
                else:
                    error_msg = f"Erro ao enviar mensagem interativa: {response.status_code}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem interativa: {e}")
            raise
    
    async def get_instance_status(self, instance: Optional[str] = None) -> Dict:
        """Obter status da instância"""
        instance = instance or self.instance_name
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{instance}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Erro ao obter status: {response.status_code}")
                    return {"state": "unknown"}
                    
        except Exception as e:
            logger.error(f"Erro ao obter status da instância: {e}")
            return {"state": "error"}
    
    def _clean_phone_number(self, number: str) -> str:
        """Limpar e formatar número de telefone"""
        # Remove caracteres não numéricos
        clean = ''.join(filter(str.isdigit, number))
        
        # Adicionar código do país se necessário (Brasil = 55)
        if len(clean) == 11 and clean.startswith('11'):
            clean = '55' + clean
        elif len(clean) == 10:
            clean = '5511' + clean
        elif len(clean) == 13 and clean.startswith('55'):
            pass  # Já tem código do país
        
        return clean + "@s.whatsapp.net"
    
    async def create_rpg_buttons(self, action_type: str = "general") -> List[Dict]:
        """Criar botões padrão para RPG"""
        if action_type == "combat":
            return [
                {"id": "attack", "text": "⚔️ Atacar"},
                {"id": "defend", "text": "🛡️ Defender"},
                {"id": "spell", "text": "✨ Magia"},
                {"id": "item", "text": "🎒 Item"}
            ]
        elif action_type == "exploration":
            return [
                {"id": "investigate", "text": "🔍 Investigar"},
                {"id": "move", "text": "🚶 Mover"},
                {"id": "interact", "text": "💬 Interagir"},
                {"id": "rest", "text": "😴 Descansar"}
            ]
        else:
            return [
                {"id": "roll_dice", "text": "🎲 Rolar Dados"},
                {"id": "status", "text": "📊 Status"},
                {"id": "inventory", "text": "🎒 Inventário"},
                {"id": "help", "text": "❓ Ajuda"}
            ]