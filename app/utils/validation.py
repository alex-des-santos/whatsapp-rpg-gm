"""
Utilitários de validação para WhatsApp RPG GM
Implementa funções auxiliares para sanitização e validação de dados
"""

import re
import unicodedata
from typing import Optional, List, Dict, Any


def sanitize_name(name: str) -> str:
    """
    Sanitiza e normaliza nome de personagem
    Remove caracteres especiais e normaliza formatação
    
    Args:
        name: Nome a ser sanitizado
        
    Returns:
        Nome sanitizado e normalizado
    """
    if not name:
        return ""
    
    # Remover espaços extras no início e fim
    name = name.strip()
    
    # Normalizar Unicode (NFD - decomposição)
    name = unicodedata.normalize('NFD', name)
    
    # Remover caracteres de controle e não-printáveis
    name = ''.join(char for char in name if unicodedata.category(char) != 'Cc')
    
    # Normalizar espaços internos (múltiplos espaços viram um)
    name = re.sub(r'\s+', ' ', name)
    
    # Capitalizar primeira letra de cada palavra
    name = name.title()
    
    return name


def validate_whatsapp_number(number: str) -> bool:
    """
    Valida número de WhatsApp
    
    Args:
        number: Número a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not number:
        return False
    
    # Remover caracteres não numéricos
    clean_number = re.sub(r'\D', '', number)
    
    # Verificar comprimento (8-15 dígitos)
    if len(clean_number) < 8 or len(clean_number) > 15:
        return False
    
    # Verificar se não é só zeros
    if clean_number == '0' * len(clean_number):
        return False
    
    return True


def sanitize_whatsapp_number(number: str) -> str:
    """
    Sanitiza número de WhatsApp removendo caracteres especiais
    
    Args:
        number: Número a ser sanitizado
        
    Returns:
        Número limpo apenas com dígitos
    """
    if not number:
        return ""
    
    # Remover tudo que não é dígito
    clean_number = re.sub(r'\D', '', number)
    
    return clean_number


def validate_dice_notation(dice_str: str) -> bool:
    """
    Valida notação de dados (ex: 1d20, 2d6+3, 1d8-1)
    
    Args:
        dice_str: String com notação de dados
        
    Returns:
        True se válida, False caso contrário
    """
    if not dice_str:
        return False
    
    # Padrão: [número]d[lados][+/-][modificador]
    pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
    
    # Limpar espaços e converter para minúsculo
    dice_str = dice_str.strip().lower()
    
    return bool(re.match(pattern, dice_str))


def parse_dice_notation(dice_str: str) -> Dict[str, int]:
    """
    Faz parse de notação de dados
    
    Args:
        dice_str: String com notação de dados
        
    Returns:
        Dicionário com componentes do dado
    """
    if not validate_dice_notation(dice_str):
        raise ValueError(f"Notação de dados inválida: {dice_str}")
    
    # Limpar e normalizar
    dice_str = dice_str.strip().lower()
    
    # Pattern para capturar grupos
    pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
    match = re.match(pattern, dice_str)
    
    if not match:
        raise ValueError(f"Não foi possível fazer parse de: {dice_str}")
    
    # Extrair componentes
    quantity = int(match.group(1) or 1)  # Default 1 se não especificado
    sides = int(match.group(2))
    modifier_str = match.group(3) or "+0"
    
    # Parse do modificador
    if modifier_str.startswith('+'):
        modifier = int(modifier_str[1:])
    else:  # Começa com '-'
        modifier = -int(modifier_str[1:])
    
    return {
        "quantity": quantity,
        "sides": sides,
        "modifier": modifier
    }


def validate_character_name_format(name: str) -> List[str]:
    """
    Valida formato de nome de personagem e retorna lista de problemas
    
    Args:
        name: Nome a ser validado
        
    Returns:
        Lista de problemas encontrados (vazia se válido)
    """
    issues = []
    
    if not name:
        issues.append("Nome não pode estar vazio")
        return issues
    
    # Sanitizar primeiro
    clean_name = sanitize_name(name)
    
    # Comprimento mínimo e máximo
    if len(clean_name) < 2:
        issues.append("Nome deve ter pelo menos 2 caracteres")
    
    if len(clean_name) > 50:
        issues.append("Nome deve ter no máximo 50 caracteres")
    
    # Verificar se contém apenas letras, espaços e apostrofes
    if not re.match(r"^[a-zA-ZÀ-ÿ\s']+$", clean_name):
        issues.append("Nome deve conter apenas letras, espaços e apostrofes")
    
    # Verificar se não é só espaços
    if clean_name.isspace():
        issues.append("Nome não pode ser apenas espaços")
    
    # Verificar palavras proibidas
    forbidden_words = [
        "admin", "system", "test", "null", "undefined",
        "gm", "master", "god", "admin"
    ]
    
    if clean_name.lower() in forbidden_words:
        issues.append(f"Nome '{clean_name}' não é permitido")
    
    return issues


def validate_equipment_format(equipment: List[Dict[str, Any]]) -> List[str]:
    """
    Valida formato de lista de equipamentos
    
    Args:
        equipment: Lista de equipamentos
        
    Returns:
        Lista de problemas encontrados
    """
    issues = []
    
    if not isinstance(equipment, list):
        issues.append("Equipamentos devem ser uma lista")
        return issues
    
    for i, item in enumerate(equipment):
        if not isinstance(item, dict):
            issues.append(f"Item {i+1}: deve ser um objeto")
            continue
        
        # Verificar campos obrigatórios
        if "name" not in item:
            issues.append(f"Item {i+1}: campo 'name' é obrigatório")
        
        if "quantity" not in item:
            issues.append(f"Item {i+1}: campo 'quantity' é obrigatório")
        else:
            # Validar quantidade
            if not isinstance(item["quantity"], int) or item["quantity"] < 0:
                issues.append(f"Item {i+1}: 'quantity' deve ser um número inteiro positivo")
        
        # Validar nome se presente
        if "name" in item and not isinstance(item["name"], str):
            issues.append(f"Item {i+1}: 'name' deve ser uma string")
        
        if "name" in item and len(item["name"].strip()) == 0:
            issues.append(f"Item {i+1}: 'name' não pode estar vazio")
    
    return issues


def validate_spells_format(spells: Dict[str, List[str]]) -> List[str]:
    """
    Valida formato de dicionário de magias
    
    Args:
        spells: Dicionário com magias por nível
        
    Returns:
        Lista de problemas encontrados
    """
    issues = []
    
    if not isinstance(spells, dict):
        issues.append("Magias devem ser um dicionário")
        return issues
    
    valid_levels = [
        "cantrips", "level_1", "level_2", "level_3", "level_4",
        "level_5", "level_6", "level_7", "level_8", "level_9"
    ]
    
    for level, spell_list in spells.items():
        # Verificar se nível é válido
        if level not in valid_levels:
            issues.append(f"Nível de magia inválido: {level}")
            continue
        
        # Verificar se é lista
        if not isinstance(spell_list, list):
            issues.append(f"Magias do {level} devem ser uma lista")
            continue
        
        # Verificar magias individuais
        for i, spell in enumerate(spell_list):
            if not isinstance(spell, str):
                issues.append(f"{level}, magia {i+1}: deve ser uma string")
            elif len(spell.strip()) == 0:
                issues.append(f"{level}, magia {i+1}: nome não pode estar vazio")
    
    return issues


def clean_text_for_whatsapp(text: str) -> str:
    """
    Limpa texto para envio via WhatsApp
    Remove/substitui caracteres problemáticos
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo para WhatsApp
    """
    if not text:
        return ""
    
    # Normalizar quebras de linha
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Limitar quebras de linha consecutivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remover espaços no final das linhas
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    
    # Limitar comprimento (WhatsApp tem limite)
    if len(text) > 4000:
        text = text[:3997] + "..."
    
    return text


def format_character_sheet_for_whatsapp(character_data: Dict[str, Any]) -> str:
    """
    Formata ficha de personagem para exibição no WhatsApp
    
    Args:
        character_data: Dados do personagem
        
    Returns:
        Ficha formatada para WhatsApp
    """
    name = character_data.get("name", "Desconhecido")
    level = character_data.get("level", 1)
    race = character_data.get("race", "")
    char_class = character_data.get("character_class", "")
    
    # Atributos
    attrs = character_data.get("attributes", {})
    mods = character_data.get("modifiers", {})
    
    # HP
    hp = character_data.get("hit_points", {})
    current_hp = hp.get("current", 0)
    max_hp = hp.get("max", 0)
    hp_status = hp.get("status", "Desconhecido")
    
    # Experiência
    exp = character_data.get("experience", {})
    current_exp = exp.get("current", 0)
    needed_exp = exp.get("needed_for_next", 0)
    
    # Formatação
    sheet = f"""🎭 **{name}**
