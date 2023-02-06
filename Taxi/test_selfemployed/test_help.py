# pylint: disable=redefined-outer-name

import pytest

from . import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_HELP_SETTINGS=(
        conftest.TAXIMETER_FNS_SELF_EMPLOYMENT_HELP_SETTINGS
    ),
)
async def test_get_help(se_client):
    park_id = '1'
    driver_id = '1'

    response = await se_client.get(
        '/self-employment/fns-se/help',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content['details'] == [
        {
            'preview_title': 'Вопрос 1',
            'title': 'Вопрос 1',
            'subtitle': 'Ответ 1',
        },
        {
            'preview_title': 'Вопрос 2',
            'title': 'Вопрос 2',
            'subtitle': 'Ответ 2',
        },
        {
            'preview_title': 'Вопрос 3',
            'title': 'Вопрос 3',
            'subtitle': 'Ответ 3',
        },
    ]
    assert content['contact_support_button_text'] == 'Связаться с поддержкой'
    assert content['phones'] == [
        {'title': 'Москва', 'number': '+74951222122'},
        {'title': 'Калуга', 'number': '+74842218111'},
        {'title': 'Россия', 'number': '88006008747'},
    ]
