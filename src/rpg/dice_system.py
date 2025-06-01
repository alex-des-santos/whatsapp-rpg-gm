"""
Sistema de Rolagem de Dados para D&D 5e
Suporte completo para expressões de dados e mecânicas especiais
"""

import re
import random
import logging
from typing import List, Tuple, Dict # Any, Optional removed
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AdvantageType(Enum):
    """Tipos de vantagem/desvantagem"""

    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


@dataclass
class DiceRoll:
    """Resultado de uma rolagem de dados"""

    expression: str
    individual_rolls: List[int]
    modifiers: int
    total: int
    is_critical: bool = False
    is_fumble: bool = False
    advantage_type: AdvantageType = AdvantageType.NORMAL

    @property
    def rolls(self) -> str:
        """String formatada dos dados rolados"""
        if self.advantage_type == AdvantageType.ADVANTAGE:
            return f"[{', '.join(map(str, self.individual_rolls))}] (vantagem)"
        elif self.advantage_type == AdvantageType.DISADVANTAGE:
            return f"[{', '.join(map(str, self.individual_rolls))}] (desvantagem)"
        else:
            return f"[{', '.join(map(str, self.individual_rolls))}]"


class DiceSystem:
    """Sistema de rolagem de dados"""

    def __init__(self):
        self.random = random.Random()
        # Patterns para diferentes tipos de expressões
        self.dice_pattern = re.compile(r"(\d*)d(\d+)([+\-]\d+)?")
        self.modifier_pattern = re.compile(r"[+\-]\d+")

    def roll(
        self, expression: str, advantage: AdvantageType = AdvantageType.NORMAL
    ) -> DiceRoll:
        """
        Rolar dados com base na expressão

        Args:
            expression: Expressão de dados (ex: "1d20+5", "2d6", "1d8+3")
            advantage: Tipo de vantagem (normal, vantagem, desvantagem)

        Returns:
            DiceRoll: Resultado da rolagem
        """
        try:
            expression = expression.lower().replace(" ", "")

            # Verificar se é uma expressão válida
            if not self._is_valid_expression(expression):
                raise ValueError(f"Expressão inválida: {expression}")

            # Extrair componentes
            dice_matches = self.dice_pattern.findall(expression)
            if not dice_matches:
                raise ValueError("Nenhum dado encontrado na expressão")

            all_rolls = []
            total_modifier = 0

            # Processar cada grupo de dados
            for match in dice_matches:
                num_dice = int(match[0]) if match[0] else 1
                die_size = int(match[1])
                modifier = int(match[2]) if match[2] else 0

                # Validar parâmetros
                if num_dice <= 0 or num_dice > 100:
                    raise ValueError("Número de dados deve estar entre 1 e 100")
                if die_size not in [4, 6, 8, 10, 12, 20, 100]:
                    raise ValueError(
                        "Tipo de dado inválido. Use d4, d6, d8, d10, d12, d20 ou d100"
                    )

                # Rolar dados
                rolls = self._roll_dice(num_dice, die_size)
                all_rolls.extend(rolls)
                total_modifier += modifier

            # Aplicar vantagem/desvantagem para d20
            if (
                len(all_rolls) == 1
                and dice_matches[0][1] == "20"
                and advantage != AdvantageType.NORMAL
            ):
                extra_roll = self._roll_dice(1, 20)[0]
                all_rolls.append(extra_roll)

                if advantage == AdvantageType.ADVANTAGE:
                    result_roll = max(all_rolls)
                else:  # DISADVANTAGE
                    result_roll = min(all_rolls)

                final_total = result_roll + total_modifier
            else:
                final_total = sum(all_rolls) + total_modifier

            # Verificar críticos (apenas para d20)
            is_critical = False
            is_fumble = False

            if (
                len(dice_matches) == 1
                and dice_matches[0][1] == "20"
                and len(all_rolls) >= 1
            ):
                highest_roll = (
                    max(all_rolls)
                    if advantage == AdvantageType.ADVANTAGE
                    else all_rolls[0]
                )
                lowest_roll = (
                    min(all_rolls)
                    if advantage == AdvantageType.DISADVANTAGE
                    else all_rolls[0]
                )

                if advantage == AdvantageType.ADVANTAGE:
                    is_critical = highest_roll == 20
                    is_fumble = False
                elif advantage == AdvantageType.DISADVANTAGE:
                    is_critical = False
                    is_fumble = lowest_roll == 1
                else:
                    is_critical = all_rolls[0] == 20
                    is_fumble = all_rolls[0] == 1

            return DiceRoll(
                expression=expression,
                individual_rolls=all_rolls,
                modifiers=total_modifier,
                total=final_total,
                is_critical=is_critical,
                is_fumble=is_fumble,
                advantage_type=advantage,
            )

        except Exception as e:
            logger.error(f"Erro na rolagem de dados: {e}")
            raise

    def _roll_dice(self, num_dice: int, die_size: int) -> List[int]:
        """Rolar múltiplos dados"""
        return [self.random.randint(1, die_size) for _ in range(num_dice)]

    def _is_valid_expression(self, expression: str) -> bool:
        """Validar se a expressão de dados é válida"""
        # Permitir apenas caracteres válidos
        allowed_chars = set("0123456789d+-")
        if not all(c in allowed_chars for c in expression):
            return False

        # Deve conter pelo menos um 'd'
        if "d" not in expression:
            return False

        return True

    def roll_ability_scores(self) -> Dict[str, int]:
        """Rolar atributos iniciais (4d6, descartar o menor)"""
        abilities = [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        scores = {}

        for ability in abilities:
            # Rolar 4d6, descartar o menor
            rolls = [self.random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            score = sum(rolls[:3])  # Somar os 3 maiores
            scores[ability] = score

        return scores

    def roll_hp(self, hit_die: int, constitution_modifier: int, level: int) -> int:
        """Rolar HP para level up"""
        if level == 1:
            # Nível 1 sempre recebe HP máximo
            return hit_die + constitution_modifier
        else:
            # Níveis seguintes rolam o dado
            roll = self.random.randint(1, hit_die)
            return roll + constitution_modifier

    def roll_initiative(self, dexterity_modifier: int) -> DiceRoll:
        """Rolar iniciativa"""
        return self.roll(f"1d20{dexterity_modifier:+d}")

    def roll_attack(
        self, attack_bonus: int, advantage: AdvantageType = AdvantageType.NORMAL
    ) -> DiceRoll:
        """Rolar ataque"""
        return self.roll(f"1d20{attack_bonus:+d}", advantage)

    def roll_damage(self, damage_dice: str, damage_bonus: int = 0) -> DiceRoll:
        """Rolar dano"""
        expression = damage_dice
        if damage_bonus != 0:
            expression += f"{damage_bonus:+d}"
        return self.roll(expression)

    def roll_save(
        self, save_bonus: int, dc: int, advantage: AdvantageType = AdvantageType.NORMAL
    ) -> Tuple[DiceRoll, bool]:
        """
        Rolar teste de resistência

        Returns:
            Tuple[DiceRoll, bool]: (resultado da rolagem, sucesso)
        """
        roll_result = self.roll(f"1d20{save_bonus:+d}", advantage)
        success = roll_result.total >= dc
        return roll_result, success

    def roll_ability_check(
        self,
        ability_modifier: int,
        proficiency_bonus: int = 0,
        advantage: AdvantageType = AdvantageType.NORMAL,
    ) -> DiceRoll:
        """Rolar teste de habilidade"""
        total_bonus = ability_modifier + proficiency_bonus
        return self.roll(f"1d20{total_bonus:+d}", advantage)

    def roll_skill_check(
        self, skill_modifier: int, advantage: AdvantageType = AdvantageType.NORMAL
    ) -> DiceRoll:
        """Rolar teste de perícia"""
        return self.roll(f"1d20{skill_modifier:+d}", advantage)


# Funções utilitárias
def get_modifier(ability_score: int) -> int:
    """Calcular modificador baseado no atributo"""
    return (ability_score - 10) // 2


def get_proficiency_bonus(level: int) -> int:
    """Calcular bônus de proficiência baseado no nível"""
    return (level - 1) // 4 + 2


def calculate_ac(
    base_ac: int, dex_modifier: int, armor_bonus: int = 0, shield_bonus: int = 0
) -> int:
    """Calcular Classe de Armadura"""
    return base_ac + dex_modifier + armor_bonus + shield_bonus


def calculate_spell_save_dc(
    spellcasting_ability_modifier: int, proficiency_bonus: int
) -> int:
    """Calcular DC de resistência de magias"""
    return 8 + spellcasting_ability_modifier + proficiency_bonus


def calculate_spell_attack_bonus(
    spellcasting_ability_modifier: int, proficiency_bonus: int
) -> int:
    """Calcular bônus de ataque mágico"""
    return spellcasting_ability_modifier + proficiency_bonus
