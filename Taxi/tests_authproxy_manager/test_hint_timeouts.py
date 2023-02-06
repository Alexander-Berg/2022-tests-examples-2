import pytest

URL = '/v1/hints/timeout-attempts'


BIG_TIMEOUT_MSG = {
    'text': (
        'Big timeouts (more than 1 second) might negatively affect UX. A user '
        'might go angry if UI starts to respond in seconds. Try to break up '
        'the big handler into several small handlers and to make some ot them '
        'asynchronous. Probably the work can be migrated to the client and '
        'made locally at the client side. Or the client may implement a local '
        'fallback in case the handler fails to respond in 1 second.'
    ),
}

MANY_ATTEMPTS_MSG = {
    'text': (
        'You should not use too many attempts (more than 3), it is too risky '
        'even with the automatic retries fallback. If the upstream timeouts '
        'from time to time even with 3 attempts, try to implement a '
        'client-side fallback in case the upstream is unavailable.'
    ),
}

SMALL_TIMEOUT_MSG = {
    'text': (
        'You\'ve set too small timeout (less than 50ms). '
        'Confused timeout with attempts?'
    ),
}

SO_MANY_ATTEMPTS_MSG = {
    'text': (
        'You\'ve set too many attempts (more than 10). Confused timeout with '
        'attempts?'
    ),
}


@pytest.mark.parametrize(
    'timeout,attempts,warnings',
    [
        (100, 1, []),
        (1, 1, [SMALL_TIMEOUT_MSG]),
        (200, 3, []),
        (1000, 1, []),
        (1001, 1, [BIG_TIMEOUT_MSG]),
        (10001, 3, [BIG_TIMEOUT_MSG]),
        (1000001, 3, [BIG_TIMEOUT_MSG]),
        (100, 3, []),
        (100, 4, [MANY_ATTEMPTS_MSG]),
        (100, 1000, [SO_MANY_ATTEMPTS_MSG]),
        (10000, 5, [BIG_TIMEOUT_MSG, MANY_ATTEMPTS_MSG]),
        (2, 200, [SMALL_TIMEOUT_MSG, SO_MANY_ATTEMPTS_MSG]),
    ],
)
async def test_ok(taxi_authproxy_manager, timeout, attempts, warnings):
    response = await taxi_authproxy_manager.post(
        URL, json={'timeout_ms': timeout, 'attempts': attempts},
    )
    assert response.status == 200
    assert response.json() == {'warnings': warnings}
