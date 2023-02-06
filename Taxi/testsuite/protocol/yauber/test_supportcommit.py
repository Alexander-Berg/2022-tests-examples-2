import pytest


@pytest.mark.parametrize('orderid', ['testorderid1', 'testorderid2'])
@pytest.mark.now('2017-03-13T12:00:00+0300')
def test_supportcommit(
        taxi_protocol, mockserver, db, orderid, load, pricing_data_preparer,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '4000000000'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:yauber_request'},
            'phones': [{'attributes': {'102': '+70001112233'}, 'id': '1111'}],
        }

    @mockserver.json_handler('/coupons/v1/couponreserve')
    def mock_couponcheck(request):
        return {
            'exists': True,
            'valid': True,
            'valid_any': True,
            'value': 500,
            'series': 'test',
        }

    @mockserver.handler('/greed-ts1f.yandex.ru:8018/simple/xmlrpc')
    def mock_billing(request):
        data = load('lpm.xml')
        return mockserver.make_response(data, content_type='text/xml')

    request = {'orderid': orderid, 'check_unfinished_commit': True}
    # NOTE: intentionally calling taxi_protocol
    response = taxi_protocol.post('/internal/ordercommit', json=request)
    assert response.status_code == 200

    proc = db.order_proc.find_one({'_id': orderid})
    assert proc is not None
    assert proc['commit_state'] == 'done'
    order = proc['order']
    if 'coupon' in order:
        assert order['coupon']['valid']
        assert order['coupon']['value'] == 500
