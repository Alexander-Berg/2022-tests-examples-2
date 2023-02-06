import pytest

FLEET_TYPE = 'uberdriver'
REQUEST_OK = {'park_id': 'ParkOne', 'app_family': FLEET_TYPE}
ENDPOINT_URL = '/v1/sync/park'


@pytest.fixture(autouse=True)
def taximeter_xservice(mockserver):
    @mockserver.json_handler('/taximeter-xservice/aggregator/db/add')
    def _agg_handler(request):
        return {}


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneUber', '{FLEET_TYPE}');""",
    ],
)
async def test_sync_park_ok(
        taxi_fleet_synchronizer, mongodb, mock_fleet_parks_list,
):
    init_parks_num = len(list(mongodb.dbparks.find({})))
    assert not list(mongodb.dbparks.find({'fleet_type': FLEET_TYPE}))

    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkOneUber',
            'city': 'CityOne',
            'login': 'loginOne - Таксометр X',
            'name': 'ParkNameOne - Таксометр X',
            'fleet_type': FLEET_TYPE,
            'is_active': True,
        },
    )
    await taxi_fleet_synchronizer.invalidate_caches()
    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json=REQUEST_OK,
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json()['mapped_park_id'] == 'ParkOneUber'

    assert len(list(mongodb.dbparks.find({}))) == init_parks_num + 1

    mapped_parks = list(mongodb.dbparks.find({'fleet_type': FLEET_TYPE}))
    assert len(mapped_parks) == 1


async def test_forbidden(
        taxi_fleet_synchronizer, mongodb, mock_fleet_parks_list,
):
    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'ParkFour', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'forbidden',
        'message': 'The park is not allowed to create new disp',
    }
    assert response.headers['X-YaTaxi-Error-Code'] == '403'


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneUber', '{FLEET_TYPE}')
        ON CONFLICT DO NOTHING;""",
    ],
)
async def test_mapped_active(
        taxi_fleet_synchronizer, mongodb, pgsql, mock_fleet_parks_list,
):
    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkOneUber',
            'city': 'CityOne',
            'login': 'loginOne - Таксометр X',
            'name': 'ParkNameOne - Таксометр X',
            'fleet_type': FLEET_TYPE,
            'is_active': True,
        },
    )

    await taxi_fleet_synchronizer.invalidate_caches()

    # delete from pg to be sure the answer from cache is returned
    with pgsql['fleet-synchronizer-db'].cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM fleet_sync.parks_mappings
            WHERE park_id = 'ParkOne'
              AND mapped_park_id = 'ParkOneUber';
            """,
        )

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'ParkOne', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'mapped_park_id': 'ParkOneUber',
        'already_existed': True,
    }


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneUber', '{FLEET_TYPE}')
        ON CONFLICT DO NOTHING;""",
    ],
)
@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        FLEET_TYPE: {'cities': [], 'enabled': True, 'park_ids': ['ParkOne']},
    },
)
async def test_mapped_not_active(
        taxi_fleet_synchronizer, mongodb, pgsql, mock_fleet_parks_list,
):
    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkOneUber',
            'city': 'CityOne',
            'login': 'loginOne - Таксометр X',
            'name': 'ParkNameOne - Таксометр X',
            'fleet_type': FLEET_TYPE,
            'is_active': False,
        },
    )

    await taxi_fleet_synchronizer.invalidate_caches()

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'ParkOne', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'mapped_park_id': 'ParkOneUber',
        'already_existed': False,
    }
    mapped_doc = mongodb.dbparks.find_one({'_id': 'ParkOneUber'})
    assert mapped_doc['is_active']


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneUber', '{FLEET_TYPE}')
        ON CONFLICT DO NOTHING;""",
    ],
)
@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        FLEET_TYPE: {
            'cities': ['CityOne'],
            'enabled': True,
            'park_ids': ['ParkOneUber'],
        },
    },
)
async def test_uberdriver(
        taxi_fleet_synchronizer, mongodb, mock_fleet_parks_list,
):
    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkOneUber',
            'city': 'CityOne',
            'login': 'loginOne - Таксометр X',
            'name': 'ParkNameOne - Таксометр X',
            'fleet_type': FLEET_TYPE,
            'is_active': True,
        },
    )

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'ParkOneUber', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'forbidden',
        'message': 'The park is not allowed to create new disp',
    }
    assert response.headers['X-YaTaxi-Error-Code'] == '403'


@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        FLEET_TYPE: {
            'cities': ['CityOne'],
            'enabled': True,
            'park_ids': ['ParkSix'],
        },
    },
)
async def test_driver_partner(
        taxi_fleet_synchronizer, mongodb, mock_fleet_parks_list,
):
    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'ParkSix', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'forbidden',
        'message': 'The park is not allowed to create new disp',
    }
    assert response.headers['X-YaTaxi-Error-Code'] == '403'


@pytest.mark.config(FLEET_SYNCHRONIZER_DO_SYNC_EVERYTHING=True)
@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        FLEET_TYPE: {
            'cities': ['CityOne'],
            'enabled': True,
            'park_ids': ['park_1'],
        },
    },
)
@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('park_1', 'uber_1', '{FLEET_TYPE}');
        """,
    ],
)
@pytest.mark.parametrize('xservice_status', [200, 404, 500])
async def test_do_sync_everything(
        taxi_fleet_synchronizer,
        mock_fleet_parks_list,
        mongodb,
        driver_work_rules,
        dispatcher_access_control,
        mockserver,
        xservice_status,
):
    dispatcher_access_control.set_init_park('park_1')
    driver_work_rules.set_rules('park_1', [1, 2])
    driver_work_rules.set_rules('uber_1', [3])

    mongodb.dbparks.update_one(
        {'_id': 'uber_1'},
        {
            '$set': {
                'city': 'CityOne',
                'fleet_type': FLEET_TYPE,
                'is_active': True,
                'login': 'loginUberOne',
            },
            '$currentDate': {
                'modified_date': {'$type': 'date'},
                'updated_ts': {'$type': 'timestamp'},
            },
        },
        upsert=True,
    )
    await taxi_fleet_synchronizer.invalidate_caches()

    @mockserver.json_handler('/taximeter-xservice/aggregator/db/add')
    def _agg_handler(request):
        return mockserver.make_response(status=xservice_status)

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={'park_id': 'park_1', 'app_family': FLEET_TYPE},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'mapped_park_id': 'uber_1',
        'already_existed': True,
    }

    assert driver_work_rules.mock_order_types_list.times_called == 1
    assert driver_work_rules.mock_order_types_put.times_called == 1
    assert driver_work_rules.mock_list_rules.times_called == 1
    assert driver_work_rules.mock_get_extended_rule.times_called == 2
    assert driver_work_rules.mock_put_extended_rule.times_called == 2

    mapped_rules = driver_work_rules.get_rules('uber_1')
    assert {rule['id'] for rule in mapped_rules} == {
        'rule_1',
        'rule_2',
        'rule_3',
    }

    dac_fixture = dispatcher_access_control
    assert dac_fixture.mock_groups_list.times_called == 2
    assert dac_fixture.mock_sync_parks_groups.times_called == 2
    assert dac_fixture.mock_sync_parks_groups_grants.times_called == 2

    assert dac_fixture.mock_parks_groups_users_list.times_called == 2
    assert dac_fixture.mock_sync_parks_users.times_called == 2
