import pytest

from document_templator.models import enumerators


_RUSSIAN_LETTERS = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'


def test_enumerators():
    number_formatter = enumerators.build_formatter('ARABIC_NUMBER', '1')
    numbers_formatter = enumerators.build_formatter('ARABIC_NUMBER', '1')
    symbol_formatter = enumerators.build_formatter(
        'UPPER_CASE_RUSSIAN_LETTER', 'А', show_parents=False,
    )
    enumerator = enumerators.TemplateEnumerator('first', number_formatter)
    sub_enumerator = enumerators.TemplateEnumerator(
        'sub_enumerator', numbers_formatter, enumerator,
    )
    sub_sub_enumerator = enumerators.TemplateEnumerator(
        'sub_sub_enumerator', symbol_formatter, sub_enumerator,
    )
    first = next(enumerator)
    assert first == '1', first

    sub_first = next(sub_enumerator)
    assert sub_first == '1.1', sub_first
    sub_sub_first = next(sub_sub_enumerator)
    assert sub_sub_first == 'А', sub_sub_first

    second = next(enumerator)
    assert second == '2', second

    sub_second = next(sub_enumerator)
    assert sub_second == '2.1', sub_second

    sub_sub_second = next(sub_sub_enumerator)
    assert sub_sub_second == 'А', sub_sub_second

    sub_sub_second = next(sub_sub_enumerator)
    assert sub_sub_second == 'Б', sub_sub_second

    sub_second = next(sub_enumerator)
    assert sub_second == '2.2', sub_second

    for index in range(32):
        sub_sub_second = next(sub_sub_enumerator)
        assert sub_sub_second == _RUSSIAN_LETTERS[index]

    for index in range(32):
        sub_sub_second = next(sub_sub_enumerator)
        assert sub_sub_second == 'А' + _RUSSIAN_LETTERS[index]


@pytest.mark.parametrize('start_symbol', ('A', 'AA', 'ABC', 'B', 'Z', 'EG'))
def test_start_symbol_in_enumerators(start_symbol):
    symbol_formatter = enumerators.build_formatter(
        'UPPER_CASE_ENGLISH_LETTER', start_symbol, show_parents=False,
    )
    enumerator = enumerators.TemplateEnumerator('first', symbol_formatter)

    assert next(enumerator) == start_symbol
