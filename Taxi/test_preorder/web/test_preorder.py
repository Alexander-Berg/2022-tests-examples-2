import aiohttp
import pytest

from preorder.controller import available_preorder

YANDEX_UID_HEADER = 'X-Yandex-UID'
USER_ID_HEADER = 'X-YaTaxi-UserId'
URL = '/4.0/preorder/v1/availability'
UMLAAS_HANDLE = '/umlaas-dispatch/v1/preorder_available'


@pytest.mark.parametrize(
    'headers, data, expected_status',
    [
        ({}, {}, 400),
        ({YANDEX_UID_HEADER: '123'}, {}, 400),
        ({USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d'}, {}, 400),
        (
            {
                USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
                YANDEX_UID_HEADER: '123',
            },
            {},
            400,
        ),
        (
            {
                USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
                YANDEX_UID_HEADER: '123',
            },
            {
                'route': 'INVALID ROUTE',
                'zone_name': 'moscow',
                'categories': ['econom'],
            },
            400,
        ),
        (
            {
                USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
                YANDEX_UID_HEADER: '123',
            },
            {'route': [], 'zone_name': 'INVALID', 'categories': ['econom']},
            400,
        ),
    ],
)
async def test_preorder_invalid_request(
        web_app_client, monkeypatch, headers, data, expected_status,
):
    response = await web_app_client.post(URL, headers=headers, json=data)

    assert response.status == expected_status


@pytest.mark.now('2019-04-25T01:10:00+0300')
async def test_preorder(web_app_client, monkeypatch, mockserver):
    monkeypatch.setattr(
        available_preorder, '_get_preorder_request_id', lambda: 'someuid4',
    )

    @mockserver.json_handler('/umlaas-dispatch' + UMLAAS_HANDLE)
    async def _umlaas_dispatch(*args, **kwargs):
        return {
            'allowed_time_info': [
                {
                    'tariff_class': 'econom',
                    'allowed_time_ranges': [
                        {
                            'from': '2019-04-26T00:00:00+0300',
                            'to': '2019-04-27T10:00:00+0300',
                            'interval_minutes': 5,
                        },
                    ],
                },
            ],
        }

    headers = {
        YANDEX_UID_HEADER: '123',
        USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
    }

    response = await web_app_client.post(
        URL,
        headers=headers,
        json={
            'route': [(1, 1), (2, 2)],
            'zone_name': 'moscow',
            'classes': ['econom'],
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {
        'preorder_request_id': 'someuid4',
        'allowed_time_info': [
            {
                'precision_minutes': 15,
                'interval_minutes': 5,
                'allowed_time_ranges': [
                    {
                        'from': '2019-04-26T00:00:00+0300',
                        'to': '2019-04-27T10:00:00+0300',
                    },
                ],
                'class': 'econom',
            },
        ],
    }
    assert 'Cache-Control' in response.headers


@pytest.mark.config(PREORDER_EMPTY_RESPONSE_FALLBACK=True)
@pytest.mark.now('2019-04-25T01:10:00+0300')
async def test_empty_response_fallback(
        web_app_client, monkeypatch, patch_aiohttp_session,
):
    monkeypatch.setattr(
        available_preorder, '_get_preorder_request_id', lambda: 'someuid4',
    )

    @patch_aiohttp_session(
        'http://umlaas-dispatch.taxi.yandex.net' + UMLAAS_HANDLE, 'POST',
    )
    def _umlaas_dispatch(*args, **kwargs):
        raise aiohttp.ServerTimeoutError

    headers = {
        YANDEX_UID_HEADER: '123',
        USER_ID_HEADER: '5ff4901c583745e089e55be4a8c7a88d',
    }

    response = await web_app_client.post(
        URL,
        headers=headers,
        json={
            'route': [(1, 1), (2, 2)],
            'zone_name': 'moscow',
            'classes': ['econom'],
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {
        'preorder_request_id': '',
        'allowed_time_info': [],
    }
    assert 'Cache-Control' in response.headers
