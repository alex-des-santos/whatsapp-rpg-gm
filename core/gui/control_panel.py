import streamlit as st
from core.game_state.manager import GameStateManager
from config import Config

class ControlPanel:
    def __init__(self):
        self.state_manager = GameStateManager(Config.GAME_STATE_PATH)
    
    def render(self):
        st.title("Painel do Mestre de Jogo")
        
        # Seção de Estado do Jogo
        st.header("Estado do Jogo")
        st.json(self.state_manager.state.dict())
        
        # Seção de Intervenção
        st.header("Intervenção Manual")
        player_id = st.text_input("ID do Jogador")
        command = st.text_area("Comando do GM")
        if st.button("Executar Comando"):
            st.success(f"Comando enviado para {player_id}")
        
        # Configurações de IA
        st.sidebar.header("Configurações de IA")
        temperature = st.sidebar.slider("Criatividade", 0.0, 1.0, 0.7)
        max_tokens = st.sidebar.number_input("Máximo de Tokens", 100, 2000, 500)
        
        # Histórico de Eventos
        st.sidebar.header("Últimos Eventos")
        for event in reversed(self.state_manager.state.history[-10:]):
            st.sidebar.text(event.get('summary', ''))

if __name__ == "__main__":
    panel = ControlPanel()
    panel.render()