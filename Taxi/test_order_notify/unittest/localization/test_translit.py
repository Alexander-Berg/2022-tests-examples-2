import pytest

from order_notify.repositories.localization import translit


DEFAULT_WORD = (
    'йЙцЦуУкКеЕнНгГшШщЩзЗхХъЪфФыЫвВаАпПрРо'
    'ОлЛдДжЖэЭёЁяЯчЧсСмМиИтТьЬбБюЮ123456789 , .'
)

DEFAULT_TRANSLIT = (
    'jJcCuUkKeEnNgGshShschSchzZhHjJfFiIvVaApPrRo'
    'OlLdDzhZheEyoYoyaYachChsSmMiItTjJbByuYu123456789 , .'
)


@pytest.mark.parametrize(
    'word, locale, expected_translit',
    [
        pytest.param(None, 'en', None, id='pword_None'),
        pytest.param('б', 'ru', 'б', id='default_locale'),
        pytest.param(DEFAULT_WORD, 'en', DEFAULT_TRANSLIT, id='translit'),
    ],
)
def test_translit(word, locale, expected_translit):
    name = translit.translit(word=word, locale=locale)
    assert name == expected_translit
