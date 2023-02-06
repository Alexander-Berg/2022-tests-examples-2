import pytest

from tests_tristero_parcels import headers


LEGAL_ENTITY_VENDOR_CFG = 'ООО Яндекс.Беру -- тест'
LEGAL_ENTITY_CARGO_CARRIER_CFG = 'ООО Яндекс.Такси - тест'


async def test_internal_update_404(taxi_tristero_parcels):
    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': '00000000-89ab-cdef-000a-000000002020', 'items': []},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('uid', [headers.USER_ID, None])
@pytest.mark.parametrize('partner_id', ['some_partner_id', None])
@pytest.mark.config(
    TRISTERO_LEGAL_ENTITIES_VENDOR={'__default__': LEGAL_ENTITY_VENDOR_CFG},
    TRISTERO_LEGAL_ENTITY_CARGO_CARRIER=LEGAL_ENTITY_CARGO_CARRIER_CFG,
)
async def test_internal_update_200(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        uid,
        partner_id,
):
    vendor = 'beru'
    token = 'some-token'
    customer_meta = {'key': 'value'}
    price = '1234'

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1,
        user_id=uid,
        depot_id=depot_id,
        vendor=vendor,
        token=token,
        price=53.5123,
    )
    order.add_parcel(1, status='reserved')
    parcel_1 = order.add_parcel(2, status='in_depot')
    measurements = {'width': 1, 'height': 2, 'length': 3, 'weight': 4}

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        assert request.json['items'][0]['source'] == vendor
        assert request.json['items'][1]['source'] == vendor + (
            ('-' + partner_id) if partner_id is not None else ''
        )

        for item in request.json['items']:
            assert item['title'] == '{} Посылка {}/{}'.format(
                vendor, order.ref_order, item['barcode'][0],
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
                    'item_id': 'wms_id_{}'.format(barcode),
                },
            )
        return {'code': 'OK', 'items': response_items}

    request_data = {
        'order_id': order.order_id,
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': parcel_1.barcode,
                'measurements': measurements,
                'description': 'description 1',
            },
            {'barcode': '1222222333333', 'measurements': measurements},
        ],
        'customer_meta': customer_meta,
        'price': price,
    }
    if partner_id:
        request_data['items'][1]['partner_id'] = partner_id

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['ref_order'] == order.ref_order
    assert response_json['uid'] == order.uid
    assert response_json['order_id'] == order.order_id
    assert response_json['depot_id'] == order.depot_id
    assert response_json['state'] == order.status
    assert response_json['customer_meta'] == customer_meta
    assert float(response_json['price']) == float(price)

    response_items = response_json['items']

    items_db = tristero_parcels_db.fetch_from_sql(
        'SELECT id, vendor, barcode, wms_id, '
        'description, status FROM parcels.items '
        'WHERE order_id = \'{}\''.format(order.order_id),
    )
    assert len(items_db) == 2
    response_items = {
        i['barcode']: {'barcode': i['barcode']} for i in response_items
    }

    req_items = {
        i['barcode']: {'description': i.get('description', None)}
        for i in request_data['items']
    }
    for i in items_db:
        assert i[2] in response_items
        assert req_items[i[2]]['description'] == i[4]

    parcel_1.update_from_db()
    assert parcel_1.status == 'in_depot'


@pytest.mark.parametrize('partner_id', ['some_partner_id', None])
@pytest.mark.config(
    TRISTERO_LEGAL_ENTITIES_VENDOR={'__default__': LEGAL_ENTITY_VENDOR_CFG},
    TRISTERO_LEGAL_ENTITY_CARGO_CARRIER=LEGAL_ENTITY_CARGO_CARRIER_CFG,
)
# TODO: спилить в https://st.yandex-team.ru/LAVKABACKEND-5933
async def test_same_barcode_hotfix(
        taxi_tristero_parcels,
        tristero_parcels_db,
        mockserver,
        pgsql,
        partner_id,
):
    vendor = 'beru'
    token = 'some-token'
    customer_meta = {'key': 'value'}

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1, depot_id=depot_id, vendor=vendor, token=token,
    )
    order2 = tristero_parcels_db.add_order(2, depot_id=depot_id, vendor=vendor)
    parcel_1 = order.add_parcel(2, status='reserved')

    measurements = {'width': 1, 'height': 2, 'length': 3, 'weight': 4}

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        for item in request.json['items']:
            assert any(
                item['title']
                == '{} Посылка {}/{}'.format(
                    vendor, order.ref_order, item['barcode'][0],
                )
                for order in [order, order2]
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
                    'item_id': 'wms_id_{}'.format(barcode),
                },
            )
        return {'code': 'OK', 'items': response_items}

    request_data = {
        'order_id': order2.order_id,
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [{'barcode': '1222222333333', 'measurements': measurements}],
        'customer_meta': customer_meta,
    }

    request_data2 = {
        'order_id': order2.order_id,
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': parcel_1.barcode,
                'measurements': measurements,
                'description': 'description 1',
            },
        ],
        'customer_meta': customer_meta,
    }

    if partner_id:
        request_data2['items'][0]['partner_id'] = partner_id

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 200
    before_request = tristero_parcels_db.fetch_from_sql(
        f""" select * from parcels.items where order_id = '{order2.order_id}'
        """,
    )

    response2 = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data2,
    )
    assert response2.status_code == 200

    after_request = tristero_parcels_db.fetch_from_sql(
        f""" select * from parcels.items where order_id = '{order2.order_id}'
        """,
    )
    assert response.json()['items'][0]['barcode'] == '1222222333333'
    if partner_id is None:
        assert before_request == after_request
    else:
        assert before_request != after_request
        assert (
            tristero_parcels_db.fetch_from_sql(
                f"""select count(*) from parcels.items where barcode =
                '{parcel_1.barcode}'""",
            )[0][0]
            == 2
        )


@pytest.mark.parametrize('error_status', [400, 409, 500])
async def test_internal_update_proxies_wms_error(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, error_status,
):
    """ /internal/v1/parcels/order should proxy error
    from WMS /items/v1/create handler """
    vendor = 'beru'
    token = 'some-token'

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1,
        user_id=headers.USER_ID,
        depot_id=depot_id,
        vendor=vendor,
        token=token,
    )
    order.add_parcel(1, status='reserved')

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        return mockserver.make_response(
            status=error_status,
            json={'code': 'some-error-code', 'message': 'some-error-message'},
        )

    request_data = {
        'order_id': order.order_id,
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': '1222222333333',
                'measurements': {
                    'width': 1,
                    'height': 2,
                    'length': 3,
                    'weight': 4,
                },
            },
        ],
    }

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == error_status
    assert _wms_items_create.has_calls is True
    response_json = response.json()
    if error_status != 500:
        assert response_json == {'message': 'some-error-message'}


async def test_internal_update_conflict(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    """ /internal/v1/parcels/order PUT should response 409
    if parcel is already recieved """
    vendor = 'beru'
    token = 'some-token'

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1,
        user_id=headers.USER_ID,
        depot_id=depot_id,
        vendor=vendor,
        token=token,
    )
    order.add_parcel(1, status='in_depot')

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        return mockserver.make_response(status=500, json={})

    request_data = {
        'order_id': order.order_id,
        'delivery_date': '2020-10-05T16:28:00.000Z',
        'items': [
            {
                'barcode': '1222222333333',
                'measurements': {
                    'width': 1,
                    'height': 2,
                    'length': 3,
                    'weight': 4,
                },
            },
        ],
    }

    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 409
    assert _wms_items_create.has_calls is False
