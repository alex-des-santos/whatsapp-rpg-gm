# src/core/game_state.py
class GameStateManager:
    def __init__(self):
        self.players = {}
        self.world_state = {
            'current_scene': 'Taverna do Dragão',
            'active_quest': 'Mistério dos Comerciantes'
        }

    async def update_character(self, character_id, updates):
        self.players[character_id].update(updates)
        await self.emit_state_update()
