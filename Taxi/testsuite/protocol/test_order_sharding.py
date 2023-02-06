import pytest

from . import test_order


@pytest.fixture(autouse=True)
def default_mock(mockserver, load_json):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return test_order.get_surge_mock_response()

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(req):
        return mockserver.make_response('', 200)


def test_sharding_default(
        taxi_protocol, load_json, default_mock, db, pricing_data_preparer,
):
    response_body = test_order.make_order(
        taxi_protocol, load_json('basic_request.json'),
    )
    order_id = response_body['orderid']

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['_shard_id'] == 0


@pytest.mark.config(ORDER_SHARDS_ENABLED=True, ORDER_SHARDS=[55])
def test_sharding(
        taxi_protocol, load_json, default_mock, db, pricing_data_preparer,
):
    response_body = test_order.make_order(
        taxi_protocol, load_json('basic_request.json'),
    )
    order_id = response_body['orderid']

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['_shard_id'] == 55
