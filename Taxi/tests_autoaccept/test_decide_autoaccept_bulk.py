import pytest


@pytest.mark.config(
    LONG_TRIP_CRITERIA={
        '__default__': {
            'econom': {'apply': 'either', 'distance': 1000, 'duration': 1000},
        },
        'moscow': {
            '__default__': {
                'apply': 'both',
                'distance': 2000,
                'duration': 2000,
            },
        },
    },
)
@pytest.mark.pgsql(
    'autoaccept', files=['driver_option.sql', 'driver_option_value.sql'],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_decide_autoaccept_bulk(
        taxi_autoaccept, load_json, driver_app_profile,
):

    driver_app_profile(taximeter_platform='android')
    body = load_json('request.json')
    response = await taxi_autoaccept.post(
        '/v1/decide-autoaccept-bulk', json=body,
    )
    assert response.json() == {
        'orders': [
            {
                'order_id': 'order_id0',
                'candidates': [
                    {
                        'driver_profile_id': 'uuid0',
                        'park_id': 'park_id0',
                        'autoaccept': {'enabled': False},
                    },
                    {
                        'driver_profile_id': 'uuid1',
                        'park_id': 'park_id1',
                        'autoaccept': {'enabled': True},
                    },
                ],
            },
            {
                'order_id': 'order_id1',
                'candidates': [
                    {
                        'driver_profile_id': 'uuid2',
                        'park_id': 'park_id2',
                        'autoaccept': {'enabled': False},
                    },
                ],
            },
        ],
    }
