import pytest

ENDPOINT = '/reports-api/v1/parks-rating/park-cities'


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=4)
@pytest.mark.now('2021-07-10T13:04:49+03:00')
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(web_app_client, headers, mock_fleet_parks, load_json):
    response = await web_app_client.get(ENDPOINT, headers=headers)

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [
            {'id': '4e49ee6d386d58f0a63dd7a42ffcca73', 'name': 'Красноярск'},
            {'id': 'e6eb3a7361bf01ed68df48c399e93e3e', 'name': 'Москва'},
            {
                'id': 'eb9648de904dcb369f102085f9a658e3',
                'name': 'Нижний Новгород',
            },
        ],
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=4)
@pytest.mark.now('2021-12-10T13:04:49+03:00')
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_empty(web_app_client, headers, mock_fleet_parks, load_json):
    response = await web_app_client.get(ENDPOINT, headers=headers)

    assert response.status == 200

    data = await response.json()
    assert data == {'items': []}
