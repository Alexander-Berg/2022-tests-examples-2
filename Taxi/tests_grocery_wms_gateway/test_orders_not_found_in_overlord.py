async def test_create_404_in_overlord(taxi_grocery_wms_gateway, mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/create')
    def mock_wms(request):
        pass

    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/add',
        json={
            'organization': 'nonexistent_depot_id',
            'customer': {'id': 'customer_id'},
            'order': {
                'id': 'order_id',
                'date': 'date string',
                'fullSum': '123.0',
                'items': [],
            },
        },
    )

    assert response.status_code == 500

    assert mock_wms.times_called == 0


async def test_info_404_in_overlord(taxi_grocery_wms_gateway, mockserver):
    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/orders/info?organization=nonexistent_depot_id&order=order_id',
    )

    assert response.status_code == 500


async def test_delete_404_in_overlord(taxi_grocery_wms_gateway, mockserver):
    await taxi_grocery_wms_gateway.invalidate_caches()

    response = await taxi_grocery_wms_gateway.delete(
        '/v1/order/order_id?organization=nonexistent_depot_id',
    )

    assert response.status_code == 500
