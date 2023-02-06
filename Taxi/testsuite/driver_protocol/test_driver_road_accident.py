import pytest


# ./flatc -b file.fbs file.json
@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.75',
    },
    ROAD_ACCIDENT_MIN_SPEED_TO_CONFIRM=0,
)
def test_driver_road_accident_simple(
        taxi_driver_protocol,
        load_binary,
        load_json,
        db,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=999&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.75 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200
    doc = db.road_accidents.find_one({'driver_id': '888'})
    fbs_json = load_json('road_accident.json')
    assert doc['db_id'] == '999'
    assert doc['driver_id'] == '888'
    assert not doc['status']
    assert fbs_json['order_id'] == doc['alias_id']


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.73',
    },
)
@pytest.mark.parametrize(
    'user_agent, code',
    [
        ('', 500),
        ('Taximeter 8.75 (562)', 401),
        ('Taximeter 8.73 (1231)', 200),
        ('Taximeter-AZ 8.74 (1111)', 401),
        ('Taximeter-AZ 8.73 (1231)', 200),
    ],
)
def test_driver_road_accident_unauth(
        user_agent, code, taxi_driver_protocol, load_binary, db,
):
    response = taxi_driver_protocol.post(
        'driver/road-accident',
        headers={'Accept-Language': 'ru', 'User-Agent': user_agent},
        data=load_binary('road_accident.bin'),
    )
    assert response.status_code == code


def test_driver_road_accident_disabled(
        taxi_driver_protocol, load_binary, db, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=999&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter-AZ 8.84 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200
    assert db.road_accidents.find_one({'driver_id': 'mydriverid'}) is None


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.75',
    },
)
def test_driver_road_accident_disabled_by_version(
        taxi_driver_protocol, load_binary, db, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=999&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter-AZ 8.84 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': True,
        'min_taximeter_version': '8.75',
    },
)
def test_driver_road_accident_allow_no_order(
        taxi_driver_protocol, load_binary, db, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=999&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter-AZ 8.84 (562)',
        },
        data=load_binary('road_accident_no_order.bin'),
    )

    assert response.status_code == 200
    doc = db.road_accidents.find({'driver_id': '888'})
    assert 'alias_id' not in doc


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.75',
    },
    ROAD_ACCIDENT_MIN_SPEED_TO_CONFIRM=1000,
)
def test_driver_road_accident_filtered_out(
        taxi_driver_protocol,
        load_binary,
        load_json,
        db,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('123', 'qwerty123', '456')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=123&session=qwerty123',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.75 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200
    assert db.road_accidents.find_one({'driver_id': '456'}) is None


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.75',
    },
    ROAD_ACCIDENT_MIN_SPEED_TO_CONFIRM=1000,
    ROAD_ACCIDENT_STORE_UNCONFIRMED=True,
)
def test_driver_road_accident_unconfirmed_stored(
        taxi_driver_protocol,
        load_binary,
        load_json,
        db,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('123', 'qwerty123', '456')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=123&session=qwerty123',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.75 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200
    doc = db.road_accidents.find_one({'driver_id': '456'})
    assert doc['status'] == 2


@pytest.mark.config(
    ROAD_ACCIDENT_PARAMS={
        'enabled': True,
        'allow_no_order': False,
        'min_taximeter_version': '8.75',
    },
    ROAD_ACCIDENT_MIN_SPEED_TO_CONFIG=100,
)
def test_driver_road_accident_confirmed(
        taxi_driver_protocol,
        load_binary,
        load_json,
        db,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('123', 'qwerty123', '456')

    response = taxi_driver_protocol.post(
        'driver/road-accident?db=123&session=qwerty123',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.75 (562)',
        },
        data=load_binary('road_accident.bin'),
    )

    assert response.status_code == 200
    doc = db.road_accidents.find_one({'driver_id': '456'})
    assert doc['status'] is None
