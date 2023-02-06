import pytest

HANDLER = '/v1/eats-couriers-binding/updates'

BINDING_1 = {
    'taxi_id': 'park_id_1_driver_id_1',
    'eats_id': 'external_id_1',
    'courier_app': 'taximeter',
}
BINDING_2 = {
    'taxi_id': 'park_id_1_driver_id_2',
    'eats_id': 'external_id_2',
    'courier_app': 'taximeter',
}
BINDING_4 = {
    'taxi_id': 'park_id_4_driver_id_4',
    'eats_id': 'external_id_4',
    'courier_app': 'eats',
}


@pytest.fixture(name='mock_fleet_parks_list')
def _mock_fleet_parks_list(mockserver, load_json):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_change_logger(request):
        return load_json('fleet_parks.json')


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    [
        pytest.param(
            {},
            200,
            {
                'has_next': False,
                'last_known_revision': '0_2_1',
                'binding': [BINDING_1, BINDING_2, BINDING_4],
            },
            id='without params',
        ),
        pytest.param(
            {'last_known_revision': '0_1_1'},
            200,
            {
                'has_next': False,
                'last_known_revision': '0_2_1',
                'binding': [BINDING_2, BINDING_4],
            },
            id='with old cursor',
        ),
        pytest.param(
            {'last_known_revision': '0_2_1'},
            200,
            {'has_next': False, 'last_known_revision': '0_2_1', 'binding': []},
            id='with last cursor',
        ),
        pytest.param(
            {'limit': 1},
            200,
            {
                'has_next': True,
                'last_known_revision': '0_1_1',
                'binding': [BINDING_1],
            },
            id='with limit',
        ),
        pytest.param(
            {'last_known_revision': '0_1_1', 'limit': 1},
            200,
            {
                'has_next': True,
                'last_known_revision': '0_1_2',
                'binding': [BINDING_2],
            },
            id='with limit and cursor',
        ),
        pytest.param(
            {'last_known_revision': '0_1_1', 'limit': 5},
            200,
            {
                'has_next': False,
                'last_known_revision': '0_2_1',
                'binding': [BINDING_2, BINDING_4],
            },
            id='with overlimit',
        ),
        pytest.param(
            {'last_known_revision': '0_3_0'}, 429, {}, id='with future cursor',
        ),
    ],
)
async def test_courier_profiles(
        taxi_driver_profiles,
        mock_fleet_parks_list,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_driver_profiles.get(HANDLER, params=params)
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ('work_status', 'expect_driver_1'),
    [
        ('working', True),
        ('not_working', False),
        ('fired', False),
        (None, False),
    ],
)
async def test_courier_profiles_skip_not_working(
        taxi_driver_profiles,
        mock_fleet_parks_list,
        mongodb,
        work_status,
        expect_driver_1,
):
    if work_status:
        mongodb.dbdrivers.update(
            {'_id': 'id_1'}, {'$set': {'work_status': work_status}},
        )
    else:
        mongodb.dbdrivers.update(
            {'_id': 'id_1'}, {'$unset': {'work_status': 1}},
        )

    expected_response = {
        'has_next': False,
        'last_known_revision': '0_2_1',
        'binding': [BINDING_1, BINDING_2, BINDING_4],
    }
    response = await taxi_driver_profiles.get(HANDLER, params={})
    assert response.status_code == 200
    if not expect_driver_1:
        expected_response['binding'].remove(BINDING_1)
    assert response.json() == expected_response


@pytest.mark.now('1970-01-01T00:00:01Z')
async def test_lagging_cursor(taxi_driver_profiles, mock_fleet_parks_list):
    expected_response = {
        'has_next': False,
        'last_known_revision': '0_1_0',  # instead of last record ts 0_2_1
        'binding': [BINDING_1, BINDING_2, BINDING_4],
    }

    response = await taxi_driver_profiles.get(HANDLER)
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_empty_revision(taxi_driver_profiles, mock_fleet_parks_list):
    expected_response = {
        'has_next': False,
        'last_known_revision': '0_2_1',
        'binding': [BINDING_1, BINDING_2, BINDING_4],
    }

    response = await taxi_driver_profiles.get(
        f'{HANDLER}?last_known_revision=',
    )
    assert response.status_code == 200
    assert response.json() == expected_response
