import pytest


@pytest.mark.parametrize(
    'accept_variant, await_response',
    [
        ('en', 'Form does not exist'),  # non exists lang: use default
        ('en, de; q=500, ru-RU', 'Formular existiert nicht'),
        ('ru-RU', 'Форма не найдена'),
    ],
)
@pytest.mark.translations(
    hiring_forms={
        'Form does not exist': {
            'ru-RU': 'Форма не найдена',
            'de': 'Formular existiert nicht',
        },
    },
)
async def test_unknow_not_found(
        accept_variant, await_response, web_app_client, web_context,
):

    if hasattr(web_context, 'translations'):
        response = await web_app_client.get(
            '/v1/form',
            params={'name': 'unknown'},
            headers={'Accept-Language': accept_variant},
        )
        assert response.status == 404
        json = await response.json()

        assert json['code'] == 'FORM_NOT_FOUND'
        assert json['message'] == await_response
    else:
        print('Translations plugin is not used')
