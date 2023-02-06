import json

import pytest

ORDER_ID = '123e4567-e89b-12d3-a456-426614174000'

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


def parametrize_geocoder_exp(
        depot_id=None, uid=None, vendor=None, personal_phone_id=None,
):
    predicate = {'type': 'true'}
    if depot_id is not None:
        predicate['depot_id'] = depot_id
    if uid is not None:
        predicate['yandex_uid'] = uid
    if vendor is not None:
        predicate['vendor'] = vendor
    if personal_phone_id is not None:
        predicate['personal_phone_id'] = personal_phone_id

    return pytest.mark.experiments3(
        name='tristero_b2b_geocoder_enable',
        consumers=['tristero-b2b/order-post'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': predicate,
                'value': {'enabled': True},
            },
        ],
        is_config=True,
    )


def _create_square_zone(location, side=0.0002):
    half_side = side / 2
    right_up_angle_lon = location['lon'] + half_side
    right_up_angle_lat = location['lat'] + half_side

    right_down_angle_lon = right_up_angle_lon
    right_down_angle_lat = location['lat'] - half_side

    left_down_angle_lon = location['lon'] - half_side
    left_down_angle_lat = right_down_angle_lat

    left_up_angle_lon = left_down_angle_lon
    left_up_angle_lat = right_up_angle_lat

    return [
        {'lon': left_up_angle_lon, 'lat': left_up_angle_lat},
        {'lon': right_up_angle_lon, 'lat': right_up_angle_lat},
        {'lon': right_down_angle_lon, 'lat': right_down_angle_lat},
        {'lon': left_down_angle_lon, 'lat': left_down_angle_lat},
        {'lon': left_up_angle_lon, 'lat': left_up_angle_lat},
    ]


def _arr_to_pos(coord, lon_lat=True):
    if not lon_lat:
        coord = coord[::-1]
    return {'lon': coord[0], 'lat': coord[1]}


@pytest.mark.parametrize('uid', ['user_id_1', None])
@pytest.mark.parametrize('customer_location', [[55.7558, 37.6173], None])
@pytest.mark.parametrize('mock_flag', [1, None])
@parametrize_geocoder_exp()
async def test_order_create_ok(
        taxi_tristero_b2b,
        mockserver,
        grocery_depots,
        uid,
        customer_location,
        yamaps,
        mock_flag,
):
    """ Checks basic order creation flow. Creation without uid must work.
        In absence of eplicit customer_location, it's being deducted
        from custormer's address """

    uri = 'ymapsbm1://geo?exit1'
    if mock_flag is not None:
        geo_object_json = {
            'description': 'Москва, Россия',
            'geocoder': {
                'address': {
                    'country': 'Россия',
                    'formatted_address': 'Россия, Москва, Садовническая улица',
                    'house': '82с2',
                    'locality': 'Москва',
                    'street': 'Садовническая улица',
                },
                'id': '8063585',
            },
            'geometry': [55.7558, 37.6173],
            'name': 'Садовническая улица, 82с2',
            'uri': uri,
        }
        yamaps.add_fmt_geo_object(geo_object_json)

    location = [37.29, 55.91]  # lon, lat
    working_hours = {
        'from': {'hour': 7, 'minute': 0},
        'to': {'hour': 23, 'minute': 0},
    }
    price = '1234.56'
    request_kind = 'hour_slot'

    customer_meta = {'key': 'value'}
    timeslot = {
        'start': '2020-09-09T18:00:00+00:00',
        'end': '2020-09-09T19:00:00+00:00',
    }
    depot = grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='depot_id',
        allow_parcels=True,
        location=_arr_to_pos(customer_location) if customer_location else None,
        auto_add_zone=False,
    )

    depot.add_zone(
        timetable=[{'day_type': 'Everyday', 'working_hours': working_hours}],
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [[_create_square_zone(depot.location)]],
        },
    )
    depot.add_zone(
        timetable=[{'day_type': 'Everyday', 'working_hours': working_hours}],
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [[_create_square_zone(_arr_to_pos(location))]],
        },
    )

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        items = []
        for i in body['items']:
            item = {
                'barcode': i['barcode'],
                'measurements': i['measurements'],
                'state': 'created',
                'state_meta': {},
                'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                    len(items),
                ),
            }
            if 'description' in i:
                item['description'] = i['description']
            items.append(item)
        assert body['timeslot'] == timeslot
        assert body['price'] == price
        if customer_location is not None:
            assert body['customer_location'] == customer_location
        else:
            assert body['customer_location'] == location
        if mock_flag is not None:
            assert body['customer_meta'] == {
                'country_iso2': 'RU',
                **customer_meta,
            }
            assert body['customer_address'] == uri
        else:
            assert body['customer_meta'] == customer_meta
            assert (
                body['customer_address']
                == 'ymapsbm1://geo?some_text&ll=37.29%2C55.91'
            )
        if uid is not None:
            assert body['uid'] == uid
        response = {
            'order_id': ORDER_ID,
            'ref_order': body['ref_order'],
            'vendor': body['vendor'],
            'delivery_date': body['delivery_date'],
            'depot_id': body['depot_id'],
            'state': 'reserved',
            'items': items,
            'customer_address': body['customer_address'],
            'customer_location': body['customer_location'],
            'token': body['token'],
            'customer_meta': customer_meta,
            'timeslot': timeslot,
            'price': body['price'],
            'request_kind': body['request_kind'],
        }
        if uid is not None:
            response['uid'] = uid
        return response

    request = {
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'depot_id',
        'customer_address': 'ymapsbm1://geo?some_text&ll={}%2C{}'.format(
            location[0], location[1],
        ),
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
            {
                'barcode': 'barcode_2',
                'measurements': {
                    'width': 2,
                    'height': 2,
                    'weight': 2,
                    'length': 2,
                },
            },
            {
                'measurements': {
                    'width': 3,
                    'height': 3,
                    'weight': 3,
                    'length': 3,
                },
            },
        ],
        'token': 'some_id',
        'customer_meta': customer_meta,
        'timeslot': timeslot,
        'price': price,
        'request_kind': request_kind,
    }
    if uid is not None:
        request['uid'] = uid
    if customer_location is not None:
        request['customer_location'] = customer_location

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == 2

    request['order_id'] = ORDER_ID
    request['vendor'] = 'beru'
    request['ref_order'] = 'ref_order_1'
    request['state'] = 'reserved'

    request.pop('items')
    if uid is not None:
        request.pop('uid')
    request.pop('delivery_date')
    got_resp = response.json()
    got_resp.pop('items')
    if customer_location is None:
        got_resp.pop('customer_location')
    if mock_flag is not None:
        got_resp.pop('customer_address')
        request.pop('customer_address')
    assert got_resp == request


