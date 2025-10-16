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
    # Quitamos solo saltos de línea de los extremos
    trimmed_newlines = text.strip("\r\n")
    # Debe quedar algo de contenido (que no sea solo espacios)
    if trimmed_newlines.strip() == "":
        return False
    # Longitud máxima
    if len(trimmed_newlines) > MAX_LEN:
        return False
    return True
