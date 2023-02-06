import pytest

from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize('body', [blackbox.PASSPORT_RESPONSE_USER_1])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_handler(mockserver, load_json, web_app_client, body):
    test_request = {
        'sourceid': 'call_center',
        'type': 'a',
        'user': {
            'id': '2a4c0c846864a71fdc6383fccdf0a29d',
            'phone': '+79998887766',
        },
        'position': [37.62251, 55.753219],
        'action': 'zero_suggest',
        'state': {'fields': [], 'location': [37.62251, 55.753219]},
    }

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _persuggest_handle(request):
        return load_json('persuggest_suggest_response.json')

    headers = {'Cookie': 'Session_id=123'}

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/form/v1/suggest',
        json=test_request,
        headers=headers,
    )

    assert response.status == 200


@pytest.mark.parametrize('body', [blackbox.PASSPORT_RESPONSE_USER_1])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_pin_drop(mockserver, load_json, web_app_client, body):
    test_request = load_json('pin_drop_request.json')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/finalsuggest')
    async def _persuggest_handle(request):
        assert request.headers['X-Request-Language'] == 'ru'
        return load_json('persuggest_finalsuggest_response.json')

    headers = {'Cookie': 'Session_id=123', 'Accept-Language': 'ru'}

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/form/v1/suggest',
        json=test_request,
        headers=headers,
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == load_json('expected_pin_drop.json')


@pytest.mark.parametrize('body', [blackbox.PASSPORT_RESPONSE_USER_1])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_unavailable(mockserver, load_json, web_app_client, body):
    test_request = load_json('pin_drop_request.json')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/finalsuggest')
    async def _persuggest_handle(request):
        assert request.headers['X-Request-Language'] == 'ru'
        return load_json('unavailable_finalsuggest_response.json')

    headers = {'Cookie': 'Session_id=123', 'Accept-Language': 'ru'}

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/form/v1/suggest',
        json=test_request,
        headers=headers,
    )

    assert response.status == 404