@parametrize_geocoder_exp()
async def test_order_create_geocoder_settlement(
        taxi_tristero_b2b, mockserver, grocery_depots, yamaps,
):
    """ Check geocoder uses locality and settlement if it's
    not empty """

    customer_location = [55.7558, 37.6173]
    uri = 'ymapsbm1://geo?exit1'
    geo_object_json = {
        'description': 'Москва, Россия',
        'geocoder': {
            'address': {
                'country': 'Россия',
                'formatted_address': (
                    'Россия, Долгопрудный, Лихачёвское шоссе, 20к4'
                ),
                'house': '20к4',
                'settlement': 'Долгопрудный',
                'street': 'Лихачёвское шоссе',
            },
            'id': '8063585',
        },
        'geometry': [55.7558, 37.6173],
        'name': 'Лихачёвское шоссе, 20к4',
        'uri': uri,
    }
    yamaps.add_fmt_geo_object(geo_object_json)

    location = [37.29, 55.91]  # lon, lat
    working_hours = {
        'from': {'hour': 7, 'minute': 0},
        'to': {'hour': 23, 'minute': 0},
    }

    customer_meta = {
        'country': 'Россия',
        'house': '20к4',
        'settlement': 'Долгопрудный',
        'street': 'Лихачёвское шоссе',
    }
    depot = grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='depot_id',
        allow_parcels=True,
        location=_arr_to_pos(customer_location),
        auto_add_zone=False,
    )

    depot.add_zone(
        timetable=[{'day_type': 'Everyday', 'working_hours': working_hours}],
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [[_create_square_zone(depot.location)]],
        },
    )

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        items = []
        for i in body['items']:
            item = {
                'barcode': i['barcode'],
                'measurements': i['measurements'],
                'state': 'created',
                'state_meta': {},
                'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                    len(items),
                ),
            }
            if 'description' in i:
                item['description'] = i['description']
            items.append(item)
        assert body['customer_address'] == uri

        response = {
            'order_id': ORDER_ID,
            'ref_order': body['ref_order'],
            'vendor': body['vendor'],
            'delivery_date': body['delivery_date'],
            'depot_id': body['depot_id'],
            'state': 'reserved',
            'items': items,
            'customer_address': body['customer_address'],
            'customer_location': body['customer_location'],
            'customer_meta': customer_meta,
        }
        return response

    request = {
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'depot_id',
        'customer_address': 'ymapsbm1://geo?some_text&ll={}%2C{}'.format(
            location[0], location[1],
        ),
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
        ],
        'token': 'some_id',
        'customer_meta': customer_meta,
    }
    request['customer_location'] = customer_location

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 200
    assert response.json()['customer_address'] == uri


