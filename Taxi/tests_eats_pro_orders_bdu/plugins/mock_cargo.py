# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest

from tests_eats_pro_orders_bdu import models


@pytest.fixture(name='load_json_var')
def _load_json_var(load_json):
    def load_json_var(path, **variables):
        def var_hook(obj):
            varname = obj['$var']
            return variables[varname]

        return load_json(path, object_hook={'$var': var_hook})

    return load_json_var


@pytest.fixture(name='default_order_id')
def _default_order_id():
    return '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'


@pytest.fixture(name='order_id_without_performer')
def _order_id_without_performer():
    return '7771622e-4091-582d-b6fc-4cb2ffdc12c0'


@pytest.fixture(name='cargo')
def mock_cargo(request, mockserver, load_json_var, default_order_id):
    class Context:
        def __init__(self):

            self.batch = False
            self.performer_info = models.TEST_SIMPLE_JSON_PERFORMER_RESULT

            if request is not None and hasattr(request, 'param'):
                if 'batch' in request.param:
                    self.batch = request.param['batch']

                if 'is_deaf_performer' in request.param:
                    self.performer_info = {
                        **models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
                        'is_deaf': request.param['is_deaf_performer'],
                    }

            if self.batch is True:
                self.waybill = load_json_var(
                    'v1_waybill_info_batch_tpl.json',
                    order_id=default_order_id,
                )
            else:
                self.waybill = load_json_var(
                    'v1_waybill_info_nobatch.json', order_id=default_order_id,
                )

    context = Context()

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(request):

        return {
            'performer': context.performer_info,
            'waybill': context.waybill,
        }

    return context


@pytest.fixture(name='cargo_orders', autouse=True)
def cargo_orders(mockserver, request):
    def fixture(url, req_json, default_order_id, cargo_status, cargo):
        @mockserver.json_handler(url)
        def _mock_order_info(request):
            assert request.json == req_json
            if cargo_status == 200:
                return {
                    'performer': cargo.performer_info,
                    'waybill': cargo.waybill,
                }
            return mockserver.make_response(
                status=cargo_status,
                json={
                    'code': 'state_mismatch',
                    'message': 'confirmation conflict',
                },
            )

    return fixture
