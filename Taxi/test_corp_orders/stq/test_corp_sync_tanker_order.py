from corp_orders.stq import corp_sync_tanker_order


async def test_corp_sync_tanker_order(
        web_app_client, stq3_context, mockserver, load_json,
):
    @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
    async def _topics_compact(request):
        return load_json('topics_compact.json')

    @mockserver.json_handler('/tanker/order/status/b2b-go')
    async def _get_order(request):
        return {
            'status': 'Completed',
            'DateCreate': '2022-01-13T09:44:57.9640000Z',
            'DateEnd': '2022-01-13T09:45:50.1020000Z',
            'stationName': 'Тестировочная №1',
            'stationAddress': 'Кремлевская наб. 1',
            'stationLocation': {
                'lon': 37.6224932711628,
                'lat': 55.7531181890418,
            },
            'columnNumber': 3,
            'fuelId': 'a100_premium',
            'fuelName': 'АИ-100 Ultimate',
            'litersRequested': 14.11,
            'litersCompleted': 24.04,
            'fuelPrice': 60.23,
            'totalDiscount': 21.64,
            'orderCost': 849.85,
            'finalCost': 1426.29,
            'logVolumes': [
                {'date': '2022-01-13T09:45:11.629Z'},
                {'date': '2022-01-13T09:45:13.657Z'},
                {'date': '2022-01-13T09:45:15.681Z', 'value': 1.34},
                {'date': '2022-01-13T09:45:17.705Z', 'value': 2.67},
                {'date': '2022-01-13T09:45:19.734Z', 'value': 4.01},
                {'date': '2022-01-13T09:45:21.759Z', 'value': 5.35},
                {'date': '2022-01-13T09:45:23.784Z', 'value': 6.68},
                {'date': '2022-01-13T09:45:25.808Z', 'value': 8.02},
                {'date': '2022-01-13T09:45:27.832Z', 'value': 9.36},
                {'date': '2022-01-13T09:45:29.856Z', 'value': 10.69},
                {'date': '2022-01-13T09:45:31.878Z', 'value': 12.03},
                {'date': '2022-01-13T09:45:33.902Z', 'value': 13.36},
                {'date': '2022-01-13T09:45:35.926Z', 'value': 14.7},
                {'date': '2022-01-13T09:45:37.95Z', 'value': 16.03},
                {'date': '2022-01-13T09:45:39.977Z', 'value': 17.37},
                {'date': '2022-01-13T09:45:42.001Z', 'value': 18.71},
                {'date': '2022-01-13T09:45:44.027Z', 'value': 20.04},
                {'date': '2022-01-13T09:45:46.052Z', 'value': 21.38},
                {'date': '2022-01-13T09:45:48.08Z', 'value': 22.72},
            ],
        }

    @mockserver.json_handler('/taxi-corp-integration/v1/departments/by_user')
    async def _corp_int_api_department_by_user(request):
        return {'departments': [{'_id': 'department_id_2'}]}

    await corp_sync_tanker_order.task(stq3_context, order_id='order_id_1')

    expected = load_json('expected_tanker_order.json')

    response = await web_app_client.get(
        '/v1/orders/tanker/find', params={'client_id': 'client_id_2'},
    )
    response_json = await response.json()
    assert response_json['orders'][0] == expected
