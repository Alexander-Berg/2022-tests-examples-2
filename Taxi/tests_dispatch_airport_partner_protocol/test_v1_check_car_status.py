import pytest

from tests_dispatch_airport_partner_protocol import common
import tests_dispatch_airport_partner_protocol.utils as utils


def check_response(
        resp, expected_results, need_to_add_default_expected_results=True,
):
    assert resp.status_code == 200, f'{expected_results}'
    resp_json = resp.json()

    driver_not_found_reasons = [
        {'code': 'DRIVER_NOT_FOUND', 'message': 'Driver not found'},
    ]

    expected_results['allowed_parkings'] = []
    if (
            'reasons' in expected_results
            and expected_results['reasons'] == driver_not_found_reasons
    ):
        expected_results['allowed_to_park'] = False
        expected_results['can_take_orders'] = False
        assert resp_json == expected_results
        return

    expected_results['driver_phone'] = ''
    expected_results['accepted_at'] = '2020-02-02T00:00:00+00:00'
    expected_results['position'] = [0.0, 0.0]
    if need_to_add_default_expected_results:
        expected_results['allowed_to_park'] = False
        expected_results['can_take_orders'] = False
        if 'reasons' not in expected_results:
            expected_results['reasons'] = [
                {'code': 'DriverBlocked', 'message': 'DriverBlocked'},
            ]
    assert resp_json['accepted_at'] is not None
    resp_json['accepted_at'] = '2020-02-02T00:00:00+00:00'
    assert resp_json == expected_results


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'not_normalized_number, expected_result',
    [
        # contains russian letters
        ('A11  1AA', {'current_parking_id': 'partner_parking1'}),
        ('B 111BB  ', {'current_parking_id': 'partner_parking1'}),
    ],
)
async def test_input_normalization(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        not_normalized_number,
        expected_result,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': not_normalized_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    check_response(resp, expected_result)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'parking_lot, car_number, expected_result',
    [
        # запрос на 1) расшаренную между двумя парковками машину C112CC (1 и 2)
        # 2) на машину, относящуюся только к этой парковке
        ('parking_lot1', 'C112CC', {'current_parking_id': 'partner_parking1'}),
        ('parking_lot1', 'A111AA', {'current_parking_id': 'partner_parking1'}),
        # запрос на 1) расшаренную между двумя парковками машину A223AA (2 и 3)
        # 2) на машину, отсутсвующую на парковке (номер 666)
        ('parking_lot2', 'A223AA', {'current_parking_id': 'partner_parking2'}),
        ('parking_lot2', 'A666AA', {'car_number': 'A666AA'}),
        # запрос на одну расшаренную между двумя парковками
        # машину A223AA (2 и 3)
        ('parking_lot3', 'A223AA', {'current_parking_id': 'partner_parking3'}),
    ],
)
async def test_return_selected_cars_on_parking_lot(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        parking_lot,
        car_number,
        expected_result,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': parking_lot, 'car_number': car_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    if car_number == 'A666AA':
        expected_result = {
            'allowed_to_park': False,
            'can_take_orders': False,
            'reasons': [
                {'code': 'DRIVER_NOT_FOUND', 'message': 'Driver not found'},
            ],
        }
        check_response(resp, expected_result, False)
    else:
        check_response(resp, expected_result)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
async def test_negative(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'not_existing_parking_lot', 'car_number': 'A111AA'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'PARKING_ZONE_NOT_FOUND'

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {
            'parking_id': 'parking_lot1',
            'car_number': 'not_existing_car_number',
        },
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'allowed_parkings': [],
        'allowed_to_park': False,
        'can_take_orders': False,
        'reasons': [
            {'code': 'DRIVER_NOT_FOUND', 'message': 'Driver not found'},
        ],
    }

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': 'A111AA'},
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
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': 'A111AA'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'adksfl34243j342ek33'},
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'iiksfl322222242ek33'},
    )
    assert resp.status_code == 200


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_dispatch_airport.sql'],
)
@pytest.mark.parametrize(
    'car_number, expected_result',
    [
        # driver not filtered
        (
            'A222AA',
            {
                'allowed_to_park': False,
                'can_take_orders': False,
                'reasons': [
                    {'code': 'filter_reason', 'message': 'filter_reason'},
                ],
            },
        ),
        # driver filtered with excluded reason
        ('A333AA', {'allowed_to_park': True, 'can_take_orders': True}),
        # driver filtered
        (
            'A111AA',
            {
                'allowed_to_park': True,
                'can_take_orders': True,
                'current_parking_id': 'partner_parking1',
            },
        ),
    ],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_return_data_from_dispatch_airport(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        car_number,
        expected_result,
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
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': car_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    check_response(resp, expected_result, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_same_car_number.sql'],
)
@pytest.mark.parametrize(
    'car_number',
    [
        # driver with no same car_number
        'A111AA',
        # driver with order id vs no order id
        'B222BB',
        # driver has no block reason vs has block reason
        'C333CC',
        # driver dbid_uuid6 vs dbid_uuid7
        'D444DD',
        # driver can take orders vs can't take orders
        'E555EE',
    ],
)
async def test_same_car_number(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        car_number,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_CHECK_ALLOWED_PROVIDERS': True,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_car_status',
        {'parking_id': 'parking_lot1', 'car_number': car_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_result = load_json('expected_same_car_number_result.json')[
        car_number
    ]

    check_response(resp, expected_result, False)


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

    for car_number in ['A111AA', 'A222AA', 'A333AA']:
        await taxi_dispatch_airport_partner_protocol.post(
            '/1.0/check_car_status',
            {'parking_id': 'parking_lot1', 'car_number': car_number},
            headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
        )

    await utils.check_handles_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        mocked_time,
    )
