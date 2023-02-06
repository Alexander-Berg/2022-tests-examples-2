import pytest

from tests_grocery_wms_gateway import consts


@pytest.mark.parametrize('payment_type', ['refund', 'payment'])
async def test_basic(
        taxi_grocery_wms_gateway, mockserver, payment_type, grocery_depots,
):
    order_id = 'external_order_id'
    date = '2020-02-17T08:46:35+00:00'
    invoice_id = 'invoice-id'
    total_wms = '10.10'
    total = '10.1'

    grocery_depots.add_depot(
        depot_test_id=1,
        legacy_depot_id=consts.DEFAULT_DEPOT_ID,
        depot_id=consts.DEFAULT_WMS_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/update-data')
    def mock_wms(request):
        assert request.json == {
            'external_id': order_id,
            'invoices': [
                {
                    'invoice_date': date,
                    'invoice_number': invoice_id,
                    'invoice_sum': total_wms,
                    'invoice_type': payment_type,
                },
            ],
            'store_id': consts.DEFAULT_WMS_DEPOT_ID,
        }

        return {
            'order': {
                'order_id': 'wms-order-id',
                'external_id': order_id,
                'status': 'reserving',
                'store_id': 'wms_depot_id',
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/invoice',
        json={
            'depot_id': consts.DEFAULT_DEPOT_ID,
            'order_id': order_id,
            'invoices': [
                {
                    'id': invoice_id,
                    'type': payment_type,
                    'total': total,
                    'date': date,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert mock_wms.times_called == 1


@pytest.mark.parametrize(
    'total,total_wms',
    [
        ('10', '10.00'),
        ('10.1', '10.10'),
        ('10.12', '10.12'),
        ('10.123', '10.12'),
        ('0.99', '0.99'),
        ('0.825', '0.83'),
    ],
)
async def test_total(
        taxi_grocery_wms_gateway, mockserver, total, total_wms, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/update-data')
    def mock_wms(request):
        assert request.json['invoices'][0]['invoice_sum'] == total_wms

        return {
            'order': {
                'order_id': 'wms-order-id',
                'external_id': 'order_id',
                'status': 'reserving',
                'store_id': 'wms_depot_id',
            },
        }

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/invoice',
        json={
            'depot_id': consts.DEFAULT_DEPOT_ID,
            'order_id': 'order_id',
            'invoices': [
                {
                    'id': 'invoice_id',
                    'type': 'payment',
                    'total': total,
                    'date': '2020-02-17T08:46:35+00:00',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert mock_wms.times_called == 1


@pytest.mark.parametrize('code', [400, 404, 409, 410])
async def test_error(
        taxi_grocery_wms_gateway, mockserver, code, grocery_depots,
):
    grocery_depots.add_depot(
        depot_test_id=1, legacy_depot_id=consts.DEFAULT_DEPOT_ID,
    )

    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/update-data')
    def mock_wms(request):
        return mockserver.make_response('{}', code)

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/invoice',
        json={
            'depot_id': consts.DEFAULT_DEPOT_ID,
            'order_id': 'order_id',
            'invoices': [
                {
                    'id': 'invoice-id',
                    'type': 'payment',
                    'total': '10.1',
                    'date': '2020-02-17T08:46:35+00:00',
                },
            ],
        },
    )

    assert response.status_code == 500
    assert mock_wms.times_called == 1