@pytest.mark.parametrize('partner_id', ['partner-id', None])
async def test_partner_id_is_forwarded_if_present(
        taxi_tristero_b2b, mockserver, partner_id,
):
    barcode = 'some-barcode'

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        request_items = body['items']
        assert len(request_items) == 1
        request_item = request_items[0]

        if partner_id is not None:
            assert request_item['partner_id'] == partner_id
        else:
            assert 'partner_id' not in request_item

        response_item = {
            'barcode': request_item['barcode'],
            'measurements': request_item['measurements'],
            'state': 'created',
            'state_meta': {},
            'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                len(request_items),
            ),
        }
        if 'description' in request_item:
            response_item['description'] = request_item['description']
        if 'partner_id' in request_item:
            response_item['partner_id'] = request_item['partner_id']

        response = {
            'order_id': ORDER_ID,
            'ref_order': body['ref_order'],
            'vendor': body['vendor'],
            'delivery_date': body['delivery_date'],
            'depot_id': body['depot_id'],
            'state': 'reserved',
            'items': [response_item],
            'token': body['token'],
        }
        return response

    item = {
        'barcode': barcode,
        'measurements': {'width': 1, 'height': 1, 'weight': 1, 'length': 1},
        'description': 'description_1',
    }
    if partner_id is not None:
        item['partner_id'] = partner_id

    request = {
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'depot_id',
        'items': [item],
        'token': 'some_id',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == 1

    assert response.json()['items'][0]['barcode'] == barcode
    if partner_id is not None:
        assert response.json()['items'][0]['partner_id'] == partner_id
    else:
        assert 'partner_id' not in response.json()['items'][0]


@pytest.mark.parametrize('depot_upd', [{'depot_id': 'another_id'}])
@pytest.mark.parametrize('customer_location', [[55.7558, 37.6173], None])
async def test_order_create_wrong_depot(
        taxi_tristero_b2b,
        mockserver,
        grocery_depots,
        depot_upd,
        customer_location,
):
    grocery_depots.add_depot(
        depot_test_id=1, depot_id='depot_id', allow_parcels=True,
    )

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        items = []
        for i in body['items']:
            item = {
                'barcode': i['barcode'],
                'measurements': i['measurements'],
                'state': 'created',
                'state_meta': {},
                'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                    len(items),
                ),
            }
            if 'description' in i:
                item['description'] = i['description']
            items.append(item)
        return {
            'order_id': ORDER_ID,
            'ref_order': body['ref_order'],
            'uid': body['uid'],
            'vendor': body['vendor'],
            'delivery_date': body['delivery_date'],
            'depot_id': body['depot_id'],
            'state': 'reserved',
            'items': items,
            'customer_address': body['customer_address'],
            'customer_location': body['customer_location'],
        }

    request = {
        'uid': 'user_id_1',
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'depot_id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
        'customer_location': customer_location,
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
        ],
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 400


@pytest.mark.parametrize('code', [409, 400])
async def test_order_create_fail(taxi_tristero_b2b, mockserver, code):
    error_message = 'some client error'

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        parcels_response = {'message': error_message}
        if code == 409:
            parcels_response['order_id'] = ORDER_ID
        return mockserver.make_response(
            json.dumps(parcels_response), status=code,
        )

    request = {
        'uid': 'user_id_1',
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'depot_id',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
            {
                'barcode': 'barcode_2',
                'measurements': {
                    'width': 2,
                    'height': 2,
                    'weight': 2,
                    'length': 2,
                },
            },
            {
                'measurements': {
                    'width': 3,
                    'height': 3,
                    'weight': 3,
                    'length': 3,
                },
            },
        ],
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == code
    response_json = response.json()
    if code == 409:
        assert response_json['order_id'] == ORDER_ID
    assert response_json['message'] == error_message


async def test_order_create_phone_number(
        taxi_tristero_b2b, mockserver, personal,
):
    """ phone_number should be exchanged to personal phone id """
    personal_phone_id = 'some-personal-phone-id'
    phone_number = '+79001234567'

    personal.check_request(
        personal_phone_id=personal_phone_id, phone=phone_number,
    )

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        assert body['personal_phone_id'] == personal_phone_id

        response = {
            'order_id': ORDER_ID,
            'ref_order': body['ref_order'],
            'vendor': body['vendor'],
            'delivery_date': body['delivery_date'],
            'depot_id': body['depot_id'],
            'state': 'reserved',
            'items': [],
            'personal_phone_id': personal_phone_id,
        }
        return response

    request = {
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'some_depot_id',
        'items': [],
        'phone_number': phone_number,
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 200
    assert personal.times_phones_store_called() == 1


async def test_order_create_personal_error(
        taxi_tristero_b2b, mockserver, personal,
):
    """ if phone_number is passed - exhange with personal is mandatory """
    phone_number = 'bad_value'
    personal.check_request(error_code=400, phone=phone_number)

    request = {
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'depot_id': 'some_depot_id',
        'items': [],
        'phone_number': phone_number,
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == 500
    assert personal.times_phones_store_called() == 1
