"""
AI Manager - Gerenciador de IA para geração de narrativa
Simula funcionalidades de múltiplos provedores LLM para o protótipo
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger


class AIManager:
    """Gerenciador de IA com múltiplos provedores"""
    
    def __init__(self, settings):
        self.settings = settings
        self._ready = False
        
        # Providers disponíveis
        self.available_providers = settings.get_available_llm_providers()
        self.primary_provider = self.available_providers[0] if self.available_providers else "mock"
        
        # Para o protótipo, usar respostas simuladas
        self.mock_mode = True
        
        # Respostas padrão para RPG
        self.rpg_responses = {
            "exploration": [
                "Você explora cuidadosamente o ambiente. Role um teste de Percepção (d20 + modificador de Sabedoria) para ver o que descobre.",
                "Ao investigar os arredores, você nota alguns detalhes interessantes. Que tipo de investigação você gostaria de fazer?",
                "O ambiente parece calmo, mas sua experiência como aventureiro lhe diz que é melhor ficar alerta.",
            ],
            "combat": [
                "Você se prepara para o combate! Role iniciativa (d20 + modificador de Destreza).",
                "O inimigo se aproxima com intenções hostis. Que ação você gostaria de tomar?",
                "É hora da batalha! Prepare-se para rolar seus dados de ataque.",
            ],
            "dialogue": [
                "O NPC olha para você com interesse. O que você gostaria de dizer?",
                "A conversa flui naturalmente. Role um teste de Persuasão se necessário.",
                "Você percebe que suas palavras têm impacto. Continue o diálogo.",
            ],
            "general": [
                "Sua ação é notada pelos outros. Como você procede?",
                "Interessante escolha! Vamos ver como isso se desenrola.",
                "O mundo reage à sua ação de forma inesperada...",
            ]
        }
        
        # Templates de prompt
        self.prompt_templates = {
            "chain_of_thought": """
Como Mestre de Jogo experiente, analyze a situação atual e responda seguindo estes passos:
1. Avalie o contexto atual da aventura
2. Considere as ações dos jogadores
3. Determine as consequências narrativas
4. Calcule qualquer mecânica necessária
5. Descreva a resposta de forma imersiva

Situação: {situation}
Ação do jogador: {player_action}
Contexto: {context}
""",
            "standard": """
Você é um Mestre de Jogo de D&D 5e experiente e criativo. 
Responda à ação do jogador de forma envolvente e imersiva.

