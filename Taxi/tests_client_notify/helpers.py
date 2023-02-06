import pytest


TRANSLATIONS = pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.translations(
                    notify={
                        'key1': {
                            'ru': '%(cost)s руб.',
                            'en': '%(cost)s dollars.',
                            'kk': '%(cost)s kzt.',
                        },
                        'hello_key': {'ru': 'Добрый день!', 'en': 'Hello!'},
                    },
                ),
            ],
            id='notify',
        ),
    ],
)
