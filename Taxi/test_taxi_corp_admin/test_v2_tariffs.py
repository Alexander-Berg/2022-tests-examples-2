import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'home_zone': 'moscow'},
            {
                'tariffs': [
                    {
                        'home_zone': 'moscow',
                        'country': 'rus',
                        'name': 'Однозонный Москва 30%',
                        'tariff_series_id': 'moscow',
                    },
                ],
            },
            id='home_zone exists',
        ),
        pytest.param(
            {'home_zone': ''},
            {
                'tariffs': [
                    {
                        'country': 'rus',
                        'home_zone': None,
                        'name': 'Многозонный 30%',
                        'tariff_series_id': 'standalone30',
                    },
                    {
                        'country': 'kaz',
                        'home_zone': None,
                        'name': 'Многозонный 40%',
                        'tariff_series_id': 'standalone40',
                    },
                    {
                        'country': 'rus',
                        'name': 'Многозонный кастомный',
                        'tariff_series_id': 'multizone_custom',
                    },
                ],
            },
            id='home_zone is None',
        ),
    ],
)
async def test_get_tariffs_by_zone(
        taxi_corp_admin_client, params, expected, load_binary,
):
    response = await taxi_corp_admin_client.get(f'/v2/tariffs', params=params)
    assert response.status == 200
    assert await response.json() == expected
