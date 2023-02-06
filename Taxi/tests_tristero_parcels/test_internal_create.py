import datetime
import decimal

import pytest

from tests_tristero_parcels import headers


LEGAL_ENTITY_VENDOR_CFG = 'ООО Яндекс.Беру -- тест'
LEGAL_ENTITY_CARGO_CARRIER_CFG = 'ООО Яндекс.Такси - тест'


def _convert_db_datetime(time):
    return time.astimezone(datetime.timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%S.%fZ',
    )


@pytest.mark.config(
    TRISTERO_LEGAL_ENTITIES_VENDOR={'__default__': LEGAL_ENTITY_VENDOR_CFG},
    TRISTERO_LEGAL_ENTITY_CARGO_CARRIER=LEGAL_ENTITY_CARGO_CARRIER_CFG,
)
@pytest.mark.parametrize(
    'address,location,meta,uid, partner_id, price, request_kind',
    [
        (None, None, {'key': 'value'}, 'user_id_1', 'partner_id', None, None),
        (
            None,
            [55.7558, 37.6173],
            {'key': 'value'},
            'user_id_1',
            'partner_id',
            '1355',
            'hour_slot',
        ),
        (
            'ymapsbm1://geo?some_text_here',
            None,
            None,
            'user_id_1',
            'partner_id',
            '0.0',
            'wide_slot',
        ),
        (
            'ymapsbm1://geo?some_text_here',
            [59.9311, 30.3609],
            None,
            'user_id_1',
            'partner_id',
            '123.45',
            'on_demand',
        ),
        (None, None, None, None, None, None, None),
    ],
)
async def test_internal_order_create(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        load_json,
        address,
        location,
        meta,
        uid,
        partner_id,
        price,
        request_kind,
):
    vendor = 'beru'
    ref_order = 'ref_order_1'
    token = 'some-token'
    measurements = {'width': 1, 'height': 2, 'length': 3, 'weight': 4}

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        for item in request.json['items']:
            assert item['title'] == '{} Посылка {}/{}'.format(
                vendor, ref_order, item['barcode'][0],
            )
            assert item['source'] == vendor + (
                ('-' + partner_id) if partner_id is not None else ''
            )
            data = item['data']
            assert data['contractor'] == LEGAL_ENTITY_VENDOR_CFG
            assert data['cargo_carrier'] == LEGAL_ENTITY_CARGO_CARRIER_CFG
            assert 'expiry_date' not in data
            assert data['width'] == measurements['width']
            assert data['height'] == measurements['height']
            assert data['length'] == measurements['length']
            assert data['weight'] == measurements['weight']
            barcode = item['barcode'][0]
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(barcode.split('_')[1]),
                },
            )
        return {'code': 'OK', 'items': response_items}

    request = {
        'ref_order': ref_order,
        'vendor': vendor,
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000000Z',
        'items': [
            {'barcode': 'barcode_1', 'measurements': measurements},
            {
                'barcode': 'barcode_2',
                'measurements': measurements,
                'description': 'description num 2',
            },
            {
                'barcode': 'barcode_3',
                'measurements': measurements,
                'description': 'description num 3',
            },
        ],
        'token': 'some-token',
        'timeslot': {
            'start': '2020-10-05T17:00:00.000000Z',
            'end': '2020-10-05T18:00:00.000000Z',
        },
        'personal_phone_id': 'some-phone-id',
    }
    if address is not None:
        request['customer_address'] = address
    if location is not None:
        request['customer_location'] = location
    if meta is not None:
        request['customer_meta'] = meta
    if uid is not None:
        request['uid'] = uid
    if partner_id is not None:
        for item in request['items']:
            item['partner_id'] = partner_id
    if price is not None:
        request['price'] = price
    if request_kind is not None:
        request['request_kind'] = request_kind

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request,
    )
    assert response.status_code == 200
    response_json = response.json()

    for field in ['ref_order', 'depot_id']:
        assert response_json[field] == request[field]
    if address is not None:
        assert response_json['customer_address'] == request['customer_address']
    if meta is not None:
        assert response_json['customer_meta'] == request['customer_meta']
    if uid is not None:
        assert response_json['uid'] == request['uid']
    if price is not None:
        assert float(response_json['price']) == float(request['price'])
    if request_kind is not None:
        assert response_json['request_kind'] == request['request_kind']

    assert response_json['state'] == 'reserved'
    response_items = response_json['items']
    assert len(response_items) == 3
    assert all([i['state'] == 'created' for i in response_items])
    assert all([i['measurements'] == measurements for i in response_items])
    assert {i['barcode'][-1] for i in response_items} == {'1', '2', '3'}

    orders_db = tristero_parcels_db.fetch_from_sql(
        'SELECT uid, depot_id, vendor, ref_order, delivery_at, status, '
        'customer_address, customer_location, token, customer_meta, '
        'timeslot_start, timeslot_end, personal_phone_id, price, request_kind '
        'FROM parcels.orders '
        'WHERE id = \'{}\''.format(response_json['order_id']),
    )
    assert len(orders_db) == 1
    order_db = orders_db[0]
    assert order_db[0] == uid
    assert order_db[1] == request['depot_id']
    assert order_db[2] == request['vendor']
    assert order_db[3] == request['ref_order']
    assert _convert_db_datetime(order_db[4]) == request['delivery_date']
    assert order_db[5] == 'reserved'
    assert order_db[6] == address
    assert (
        order_db[7] == location
        if not location
        else '(' + str(location[0]) + ',' + str(location[1]) + ')'
    )
    assert order_db[8] == token
    assert order_db[9] == (meta if meta else {})
    assert _convert_db_datetime(order_db[10]) == request['timeslot']['start']
    assert _convert_db_datetime(order_db[11]) == request['timeslot']['end']
    assert order_db[12] == request['personal_phone_id']
    assert order_db[13] == (
        decimal.Decimal(price) if price is not None else None
    )
    assert order_db[14] == request_kind

    items_db = tristero_parcels_db.fetch_from_sql(
        'SELECT id, vendor, barcode, wms_id, '
        'description, status FROM parcels.items '
        'WHERE order_id = \'{}\''.format(response_json['order_id']),
    )
    assert len(items_db) == 3
    assert all([i[1] == request['vendor'] for i in items_db])
    assert all([i[5] == 'created' for i in items_db])

    expected_items = {
        i['id']: {'barcode': i['barcode']} for i in response_items
    }
    fetched_items = {i[0]: {'barcode': i[2]} for i in items_db}
    assert expected_items == fetched_items


