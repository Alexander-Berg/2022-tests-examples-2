import pytest


TRANSLATIONS = pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.translations(
                    taximeter_messages={
                        'key1': {
                            'ru': '%(cost)s руб.',
                            'en': '%(cost)s dollars.',
                            'kk': '%(cost)s kzt.',
                        },
                        'hello_key': {'ru': 'Добрый день!', 'en': 'Hello!'},
                    },
                ),
            ],
            id='taximeter_messages',
        ),
    ],
)
