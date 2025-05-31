"""
Sistema de Rolagem de Dados para D&D 5e
Utiliza a biblioteca 'dice' para parsing e avaliação de notação de dados
"""

import re
import random
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

try:
    import dice
    DICE_LIBRARY_AVAILABLE = True
except ImportError:
    DICE_LIBRARY_AVAILABLE = False
    logger.warning("Biblioteca 'dice' não encontrada, usando implementação simples")


@dataclass
class DiceResult:
    """Resultado de uma rolagem de dados"""
    expression: str
    total: int
    individual_rolls: List[int]
    modifiers: int
    critical: bool = False
    fumble: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Converte resultado para dicionário"""
        return {
            "expression": self.expression,
            "total": self.total,
            "individual_rolls": self.individual_rolls,
            "modifiers": self.modifiers,
            "critical": self.critical,
            "fumble": self.fumble,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SkillCheck:
    """Resultado de um teste de habilidade"""
    skill_name: str
    dice_result: DiceResult
    difficulty_class: int
    success: bool
    character_name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Converte teste para dicionário"""
        return {
            "skill_name": self.skill_name,
            "dice_result": self.dice_result.to_dict(),
            "difficulty_class": self.difficulty_class,
            "success": self.success,
            "character_name": self.character_name
        }


class DiceSystem:
    """Sistema principal de rolagem de dados"""
    
    def __init__(self):
        self.roll_history: List[DiceResult] = []
        self._ready = True
        
        # Configurações D&D 5e
        self.advantage_disadvantage = {
            "advantage": "roll twice, take highest",
            "disadvantage": "roll twice, take lowest"
        }
        
        # DCs padrão D&D 5e
        self.standard_dcs = {
            "very_easy": 5,
            "easy": 10,
            "medium": 15,
            "hard": 20,
            "very_hard": 25,
            "nearly_impossible": 30
        }
        
        # Modificadores de habilidade
        self.skill_modifiers = {
            "strength": ["athletics"],
            "dexterity": ["acrobatics", "sleight_of_hand", "stealth"],
            "intelligence": ["arcana", "history", "investigation", "nature", "religion"],
            "wisdom": ["animal_handling", "insight", "medicine", "perception", "survival"],
            "charisma": ["deception", "intimidation", "performance", "persuasion"]
        }
        
    def is_ready(self) -> bool:
        """Verifica se o sistema está pronto"""
        return self._ready
    
    def roll(self, expression: str, advantage: Optional[str] = None) -> DiceResult:
        """
        Rola dados usando expressão padrão
        
        Args:
            expression: Expressão de dados (ex: "1d20+5", "2d6", "1d8+3")
            advantage: "advantage", "disadvantage" ou None
        
        Returns:
            DiceResult com resultado da rolagem
        """
        try:
            if DICE_LIBRARY_AVAILABLE:
                return self._roll_with_library(expression, advantage)
            else:
                return self._roll_simple(expression, advantage)
        
        except Exception as e:
            logger.error(f"Erro na rolagem de dados: {e}")
            # Fallback para rolagem simples
            return self._roll_simple("1d20", advantage)
    
    def _roll_with_library(self, expression: str, advantage: Optional[str] = None) -> DiceResult:
        """Rola dados usando a biblioteca 'dice'"""
        try:
            # Rolar uma vez ou duas (para advantage/disadvantage)
            rolls_needed = 2 if advantage in ["advantage", "disadvantage"] else 1
            
            results = []
            individual_rolls_all = []
            
            for _ in range(rolls_needed):
                result = dice.roll(expression)
                results.append(int(result))
                
                # Extrair rolagens individuais (simplificado)
                individual_rolls = self._extract_individual_rolls(expression, int(result))
                individual_rolls_all.extend(individual_rolls)
            
            # Aplicar advantage/disadvantage
            if advantage == "advantage":
                total = max(results)
            elif advantage == "disadvantage":
                total = min(results)
            else:
                total = results[0]
            
            # Detectar críticos e falhas críticas (apenas para d20)
            critical = False
            fumble = False
            if "d20" in expression.lower():
                natural_rolls = [r for r in individual_rolls_all if r in [1, 20]]
                critical = 20 in natural_rolls
                fumble = 1 in natural_rolls
            
            modifiers = self._extract_modifiers(expression)
            
            result = DiceResult(
                expression=expression,
                total=total,
                individual_rolls=individual_rolls_all,
                modifiers=modifiers,
                critical=critical,
                fumble=fumble
            )
            
            self.roll_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Erro na biblioteca dice: {e}")
            return self._roll_simple(expression, advantage)
    
    def _roll_simple(self, expression: str, advantage: Optional[str] = None) -> DiceResult:
        """Implementação simples de rolagem sem biblioteca externa"""
        try:
            # Parse da expressão (ex: "2d6+3", "1d20", "3d8-2")
            pattern = r'(\d*)d(\d+)([+-]\d+)?'
            match = re.match(pattern, expression.strip())
            
            if not match:
                # Fallback para 1d20
                num_dice, sides, modifier = 1, 20, 0
            else:
                num_dice = int(match.group(1)) if match.group(1) else 1
                sides = int(match.group(2))
                modifier = int(match.group(3)) if match.group(3) else 0
            
            # Rolar dados
            rolls_needed = 2 if advantage in ["advantage", "disadvantage"] else 1
            all_totals = []
            all_individual_rolls = []
            
            for _ in range(rolls_needed):
                individual_rolls = [random.randint(1, sides) for _ in range(num_dice)]
                total_without_modifier = sum(individual_rolls)
                total_with_modifier = total_without_modifier + modifier
                
                all_totals.append(total_with_modifier)
                all_individual_rolls.extend(individual_rolls)
            
            # Aplicar advantage/disadvantage
            if advantage == "advantage":
                final_total = max(all_totals)
            elif advantage == "disadvantage":
                final_total = min(all_totals)
            else:
                final_total = all_totals[0]
            
            # Detectar críticos (apenas para d20)
            critical = False
            fumble = False
            if sides == 20:
                natural_rolls = [r for r in all_individual_rolls if r in [1, 20]]
                critical = 20 in natural_rolls
                fumble = 1 in natural_rolls and final_total <= 1 + modifier
            
            result = DiceResult(
                expression=expression,
                total=final_total,
                individual_rolls=all_individual_rolls,
                modifiers=modifier,
                critical=critical,
                fumble=fumble
            )
            
            self.roll_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Erro na rolagem simples: {e}")
            # Último fallback
            total = random.randint(1, 20)
            return DiceResult(
                expression="1d20",
                total=total,
                individual_rolls=[total],
                modifiers=0,
                critical=total == 20,
                fumble=total == 1
            )
    
    def _extract_individual_rolls(self, expression: str, total: int) -> List[int]:
        """Extrai rolagens individuais de uma expressão (simplificado)"""
        # Esta é uma versão simplificada
        # Em uma implementação completa, seria mais complexa
        return [total]  # Placeholder
    
    def _extract_modifiers(self, expression: str) -> int:
        """Extrai modificadores de uma expressão"""
        pattern = r'([+-]\d+)'
        matches = re.findall(pattern, expression)
        return sum(int(match) for match in matches)
    
    def skill_check(self, skill_name: str, modifier: int, difficulty_class: int, 
                   advantage: Optional[str] = None, character_name: Optional[str] = None) -> SkillCheck:
        """
        Realiza teste de habilidade D&D 5e
        
        Args:
            skill_name: Nome da habilidade
            modifier: Modificador total da habilidade
            difficulty_class: Classe de Dificuldade (DC)
            advantage: "advantage", "disadvantage" ou None
            character_name: Nome do personagem (opcional)
        
        Returns:
            SkillCheck com resultado do teste
        """
        try:
            expression = f"1d20+{modifier}" if modifier >= 0 else f"1d20{modifier}"
            dice_result = self.roll(expression, advantage)
            
            success = dice_result.total >= difficulty_class
            
            skill_check_result = SkillCheck(
                skill_name=skill_name,
                dice_result=dice_result,
                difficulty_class=difficulty_class,
                success=success,
                character_name=character_name
            )
            
            logger.info(f"Teste de {skill_name}: {dice_result.total} vs DC {difficulty_class} - {'SUCESSO' if success else 'FALHA'}")
            
            return skill_check_result
            
        except Exception as e:
            logger.error(f"Erro no teste de habilidade: {e}")
            raise
    
    def saving_throw(self, save_type: str, modifier: int, difficulty_class: int,
                    advantage: Optional[str] = None, character_name: Optional[str] = None) -> SkillCheck:
        """Realiza teste de resistência"""
        return self.skill_check(f"Saving Throw ({save_type})", modifier, difficulty_class, advantage, character_name)
    
    def attack_roll(self, attack_bonus: int, armor_class: int, 
                   advantage: Optional[str] = None, character_name: Optional[str] = None) -> SkillCheck:
        """Realiza rolagem de ataque"""
        return self.skill_check("Attack Roll", attack_bonus, armor_class, advantage, character_name)
    
    def damage_roll(self, damage_expression: str) -> DiceResult:
        """Rola dano"""
        return self.roll(damage_expression)
    
    def get_ability_modifier(self, ability_score: int) -> int:
        """Calcula modificador de habilidade D&D 5e"""
        return (ability_score - 10) // 2
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Calcula bônus de proficiência baseado no nível"""
        return 2 + ((level - 1) // 4)
    
    def get_roll_history(self, limit: int = 10) -> List[Dict]:
        """Obtém histórico de rolagens"""
        return [result.to_dict() for result in self.roll_history[-limit:]]
    
    def clear_history(self):
        """Limpa histórico de rolagens"""
        self.roll_history.clear()
        logger.info("Histórico de rolagens limpo")
    
    def format_roll_result(self, result: DiceResult) -> str:
        """Formata resultado de rolagem para exibição"""
        base_text = f"🎲 {result.expression}: **{result.total}**"
        
        if len(result.individual_rolls) > 1:
            rolls_text = " + ".join(map(str, result.individual_rolls))
            if result.modifiers != 0:
                modifier_text = f" + {result.modifiers}" if result.modifiers > 0 else f" {result.modifiers}"
                base_text += f" ({rolls_text}{modifier_text})"
            else:
                base_text += f" ({rolls_text})"
        
        if result.critical:
            base_text += " ✨ **CRÍTICO!**"
        elif result.fumble:
            base_text += " 💥 **FALHA CRÍTICA!**"
        
        return base_text
    
    def format_skill_check(self, check: SkillCheck) -> str:
        """Formata teste de habilidade para exibição"""
        result_emoji = "✅" if check.success else "❌"
        success_text = "SUCESSO" if check.success else "FALHA"
        
        text = f"{result_emoji} **{check.skill_name}**: {check.dice_result.total} vs DC {check.difficulty_class} - **{success_text}**"
        
        if check.character_name:
            text = f"**{check.character_name}** - {text}"
        
        if check.dice_result.critical:
            text += " ✨ **CRÍTICO!**"
        elif check.dice_result.fumble:
            text += " 💥 **FALHA CRÍTICA!**"
        
        return text