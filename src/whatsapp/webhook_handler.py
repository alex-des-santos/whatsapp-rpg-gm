"""
Webhook Handler para Evolution API
Processa mensagens recebidas do WhatsApp
"""

import json
import re
from typing import Dict, List, Any, Optional
from fastapi.responses import JSONResponse
from loguru import logger


class WebhookHandler:
    """Manipulador de webhook para receber eventos do WhatsApp"""
    
    def __init__(self, game_manager, ai_manager, dice_system, hitl_manager, settings):
        """
        Inicializa o webhook handler
        
        Args:
            game_manager: Gerenciador de estado do jogo
            ai_manager: Gerenciador de IA
            dice_system: Sistema de dados
            hitl_manager: Sistema HITL
            settings: Configurações
        """
        self.game_manager = game_manager
        self.ai_manager = ai_manager
        self.dice_system = dice_system
        self.hitl_manager = hitl_manager
        self.settings = settings
        
        # Mapear números de telefone para IDs de jogador
        self.phone_to_player_id = {}
        
        # Mapeamento de comandos
        self.commands = {
            "start": self._handle_start_command,
            "criar-personagem": self._handle_create_character_command,
            "rolar": self._handle_roll_dice_command,
            "status": self._handle_status_command,
            "inventario": self._handle_inventory_command,
            "help": self._handle_help_command
        }
    
    async def handle_webhook(self, body: bytes, headers: Dict) -> JSONResponse:
        """
        Processa webhook recebido da Evolution API
        
        Args:
            body: Corpo da requisição
            headers: Cabeçalhos HTTP
            
        Returns:
            JSONResponse com resposta
        """
        try:
            # Validar webhook
            if not self._validate_webhook(headers):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Não autorizado"}
                )
            
            # Decodificar corpo
            body_str = body.decode("utf-8")
            payload = json.loads(body_str)
            
            # Processar por tipo de evento
            event_type = self._get_event_type(payload)
            instance = self._get_instance_name(payload)
            
            if event_type == "messages.upsert":
                await self._handle_message(payload, instance)
            elif event_type == "connection.update":
                await self._handle_connection_update(payload, instance)
            elif event_type in ["groups.update", "group-participants.update"]:
                await self._handle_group_event(payload, instance)
            
            # Ack sempre
            return JSONResponse(
                status_code=200,
                content={"status": "success"}
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    def _validate_webhook(self, headers: Dict) -> bool:
        """Validar webhook com token"""
        if not self.settings.webhook_token:
            return True  # Se não há token configurado, aceitar todos
        
        auth_header = headers.get("authorization", "")
        token = auth_header.replace("Bearer ", "")
        
        return token == self.settings.webhook_token
    
    def _get_event_type(self, payload: Dict) -> str:
        """Extrair tipo de evento"""
        return payload.get("event", "unknown")
    
    def _get_instance_name(self, payload: Dict) -> str:
        """Extrair nome da instância"""
        return payload.get("instance", "unknown")
    
    async def _handle_message(self, payload: Dict, instance: str):
        """
        Processa mensagem recebida
        
        Args:
            payload: Dados da mensagem
            instance: Nome da instância
        """
        try:
            # Extrair informações da mensagem
            message_data = payload.get("data", {})
            
            # Verificar se é mensagem de usuário
            message_type = message_data.get("messageType", "")
            if message_type != "conversation":
                logger.debug(f"Ignorando mensagem tipo: {message_type}")
                return
            
            # Obter dados relevantes
            sender = message_data.get("key", {}).get("remoteJid", "")
            message_text = message_data.get("message", {}).get("conversation", "")
            
            if not sender or not message_text:
                logger.debug("Mensagem inválida ou incompleta")
                return
            
            # Limpar número de telefone
            clean_sender = self._clean_phone_number(sender)
            
            # Mapear para player_id (ou criar se não existir)
            player_id = self.phone_to_player_id.get(clean_sender)
            if not player_id:
                player_id = f"player_{clean_sender}"
                self.phone_to_player_id[clean_sender] = player_id
            
            # Processar comando ou mensagem
            logger.info(f"Mensagem de {clean_sender}: {message_text}")
            await self._process_message(message_text, player_id, clean_sender, instance)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            # Não levantar exceção para evitar falhas no webhook
    
    async def _handle_connection_update(self, payload: Dict, instance: str):
        """Processa atualizações de conexão"""
        try:
            connection_data = payload.get("data", {})
            state = connection_data.get("state", "")
            
            logger.info(f"Estado da conexão: {state} (instância: {instance})")
            
        except Exception as e:
            logger.error(f"Erro ao processar atualização de conexão: {e}")
    
    async def _handle_group_event(self, payload: Dict, instance: str):
        """Processa eventos de grupo"""
        try:
            logger.info(f"Evento de grupo recebido: {payload.get('event')}")
            # Em uma implementação real, processar eventos de grupo conforme necessário
            
        except Exception as e:
            logger.error(f"Erro ao processar evento de grupo: {e}")
    
    async def _process_message(self, message: str, player_id: str, sender: str, instance: str):
        """
        Processa mensagem do jogador
        
        Args:
            message: Texto da mensagem
            player_id: ID do jogador
            sender: Número do remetente
            instance: Nome da instância
        """
        try:
            # Verificar se é um comando
            if message.startswith("/"):
                await self._process_command(message, player_id, sender, instance)
            else:
                # Enviar para o fluxo normal de processamento
                await self._process_regular_message(message, player_id, sender, instance)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            
            # Enviar mensagem de erro para o usuário
            error_message = f"❌ Ocorreu um erro ao processar sua mensagem:\n{str(e)}"
            await self._send_message(sender, error_message, instance)
    
    async def _process_command(self, message: str, player_id: str, sender: str, instance: str):
        """
        Processa comando do jogador
        
        Args:
            message: Texto do comando
            player_id: ID do jogador
            sender: Número do remetente
            instance: Nome da instância
        """
        # Extrair comando e argumentos
        parts = message[1:].split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        logger.info(f"Comando recebido: /{command} {' '.join(args)}")
        
        # Verificar se comando existe
        if command in self.commands:
            # Executar handler do comando
            await self.commands[command](args, player_id, sender, instance)
        else:
            # Comando desconhecido
            await self._send_message(
                sender, 
                f"❓ Comando desconhecido: /{command}\nDigite /help para ver comandos disponíveis.",
                instance
            )
    
    async def _process_regular_message(self, message: str, player_id: str, sender: str, instance: str):
        """
        Processa mensagem regular (não-comando) do jogador
        
        Args:
            message: Texto da mensagem
            player_id: ID do jogador
            sender: Número do remetente
            instance: Nome da instância
        """
        try:
            # Verificar se jogador tem personagem
            character = await self.game_manager.get_character(player_id)
            
            if not character:
                # Jogador sem personagem
                await self._send_message(
                    sender,
                    "🧙‍♂️ Bem-vindo ao RPG via WhatsApp!\n\n"
                    "Parece que você ainda não tem um personagem. Para começar a jogar, "
                    "crie um personagem com o comando /criar-personagem.",
                    instance
                )
                return
            
            # Processar ação com Game Manager
            result = await self.game_manager.process_player_action(player_id, message)
            
            # Verificar se é necessário rolar dados
            if result.get("requires_dice", False):
                dice_expression = result.get("dice_expression", "1d20")
                dice_result = self.dice_system.roll(dice_expression)
                
                # Adicionar resultado dos dados ao contexto
                result["context"]["dice_result"] = dice_result.to_dict()
                
                # Enviar resultado dos dados
                dice_message = self.dice_system.format_roll_result(dice_result)
                await self._send_message(sender, dice_message, instance)
            
            # Processar com IA se não for uma ação especial
            if result.get("type") in ["general", "dialogue"]:
                # Enviar mensagem de typing
                await self._send_message(sender, "🤔 *Pensando...*", instance)
                
                # Gerar resposta com IA
                ai_response = await self.ai_manager.generate_response(
                    message, player_id, result["context"]
                )
                
                # Verificar se IA solicitou HITL
                if ai_response.get("needs_human_intervention", False):
                    # Notificar sistema HITL
                    await self.hitl_manager.trigger_intervention(
                        "AI solicitou intervenção",
                        {
                            "player_id": player_id,
                            "sender": sender,
                            "message": message,
                            "context": result["context"]
                        }
                    )
                
                # Enviar resposta
                await self._send_message(sender, ai_response["text"], instance)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await self._send_message(
                sender, 
                "❌ Erro ao processar sua mensagem. Por favor, tente novamente.",
                instance
            )
    
    async def _send_message(self, recipient: str, message: str, instance: str):
        """
        Envia mensagem via Evolution API
        
        Args:
            recipient: Número do destinatário
            message: Texto da mensagem
            instance: Nome da instância
        """
        try:
            if not hasattr(self, "_evolution_client"):
                # Módulos circulares não são ideais, mas funcionam neste caso
                from src.whatsapp.evolution_client import EvolutionClient
                self._evolution_client = EvolutionClient(self.settings)
                await self._evolution_client.initialize()
            
            await self._evolution_client.send_message(recipient, message, instance)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    def _clean_phone_number(self, phone: str) -> str:
        """Limpa número de telefone"""
        # Remover sufixo @s.whatsapp.net ou @g.us
        clean = phone.split('@')[0]
        
        # Remover caracteres não numéricos
        clean = ''.join(filter(str.isdigit, clean))
        
        return clean
    
    # Handlers de comando
    
    async def _handle_start_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Iniciar o jogo"""
        await self._send_message(
            sender,
            "🎲 *Bem-vindo ao RPG via WhatsApp!*\n\n"
            "Este é um sistema automatizado de RPG usando IA como Mestre de Jogo.\n\n"
            "Para começar, use um dos seguintes comandos:\n"
            "• */criar-personagem* - Cria um novo personagem\n"
            "• */status* - Mostra status do seu personagem\n"
            "• */rolar [expressão]* - Rola dados (ex: /rolar 2d6+3)\n"
            "• */help* - Mostra todos os comandos\n\n"
            "Ou simplesmente envie uma mensagem descrevendo o que seu personagem faz!",
            instance
        )
    
    async def _handle_create_character_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Criar novo personagem"""
        # Verificar se já tem personagem
        existing_character = await self.game_manager.get_character(player_id)
        if existing_character:
            await self._send_message(
                sender,
                f"⚠️ Você já tem um personagem: *{existing_character.name}* (Nível {existing_character.level} {existing_character.char_class})\n\n"
                "No momento não é possível ter mais de um personagem por jogador.",
                instance
            )
            return
        
        # Personagem padrão
        default_character = {
            "name": "Aventureiro",
            "class": "Fighter",
            "level": 1,
            "hp": 10,
            "stats": {
                "strength": 14,
                "dexterity": 12,
                "constitution": 13,
                "intelligence": 10,
                "wisdom": 11,
                "charisma": 12
            },
            "location": "Taverna do Dragão Dourado",
            "inventory": ["Espada Curta", "Escudo", "Mochila", "10 peças de ouro"]
        }
        
        # Criar personagem
        character = await self.game_manager.create_character(player_id, default_character)
        
        # Enviar confirmação
        await self._send_message(
            sender,
            f"✅ Personagem criado com sucesso!\n\n"
            f"*{character.name}*\n"
            f"Nível {character.level} {character.char_class}\n\n"
            f"*Atributos:*\n"
            f"• Força: {character.stats['strength']} ({'+' if character.get_modifier('strength') >= 0 else ''}{character.get_modifier('strength')})\n"
            f"• Destreza: {character.stats['dexterity']} ({'+' if character.get_modifier('dexterity') >= 0 else ''}{character.get_modifier('dexterity')})\n"
            f"• Constituição: {character.stats['constitution']} ({'+' if character.get_modifier('constitution') >= 0 else ''}{character.get_modifier('constitution')})\n"
            f"• Inteligência: {character.stats['intelligence']} ({'+' if character.get_modifier('intelligence') >= 0 else ''}{character.get_modifier('intelligence')})\n"
            f"• Sabedoria: {character.stats['wisdom']} ({'+' if character.get_modifier('wisdom') >= 0 else ''}{character.get_modifier('wisdom')})\n"
            f"• Carisma: {character.stats['charisma']} ({'+' if character.get_modifier('charisma') >= 0 else ''}{character.get_modifier('charisma')})\n\n"
            f"*Inventário:*\n" + "\n".join([f"• {item}" for item in character.inventory]),
            instance
        )
    
    async def _handle_roll_dice_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Rolar dados"""
        # Verificar se tem expressão
        if not args:
            await self._send_message(
                sender,
                "⚠️ Uso: /rolar [expressão]\n"
                "Exemplos: /rolar 1d20, /rolar 2d6+3, /rolar 1d8+2",
                instance
            )
            return
        
        # Obter expressão
        expression = args[0]
        
        try:
            # Validar expressão com regex
            if not re.match(r'^\d*d\d+([+-]\d+)?$', expression):
                raise ValueError(f"Expressão inválida: {expression}")
            
            # Rolar dados
            result = self.dice_system.roll(expression)
            
            # Formatar resultado
            formatted = self.dice_system.format_roll_result(result)
            
            # Enviar resultado
            await self._send_message(sender, formatted, instance)
            
        except Exception as e:
            await self._send_message(
                sender,
                f"❌ Erro ao rolar dados: {str(e)}\n"
                "Use o formato: 1d20, 2d6+3, etc.",
                instance
            )
    
    async def _handle_status_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Mostrar status do personagem"""
        # Obter personagem
        character = await self.game_manager.get_character(player_id)
        
        if not character:
            await self._send_message(
                sender,
                "⚠️ Você ainda não tem um personagem.\n"
                "Use /criar-personagem para criar um.",
                instance
            )
            return
        
        # Enviar status
        hp_percent = (character.hp_current / character.hp_max) * 100
        hp_bar = "▓" * int(hp_percent // 10) + "░" * (10 - int(hp_percent // 10))
        
        await self._send_message(
            sender,
            f"📊 *Status do Personagem*\n\n"
            f"*{character.name}*\n"
            f"Nível {character.level} {character.char_class}\n\n"
            f"*HP:* {character.hp_current}/{character.hp_max} ({int(hp_percent)}%)\n"
            f"{hp_bar}\n\n"
            f"*Atributos:*\n"
            f"• Força: {character.stats['strength']} ({'+' if character.get_modifier('strength') >= 0 else ''}{character.get_modifier('strength')})\n"
            f"• Destreza: {character.stats['dexterity']} ({'+' if character.get_modifier('dexterity') >= 0 else ''}{character.get_modifier('dexterity')})\n"
            f"• Constituição: {character.stats['constitution']} ({'+' if character.get_modifier('constitution') >= 0 else ''}{character.get_modifier('constitution')})\n"
            f"• Inteligência: {character.stats['intelligence']} ({'+' if character.get_modifier('intelligence') >= 0 else ''}{character.get_modifier('intelligence')})\n"
            f"• Sabedoria: {character.stats['wisdom']} ({'+' if character.get_modifier('wisdom') >= 0 else ''}{character.get_modifier('wisdom')})\n"
            f"• Carisma: {character.stats['charisma']} ({'+' if character.get_modifier('charisma') >= 0 else ''}{character.get_modifier('charisma')})\n\n"
            f"*Localização:* {character.location}\n"
            f"*Status:* {character.status}",
            instance
        )
    
    async def _handle_inventory_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Mostrar inventário do personagem"""
        # Obter personagem
        character = await self.game_manager.get_character(player_id)
        
        if not character:
            await self._send_message(
                sender,
                "⚠️ Você ainda não tem um personagem.\n"
                "Use /criar-personagem para criar um.",
                instance
            )
            return
        
        # Enviar inventário
        await self._send_message(
            sender,
            f"🎒 *Inventário de {character.name}*\n\n" + 
            "\n".join([f"• {item}" for item in character.inventory]),
            instance
        )
    
    async def _handle_help_command(self, args: List[str], player_id: str, sender: str, instance: str):
        """Mostrar ajuda"""
        await self._send_message(
            sender,
            "🎲 *Comandos Disponíveis*\n\n"
            "• */start* - Iniciar o jogo\n"
            "• */criar-personagem* - Criar um novo personagem\n"
            "• */status* - Mostrar status do seu personagem\n"
            "• */inventario* - Mostrar inventário do seu personagem\n"
            "• */rolar [expressão]* - Rolar dados (ex: /rolar 2d6+3)\n"
            "• */help* - Mostrar esta ajuda\n\n"
            "Além dos comandos, você pode simplesmente enviar mensagens descrevendo o que seu personagem faz, e o Mestre de Jogo IA irá responder!",
            instance
        )