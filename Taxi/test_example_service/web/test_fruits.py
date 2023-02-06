import datetime

import pytest

TIMESTAMP_NOW = 1578466800
NOW = datetime.datetime.utcfromtimestamp(TIMESTAMP_NOW)


@pytest.mark.now(NOW.isoformat())
async def test_fruits_eaten(
        web_app_client, web_app, get_stats_by_label_values,
):
    response = await web_app_client.post(
        '/fruits/eaten',
        json={
            'fruits': [
                'banana',
                'apple',
                'banana',
                'apple',
                'apple',
                'cantaloupe',
            ],
        },
    )
    assert response.status == 200
    assert await response.text() == ''
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'fruits.eaten'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'fruit_kind': 'banana', 'sensor': 'fruits.eaten'},
            'value': 2,
            'timestamp': None,
        },
        {
            'kind': 'IGAUGE',
            'labels': {'fruit_kind': 'apple', 'sensor': 'fruits.eaten'},
            'value': 3,
            'timestamp': None,
        },
    ]


@pytest.mark.now(NOW.isoformat())
async def test_fruits_time_spent(
        web_app_client, web_app, get_single_stat_by_label_values,
):
    response = await web_app_client.post(
        '/fruits/eaten', json={'fruits': ['banana'], 'time_spent': 13},
    )
    assert response.status == 200
    assert await response.text() == ''
    stat = get_single_stat_by_label_values(
        web_app['context'], {'sensor': 'fruits.time_spent'},
    )
    assert stat == {
        'kind': 'DGAUGE',
        'labels': {'sensor': 'fruits.time_spent'},
        'value': 13,
        'timestamp': TIMESTAMP_NOW,
    }
