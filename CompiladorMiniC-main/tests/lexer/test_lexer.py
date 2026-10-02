"""Pruebas exhaustivas del analizador léxico de Mini C.

Verifica la especificación del skill 'analizador-lexico-mini-c' (Taller N°6):
alfabeto, palabras reservadas, tipos de token, políticas de separación,
prioridades, posiciones, formato de salida y diagnósticos LEX001.
"""

from minic.compiler import compile_source
from minic.diagnostics.diagnostic import Diagnostic
from minic.lexer.lexer import Lexer
from minic.lexer.token import Token
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section_7_case_1_tokens_and_format() -> None:
    """Caso 1 de la sección 7 de la especificación:

    Fuente:
        int2 = 12abc;
        whilex == -5
    """
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    formatted = [format_token(t) for t in tokens]
    expected_lines = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected_lines

    # Verificación de los atributos de cada Token
    assert tokens[0] == Token(TokenType.IDENTIFIER, "int2", None, 1, 1)
    assert tokens[1] == Token(TokenType.ASSIGN, "=", None, 1, 6)
    assert tokens[2] == Token(TokenType.INTEGER_LITERAL, "12", 12, 1, 8)
    assert tokens[3] == Token(TokenType.IDENTIFIER, "abc", None, 1, 10)
    assert tokens[4] == Token(TokenType.SEMICOLON, ";", None, 1, 13)
    assert tokens[5] == Token(TokenType.IDENTIFIER, "whilex", None, 2, 1)
    assert tokens[6] == Token(TokenType.EQUAL_EQUAL, "==", None, 2, 8)
    assert tokens[7] == Token(TokenType.MINUS, "-", None, 2, 11)
    assert tokens[8] == Token(TokenType.INTEGER_LITERAL, "5", 5, 2, 12)
    assert tokens[9] == Token(TokenType.EOF, "", None, 2, 13)


def test_section_7_case_2_with_errors() -> None:
    """Caso 2 de la sección 7 de la especificación (fuente con errores):

    Fuente:
        int x = @;
        x ! = 0; // fin
    """
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    # Diagnósticos esperados
    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diagnostics

    # Tokens esperados
    formatted_tokens = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_tokens


def test_all_15_token_types() -> None:
    """Reconoce los 15 tipos de token de TokenType."""
    source = "int while x 42 = + - == != ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    types = [t.type for t in tokens]
    assert types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.INTEGER_LITERAL,
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_keywords_vs_identifiers_priority() -> None:
    """Prioridad Grupo 1: KW_INT / KW_WHILE > IDENTIFIER tras leer el nombre completo."""
    source = "int integer while while1 _int _while"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    expected = [
        (TokenType.KW_INT, "int"),
        (TokenType.IDENTIFIER, "integer"),
        (TokenType.KW_WHILE, "while"),
        (TokenType.IDENTIFIER, "while1"),
        (TokenType.IDENTIFIER, "_int"),
        (TokenType.IDENTIFIER, "_while"),
        (TokenType.EOF, ""),
    ]
    actual = [(t.type, t.lexeme) for t in tokens]
    assert actual == expected


def test_double_vs_single_operators_priority() -> None:
    """Prioridad Grupo 2: EQUAL_EQUAL > ASSIGN (máxima coincidencia)."""
    source = "=== =="
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    actual = [(t.type, t.lexeme) for t in tokens]
    assert actual == [
        (TokenType.EQUAL_EQUAL, "=="),
        (TokenType.ASSIGN, "="),
        (TokenType.EQUAL_EQUAL, "=="),
        (TokenType.EOF, ""),
    ]


def test_integer_literal_values_and_separation() -> None:
    """Literales enteros: valor numérico int, regla 5 (12abc -> 12 y abc)."""
    source = "007 12345 0 999abc"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert tokens[0] == Token(TokenType.INTEGER_LITERAL, "007", 7, 1, 1)
    assert tokens[1] == Token(TokenType.INTEGER_LITERAL, "12345", 12345, 1, 5)
    assert tokens[2] == Token(TokenType.INTEGER_LITERAL, "0", 0, 1, 11)
    assert tokens[3] == Token(TokenType.INTEGER_LITERAL, "999", 999, 1, 13)
    assert tokens[4] == Token(TokenType.IDENTIFIER, "abc", None, 1, 16)
    assert tokens[5].type == TokenType.EOF


def test_whitespace_and_position_rules() -> None:
    """Reglas de posición:

    - \\t cuenta como 1 columna.
    - \\r suelto cuenta como 1 columna (no abre línea).
    - Solo \\n abre nueva línea y reinicia columna en 1.
    """
    source = "a\tb\rc\nd"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    # 'a' está en 1:1, \t es 1:2 -> 'b' está en 1:3
    # \r es 1:4 -> 'c' está en 1:5
    # \n salta a línea 2, columna 1 -> 'd' está en 2:1
    assert tokens[0] == Token(TokenType.IDENTIFIER, "a", None, 1, 1)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "b", None, 1, 3)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "c", None, 1, 5)
    assert tokens[3] == Token(TokenType.IDENTIFIER, "d", None, 2, 1)
    assert tokens[4] == Token(TokenType.EOF, "", None, 2, 2)


def test_empty_source() -> None:
    """Fuente vacía produce exactamente un EOF en línea 1 columna 1."""
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0] == Token(TokenType.EOF, "", None, 1, 1)


def test_trailing_newline_eof_position() -> None:
    """Fuente con \\n final coloca EOF en la nueva línea."""
    tokens, diagnostics = Lexer("int x;\n").scan()
    assert diagnostics == []
    assert tokens[-1] == Token(TokenType.EOF, "", None, 2, 1)


def test_unrecognized_characters_recovery() -> None:
    """Múltiples caracteres no reconocidos generan LEX001 y continúan hasta EOF."""
    source = "$ % &"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 3
    assert diagnostics[0] == Diagnostic("LEX001", "error", "Carácter no reconocido: '$'", 1, 1)
    assert diagnostics[1] == Diagnostic("LEX001", "error", "Carácter no reconocido: '%'", 1, 3)
    assert diagnostics[2] == Diagnostic("LEX001", "error", "Carácter no reconocido: '&'", 1, 5)
    assert len(tokens) == 1
    assert tokens[0] == Token(TokenType.EOF, "", None, 1, 6)


def test_compile_source_integration() -> None:
    """Integración con compiler.compile_source(text, stages=('lexer',))."""
    result = compile_source("int x = 10;")
    assert result.diagnostics == []
    assert result.tokens is not None
    assert len(result.tokens) == 6
    assert result.tokens[-1].type == TokenType.EOF
