import datetime

import pytest


@pytest.mark.now('2020-01-01T23:00:00.0')
async def test_downtime_cancel_200(web_app_client, db):
    response = await web_app_client.post(
        '/downtime/cancel/', json={'downtime_id': 'downtime_id1'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == {'dc': 'vla', 'queues': ['queue1', 'queue2']}
    affected = []
    docs = await db.stq_config.find(
        {'hosts_downtime.id': 'downtime_id1'},
    ).to_list(None)
    for doc in docs:
        affected.append(doc['_id'])
        assert doc['hosts_downtime']['until'] == datetime.datetime(
            2020, 1, 1, 23,
        )
    assert affected == ['queue1', 'queue2']


@pytest.mark.parametrize(
    'donwtime_id, expected',
    [
        ('downtime_id2', {'dc': 'vla', 'queues': ['queue5', 'queue6']}),
        (
            'downtime_id4',
            {'dc': 'vla', 'queues': ['queue7'], 'tplatform_namespace': 'taxi'},
        ),
    ],
)
async def test_downtime_cancel_with_tplatform(
        web_app_client, db, donwtime_id, expected,
):
    response = await web_app_client.post(
        '/downtime/cancel/', json={'downtime_id': donwtime_id},
    )
    assert response.status == 200
    result = await response.json()
    assert result == expected


async def test_downtime_cancel_404(web_app_client):
    response = await web_app_client.post(
        '/downtime/cancel/', json={'downtime_id': 'downtime_id3'},
    )
    assert response.status == 404
