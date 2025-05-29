import requests
from config import Config

class WhatsAppIntegration:
    def __init__(self):
        self.base_url = Config.EVOLUTION_API_URL
        self.headers = {
            "apikey": Config.EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
    
    def send_message(self, to, message, buttons=None):
        payload = {
            "number": to,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": message
            }
        }
        
        if buttons:
            payload["buttonMessage"] = {
                "buttons": buttons,
                "text": message,
                "footer": "Escolha uma ação"
            }
        
        response = requests.post(
            f"{self.base_url}/message/send",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def process_incoming(self, message_data):
        # Implementar lógica de processamento de mensagens
        pass