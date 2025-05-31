"""
AI Coordinator - Coordenador de Inteligência Artificial
Gerencia múltiplos provedores de IA e geração de respostas
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Provedores de IA disponíveis"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"

class AICoordinator:
    """Coordenador de IA para geração de respostas como GM"""

    def __init__(self):
        self.providers = {}
        self.default_provider = AIProvider(settings.DEFAULT_AI_PROVIDER)
        self.fallback_order = [AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.GOOGLE, AIProvider.OLLAMA]

        self._initialize_providers()
        logger.info(f"AI Coordinator inicializado com provedor padrão: {self.default_provider.value}")

    def _initialize_providers(self):
        """Inicializar provedores de IA disponíveis"""

        # OpenAI
        if settings.OPENAI_API_KEY:
            self.providers[AIProvider.OPENAI] = OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )

        # Anthropic
        if settings.ANTHROPIC_API_KEY:
            self.providers[AIProvider.ANTHROPIC] = AnthropicProvider(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS
            )

        # Google AI
        if settings.GOOGLE_API_KEY:
            self.providers[AIProvider.GOOGLE] = GoogleProvider(
                api_key=settings.GOOGLE_API_KEY,
                model=settings.GOOGLE_MODEL
            )

        # Ollama (sempre disponível se URL configurada)
        self.providers[AIProvider.OLLAMA] = OllamaProvider(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL
        )

    async def generate_response(self, prompt: str, context: Dict[str, Any] = None, 
                              provider: Optional[AIProvider] = None) -> str:
        """
        Gerar resposta usando IA

        Args:
            prompt: Prompt para a IA
            context: Contexto adicional (sessão, personagem, etc.)
            provider: Provedor específico (usa padrão se None)

        Returns:
            str: Resposta gerada pela IA
        """
        provider = provider or self.default_provider
        context = context or {}

        # Enriquecer prompt com contexto
        enriched_prompt = self._enrich_prompt(prompt, context)

        # Tentar provedor principal
        if provider in self.providers:
            try:
                response = await self.providers[provider].generate(enriched_prompt)
                if response:
                    logger.info(f"Resposta gerada com sucesso usando {provider.value}")
                    return response
            except Exception as e:
                logger.warning(f"Erro no provedor {provider.value}: {e}")

        # Tentar provedores de fallback
        for fallback_provider in self.fallback_order:
            if fallback_provider in self.providers and fallback_provider != provider:
                try:
                    response = await self.providers[fallback_provider].generate(enriched_prompt)
                    if response:
                        logger.info(f"Resposta gerada usando fallback {fallback_provider.value}")
                        return response
                except Exception as e:
                    logger.warning(f"Erro no fallback {fallback_provider.value}: {e}")

        # Se todos falharam, retornar resposta padrão
        logger.error("Todos os provedores de IA falharam")
        return self._get_fallback_response(context)

    def _enrich_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enriquecer prompt com contexto"""
        system_prompt = """
        Você é um Mestre de Jogo (GM) experiente de Dungeons & Dragons 5ª Edição.
        Você é criativo, imparcial e focado em criar uma experiência divertida para os jogadores.

        Diretrizes importantes:
        - Seja descritivo mas conciso
        - Mantenha o tom apropriado para a situação
        - Sugira rolagens quando necessário
        - Não tome decisões pelos jogadores
        - Mantenha a coerência narrativa
        - Responda sempre em português brasileiro
        - Use no máximo 200 palavras por resposta
        """

        context_info = ""
        if context.get('session'):
            session = context['session']
            context_info += f"\nCenário atual: {session.get('current_scene', 'Desconhecido')}"
            context_info += f"\nLocalização: {session.get('world_state', {}).get('location', 'Desconhecida')}"
            context_info += f"\nEstado da sessão: {session.get('state', 'Ativo')}"

        if context.get('character'):
            char = context['character']
            context_info += f"\nPersonagem ativo: {char.get('name', 'Desconhecido')}"
            context_info += f"\nClasse/Raça: {char.get('character_class', '')} {char.get('race', '')}"

        return f"{system_prompt}\n\nContexto:{context_info}\n\nSituação atual:\n{prompt}"

    def _get_fallback_response(self, context: Dict[str, Any]) -> str:
        """Resposta de emergência quando IA não funciona"""
        fallback_responses = [
            "O Mestre precisa de um momento para processar essa situação...",
            "Algo inesperado acontece... Role um d20 para descobrir o que!",
            "A situação se torna mais complexa. Aguarde enquanto o GM analisa as possibilidades.",
            "Um vento misterioso sopra pelo local, trazendo uma sensação de mudança...",
            "O tempo parece se arrastar por um momento enquanto todos processam a situação."
        ]

        import random
        return random.choice(fallback_responses)

    async def generate_character_description(self, character_data: Dict[str, Any]) -> str:
        """Gerar descrição de personagem"""
        prompt = f"""
        Crie uma descrição física interessante e detalhada para este personagem de D&D:

        Nome: {character_data.get('name')}
        Raça: {character_data.get('race')}
        Classe: {character_data.get('character_class')}
        Background: {character_data.get('background', 'Aventureiro')}

        A descrição deve ter entre 50-100 palavras e incluir:
        - Aparência física
        - Traços marcantes
        - Estilo de vestimenta/equipamento
        - Uma característica única
        """

        return await self.generate_response(prompt)

    async def generate_npc(self, location: str, purpose: str) -> str:
        """Gerar NPC para a sessão"""
        prompt = f"""
        Crie um NPC interessante para esta situação:

        Localização: {location}
        Propósito: {purpose}

        Inclua:
        - Nome e aparência
        - Personalidade básica
        - Motivação principal
        - Como pode interagir com os jogadores
        """

        return await self.generate_response(prompt)

    async def generate_encounter(self, party_level: int, environment: str) -> str:
        """Gerar encontro apropriado"""
        prompt = f"""
        Crie um encontro de D&D 5e para:

        Nível do grupo: {party_level}
        Ambiente: {environment}

        Inclua:
        - Tipo de encontro (combate, social, exploração)
        - Inimigos ou desafios específicos
        - Recompensas possíveis
        - Descrição da cena
        """

        return await self.generate_response(prompt)

