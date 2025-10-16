# Soporta ambos layouts, por si tu pythonpath apunta a 'src' o a la raíz
try:
    from src.validation import is_valid_message
except ImportError:
    from src.validation import is_valid_message

def test_rejects_none_empty_and_spaces():
    assert is_valid_message(None) is False
    assert is_valid_message("") is False
    assert is_valid_message("   ") is False
    assert is_valid_message("\n") is False
    assert is_valid_message(" \r\n ") is False

def test_accepts_normal_message():
    assert is_valid_message("hola mundo") is True
    assert is_valid_message("  hola   ") is True  # espacios alrededor ok

def test_rejects_too_long():
    assert is_valid_message("a" * 257) is False

def test_accepts_exact_limit():
    assert is_valid_message("a" * 256) is True