@pytest.mark.config(
    TRISTERO_LEGAL_ENTITIES_VENDOR={'__default__': LEGAL_ENTITY_VENDOR_CFG},
    TRISTERO_LEGAL_ENTITY_CARGO_CARRIER=LEGAL_ENTITY_CARGO_CARRIER_CFG,
)
async def test_internal_same_ref_order(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    ref_order = 'same-ref-order'
    vendors = ['beru', 'ne beru', 'random-vendor']
    responses = []
    measurements = {'width': 1, 'height': 2, 'length': 3, 'weight': 4}

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        for item in request.json['items']:
            assert item['title'] == '{} Посылка {}/{}'.format(
                vendors[int(item['barcode'][0][-1])],
                ref_order,
                item['barcode'][0],
            )
            data = item['data']
            assert data['contractor'] == LEGAL_ENTITY_VENDOR_CFG
            assert data['cargo_carrier'] == LEGAL_ENTITY_CARGO_CARRIER_CFG
            assert 'expiry_date' not in data
            assert data['width'] == measurements['width']
            assert data['height'] == measurements['height']
            assert data['length'] == measurements['length']
            assert data['weight'] == measurements['weight']
            barcode = item['barcode'][0]
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(barcode.split('_')[1]),
                },
            )
        return {'code': 'OK', 'items': response_items}

    for i, vendor in enumerate(vendors):
        request = {
            'ref_order': ref_order,
            'vendor': vendor,
            'depot_id': 'depot_id_1',
            'delivery_date': '2020-10-05T16:28:00.000000Z',
            'items': [
                {
                    'barcode': 'barcode_1' + str(i),
                    'measurements': measurements,
                },
                {
                    'barcode': 'barcode_2' + str(i),
                    'measurements': measurements,
                    'description': 'description num 2',
                },
                {
                    'barcode': 'barcode_3' + str(i),
                    'measurements': measurements,
                    'description': 'description num 3',
                },
            ],
            'token': 'some-token',
            'timeslot': {
                'start': '2020-10-05T17:00:00.000000Z',
                'end': '2020-10-05T18:00:00.000000Z',
            },
            'personal_phone_id': 'some-phone-id',
        }
        response = await taxi_tristero_parcels.post(
            '/internal/v1/parcels/order',
            headers=headers.DEFAULT_HEADERS,
            json=request,
        )
        responses.append(response)

    assert all([response.status_code == 200 for response in responses])
    orders_db = tristero_parcels_db.fetch_from_sql(
        'SELECT id, ref_order, vendor FROM '
        'parcels.orders WHERE ref_order = \'{}\''.format(ref_order),
    )
    assert len(orders_db) == 3
    assert sorted([order[2] for order in orders_db]) == sorted(vendors)


