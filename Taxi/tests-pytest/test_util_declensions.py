import pytest

from taxi.util import declensions


CONFIG = {
    'az': 'two_form',
    'en': 'two_form',
    'hy': 'two_form',
    'ka': 'single_form',
    'kk': 'single_form',
    'zh': 'single_form',
    'ro': 'ro_form',
    'ru': 'ru_form',
    'uk': 'ru_form'
}


@pytest.mark.parametrize('locale,n,result', [
    ('az', 1, 1),
    ('az', 2, 2),
    ('az', 10, 2),

    ('en', 1, 1),
    ('en', 2, 2),
    ('en', 10, 2),

    ('hy', 1, 1),
    ('hy', 2, 2),
    ('hy', 7, 2),

    ('ka', 1, 1),
    ('ka', 2, 1),
    ('ka', 7, 1),

    ('kk', 1, 1),
    ('kk', 2, 1),
    ('kk', 7, 1),

    ('ro', 0, 2),
    ('ro', 1, 1),
    ('ro', 2, 2),
    ('ro', 3, 2),
    ('ro', 4, 2),
    ('ro', 5, 2),
    ('ro', 6, 2),
    ('ro', 10, 2),
    ('ro', 11, 2),
    ('ro', 15, 2),
    ('ro', 19, 2),
    ('ro', 20, 3),
    ('ro', 100, 3),
    ('ro', 101, 2),
    ('ro', 110, 2),
    ('ro', 120, 3),

    ('ru', 1, 1),
    ('ru', 2, 2),
    ('ru', 3, 2),
    ('ru', 4, 2),
    ('ru', 5, 3),
    ('ru', 11, 3),
    ('ru', 21, 1),
    ('ru', 50, 3),

    ('uk', 1, 1),
    ('uk', 2, 2),
    ('uk', 3, 2),
    ('uk', 4, 2),
    ('uk', 5, 3),
    ('uk', 11, 3),
    ('uk', 21, 1),
    ('uk', 50, 3),
])
@pytest.mark.filldb(_fill=False)
def test_decline(locale, n, result):
    assert declensions.decline(locale, n, CONFIG) == result


@pytest.mark.parametrize('lang,exc', [
    ('az', False),
    ('en', False),
    ('hy', False),
    ('ka', False),
    ('kk', False),
    ('ro', False),
    ('ru', False),
    ('uk', False),
    ('est', True)
])
@pytest.mark.filldb(_fill=False)
def test_languages(lang, exc):
    if exc:
        with pytest.raises(declensions.LanguageNotFoundError):
            declensions.decline(lang, 1, CONFIG)
    else:
        result = declensions.decline(lang, 1, CONFIG)
        assert result is not None
