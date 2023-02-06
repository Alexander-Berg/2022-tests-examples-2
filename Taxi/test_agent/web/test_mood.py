import asyncio
import datetime
import uuid

import aiohttp
import pytest

NOW = datetime.datetime(2021, 11, 5, 1)


@pytest.mark.now((NOW + datetime.timedelta(hours=0)).isoformat())
@pytest.mark.parametrize(
    'headers,status_code,expected_json',
    [
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'},
            200,
            {'show_csat': True},
        ),
    ],
)
async def test_mood_csat_avaliable1(
        web_app_client, headers, status_code, expected_json,
):
    response: aiohttp.ClientResponse = await web_app_client.get(
        '/mood/csat_available', headers=headers,
    )
    assert response.status == status_code
    assert await response.json() == expected_json


@pytest.mark.parametrize(
    'headers,status_code,expected_json',
    [
        (
            {'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'},
            200,
            {'show_csat': True},
        ),
    ],
)
@pytest.mark.now((NOW + datetime.timedelta(hours=36.1)).isoformat())
async def test_mood_csat_avaliable2(
        web_app_client, headers, status_code, expected_json,
):
    response: aiohttp.ClientResponse = await web_app_client.get(
        '/mood/csat_available', headers=headers,
    )
    assert response.status == status_code
    assert await response.json() == expected_json


@pytest.mark.parametrize(
    'headers,status_code,expected_json',
    [
        (
            {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-RU'},
            200,
            {'show_csat': True},
        ),
    ],
)
@pytest.mark.now((NOW + datetime.timedelta(hours=72.1)).isoformat())
async def test_mood_csat_avaliable3(
        web_app_client, headers, status_code, expected_json,
):
    response: aiohttp.ClientResponse = await web_app_client.get(
        '/mood/csat_available', headers=headers,
    )
    assert response.status == status_code
    assert await response.json() == expected_json


@pytest.mark.parametrize(
    'headers,status_code,expected_json',
    [
        (
            {'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'},
            200,
            {'show_csat': False},
        ),
    ],
)
@pytest.mark.now((NOW + datetime.timedelta(hours=1)).isoformat())
async def test_mood_csat_avaliable4(
        web_app_client, headers, status_code, expected_json,
):
    response: aiohttp.ClientResponse = await web_app_client.get(
        '/mood/csat_available', headers=headers,
    )
    assert response.status == status_code
    assert await response.json() == expected_json


@pytest.mark.now(NOW.isoformat())
async def test_mood_send_csat(web_app_client, web_context):
    async with web_context.pg.slave_pool.acquire() as conn:
        await conn.execute('DELETE from agent.user_history_mood')

    request_id = str(uuid.uuid4())

    coroutine = web_app_client.post(
        '/mood/send_csat',
        headers={'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'},
        json={
            'mood_value': 3,
            'comment': 'все норм',
            'request_id': request_id,
        },
    )

    responses = await asyncio.gather(coroutine, coroutine)

    assert responses[0].status == 200
    assert responses[1].status == 200

    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * from agent.user_history_mood')

    assert len(rows) == 1
    assert rows[0]['dt'] == NOW
    assert rows[0]['login'] == 'unholy'
    assert rows[0]['mood_value'] == 3
    assert rows[0]['comment'] == 'все норм'


@pytest.mark.now('2021-11-07T12:00:00+0000')
@pytest.mark.parametrize(
    'url,headers,status_code,response_content',
    [
        (
            '/mood/history',
            {'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'},
            200,
            {
                'moods': [
                    {
                        'mood_value': 5,
                        'date': '2021-11-05T04:00:00+03:00',
                        'comment': 'круто все',
                    },
                    {'mood_value': 4, 'date': '2021-11-03T04:00:00+03:00'},
                ],
            },
        ),
        (
            '/mood/history?start_dt=2021-11-05%2001%3A00%3A00',
            {'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'},
            200,
            {
                'moods': [
                    {
                        'mood_value': 5,
                        'date': '2021-11-05T04:00:00+03:00',
                        'comment': 'круто все',
                    },
                ],
            },
        ),
        (
            '/mood/history',
            {'X-Yandex-Login': 'user', 'Accept-Language': 'ru-RU'},
            200,
            {'moods': []},
        ),
    ],
)
async def test_get_mood_history(
        web_app_client, url, headers, status_code, response_content,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == status_code
    content = await response.json()
    assert content == response_content
