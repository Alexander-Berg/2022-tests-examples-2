import pytest

from tests_dispatch_airport_partner_protocol import common
import tests_dispatch_airport_partner_protocol.utils as utils


def check_response(
        resp, expected_results, need_to_add_default_expected_results=True,
):
    assert resp.status_code == 200, f'{expected_results}'
    resp_json = resp.json()
    if need_to_add_default_expected_results:
        expected_results['allow_issue'] = False
    assert resp_json == expected_results


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'not_normalized_number',
    [
        # contains russian letters
        'A11  1AA',
        'B 111BB  ',
    ],
)
async def test_input_normalization(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        not_normalized_number,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': not_normalized_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    check_response(resp, {})


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
@pytest.mark.parametrize(
    'venue_id, car_number',
    [
        # запрос на 1) расшаренную между двумя парковками машину C112CC (1 и 2)
        # 2) на машину, относящуюся только к этой парковке
        ('venue_id1', 'C112CC'),
        ('venue_id1', 'A111AA'),
        # запрос на 1) расшаренную между двумя парковками машину A223AA (2 и 3)
        # 2) на машину, отсутсвующую на парковке (номер 666)
        ('venue_id2', 'A223AA'),
        ('venue_id2', 'A666AA'),
        # запрос на одну расшаренную между двумя парковками
        # машину A223AA (2 и 3)
        ('venue_id3', 'A223AA'),
    ],
)
async def test_return_selected_car_on_parking_lot(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        venue_id,
        car_number,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
                'venue_id2': 'parking_lot2',
                'venue_id3': 'parking_lot3',
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': venue_id, 'car_number': car_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    if car_number == 'A666AA':
        expected_result = {
            'allow_issue': False,
            'reasons': [
                {'code': 'DRIVER_NOT_FOUND', 'message': 'Driver not found'},
            ],
        }
        check_response(resp, expected_result, False)
    else:
        check_response(resp, {})


@pytest.mark.config()
@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_car_info.sql'],
)
@pytest.mark.parametrize(
    'car_number', ['A444AA', 'B444BB', 'C444CC', 'D444DD', 'E444EE'],
)
async def test_return_car_info(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        load_json,
        car_number,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
            },
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_CHECK_ALLOWED_PROVIDERS': True,
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': car_number},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )

    expected_result = load_json('expected_car_info.json')[car_number]

    check_response(resp, expected_result, False)


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol', files=['parking_drivers.sql'],
)
async def test_negative(
        taxi_dispatch_airport_partner_protocol, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
                'venue_id2': 'not_existing_parking_lot',
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'not_existing_venue', 'car_number': 'A111AA'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'VENUE_NOT_FOUND'

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id2', 'car_number': 'A111AA'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'PARKING_ZONE_NOT_FOUND'

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'not_existing_car_number'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'allow_issue': False,
        'reasons': [
            {'code': 'DRIVER_NOT_FOUND', 'message': 'Driver not found'},
        ],
    }

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'A111AA'},
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
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'A111AA'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'adksfl34243j342ek33'},
    )
    assert resp.status_code == 200

    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/check_issue_rfid',
        {'venue_id': 'venue_id1', 'car_number': 'A111AA'},
        headers={'YaTaxi-Api-Key': 'iiksfl322222242ek33'},
    )
    assert resp.status_code == 200


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
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_RFID_VENUES_MAPPING': {
                'venue_id1': 'parking_lot1',
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    for car_number in ['A111AA', 'A222AA', 'A333AA']:
        await taxi_dispatch_airport_partner_protocol.post(
            '/1.0/check_issue_rfid',
            {'venue_id': 'venue_id1', 'car_number': car_number},
            headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
        )

    await utils.check_handles_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        mocked_time,
        True,
    )
