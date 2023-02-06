import json

import pytest


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


def make_response(mockserver, response, status=200):
    if isinstance(response, dict):
        response = json.dumps(response)
    return mockserver.make_response(response, status)


@pytest.fixture
def mock_debts(mockserver):
    default_limit = {
        'remaining_limit': 50,
        'currency': 'RUB',
        'has_debts': False,
    }

    class Context:
        limit_raw = [default_limit, 200]

        def set_limit_raw(self, resp, status=200):
            self.limit_raw = [resp, status]

    context = Context()

    @mockserver.handler('/debts/v1/overdraft/limit')
    def mock_limit(request):
        return make_response(
            mockserver, context.limit_raw[0], context.limit_raw[1],
        )

    return context


@pytest.fixture
def mock_statistics(mockserver):
    class Context:
        health_raw = [{'fallbacks': []}, 200]
        store_raw = [{}, 200]

        def set_health_raw(self, resp, status=200):
            self.health_raw = [resp, status]

        def set_store_raw(self, resp, status=200):
            self.store_raw = [resp, status]

        def set_health(self, fallbacks):
            self.health_raw[0]['fallbacks'] = fallbacks

    context = Context()

    @mockserver.handler('/statistics/v1/service/health')
    def mock_health(request):
        return make_response(
            mockserver, context.health_raw[0], context.health_raw[1],
        )

    @mockserver.handler('/statistics/v1/metrics/store')
    def mock_store(request):
        return make_response(
            mockserver, context.store_raw[0], context.store_raw[1],
        )

    return context


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
@pytest.mark.parametrize(
    'code, response, expected_code',
    [
        (200, '', 200),
        (200, {}, 200),
        (
            200,
            {'remaining_limit': 50, 'currency': 'RUB', 'has_debts': False},
            200,
        ),
        (400, '', 500),
        (500, {}, 500),
    ],
)
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
def test_commit_overdraft_servererror(
        taxi_protocol,
        db,
        surge,
        mock_debts,
        code,
        response,
        expected_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    mock_debts.set_limit_raw(response, status=code)

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': 'order_id_1',
    }
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == expected_code


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
@pytest.mark.parametrize(
    'content,accepted,expected_code',
    [
        (
            {'remaining_limit': 50, 'currency': 'RUB', 'has_debts': False},
            [],
            200,
        ),
        (
            {'remaining_limit': 0, 'currency': 'RUB', 'has_debts': False},
            [],
            200,
        ),
        (
            {'remaining_limit': 50, 'currency': 'RUB', 'has_debts': True},
            ['overdraft'],
            200,
        ),
        (
            {'remaining_limit': 50, 'currency': 'RUB', 'has_debts': True},
            [],
            406,
        ),
        (
            {'remaining_limit': 0, 'currency': 'RUB', 'has_debts': True},
            ['overdraft'],
            406,
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
def test_commit_overdraft_ok(
        taxi_protocol,
        mock_debts,
        db,
        surge,
        content,
        accepted,
        expected_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'order_id_1'
    mock_debts.set_limit_raw(content)

    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.request.accepted': accepted}},
    )
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == expected_code


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True, DEBTS_AUTOFALLBACK_ENABLED=True,
)
@pytest.mark.parametrize(
    'code,response,expected_code',
    [
        (400, '', 200),
        (500, '', 200),
        (200, '', 200),
        (200, {}, 200),
        (200, {'fallbacks': {}}, 200),
        (200, {'fallbacks': []}, 200),
    ],
)
def test_overdraft_statistics_fail(
        taxi_protocol,
        mock_debts,
        mock_statistics,
        surge,
        code,
        response,
        expected_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'order_id_1'
    mock_statistics.set_health_raw(response, status=code)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == expected_code


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True, DEBTS_AUTOFALLBACK_ENABLED=True,
)
@pytest.mark.parametrize(
    'fallback,code', [('ordercommit.overdraft', 200), ('some_fallback', 500)],
)
def test_overdraft_statistics_autofallback(
        taxi_protocol,
        mock_debts,
        mock_statistics,
        surge,
        fallback,
        code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'order_id_1'
    mock_statistics.set_health([fallback])
    mock_debts.set_limit_raw('', status=500)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == code


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True, DEBTS_AUTOFALLBACK_ENABLED=False,
)
def test_overdraft_statistics_config(
        taxi_protocol, mock_debts, mock_statistics, surge,
):
    order_id = 'order_id_1'
    mock_statistics.set_health_raw('', 500)
    mock_debts.set_limit_raw('', status=500)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 500


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True, DEBTS_AUTOFALLBACK_ENABLED=True,
)
def test_overdraft_statistics_store_fail(
        taxi_protocol,
        mock_debts,
        mock_statistics,
        surge,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'order_id_1'
    mock_statistics.set_health_raw('', 500)
    mock_statistics.set_store_raw('', 500)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200


@pytest.mark.now('2018-08-10T03:00:05+0300')
@pytest.mark.experiments3(filename='experiments3_overdraft.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    DEBTS_AUTOFALLBACK_ENABLED=True,
    STATISTICS_ENABLE_SEND=False,
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'service': 'ordercommit',
            'enabled': True,
            'fallbacks': ['ordercommit.overdraft'],
        },
    ],
)
def test_overdraft_statistics_store_override(
        taxi_protocol,
        mock_debts,
        mock_statistics,
        surge,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'order_id_1'
    mock_statistics.set_health_raw('', 500)
    mock_statistics.set_store_raw('', 500)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200
