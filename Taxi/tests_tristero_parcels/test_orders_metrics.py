# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers

from tests_tristero_parcels import headers


async def test_order_creation_metrics(
        taxi_tristero_parcels, taxi_tristero_parcels_monitor, mockserver,
):
    """ When order created metrics value should increase """

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        for item in request.json['items']:
            barcode = item['barcode'][0]
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(barcode.split('_')[1]),
                },
            )
        return {'code': 'OK', 'items': response_items}

    request = {
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

    async with metrics_helpers.MetricsCollector(
            taxi_tristero_parcels_monitor,
            sensor='tristero_parcels_created_orders',
    ) as collector:
        for _ in range(3):
            response = await taxi_tristero_parcels.post(
                '/internal/v1/parcels/order', json=request,
            )
            assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    # order creation retry shouldn`t increment metric
    assert metric.value == 1
    assert metric.labels == {
        'city_name': 'Moscow',
        'country': 'Russia',
        'sensor': 'tristero_parcels_created_orders',
    }


async def test_order_cancellation_metrics(
        taxi_tristero_parcels,
        taxi_tristero_parcels_monitor,
        tristero_parcels_db,
        mockserver,
):
    """ When order canceled metrics value should increase """

    @mockserver.json_handler('/grocery-wms/api/external/items/v1/create')
    def _wms_items_create(request):
        response_items = []
        for item in request.json['items']:
            barcode = item['barcode'][0]
            response_items.append(
                {
                    'external_id': item['external_id'],
                    'item_id': 'wms_id_{}'.format(barcode.split('_')[1]),
                },
            )
        return {'code': 'OK', 'items': response_items}

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

    async with metrics_helpers.MetricsCollector(
            taxi_tristero_parcels_monitor,
            sensor='tristero_parcels_canceled_orders',
    ) as collector:
        response = await taxi_tristero_parcels.post(
            '/internal/v1/parcels/cancel-order',
            headers=headers.DEFAULT_HEADERS,
            json=request_data,
        )
        assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'city_name': 'Moscow',
        'country': 'Russia',
        'sensor': 'tristero_parcels_canceled_orders',
    }
