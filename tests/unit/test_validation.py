"""
Validación de mensajes del chat.
Reglas:
- No nulos.
- No vacíos (ni solo espacios) tras quitar \r\n y espacios extremos.
- Máximo 256 chars.
"""

MAX_LEN = 256

def is_valid_message(text: str) -> bool:
    if text is None:
        return False
    # Primero quitamos solo saltos de línea finales para no “matar” espacios internos
    trimmed_newlines = text.strip("\r\n")
    # Luego validamos contenido no vacío al remover espacios a los costados
    if trimmed_newlines.strip() == "":
        return False
    if len(trimmed_newlines) > MAX_LEN:
        return False
    return True
