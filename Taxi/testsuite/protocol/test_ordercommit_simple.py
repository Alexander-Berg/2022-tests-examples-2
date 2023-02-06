import pytest

# Some tests for /3.0/ordercommit share tests for /order and
# /internal/ordercommit: some of these tests were parametrized to run
# for both APIs.


@pytest.fixture()
def surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


def test_ordercommit_noorder(taxi_protocol, db):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '11111111111111111111111111111111',
    }
    query = {'_id': request['orderid']}
    assert db.order_proc.find_one(query) is None

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 410


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.parametrize(
    'draft_lifetime_sec,exp_code', [(4, 410), (5, 200), (6, 200)],
)
def test_ordercommit_too_old_draft(
        taxi_protocol,
        config,
        mockserver,
        surge,
        draft_lifetime_sec,
        exp_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    config.set_values(dict(ORDER_DRAFT_ACTIVE_TIME_SEC=draft_lifetime_sec))
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047400',
    }

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == exp_code


def test_ordercommit_match_source_id(taxi_protocol, db):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
    }
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    query = {'_id': request['orderid']}
    order = db.orders.find_one(query)
    order_proc = db.order_proc.find_one(query)
    assert order.get('source') == order_proc.get('order', {}).get('source')


def test_ordercommit_ok(taxi_protocol, db):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
    }
    query = {'_id': request['orderid']}
    assert db.order_proc.find_one(query) is not None

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200
