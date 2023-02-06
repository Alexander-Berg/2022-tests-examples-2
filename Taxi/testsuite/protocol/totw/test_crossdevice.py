import pytest


ORDER_ID = '8c83b49edb274ce0992f337061047375'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
CROSSDEVICE_USER_ID = 'deadbeefdeadbeefdeadbeef00000075'


# In theory, every test in totw/ folder should be duplicated for Alice
# In practice, it would create too much noise at the moment.
# If alice-crossdevice succeedes, more tests should be written to
# enforce crossdevice
@pytest.mark.filldb(users='crossdevice')
def test_ordinary(taxi_protocol, mockserver):
    o_resp = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': USER_ID,
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    cd_resp = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': CROSSDEVICE_USER_ID,
            'orderid': ORDER_ID,
        },
    )
    assert o_resp.status_code == cd_resp.status_code
    o_json = o_resp.json()
    cd_json = cd_resp.json()
    assert o_json == cd_json
    assert cd_json['can_make_more_orders'] == 'not_modified'


@pytest.mark.filldb(users='crossdevice')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=1,
    MAX_UNFINISHED_ORDERS=1,  # aka max orders per phone id
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
)
@pytest.mark.parametrize('crossdevice_enabled', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_cancel(
        db,
        taxi_protocol,
        mockserver,
        tracker,
        now,
        crossdevice_enabled,
        config,
):
    config.set_values(dict(CROSSDEVICE_ENABLED=crossdevice_enabled))
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )
    request = {'break': 'user', 'id': CROSSDEVICE_USER_ID, 'orderid': ORDER_ID}
    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200, response.text
    content = response.json()
    if not crossdevice_enabled:
        assert content['status'] == 'waiting', content
        assert content['can_make_more_orders'] == 'not_modified'
        return
    assert content['status'] == 'cancelled', content
    assert content['can_make_more_orders'] == 'allowed'
