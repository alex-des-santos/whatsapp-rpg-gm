import openai
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
from config import Config
from ..game_state.models import Character

class AIModule:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.index = self._build_index()
    
    def _build_index(self):
        try:
            documents = SimpleDirectoryReader(Config.RPG_DATA_PATH).load_data()
            return GPTVectorStoreIndex.from_documents(documents)
        except:
            return None
    
    def generate_response(self, context, player_action, character: Character):
        prompt = self._build_prompt(context, player_action, character)
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _build_prompt(self, context, action, character):
        return f"""
        Você é um mestre de jogo de RPG especialista em D&D 5e. 
        Contexto atual: {context}
        Estado do personagem: 
          Nível: {character.level}
          HP: {character.hp}/{character.max_hp}
          Localização: {character.location}
        
        O jogador realizou a ação: {action}
        
        [PENSAMENTO PASSO-A-PASSO]
        1. Analise o contexto e a ação
        2. Verifique consistência com as regras de D&D
        3. Considere o estado atual do personagem
        4. Decida consequências lógicas
        5. Gere resposta narrativa imersiva
        
        [RESPOSTA]
        """