@pytest.mark.parametrize(
    'vendor, token, expected_status_code, order_status',
    [
        pytest.param(None, None, 409, 'reserved', id='request error'),
        pytest.param(
            'some-vendor', 'some-token', 200, 'reserved', id='request retry',
        ),
        pytest.param(
            'some-vendor',
            'some-token',
            409,
            'created',
            id='order created but not reserved',
        ),
    ],
)
async def test_internal_order_create_409(
        taxi_tristero_parcels,
        tristero_parcels_db,
        vendor,
        token,
        expected_status_code,
        order_status,
):
    with tristero_parcels_db as db:
        order = db.add_order(
            1, token=token, vendor=vendor, status=order_status,
        )
    await taxi_tristero_parcels.invalidate_caches()

    request = {
        'ref_order': order.ref_order,
        'vendor': order.vendor,
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        ],
    }
    if vendor:
        request['vendor'] = vendor

    if token:
        request['token'] = token
    else:
        request['token'] = 'some-other-token'

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order', json=request,
    )
    assert response.status_code == expected_status_code
    assert response.json()['order_id'] == order.order_id


async def test_internal_order_create_load_all_items_bug(
        taxi_tristero_parcels, tristero_parcels_db, testpoint,
):
    """Test bug LAVKABACKEND-4307"""

    with tristero_parcels_db as db:
        order_1 = db.add_order(1)
        parcel_1 = order_1.add_parcel(1)
        order_2 = db.add_order(2)
        order_2.add_parcel(2)

    await taxi_tristero_parcels.invalidate_caches()

    @testpoint('order_items')
    def check_items_quantity(data):
        assert len(data['items']) == 1
        assert data['items'][0] == parcel_1.barcode

    request = {
        'ref_order': order_1.ref_order,
        'vendor': order_1.vendor,
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        ],
    }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order', json=request,
    )
    assert response.status_code == 409
    assert check_items_quantity.times_called == 1


async def test_internal_create_updated(
        taxi_tristero_parcels, tristero_parcels_db, testpoint, mocked_time,
):
    with tristero_parcels_db as db:
        order_1 = db.add_order(1)

        order_1.add_parcel(1)
        now = datetime.datetime.now(datetime.timezone.utc)

        order_1.set_updated(now)

    @testpoint('order_items')
    def check_items_quantity(data):
        print(data['items'])
        assert len(data['items']) == 1
        assert (
            datetime.datetime.strptime(
                data['updated'], '%Y-%m-%dT%H:%M:%S.%f%z',
            )
            == now
        )

    request = {
        'ref_order': order_1.ref_order,
        'vendor': order_1.vendor,
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        ],
    }

    await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order', json=request,
    )
    assert check_items_quantity.times_called == 1


@pytest.mark.parametrize('error_status', [400, 409])
async def test_internal_create_bad_request(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, error_status,
):
    """ /internal/v1/parcels/order POST return 400 on
    WMS /items/v1/create handler 4xx error """

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        return mockserver.make_response(
            status=error_status,
            json={'code': 'some-error-code', 'message': 'some-error-message'},
        )

    request_data = {
        'ref_order': '123456',
        'vendor': 'beru',
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        ],
    }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 400
    assert _wms_items_create.has_calls is True
    assert response.json() == {'message': 'some-error-message'}


@pytest.mark.parametrize('items_limit', [10, 5, 2, 1])
async def test_internal_create_in_parts_basics(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        taxi_config,
        items_limit,
):
    """Split huge wms creation request in parts, then combine responses"""

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        assert len(request.json['items']) <= items_limit
        response_items = []
        for item in request.json['items']:
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(
                        item['barcode'][0].split('_')[1],
                    ),
                },
            )
        return {'code': 'OK', 'items': response_items}

    taxi_config.set(
        TRISTERO_PARCELS_WMS_CREATE_SETTINGS={'items_limit': items_limit},
    )

    request_data = {
        'ref_order': '123456',
        'vendor': 'beru',
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [],
    }
    items_size = 13
    for i in range(items_size):
        request_data['items'].append(
            {
                'barcode': 'barcode_' + str(i),
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        )

    expected_wms_requests = (items_size - 1) // items_limit + 1

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == items_size
    assert _wms_items_create.times_called == expected_wms_requests


@pytest.mark.parametrize('error_status', [400, 409])
async def test_internal_create_in_parts_fail(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        taxi_config,
        error_status,
):
    """Fail and respond 400 if wms fails anywhere"""

    items_limit = 5

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        return mockserver.make_response(
            status=error_status,
            json={'code': 'some-error-code', 'message': 'some-error-message'},
        )

    taxi_config.set(
        TRISTERO_PARCELS_WMS_CREATE_SETTINGS={'items_limit': items_limit},
    )

    request_data = {
        'ref_order': '123456',
        'vendor': 'beru',
        'uid': 'user_id_1',
        'depot_id': 'depot_id_1',
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [],
    }
    items_size = 13
    for i in range(items_size):
        request_data['items'].append(
            {
                'barcode': 'barcode_' + str(i),
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': 1,
                },
            },
        )

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 400
    assert _wms_items_create.has_calls is True
    assert response.json() == {'message': 'some-error-message'}
