# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest


@pytest.fixture
def mock_eats_orderhistory_error(mockserver):
    @mockserver.json_handler(
        '/eats-orderhistory-py3/internal-api/v1/orders/retrieve',
    )
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_fallbacks(mock_statistics, web_app):
    async def _impl(fallbacks):
        @mock_statistics('/v1/service/health')
        def _health_handler(request):
            assert request.args['service']

            return {'fallbacks': fallbacks}

        await web_app['context'].refresh_caches()

    return _impl


@pytest.fixture(autouse=True)
def mock_shuttle_control(mockserver):
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/list',
    )
    async def handler_shuttle_control(request):
        return {'orders': []}

    return handler_shuttle_control


@pytest.fixture
def mock_all_services(
        load_json,
        mockserver,
        mock_cargo_c2c,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        mock_grocery_order_log,
        mock_yandex_drive,
        mock_iiko_integration,
):
    def _impl(error_services):
        @mock_cargo_c2c('/orderhistory/v1/list')
        async def handler_cargo_c2c(request):
            if 'cargo_c2c' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            return load_json('cargo_c2c_resp.json')

        @mock_ridehistory('/v2/list')
        async def handler_taxi(request):
            if 'ridehistory' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            return load_json('ridehistory_resp_one.json')

        @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
        async def handler_eats(request):
            if 'eats' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            resp = load_json('eats_oh_resp_simple.json')
            resp['orders'] = [
                order
                for order in resp['orders']
                if order['service'] in request.json['services']
            ]

            return resp

        @mock_grocery_order_log('/internal/orders/v1/retrieve')
        async def handler_grocery(request):
            if 'standalone_grocery' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            return load_json('grocery_oh_resp_simple.json')

        @mock_yandex_drive('/sessions/list')
        async def handler_drive(request):
            if 'drive' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            return load_json('drive_list_basic.json')

        @mock_iiko_integration('/iiko-integration/v1/orderhistory/list')
        async def handler_qr(request):
            if 'qr_pay' in error_services:
                return mockserver.make_response(
                    status=500, json={'code': '500', 'message': '500'},
                )

            return load_json('qr_orderhistory_resp.json')

        return {
            'cargo_c2c': handler_cargo_c2c,
            'ridehistory': handler_taxi,
            'eats': handler_eats,
            'standalone_grocery': handler_grocery,
            'drive': handler_drive,
            'qr_pay': handler_qr,
        }

    return _impl
