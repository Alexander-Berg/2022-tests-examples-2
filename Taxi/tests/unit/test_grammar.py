from pahtest.grammar import Lexeme

L = Lexeme.from_fields


def test_lexeme_cast():
    # - cast scalar
    lexeme = L('arg', types=[bool, int, float, str], to_cast=str)
    assert '123' == lexeme.cast(123)
    # - cast dict, list
    lexeme = L('arg', types=[str], to_cast=list)
    assert list('123') == lexeme.cast('123')
    # - no cast
    lexeme = L('arg', types=[int], to_cast=None)
    assert 123 == lexeme.cast(123)
