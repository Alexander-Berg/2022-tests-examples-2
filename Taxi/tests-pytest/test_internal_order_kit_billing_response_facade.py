import pytest


from taxi.internal.order_kit import billing_response_facade


@pytest.mark.parametrize('billing_response,expected', [
    (
        {'status_code': 'blacklisted', 'payment_resp_code': 'ignored'},
        'blacklisted',
    ),
    (
        {'payment_resp_code': 'blacklisted'},
        'blacklisted',
    ),
])
@pytest.mark.filldb(_fill=False)
def test_status_code(billing_response, expected):
    facade = billing_response_facade.Facade(billing_response)
    assert facade.status_code == expected


@pytest.mark.parametrize('billing_response,expected', [
    (
        {'status_desc': 'frauder', 'payment_resp_desc': 'ignored'},
        'frauder',
    ),
    (
        {'payment_resp_desc': 'frauder'},
        'frauder',
    ),
])
@pytest.mark.filldb(_fill=False)
def test_status_desc(billing_response, expected):
    facade = billing_response_facade.Facade(billing_response)
    assert facade.status_desc == expected


@pytest.mark.parametrize('billing_response,expected', [
    (
        {'postauth_ts_msec': '1000', 'clear_ts': 'ignored'},
        '1000'
    ),
    (
        {'clear_ts': '1'},
        '1000'
    ),
    (
        {},
        None,
    )
])
@pytest.mark.filldb(_fill=False)
def test_postauth_ts_msec(billing_response, expected):
    facade = billing_response_facade.Facade(billing_response)
    assert facade.postauth_ts_msec == expected
