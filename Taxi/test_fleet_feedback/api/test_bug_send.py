import aiohttp.web
import pytest

from taxi import settings


@pytest.mark.config(FLEET_FEEDBACK_BUG_EMAIL={'email': 'test@yandex-team.ru'})
async def test_success(
        web_app_client,
        mock_parks,
        mock_dac_users,
        mock_sticker,
        load_json,
        load,
        headers,
):
    stub = load_json('common.json')

    resulting_mail = load('full_mail.xml')
    resulting_mail = resulting_mail.replace(
        'unstable', settings.get_environment(),
    )

    @mock_sticker('/send-internal/')
    async def _send_mail(request):
        body = request.json
        text = body.pop('body')
        assert body.pop('idempotence_token')
        assert text == resulting_mail

        assert body == stub['sticker']['request']
        return aiohttp.web.json_response({})

    response = await web_app_client.post(
        '/feedback-api/v1/bug/send',
        headers={**headers, 'X-Idempotency-Token': '1234'},
        json={
            'login': 'tarasalk',
            'label': 'test label',
            'browser': 'Netscape Navigator 9.0',
            'text': 'Всё сломалось!',
            'contact': '8-800-555-35-55',
            'url': 'https://fleet.yandex.ru/broken-page/',
            'screen_size': {'width': 640, 'height': 480},
        },
    )

    assert response.status == 200