📊 **Nível {level} {race} {char_class}**

⚔️ **Atributos:**
💪 FOR: {attrs.get('strength', 10)} ({mods.get('strength', 0):+d})
🏃 DES: {attrs.get('dexterity', 10)} ({mods.get('dexterity', 0):+d})
🛡️ CON: {attrs.get('constitution', 10)} ({mods.get('constitution', 0):+d})
🧠 INT: {attrs.get('intelligence', 10)} ({mods.get('intelligence', 0):+d})
🦉 SAB: {attrs.get('wisdom', 10)} ({mods.get('wisdom', 0):+d})
💬 CAR: {attrs.get('charisma', 10)} ({mods.get('charisma', 0):+d})

❤️ **HP:** {current_hp}/{max_hp} ({hp_status})
🛡️ **CA:** {character_data.get('armor_class', 10)}
⭐ **XP:** {current_exp} ({needed_exp} para próximo nível)

🎯 **Bônus Prof.:** +{character_data.get('proficiency_bonus', 2)}"""
    
    return clean_text_for_whatsapp(sheet)


def validate_json_structure(data: Any, schema: Dict[str, Any]) -> List[str]:
    """
    Valida estrutura JSON contra schema simples
    
    Args:
        data: Dados a serem validados
        schema: Schema de validação
        
    Returns:
        Lista de problemas encontrados
    """
    issues = []
    
    def validate_field(value, field_schema, field_path=""):
        field_issues = []
        
        # Verificar tipo
        expected_type = field_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                field_issues.append(f"{field_path}: deve ser string")
            elif expected_type == "integer" and not isinstance(value, int):
                field_issues.append(f"{field_path}: deve ser inteiro")
            elif expected_type == "number" and not isinstance(value, (int, float)):
                field_issues.append(f"{field_path}: deve ser número")
            elif expected_type == "boolean" and not isinstance(value, bool):
                field_issues.append(f"{field_path}: deve ser boolean")
            elif expected_type == "array" and not isinstance(value, list):
                field_issues.append(f"{field_path}: deve ser array")
            elif expected_type == "object" and not isinstance(value, dict):
                field_issues.append(f"{field_path}: deve ser objeto")
        
        # Verificar valor mínimo
        if "minimum" in field_schema and isinstance(value, (int, float)):
            if value < field_schema["minimum"]:
                field_issues.append(f"{field_path}: valor mínimo é {field_schema['minimum']}")
        
        # Verificar valor máximo
        if "maximum" in field_schema and isinstance(value, (int, float)):
            if value > field_schema["maximum"]:
                field_issues.append(f"{field_path}: valor máximo é {field_schema['maximum']}")
        
        # Verificar comprimento mínimo
        if "minLength" in field_schema and isinstance(value, str):
            if len(value) < field_schema["minLength"]:
                field_issues.append(f"{field_path}: comprimento mínimo é {field_schema['minLength']}")
        
        # Verificar comprimento máximo
        if "maxLength" in field_schema and isinstance(value, str):
            if len(value) > field_schema["maxLength"]:
                field_issues.append(f"{field_path}: comprimento máximo é {field_schema['maxLength']}")
        
        return field_issues
    
    # Validar campos obrigatórios
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            issues.append(f"Campo obrigatório '{field}' não encontrado")
    
    # Validar propriedades
    properties = schema.get("properties", {})
    for field_name, field_schema in properties.items():
        if field_name in data:
            field_issues = validate_field(data[field_name], field_schema, field_name)
            issues.extend(field_issues)
    
    return issues