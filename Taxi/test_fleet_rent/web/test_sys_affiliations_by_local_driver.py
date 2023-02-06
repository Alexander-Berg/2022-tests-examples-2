import pytest

from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_many(web_app_client, web_context: wc.Context):
    response = await web_app_client.get(
        '/v1/sys/affiliations/by-local-driver',
        params={'park_id': 'park_id', 'driver_profile_id': 'local_driver_id1'},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'records': [
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
                'local_driver_id': 'local_driver_id1',
                'original_driver_park_id': 'original_driver_park_id2',
                'original_driver_id': 'original_driver_id2',
                'creator_uid': 'creator_uid',
                'created_at': '2020-01-02T03:00:00+03:00',
                'modified_at': '2020-01-02T03:00:00+03:00',
                'state': 'new',
            },
        ],
    }


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_no_affiliation(web_app_client, web_context: wc.Context):
    response = await web_app_client.get(
        '/v1/sys/affiliations/by-local-driver',
        params={'park_id': 'park_id', 'driver_profile_id': 'asd'},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'records': []}
