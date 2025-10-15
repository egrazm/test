"""
Validación de mensajes del chat.
Reglas:
- No nulos.
- No vacíos (ni solo espacios) tras quitar \r\n y espacios extremos.
- Máximo 256 chars.
"""

MAX_LEN = 256

def is_valid_message(text: str) -> bool:
    """Devuelve True si `text` cumple las reglas del protocolo."""
    # Día 2 (TDD) implementará esta función.
    return False  # placeholder para que las primeras pruebas fallen (RED)