Ação do jogador: {player_action}
Contexto atual: {context}
"""
        }
    
    async def initialize(self):
        """Inicializar AI Manager"""
        try:
            logger.info("Inicializando AI Manager...")
            
            if self.mock_mode:
                logger.info("🤖 Modo mock ativado - usando respostas simuladas")
            else:
                # Em produção, inicializar clientes de IA reais
                await self._initialize_llm_clients()
            
            self._ready = True
            logger.info("✅ AI Manager inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar AI Manager: {e}")
            # Em desenvolvimento, continuar em modo mock
            self.mock_mode = True
            self._ready = True
            logger.warning("Continuando em modo mock")
    
    def is_ready(self) -> bool:
        """Verifica se o AI Manager está pronto"""
        return self._ready
    
    async def _initialize_llm_clients(self):
        """Inicializar clientes LLM reais (para produção)"""
        # TODO: Implementar inicialização real dos clientes
        # OpenAI, Anthropic, Google, etc.
        pass
    
    async def generate_response(self, player_message: str, player_id: str, context: Dict) -> Dict:
        """
        Gera resposta de IA para ação do jogador
        
        Args:
            player_message: Mensagem/ação do jogador
            player_id: ID do jogador
            context: Contexto da sessão
            
        Returns:
            Dict com resposta da IA
        """
        try:
            if self.mock_mode:
                return await self._generate_mock_response(player_message, player_id, context)
            else:
                return await self._generate_real_response(player_message, player_id, context)
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            # Fallback para resposta mock
            return {
                "text": "❓ Desculpe, não consegui processar sua ação. Pode tentar novamente?",
                "provider": "fallback",
                "needs_human_intervention": False
            }
    
    async def _generate_mock_response(self, player_message: str, player_id: str, context: Dict) -> Dict:
        """Gera resposta simulada para desenvolvimento"""
        
        # Determinar tipo de ação
        action_type = self._determine_action_type(player_message)
        
        # Obter respostas possíveis
        possible_responses = self.rpg_responses.get(action_type, self.rpg_responses["general"])
        
        # Adicionar contexto específico do personagem
        character = context.get("character")
        if character:
            char_name = character.get("name", "Aventureiro")
            char_location = character.get("location", "local desconhecido")
        else:
            char_name = "Aventureiro"
            char_location = "local desconhecido"
        
        # Escolher resposta base
        base_response = random.choice(possible_responses)
        
        # Personalizar resposta
        personalized_response = f"**{char_name}**, {base_response}"
        
        # Adicionar contexto de localização ocasionalmente
        if random.random() < 0.3:  # 30% das vezes
            personalized_response += f"\n\n*Você está atualmente em: {char_location}*"
        
        # Simular necessidade de HITL ocasionalmente
        needs_hitl = self._should_trigger_hitl(player_message, context)
        
        return {
            "text": personalized_response,
            "provider": "mock",
            "action_type": action_type,
            "needs_human_intervention": needs_hitl,
            "confidence": random.uniform(0.7, 0.95)
        }
    
    async def _generate_real_response(self, player_message: str, player_id: str, context: Dict) -> Dict:
        """Gera resposta usando LLM real (para produção)"""
        # TODO: Implementar chamadas reais para OpenAI, Anthropic, etc.
        
        # Por enquanto, fallback para mock
        return await self._generate_mock_response(player_message, player_id, context)
    
    def _determine_action_type(self, message: str) -> str:
        """Determina tipo de ação baseado na mensagem"""
        message_lower = message.lower()
        
        # Palavras-chave para cada tipo
        exploration_keywords = ["investigar", "procurar", "explorar", "examinar", "olhar", "observar"]
        combat_keywords = ["atacar", "lutar", "combate", "golpe", "espada", "arco", "magia ofensiva"]
        dialogue_keywords = ["falar", "conversar", "perguntar", "dizer", "responder", "dialogar"]
        
        if any(keyword in message_lower for keyword in combat_keywords):
            return "combat"
        elif any(keyword in message_lower for keyword in exploration_keywords):
            return "exploration"
        elif any(keyword in message_lower for keyword in dialogue_keywords):
            return "dialogue"
        else:
            return "general"
    
    def _should_trigger_hitl(self, message: str, context: Dict) -> bool:
        """Determina se deve acionar sistema HITL"""
        
        # Situações que podem requerer HITL
        complex_keywords = [
            "matar", "morrer", "morte", "suicídio",
            "trapaça", "roubar", "crime",
            "relacionamento", "romance", "sexo",
            "política", "religião",
            "bug", "erro", "problema"
        ]
        
        message_lower = message.lower()
        
        # Verificar palavras-chave complexas
        if any(keyword in message_lower for keyword in complex_keywords):
            return True
        
        # Mensagens muito longas podem ser complexas
        if len(message) > 300:
            return True
        
        # Verificar se há muitas perguntas seguidas
        question_marks = message.count("?")
        if question_marks > 3:
            return True
        
        # Aleatoriamente para testing (5% das vezes)
        if random.random() < 0.05:
            return True
        
        return False
    
    async def test_prompt(self, prompt: str, technique: str = "standard", provider: str = None) -> Dict:
        """
        Testa prompt específico (para interface de desenvolvimento)
        
        Args:
            prompt: Prompt a testar
            technique: Técnica de prompt (standard, chain_of_thought, etc.)
            provider: Provedor específico a usar
            
        Returns:
            Resultado do teste
        """
        try:
            if self.mock_mode:
                return {
                    "response": f"Resposta simulada para: {prompt[:50]}...",
                    "technique": technique,
                    "provider": provider or "mock",
                    "tokens_used": random.randint(50, 200),
                    "response_time": random.uniform(0.5, 2.0)
                }
            else:
                # TODO: Implementar teste real
                return {
                    "response": "Teste real não implementado ainda",
                    "technique": technique,
                    "provider": provider or self.primary_provider,
                    "error": "Real LLM not implemented"
                }
                
        except Exception as e:
            logger.error(f"Erro no teste de prompt: {e}")
            return {
                "error": str(e),
                "technique": technique,
                "provider": provider or "unknown"
            }
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        if self.mock_mode:
            return ["mock"]
        return self.available_providers
    
    def get_provider_status(self) -> Dict:
        """Retorna status dos provedores"""
        if self.mock_mode:
            return {
                "mock": {
                    "status": "active",
                    "response_time": "< 1s",
                    "requests_today": random.randint(0, 100)
                }
            }
        
        # TODO: Implementar status real dos provedores
        return {}
    
    async def generate_narrative_description(self, scene_type: str, context: Dict) -> str:
        """Gera descrição narrativa para cenas"""
        descriptions = {
            "tavern": [
                "A taverna está movimentada, com o som de conversas e o cheiro de ensopado no ar.",
                "Velas tremulam nas mesas de madeira escura, criando sombras dançantes nas paredes.",
                "O barulho de canecas batendo e risadas ecoa pela taverna lotada."
            ],
            "forest": [
                "A floresta está silenciosa, exceto pelo canto distante de pássaros.",
                "Raios de sol filtram através da copa das árvores, criando um padrão mosqueado no chão.",
                "O cheiro de terra úmida e folhas em decomposição preenche o ar."
            ],
            "dungeon": [
                "Corredores de pedra úmida se estendem à frente, mergulhados em sombras.",
                "O eco de seus passos ressoa pelas passagens escuras.",
                "Uma corrente de ar frio traz consigo um cheiro de mofo e mistério."
            ]
        }
        
        return random.choice(descriptions.get(scene_type, descriptions["tavern"]))
    
    async def cleanup(self):
        """Limpeza na finalização"""
        logger.info("Finalizando AI Manager...")
        self._ready = False