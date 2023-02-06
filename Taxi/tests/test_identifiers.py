import pytest

from model_gen.parse import Identifier


def test_simple():
    prop_id = Identifier.from_snake_case('my_property')
    assert prop_id.pascal_case == 'MyProperty'
    assert prop_id.snake_case == 'my_property'
    assert prop_id.camel_case == 'myProperty'

    def_id = Identifier.from_pascal_case('MyClass')
    assert def_id.snake_case == 'my_class'


def test_complex():
    identifier = Identifier(['a', 'b', 'c4', 'd5f'])
    assert identifier.snake_case == 'a_b_c4_d5f'
    assert identifier.pascal_case == 'ABC4D5f'
    assert identifier.camel_case == 'aBC4D5f'

    assert Identifier.from_snake_case(identifier.snake_case) == identifier
    assert Identifier.from_pascal_case(identifier.pascal_case) == identifier


@pytest.mark.parametrize(
    'parts',
    [
        ['invalid', 'char_s'],
        ['invalid', 'char%s'],
        ['capital', 'leTTers'],
        ['', 'empty', 'part'],
        [],
        ['start', 'with', '3digit'],
    ],
)
def test_invalid_parts(parts):
    with pytest.raises(Exception):
        Identifier(parts)


@pytest.mark.parametrize(
    'value',
    [
        'PascalCase',
        'camelCase',
        'invalid_character,s',
        '1st_digit',
        'double__underscore',
    ],
)
def test_invalid_snake_case(value):
    with pytest.raises(Exception):
        Identifier.from_snake_case(value)


@pytest.mark.parametrize(
    'value',
    [
        'snake_case',
        'camelCase',
        'InvalidCharacter,s',
        '1stDigit',
        'SomeUnderscore_',
    ],
)
def test_invalid_pascal_case(value):
    with pytest.raises(Exception):
        Identifier.from_pascal_case(value)
