import pytest


@pytest.mark.parametrize(
    ('cargo_limits_disabled', 'overdraft_enabled', 'expected_status'),
    [
        pytest.param(
            False,
            True,
            406,
            marks=[
                pytest.mark.config(
                    COMMIT_PLUGINS_ENABLED=True,
                    CARGO_ORDERS_PHOENIX_DISABLE_TAXI_LIMITS=False,
                ),
                pytest.mark.experiments3(
                    filename='experiments3_overdraft_enabled.json',
                ),
            ],
            id='overdraft_debt',
        ),
        pytest.param(
            True,
            True,
            200,
            marks=[
                pytest.mark.config(
                    COMMIT_PLUGINS_ENABLED=True,
                    CARGO_ORDERS_PHOENIX_DISABLE_TAXI_LIMITS=True,
                ),
                pytest.mark.experiments3(
                    filename='experiments3_overdraft_cargo.json',
                ),
            ],
            id='overdraft_ignored',
        ),
        pytest.param(
            False,
            False,
            200,
            marks=pytest.mark.config(
                COMMIT_PLUGINS_ENABLED=False,
                CARGO_ORDERS_PHOENIX_DISABLE_TAXI_LIMITS=False,
            ),
            id='orderlocks_not_triggered_for_cargo',
        ),
        pytest.param(
            True,
            False,
            200,
            marks=pytest.mark.config(
                COMMIT_PLUGINS_ENABLED=False,
                CARGO_ORDERS_PHOENIX_DISABLE_TAXI_LIMITS=True,
            ),
            id='orderlocks_ignored',
        ),
    ],
)
def test_disabled_unpaid_check_for_delivery(
        taxi_integration,
        pricing_data_preparer,
        mockserver,
        cargo_limits_disabled,
        overdraft_enabled,
        expected_status,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/debts/v1/overdraft/limit')
    def mock_debts(request):
        return {'remaining_limit': 0, 'currency': 'RUB', 'has_debts': True}

    order_id = '272fbd2b67b0bb9c5135d71d1d1a848b'
    request = {'id': '0c1dd6723153692ec43a5827e3603ac9', 'orderid': order_id}

    resp = taxi_integration.post('v1/orders/commit', request)
    assert resp.status_code == expected_status
    if expected_status == 200:
        assert resp.json()['orderid'] == order_id
        assert resp.json()['status'] == 'search'

    if expected_status == 406:
        assert resp.json() == {'error': {'code': 'DEBT_USER'}}

    if not cargo_limits_disabled and overdraft_enabled:
        assert mock_debts.times_called == 1
    else:
        assert mock_debts.times_called == 0

    # c2c
    order_id = '272fbd2b67b0bb9c5135d71d1d1a848c'
    request = {'id': '0c1dd6723153692ec43a5827e3603ac9', 'orderid': order_id}

    resp = taxi_integration.post('v1/orders/commit', request)
    assert resp.status_code == 406 if overdraft_enabled else 200
