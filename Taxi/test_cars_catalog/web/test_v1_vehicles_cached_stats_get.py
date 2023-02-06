import pytest


@pytest.mark.now('2020-06-01T00:00:00Z+00:00')
@pytest.mark.pgsql('cars_catalog', files=['test_get.sql'])
async def test_check(web_app_client):
    response1 = await web_app_client.get(
        '/v1/vehicles/cached-stats', params={'limit': 1},
    )
    data1 = await response1.json()
    assert data1 == {
        'stats': [
            {
                'mark_code': 'mark',
                'model_code': 'model',
                'year': 2010,
                'adjusted_age': 10,
                'price': '100',
            },
        ],
        'latest_revision': 1,
    }

    response2 = await web_app_client.get(
        '/v1/vehicles/cached-stats', params={'limit': 1, 'latest_revision': 1},
    )
    data2 = await response2.json()
    assert data2 == {
        'stats': [
            {
                'mark_code': 'mark',
                'model_code': 'model',
                'year': 2011,
                'adjusted_age': 9,
                'price': '200',
            },
        ],
        'latest_revision': 2,
    }

    response3 = await web_app_client.get(
        '/v1/vehicles/cached-stats', params={'limit': 1, 'latest_revision': 2},
    )
    data3 = await response3.json()
    assert data3 == {'stats': [], 'latest_revision': 2}