class BaseAIProvider:
    """Classe base para provedores de IA"""

    def __init__(self, **kwargs):
        self.config = kwargs

    async def generate(self, prompt: str) -> str:
        """Gerar resposta - deve ser implementado pelas subclasses"""
        raise NotImplementedError

class OpenAIProvider(BaseAIProvider):
    """Provedor OpenAI"""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        super().__init__(api_key=api_key, model=model, max_tokens=max_tokens, temperature=temperature)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicializar cliente OpenAI"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.config['api_key'])
        except ImportError:
            logger.error("openai package not installed")
            self.client = None

    async def generate(self, prompt: str) -> str:
        """Gerar resposta usando OpenAI"""
        if not self.client:
            raise Exception("OpenAI client not initialized")

        try:
            response = await self.client.chat.completions.create(
                model=self.config['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Erro OpenAI: {e}")
            raise

class AnthropicProvider(BaseAIProvider):
    """Provedor Anthropic"""

    def __init__(self, api_key: str, model: str, max_tokens: int):
        super().__init__(api_key=api_key, model=model, max_tokens=max_tokens)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.config['api_key'])
        except ImportError:
            logger.error("anthropic package not installed")
            self.client = None

    async def generate(self, prompt: str) -> str:
        if not self.client:
            raise Exception("Anthropic client not initialized")

        try:
            response = await self.client.messages.create(
                model=self.config['model'],
                max_tokens=self.config['max_tokens'],
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Erro Anthropic: {e}")
            raise

class GoogleProvider(BaseAIProvider):
    """Provedor Google AI"""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key=api_key, model=model)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config['api_key'])
            self.client = genai.GenerativeModel(self.config['model'])
        except ImportError:
            logger.error("google-generativeai package not installed")
            self.client = None

    async def generate(self, prompt: str) -> str:
        if not self.client:
            raise Exception("Google AI client not initialized")

        try:
            response = await self.client.generate_content_async(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Erro Google AI: {e}")
            raise

class OllamaProvider(BaseAIProvider):
    """Provedor Ollama (LLM local)"""

    def __init__(self, base_url: str, model: str):
        super().__init__(base_url=base_url, model=model)

    async def generate(self, prompt: str) -> str:
        """Gerar resposta usando Ollama"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config['base_url']}/api/generate",
                    json={
                        "model": self.config['model'],
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get('response', '').strip()
                else:
                    raise Exception(f"Ollama error: {response.status_code}")

        except Exception as e:
            logger.error(f"Erro Ollama: {e}")
            raise
