from integration.whatsapp_evolution import WhatsAppIntegration
from config import Config

class InterventionSystem:
    def __init__(self):
        self.whatsapp = WhatsAppIntegration()
    
    def request_intervention(self, context, player_id, confidence):
        message = (
            "⚠️ **INTERVENÇÃO REQUERIDA** ⚠️\n"
            f"Jogador: {player_id}\n"
            f"Confiança: {confidence:.2f}\n\n"
            f"Contexto:\n{context}"
        )
        self.whatsapp.send_message(Config.GM_PHONE, message)
    
    def process_gm_response(self, response, original_context):
        # Implementar lógica para aplicar decisão do GM
        pass