# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest

from tests_grocery_pro_bdu import models


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


@pytest.fixture(name='my_waybill_assemble', autouse=True)
def _my_waybill_assemble(load_json_var, default_order_id):
    waybill = load_json_var(
        'v1_waybill_info_batch_tpl.json', order_id=default_order_id,
    )
    waybill['execution']['points'][0]['is_resolved'] = False
    waybill['execution']['points'][1]['is_resolved'] = False
    return waybill


@pytest.fixture(name='my_waybill_pickup', autouse=True)
def _my_waybill_pickup(load_json_var, default_order_id):
    waybill = load_json_var(
        'v1_waybill_info_batch_tpl.json', order_id=default_order_id,
    )
    waybill['execution']['points'][0]['is_resolved'] = False
    waybill['execution']['points'][1]['is_resolved'] = False
    waybill['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T14:00:00+00:00'
    return waybill


@pytest.fixture(name='my_waybill_return', autouse=True)
def _my_waybill_return(load_json, default_order_id):
    waybill = load_json('v1_waybill_info_nobatch.json')
    waybill['execution']['points'][0]['is_resolved'] = True
    waybill['execution']['points'][1]['is_resolved'] = True
    return waybill


@pytest.fixture(name='my_waybill_going_to_client', autouse=True)
def _my_waybill_going_to_client(load_json, default_order_id):
    waybill = load_json('v1_waybill_info_nobatch.json')
    waybill['execution']['points'][0]['is_resolved'] = True
    return waybill


@pytest.fixture(name='my_waybill_at_client', autouse=True)
def _my_waybill_at_client(load_json, default_order_id):
    waybill = load_json('v1_waybill_info_nobatch.json')
    waybill['execution']['points'][0]['is_resolved'] = True
    waybill['execution']['points'][1]['visit_status'] = 'arrived'
    return waybill


@pytest.fixture(name='my_waybill_order_cancelled', autouse=True)
def _my_waybill_order_cancelled(load_json, default_order_id):
    waybill = load_json('order_cancelled_waybill.json')
    return waybill


@pytest.fixture(name='cargo')
def mock_cargo(mockserver, load_json_var, default_order_id):
    class Context:
        def __init__(self):
            self.claim_id = 'claim_1'

    context = Context()

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(request):
        waybill = load_json_var(
            'v1_waybill_info_batch_tpl.json', order_id=default_order_id,
        )
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': waybill,
        }

    return context
