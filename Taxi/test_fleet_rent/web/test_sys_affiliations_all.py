import pytest

from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_all(web_app_client, web_context: wc.Context):
    response1 = await web_app_client.get(
        '/v1/sys/affiliations/all', params={'limit': 2},
    )
    assert response1.status == 200
    data1 = await response1.json()
    cursor1 = data1['cursor']
    records1 = data1['records']
    assert records1 == [
        {
            'record_id': 'record_id1',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id1',
            'original_driver_park_id': 'original_driver_park_id1',
            'original_driver_id': 'original_driver_id1',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-01T03:00:00+03:00',
            'modified_at': '2020-01-01T03:00:00+03:00',
            'state': 'park_recalled',
        },
        {
            'record_id': 'record_id2',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id2',
            'original_driver_park_id': 'original_driver_park_id2',
            'original_driver_id': 'original_driver_id2',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-02T03:00:00+03:00',
            'modified_at': '2020-01-02T03:00:00+03:00',
            'state': 'new',
        },
    ]

    response2 = await web_app_client.get(
        '/v1/sys/affiliations/all', params={'limit': 2, 'cursor': cursor1},
    )
    assert response2.status == 200
    data2 = await response2.json()
    cursor2 = data2['cursor']
    records2 = data2['records']
    assert records2 == [
        {
            'record_id': 'record_id3',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id3',
            'original_driver_park_id': 'original_driver_park_id3',
            'original_driver_id': 'original_driver_id3',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-03T03:00:00+03:00',
            'modified_at': '2020-01-02T03:00:00+03:00',
            'state': 'rejected',
        },
        {
            'record_id': 'record_id4',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id4',
            'original_driver_park_id': 'original_driver_park_id4',
            'original_driver_id': 'original_driver_id4',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-04T03:00:00+03:00',
            'modified_at': '2020-01-04T03:00:00+03:00',
            'state': 'accepted',
        },
    ]

    response3 = await web_app_client.get(
        '/v1/sys/affiliations/all', params={'limit': 2, 'cursor': cursor2},
    )
    assert response3.status == 200
    data3 = await response3.json()
    cursor3 = data3['cursor']
    records3 = data3['records']

    assert records3 == []
    assert cursor3 == cursor2
