import random
import re

class DiceRoller:
    @staticmethod
    def roll(dice_code):
        """Roll dice in D&D notation (e.g., '2d6+3')"""
        match = re.match(r"(\d+)d(\d+)([\+\-]\d+)?", dice_code)
        if not match:
            return "Formato inválido! Use 'NdM±X' (ex: 2d6+1)"
        
        num_dice = int(match.group(1))
        dice_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        rolls = [random.randint(1, dice_size) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return {
            "result": total,
            "rolls": rolls,
            "modifier": modifier,
            "expression": dice_code
        }
    
    @staticmethod
    def skill_check(attribute_value, difficulty=10):
        roll = random.randint(1, 20)
        success = (roll + attribute_value) >= difficulty
        return {
            "roll": roll,
            "total": roll + attribute_value,
            "success": success,
            "dc": difficulty
        }