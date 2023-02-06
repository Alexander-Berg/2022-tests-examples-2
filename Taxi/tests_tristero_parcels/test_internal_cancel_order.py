import pytest

from tests_tristero_parcels import headers


LEGAL_ENTITY_VENDOR_CFG = 'ООО Яндекс.Беру -- тест'
LEGAL_ENTITY_CARGO_CARRIER_CFG = 'ООО Яндекс.Такси - тест'


@pytest.mark.config(
    TRISTERO_LEGAL_ENTITIES_VENDOR={'__default__': LEGAL_ENTITY_VENDOR_CFG},
    TRISTERO_LEGAL_ENTITY_CARGO_CARRIER=LEGAL_ENTITY_CARGO_CARRIER_CFG,
)
@pytest.mark.parametrize(
    'initial_status,result_status,call_wms,result_code',
    [
        ('created', 'cancelled', True, 200),
        ('reserved', 'cancelled', True, 200),
        ('expecting_delivery', 'cancelled', True, 200),
        ('received_partialy', 'cancelled', True, 200),
        ('received', 'cancelled', True, 200),
        ('delivered_partially', 'delivered_partially', False, 409),
        ('delivered', 'delivered', False, 409),
        ('cancelled', 'cancelled', True, 404),
    ],
)
async def test_internal_cancel_order(
        taxi_tristero_parcels,
        mockserver,
        tristero_parcels_db,
        initial_status,
        result_status,
        call_wms,
        result_code,
):
    request_data = {
        'order_id': '00000000-89ab-cdef-000a-000000002020',
        'reason': 'because I can',
        'ref-doc': 'refdoc1',
        'doc-date': '2020-10-05T16:28:00.000Z',
    }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/cancel-order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == 404

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1, user_id=headers.USER_ID, depot_id=depot_id, status=initial_status,
    )
    order.add_parcel(2, status='in_depot')
    order.add_parcel(3, status='in_depot')

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_doc_create(request):
        response_items = []
        for item in request.json['items']:
            barcode = item['barcode'][0]
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(barcode),
                },
            )
            data = item['data']
            assert data['expiry_date'] == data['delivery']
            assert data['contractor'] == LEGAL_ENTITY_VENDOR_CFG
            assert data['cargo_carrier'] == LEGAL_ENTITY_CARGO_CARRIER_CFG
        if result_code != 200:
            return mockserver.make_response(json={}, status=result_code)
        return {'code': 'OK', 'items': response_items}

    request_data['order_id'] = order.order_id
    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/cancel-order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == result_code

    if result_code in {200, 404}:
        response = await taxi_tristero_parcels.post(
            '/internal/v1/parcels/cancel-order',
            headers=headers.DEFAULT_HEADERS,
            json=request_data,
        )
        assert response.status_code == 404

    data_at_db = tristero_parcels_db.fetch_from_sql(
        'SELECT status, service_notes FROM parcels.orders '
        'WHERE id=\'{}\''.format(order.order_id),
    )
    assert data_at_db[0][0] == result_status
    if result_code == 200:
        assert data_at_db[0][1] == request_data['reason']


@pytest.mark.parametrize('error_status', [400, 409, 500])
async def test_internal_cancel_order_bad_request(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, error_status,
):
    """ /internal/v1/parcels/cancel-order should proxy error
    from WMS /items/v1/create handler """

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        return mockserver.make_response(
            status=error_status,
            json={'code': 'some-error-code', 'message': 'some-error-message'},
        )

    depot_id = tristero_parcels_db.make_depot_id(1)
    order = tristero_parcels_db.add_order(
        1, user_id=headers.USER_ID, depot_id=depot_id, status='reserved',
    )
    order.add_parcel(2, status='in_depot')

    request_data = {
        'order_id': order.order_id,
        'reason': 'because I can',
        'ref-doc': 'refdoc1',
        'doc-date': '2020-10-05T16:28:00.000Z',
    }

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/cancel-order',
        headers=headers.DEFAULT_HEADERS,
        json=request_data,
    )
    assert response.status_code == error_status
    assert _wms_items_create.has_calls is True
    response_json = response.json()
    if error_status != 500:
        assert response_json == {'message': 'some-error-message'}
