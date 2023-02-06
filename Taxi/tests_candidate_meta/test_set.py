import datetime
import json

import pytest


def get_meta(pgsql):
    cursor = pgsql['candidate-meta'].conn.cursor()
    cursor.execute('SELECT * FROM metadata.candidate_metadata')
    res = []
    for row in cursor.fetchall():

        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]

        res[len(res) - 1]['metadata'] = json.loads(
            res[len(res) - 1]['metadata'],
        )

        del res[len(res) - 1]['id']

    return res


def get_meta_new(pgsql):
    cursor = pgsql['candidate-meta'].conn.cursor()
    cursor.execute('SELECT * FROM metadata.candidate_metadata_v2 ORDER BY key')
    res = []
    for row in cursor.fetchall():

        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]

        del res[len(res) - 1]['id']

    return res


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('candidate-meta', files=[])
@pytest.mark.servicetest
@pytest.mark.config(
    CANDIDATE_META_DB={'read-new': True, 'write-new': True, 'write-old': True},
)
async def test_set_clean(taxi_candidate_meta, pgsql):
    response = await taxi_candidate_meta.post(
        '/v1/candidate/meta/set',
        json={
            'order_id': 'order',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
            'metadata': {'key': 'value'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert get_meta(pgsql) == [
        {
            'order_id': 'order',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
            'metadata': {'key': 'value'},
            'created': datetime.datetime(2019, 1, 1, 0, 0),
        },
    ]

    assert get_meta_new(pgsql) == [
        {
            'created': datetime.datetime(2019, 1, 1, 0, 0),
            'driver_profile_id': 'uuid',
            'key': 'key',
            'order_id': 'order',
            'park_id': 'park',
            'value': ['value'],
        },
    ]


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('candidate-meta', files=['test.sql'])
@pytest.mark.servicetest
@pytest.mark.config(
    CANDIDATE_META_DB={'read-new': True, 'write-new': True, 'write-old': True},
)
async def test_set_update(taxi_candidate_meta, pgsql):
    response = await taxi_candidate_meta.post(
        '/v1/candidate/meta/set',
        json={
            'order_id': 'order',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
            'metadata': {'key': 'value'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert get_meta(pgsql) == [
        {
            'order_id': 'order',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
            'metadata': {'key': 'value'},
            'created': datetime.datetime(2019, 1, 1, 0, 0),
        },
    ]

    assert get_meta_new(pgsql) == [
        {
            'created': datetime.datetime(2019, 1, 1, 0, 0),
            'driver_profile_id': 'uuid',
            'key': 'key',
            'order_id': 'order',
            'park_id': 'park',
            'value': ['value'],
        },
    ]
