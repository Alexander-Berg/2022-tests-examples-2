import pytest

from . import utils


@pytest.mark.pgsql('driver_promocodes', files=['series.sql'])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_promocodes_enabled',
    consumers=['driver-promocodes/driver'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.parametrize(
    'park_id,driver_id,name,code,response_list',
    [
        # ok
        (
            'park_0',
            'driver_0',
            'test-series-1',
            200,
            'expected_promocode.json',
        ),
        # not exists
        ('park_0', 'driver_0', 'not-existing-series', 404, None),
        # profile already added
        pytest.param(
            'park_0',
            'driver_0',
            'test-series-1',
            409,
            None,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes.sql'],
            ),
        ),
        # uniq already added
        pytest.param(
            'park_1',
            'driver_1',
            'test-series-1',
            409,
            None,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes.sql'],
            ),
        ),
        # exp not matched
        ('park_0', 'driver_0', 'test-series-2', 400, None),
        # exp override
        pytest.param(
            'park_0',
            'driver_0',
            'test-series-2',
            200,
            None,
            marks=pytest.mark.config(
                DRIVER_PROMOCODES_SERIES_EXPERIMENT_OVERRIDES={
                    'test-series-2': 'driver_promocodes_enabled',
                },
            ),
        ),
    ],
)
async def test_driver_promocodes_add_by_name(
        taxi_driver_promocodes,
        parks,
        load_json,
        mockserver,
        park_id,
        driver_id,
        name,
        code,
        response_list,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': f'{park_id}_{driver_id}',
                    'data': {'unique_driver_id': 'unique_0'},
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        return {
            'profiles': [
                {
                    'unique_driver_id': 'unique_0',
                    'data': [
                        {
                            'park_id': 'park_0',
                            'driver_profile_id': 'driver_0',
                            'park_driver_profile_id': 'park_0_driver_0',
                        },
                        {
                            'park_id': 'park_1',
                            'driver_profile_id': 'driver_1',
                            'park_driver_profile_id': 'park_1_driver_1',
                        },
                    ],
                },
            ],
        }

    response = await taxi_driver_promocodes.post(
        'driver/v1/promocodes/v1/add-by-name',
        json={'name': name},
        headers={
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
            'X-Request-Application': 'taximeter',
            'X-Request-Application-Version': '9.37 (1234)',
            'X-Request-Platform': 'android',
            'Accept-Language': 'ru',
        },
    )
    assert response.status_code == code
    if response_list:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list', params={'name': name},
        )
        assert utils.remove_not_testable_promocodes(
            response.json(),
        ) == utils.remove_not_testable_promocodes(load_json(response_list))
