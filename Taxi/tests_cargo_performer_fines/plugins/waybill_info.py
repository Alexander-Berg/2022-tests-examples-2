import pytest


@pytest.fixture(name='waybill_info_request_property')
def _waybill_info_request_property(load_json):
    def handler(path='cargo-dispatch/waybill_info_default.json'):
        return load_json(path)

    return handler


@pytest.fixture(name='mock_waybill_info')
def _mock_driver_tags(mockserver, default_cargo_order_id, load_json):
    def handler(
            path='cargo-dispatch/waybill_info_default.json',
            cargo_order_id=default_cargo_order_id,
    ):
        @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
        def _mock(request):
            assert request.query['cargo_order_id'] == cargo_order_id
            return load_json(path)

    return handler
