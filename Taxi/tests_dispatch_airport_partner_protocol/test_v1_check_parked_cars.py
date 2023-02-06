import pytest

from tests_dispatch_airport_partner_protocol import common
import tests_dispatch_airport_partner_protocol.utils as utils


def check_response(
        resp, expected_results, need_to_add_default_expected_results=True,
):
    assert resp.status_code == 200
    resp_json = resp.json()
    resp_json['results'].sort(key=lambda e: (e['car_number']))

    for value in expected_results:
        value['allowed_parkings'] = []
        value['driver_phone'] = ''
        value['accepted_at'] = '2020-02-02T00:00:00+00:00'
    if need_to_add_default_expected_results:
        for value in expected_results:
            value['allowed_to_park'] = False
            value['can_take_orders'] = False
            value['reasons'] = [
                {'code': 'DriverBlocked', 'message': 'DriverBlocked'},
            ]

    for value in resp_json['results']:
        assert value['accepted_at'] is not None
        value['accepted_at'] = '2020-02-02T00:00:00+00:00'
    assert resp_json == {'results': expected_results}


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
async def test_input_normalization(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    # contains russian letters
    not_normalized_numbers = ['A11  1AA', 'B 111BB  ']

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1', 'car_numbers': not_normalized_numbers},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    expected_results = [{'car_number': 'A111AA'}, {'car_number': 'B111BB'}]
    check_response(resp, expected_results)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'parking_lot, expected_results',
    [
        (
            # на парковке 2 типа машин
            # 1) машины только на этой парковке
            # 2) машина шаренная между парковками (C112CC на 1 и 2 парковки)
            'parking_lot1',
            [
                {'car_number': 'A111AA'},
                {'car_number': 'B111BB'},
                {'car_number': 'C112CC'},
            ],
        ),
        (
            # на парковке 2 машины шаренные между двумя парковками
            # A223AA - между 2 и 3, C112CC между 1 и 2
            'parking_lot2',
            [{'car_number': 'A223AA'}, {'car_number': 'C112CC'}],
        ),
        # на парковке одна шаренная машина
        ('parking_lot3', [{'car_number': 'A223AA'}]),
        (
            # парковка без шаренных машин
            'parking_lot4',
            [
                {'car_number': 'A444AA'},
                {'car_number': 'B444BB'},
                {'car_number': 'C444CC'},
                {'car_number': 'E444EE'},
            ],
        ),
        # парковка без машин
        ('parking_lot5', []),
    ],
)
async def test_return_all_cars_on_parking_lot(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        parking_lot,
        expected_results,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': parking_lot},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    check_response(resp, expected_results)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'parking_lot, selected_cars, expected_results',
    [
        # запрос с пустым списком
        ('parking_lot1', [], []),
        # запрос на 1) расшаренную между двумя парковками машину C112CC (1 и 2)
        # 2) на машину, относящуюся только к этой парковке
        (
            'parking_lot1',
            ['C112CC', 'A111AA'],
            [{'car_number': 'A111AA'}, {'car_number': 'C112CC'}],
        ),
        # запрос на 1) расшаренную между двумя парковками машину A223AA (2 и 3)
        # 2) на машину, отсутсвующую на парковке (номер 666)
        ('parking_lot2', ['A223AA', 'A666AA'], [{'car_number': 'A223AA'}]),
        # запрос на одну расшаренную между двумя парковками
        # машину A223AA (2 и 3)
        ('parking_lot3', ['A223AA'], [{'car_number': 'A223AA'}]),
        # запрос на несколько машин, принадлежащих только этой парковке
        (
            'parking_lot4',
            ['A444AA', 'B444BB', 'C444CC', 'E444EE'],
            [
                {'car_number': 'A444AA'},
                {'car_number': 'B444BB'},
                {'car_number': 'C444CC'},
                {'car_number': 'E444EE'},
            ],
        ),
        # запрос на одну несуществующую на парковке машину
        ('parking_lot5', ['A666AA'], []),
    ],
)
async def test_return_selected_cars_on_parking_lot(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        parking_lot,
        selected_cars,
        expected_results,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': parking_lot, 'car_numbers': selected_cars},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    check_response(resp, expected_results)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_no_car_number.sql'],
)
@pytest.mark.parametrize(
    'parking_lot, expected_results',
    [
        ('parking_lot1', [{'car_number': 'A111AA'}, {'car_number': 'C112CC'}]),
        ('parking_lot2', []),
    ],
)
async def test_parking_drivers_no_car_number(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        parking_lot,
        expected_results,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': parking_lot},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    check_response(resp, expected_results)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_no_car_number.sql'],
)
async def test_negative(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot_not_exists'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'PARKING_ZONE_NOT_FOUND'

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot_not_exists'},
        headers={'YaTaxi-Api-Key': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot_not_exists'},
        headers={},
    )
    assert resp.status_code == 400


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
async def test_check_api_token(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers={'YaTaxi-Api-Key': 'adksfl34243j342ek33'},
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers={'YaTaxi-Api-Key': 'iiksfl322222242ek33'},
    )
    assert resp.status_code == 200


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_with_order_data.sql'],
)
async def test_return_data_about_order(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    expected_results = [
        # driver without order data
        {'car_number': 'A111AA'},
        # driver with order_id data only
        {'car_number': 'A222AA', 'order_id': 'order_id2'},
        # driver with order_id and 'none' order_status value
        {
            'car_number': 'A333AA',
            'order_id': 'order_id3',
            'order_status': 'driving',
        },
        # drivers with different order_status values
        {
            'car_number': 'A444AA',
            'order_id': 'order_id4',
            'order_status': 'driving',
        },
        {
            'car_number': 'A555AA',
            'order_id': 'order_id5',
            'order_status': 'waiting',
        },
        {
            'car_number': 'A666AA',
            'order_id': 'order_id6',
            'order_status': 'complete',
        },
        {
            'car_number': 'A777AA',
            'order_id': 'order_id7',
            'order_status': 'expired',
        },
    ]
    check_response(resp, expected_results)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_with_driver_diagnostics_info.sql'],
)
async def test_return_data_from_driver_diagnostics(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_NOT_ALLOWED_TO_PARK_REASONS': (
                load_json('not_allowed_to_park_reasons.json')
            ),
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_results = [
        # driver with one tariff
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A111AA',
            'enabled_classes': ['econom'],
        },
        # driver with many tariffs
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A222AA',
            'enabled_classes': ['econom', 'comfort', 'business'],
        },
        # driver without enable tariffs
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A333AA',
            'enabled_classes': [],
        },
        # driver with one block reason
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A444AA',
            'enabled_classes': [],
            'reasons': [{'code': 'fraud', 'message': 'fraud'}],
        },
        # driver with many blocks reason
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A555AA',
            'enabled_classes': [],
            'reasons': [
                {'code': 'one_more_reason', 'message': 'one_more_reason'},
                {'code': 'tired', 'message': 'tired'},
                {'code': 'fraud', 'message': 'fraud'},
            ],
        },
    ]
    check_response(resp, expected_results, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_status.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_return_data_from_driver_status(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_NOT_ALLOWED_TO_PARK_REASONS': (
                load_json('not_allowed_to_park_reasons.json')
            ),
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_results = [
        # driver without driver_status info
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A111AA',
            'reasons': [
                {
                    'code': 'unacceptable_driver_status_translated',
                    'message': 'unacceptable_driver_status_translated',
                },
            ],
        },
        # driver online, no other block reasons
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A222AA',
        },
        # driver offline, no other block reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A333AA',
            'reasons': [
                {
                    'code': 'unacceptable_driver_status_translated',
                    'message': 'unacceptable_driver_status_translated',
                },
            ],
        },
        # driver busy, no other block reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A444AA',
            'reasons': [
                {
                    'code': 'unacceptable_driver_status_translated',
                    'message': 'unacceptable_driver_status_translated',
                },
            ],
        },
        # driver online, has other block reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A555AA',
            'reasons': [{'code': 'fraud', 'message': 'fraud'}],
        },
        # driver offline, has other block reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A666AA',
            'reasons': [
                {'code': 'fraud', 'message': 'fraud'},
                {
                    'code': 'unacceptable_driver_status_translated',
                    'message': 'unacceptable_driver_status_translated',
                },
            ],
        },
        # driver busy, has other block reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A777AA',
            'reasons': [
                {'code': 'fraud', 'message': 'fraud'},
                {
                    'code': 'unacceptable_driver_status_translated',
                    'message': 'unacceptable_driver_status_translated',
                },
            ],
        },
    ]
    check_response(resp, expected_results, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_return_data_from_dispatch_airport(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_EXCLUDED_FILTER_REASONS': [
                'excluded_filter_reason',
            ],
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    udid_hash = (
        '49c966a0532862c16c6a8d0598d393cb4c2cb86709be8a24186c8e78a5264c36'
    )
    expected_results = [
        # driver filtered
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A222AA',
            'current_parking_id': 'partner_parking1',
            'reasons': [{'code': 'filter_reason', 'message': 'filter_reason'}],
        },
        # driver filtered with excluded reason
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A333AA',
            'current_parking_id': 'partner_parking1',
        },
        # driver not filtered, empty times_queued
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A444AA',
            'current_parking_id': 'partner_parking1',
            'unique_driver_id': udid_hash,
        },
        # driver not filtered
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'А 111 АА',
            'current_parking_id': 'partner_parking1',
            'unique_driver_id': udid_hash,
            'times_queued': [
                {
                    'class': 'econom',
                    'time_queued': '2020-02-02T00:00:00+00:00',
                },
            ],
        },
    ]
    check_response(resp, expected_results, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_tags.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_check_driver_tags(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_results = [
        # driver with tag reasons
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'A222AA',
            'reasons': [
                {
                    'code': 'forbidden_tag_reason',
                    'message': 'forbidden_tag_reason',
                },
            ],
        },
        # driver with no tag reasons
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'А 111 АА',
        },
    ]
    check_response(resp, expected_results, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_same_car_number.sql'],
)
async def test_same_car_number(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_CHECK_ALLOWED_PROVIDERS': True,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_results = [
        # driver with no same car_number
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'A111AA',
        },
        # driver with order id vs no order id
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'B222BB_1',
            'order_id': 'order_id1',
        },
        # driver has no block reason vs has block reason
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'C333CC_1',
        },
        # driver dbid_uuid6 vs dbid_uuid7
        {
            'allowed_to_park': False,
            'can_take_orders': False,
            'car_number': 'D444DD_1',
            'reasons': [{'code': 'DriverBlocked', 'message': 'DriverBlocked'}],
        },
        # driver can take orders vs can't take orders
        {
            'allowed_to_park': True,
            'can_take_orders': True,
            'car_number': 'E555EE_1',
        },
    ]
    check_response(resp, expected_results, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers_metrics.sql'],
)
async def test_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        taxi_config,
        load_json,
        mocked_time,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_parked_cars',
        {'parking_id': 'parking_lot1'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    await utils.check_handles_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        mocked_time,
    )
