import pytest

from taxi import i18n
from taxi import translations

HIRING_FORMS_TRANSLATIONS = {
    'text_search.truncated': {'en': 'text search truncated'},
}


@pytest.mark.parametrize(
    'input_string, accept_language, code, answer',
    [
        ('Some string', 'en', 200, 'Some string'),
        ('Some string', 'ru-RU', 200, 'Некоторая строка'),
        ('Some string', 'uk', 200, 'Деякий рядок'),
        ('Some string', 'by', 200, 'Нейкая радок'),
        ('Some string', 'en, de; q=500, ru-RU', 200, 'Uine saite'),
        ('Some string', 'ar', 200, 'Some string'),
        ('Wrong string', 'en', 200, 'Wrong string'),
    ],
)
# Декоратор добавляет переводы
@pytest.mark.translations(
    hiring_forms={
        'Some string': {
            'ru-RU': 'Некоторая строка',
            'uk': 'Деякий рядок',
            'by': 'Нейкая радок',
            'de': 'Uine saite',
        },
    },
)
async def test_some_translation(
        input_string, accept_language, code, answer, web_app_client,
):
    response = await web_app_client.post(
        '/translations/example',
        params={'input_string': input_string},
        headers={'Accept-Language': accept_language},
    )
    assert response.status == code
    content = await response.text()
    assert content == answer


@pytest.mark.translations(hiring_forms=HIRING_FORMS_TRANSLATIONS)
async def test_specified_translations(web_context):
    translation = web_context.translations.hiring_forms.get_string(
        'text_search.truncated', 'en',
    )
    assert translation == 'text search truncated'


@pytest.mark.translations(hiring_forms=HIRING_FORMS_TRANSLATIONS)
async def test_missing_patched_translations(web_context):
    with pytest.raises(translations.BlockNotFoundError) as excinfo:
        web_context.translations.something.get_string(
            'text_search.truncated', 'en',
        )

    assert excinfo.value.args == ('something',)


async def test_missing_not_patched_translations(web_context):
    with pytest.raises(translations.BlockNotFoundError) as excinfo:
        web_context.translations.something.get_string(
            'text_search.truncated', 'en',
        )

    assert excinfo.value.args == (
        '\'something\' not in dict_keys([\'hiring_forms\', \'order\'])',
    )


@pytest.mark.translations(hiring_forms=HIRING_FORMS_TRANSLATIONS)
async def test_with_i18n(web_context):
    i18n.set_context(languages=('en',))
    translation1 = i18n.translate('text_search.truncated')
    translation2 = i18n.translate(
        'text_search.truncated', keyset='hiring_forms',
    )
    translation3 = i18n.translate(
        'text_search.truncated', keyset=web_context.translations.hiring_forms,
    )
    assert translation1 == 'text search truncated'
    assert translation2 == 'text search truncated'
    assert translation3 == 'text search truncated'


async def test_translations(web_context):
    assert web_context.translations.order
    assert web_context.translations.hiring_forms
    with pytest.raises(translations.BlockNotFoundError):
        assert web_context.translations.client_messages
