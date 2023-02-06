import pytest

from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_list(web_app_client, web_context: wc.Context):
    response1 = await web_app_client.post(
        '/v1/park/affiliations/list',
        params={'park_id': 'park_id'},
        json={
            'created_at': {
                'from': '2020-01-01T00:00:00+00:00',
                'to': '2020-01-05T00:00:00+00:00',
            },
            'states': ['new', 'accepted'],
            'limit': 1,
        },
    )
    assert response1.status == 200
    data1 = await response1.json()
    cursor1 = data1['cursor']
    driver_affiliation_records1 = data1['driver_affiliation_records']
    assert driver_affiliation_records1 == [
        {
            'record_id': 'record_id4',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id4',
            'original_driver_park_id': 'original_driver_park_id4',
            'original_driver_id': 'original_driver_id4',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-04T03:00:00+03:00',
            'modified_at': '2020-01-05T03:00:00+03:00',
            'state': 'accepted',
        },
    ]

    response2 = await web_app_client.post(
        '/v1/park/affiliations/list',
        params={'park_id': 'park_id'},
        json={
            'created_at': {
                'from': '2020-01-02T00:00:00+00:00',
                'to': '2020-01-5T00:00:00+00:00',
            },
            'states': ['new', 'accepted'],
            'limit': 1,
            'cursor': cursor1,
        },
    )
    assert response2.status == 200
    data2 = await response2.json()
    assert data2.get('cursor') is None
    driver_affiliation_records2 = data2['driver_affiliation_records']
    assert driver_affiliation_records2 == [
        {
            'record_id': 'record_id2',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id2',
            'original_driver_park_id': 'original_driver_park_id2',
            'original_driver_id': 'original_driver_id2',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-02T03:00:00+03:00',
            'modified_at': '2020-01-03T03:00:00+03:00',
            'state': 'new',
        },
    ]


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_aggregations(web_app_client, web_context: wc.Context):
    response = await web_app_client.post(
        '/v1/park/affiliations/aggregations',
        params={'park_id': 'park_id'},
        json={
            'created_at': {
                'from': '2020-01-01T00:00:00+00:00',
                'to': '2020-01-05T00:00:00+00:00',
            },
            'states': ['new', 'accepted'],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'total_records': 2}


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_default_aggregations(web_app_client, web_context: wc.Context):
    response = await web_app_client.post(
        '/v1/park/affiliations/aggregations',
        params={'park_id': 'park_id'},
        json={},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'total_records': 3}


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_modified_at(web_app_client, web_context: wc.Context):
    response1 = await web_app_client.post(
        '/v1/park/affiliations/list',
        params={'park_id': 'park_id'},
        json={
            'modified_at': {
                'from': '2020-01-03T00:00:00+00:00',
                'to': '2020-01-05T00:00:00+00:00',
            },
        },
    )
    assert response1.status == 200
    data1 = await response1.json()
    driver_affiliation_records_ids = [
        r['record_id'] for r in data1['driver_affiliation_records']
    ]
    assert driver_affiliation_records_ids == ['record_id3', 'record_id2']

    response2 = await web_app_client.post(
        '/v1/park/affiliations/aggregations',
        params={'park_id': 'park_id'},
        json={
            'modified_at': {
                'from': '2020-01-03T00:00:00+00:00',
                'to': '2020-01-05T00:00:00+00:00',
            },
        },
    )
    assert response2.status == 200
    data2 = await response2.json()
    assert data2 == {'total_records': 2}
