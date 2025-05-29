from integration.whatsapp_evolution import WhatsAppIntegration
from core.game_state.manager import GameStateManager
from core.ai_module.llm_integration import AIModule
from core.dice_system.roller import DiceRoller
from core.hitl.intervention import InterventionSystem
from config import Config
import threading

def start_whatsapp_listener():
    whatsapp = WhatsAppIntegration()
    state_manager = GameStateManager(Config.GAME_STATE_PATH)
    ai_module = AIModule()
    dice_roller = DiceRoller()
    hitl_system = InterventionSystem()
    
    # Aqui você implementaria o loop de escuta de mensagens
    # usando a API da Evolution

def start_gui():
    from gui.control_panel import ControlPanel
    panel = ControlPanel()
    panel.render()

if __name__ == "__main__":
    # Iniciar GUI em thread separada
    gui_thread = threading.Thread(target=start_gui)
    gui_thread.start()
    
    # Iniciar listener do WhatsApp
    start_whatsapp_listener()