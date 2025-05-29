import json
import os
from .models import GameState, Character

class GameStateManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = self._load_state()
    
    def _load_state(self):
        if not os.path.exists(self.file_path):
            return GameState()
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return GameState(**data)
        except:
            return GameState()
    
    def save_state(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.state.dict(), f, indent=2)
    
    def get_character(self, player_id):
        return self.state.characters.get(player_id, Character())
    
    def update_character(self, player_id, character_data):
        if player_id not in self.state.characters:
            self.state.characters[player_id] = Character()
        self.state.characters[player_id].update(**character_data)
        self.save_state()
    
    def add_game_event(self, event):
        self.state.history.append(event)
        if len(self.state.history) > 100:  # Keep last 100 events
            self.state.history.pop(0)
        self.save_state()