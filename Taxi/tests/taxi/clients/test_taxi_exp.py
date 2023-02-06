# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import functools

import aiohttp
import pytest

from taxi.clients import taxi_exp


@pytest.fixture
def taxi_exp_client(test_taxi_app):
    return taxi_exp.TaxiExpClient(
        test_taxi_app.session,
        test_taxi_app.config,
        'test_service',
        test_taxi_app.tvm,
    )


def mark_default_config(func):
    @functools.wraps(func)
    @pytest.mark.config(
        TAXI_EXP_CLIENT_SETTINGS={
            '__default__': {
                '__default__': {
                    'num_retries': 0,
                    'retry_delay_ms': [50],
                    'request_timeout_ms': 250,
                },
            },
        },
    )
    async def _wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return _wrapper


@pytest.mark.config(
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'num_retries': 0,
                'retry_delay_ms': [50],
                'request_timeout_ms': 250,
            },
            'v1/experiments/': {
                'num_retries': 2,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
        'new_service': {
            '__default__': {
                'num_retries': 2,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
            'v1/experiments/': {
                'num_retries': 3,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
    },
)
def test_config(test_taxi_app, taxi_exp_client):
    # __default__ -> __default__
    res = taxi_exp_client._settings.get_request_params('unknown')
    assert res.num_retries == 0
    assert res.retry_delay_ms == [50]
    assert res.request_timeout_ms == 250

    # __default__ -> v1/experiments/
    res = taxi_exp_client._settings.get_request_params('v1/experiments/')
    assert res.num_retries == 2
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    taxi_exp_client = taxi_exp.TaxiExpClient(
        test_taxi_app.session,
        test_taxi_app.config,
        'new_service',
        test_taxi_app.tvm,
    )

    # new_service -> v1/experiments/
    res = taxi_exp_client._settings.get_request_params('v1/experiments/')
    assert res.num_retries == 3
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    # new_service -> __default__
    res = taxi_exp_client._settings.get_request_params('unknown')
    assert res.num_retries == 2
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    assert taxi_exp_client._settings.fetch_delay(res.retry_delay_ms, 0) == 50
    assert taxi_exp_client._settings.fetch_delay(res.retry_delay_ms, 1) == 5
    assert taxi_exp_client._settings.fetch_delay(res.retry_delay_ms, 2) == 7
    assert taxi_exp_client._settings.fetch_delay(res.retry_delay_ms, 12) == 7


@pytest.mark.config(
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'num_retries': 0,
                'retry_delay_ms': [50],
                'request_timeout_ms': 250,
            },
        },
        'test_service': {
            'v1/experiments/': {
                'num_retries': 5,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
    },
)
@pytest.mark.parametrize('failed_number', [4, 6])
async def test_connection_error(
        test_taxi_app,
        taxi_exp_client,
        patch_aiohttp_session,
        response_mock,
        failed_number,
        monkeypatch,
):
    base_url = 'http://taxi-exp-test'
    monkeypatch.setattr(taxi_exp_client, '_base_url', base_url)
    retries_count = 0

    @patch_aiohttp_session(base_url, 'POST')
    def _patch_request(*args, **kwargs):
        nonlocal retries_count
        if retries_count < failed_number:
            retries_count += 1
            if retries_count // 2:
                raise aiohttp.ClientConnectionError
            else:
                return response_mock(json={}, status=500)
        else:
            return response_mock(json={})

    try:
        await taxi_exp_client.create_exp(name='hello', data={})
        assert failed_number < 5
    except taxi_exp.RemoteError:
        assert failed_number > 5

    await test_taxi_app.session.close()


@mark_default_config
async def test_request_error(test_taxi_app, taxi_exp_client, mockserver):
    @mockserver.json_handler('/taxi-exp', prefix=True)
    def _handler(*args, **kwargs):
        return mockserver.make_response(
            json={'message': 'Message', 'code': 'ERROR_CODE'}, status=400,
        )

    try:
        await taxi_exp_client.create_exp(name='hello', data={})
    except taxi_exp.RequestError as exc:
        assert str(exc) == (
            'Request to taxi_exp failed: (response_code=400): '
            '{"message": "Message", "code": "ERROR_CODE"}'
        )
    else:
        assert False

    await test_taxi_app.session.close()
