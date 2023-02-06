# pylint: disable=protected-access
import asyncio
import dataclasses
import datetime
import itertools
import typing
from typing import NamedTuple

import aiohttp
from aiohttp import web
import pytest

from generated.clients import yet_another_service as yas_module
from taxi import stats as stats_module


TIMESTAMP_NOW = 1509498600
NOW = datetime.datetime.utcfromtimestamp(TIMESTAMP_NOW).isoformat()
PING_DESTINATION = '$mockserver_https/yet-another-service/ping-GET'
PARAM_DESTINATION = (
    '$mockserver_https/yet-another-service/path-parameters/name-GET'
)


class Stats(NamedTuple):
    handler: typing.Any
    dump: typing.Callable


@pytest.fixture(name='stats')
def mocked_stats(web_context, mockserver):
    @mockserver.json_handler('/solomon/unittests')
    def handler(request):
        return mockserver.make_response()

    return Stats(handler, web_context.stats._gather_and_send_data)


@pytest.fixture(name='client')
@pytest.mark.now(NOW)
def yas_fixture(web_context):
    return web_context.clients.yet_another_service


def _get_dest_sensor(
        sensor_name,
        value=None,
        http_destination=PING_DESTINATION,
        kind='IGAUGE',
        timestamp=None,
        **labels,
):
    sensor = {
        'kind': kind,
        'labels': {
            'application': 'example_service_web',
            'http_destination': http_destination,
            'sensor': sensor_name,
            **labels,
        },
    }
    if value is None:
        return sensor

    if kind == 'HIST':
        sensor['hist'] = value
    else:
        sensor['value'] = value

    if timestamp is not None:
        sensor['ts'] = timestamp

    return sensor


@dataclasses.dataclass
class Params:
    handler_responses: typing.Iterable
    handler_calls: int
    timer_return_values: typing.List[float]
    hist_bounds: typing.List[float]
    hist_buckets: typing.List[int]
    hist_inf: int
    success_code: typing.Optional[int] = 200
    fails_resp_codes: typing.Optional[typing.Dict[int, int]] = None
    attempts: int = 1
    resp_1xx: int = 0
    resp_2xx: int = 0
    resp_3xx: int = 0
    resp_4xx: int = 0
    resp_5xx: int = 0
    total_fail: int = 0
    total_ok: int = 0
    errors_ok: int = 0
    errors_payload: int = 0
    errors_connection: int = 0
    errors_response: int = 0
    errors_unknown: int = 0
    errors_timeout: int = 0
    exception_cls: typing.Any = None
    exception_args: tuple = ()
    destination: str = ''


def _make_params(
        success_code: typing.Optional[int] = None,
        fails_resp_codes: typing.Optional[typing.Dict[int, int]] = None,
        attempts: int = 1,
        resp_1xx: int = 0,
        resp_2xx: int = 0,
        resp_3xx: int = 0,
        resp_4xx: int = 0,
        resp_5xx: int = 0,
        total_fail: int = 0,
        total_ok: int = 0,
        errors_ok: int = 0,
        errors_payload: int = 0,
        errors_connection: int = 0,
        errors_response: int = 0,
        errors_unknown: int = 0,
        errors_timeout: int = 0,
        exception_cls: typing.Any = None,
        exception_args: tuple = (),
        destination: str = PING_DESTINATION,
):
    assert attempts >= 1

    cases: list = []
    for code, value in (fails_resp_codes or {}).items():
        cases.extend([code] * value)
    handler_calls = len(cases)

    if errors_timeout:
        cases.extend(['timeout'] * errors_timeout)
    if errors_payload:
        cases.extend(['payload'] * errors_payload)
    if errors_connection:
        cases.extend(['connection'] * errors_connection)
    if errors_response:
        cases.extend(['response'] * errors_response)
    if errors_unknown:
        cases.extend(['unknown'] * errors_unknown)

    if success_code:
        cases.append(success_code)
        handler_calls += 1

    assert attempts == len(cases)

    hist_bounds = stats_module.BucketsAggregation.DEFAULT_BOUNDS
    hist_buckets = [0] * len(hist_bounds)
    hist_inf = 0
    timer_return_values = []

    for i in range(attempts):
        if i < len(hist_buckets):
            hist_buckets[i] = 1
            # adding 0 before each timing for start_time call
            timer_return_values.extend([0, hist_bounds[i]])
        else:
            hist_inf += 1
            timer_return_values.extend([0, hist_bounds[-1] + 1])

    return pytest.param(
        Params(
            handler_responses=cases,
            handler_calls=handler_calls,
            timer_return_values=timer_return_values,
            hist_bounds=hist_bounds,
            hist_buckets=hist_buckets,
            hist_inf=hist_inf,
            success_code=success_code,
            fails_resp_codes=fails_resp_codes,
            attempts=attempts,
            resp_1xx=resp_1xx,
            resp_2xx=resp_2xx,
            resp_3xx=resp_3xx,
            resp_4xx=resp_4xx,
            resp_5xx=resp_5xx,
            total_fail=total_fail,
            total_ok=total_ok,
            errors_ok=errors_ok,
            errors_payload=errors_payload,
            errors_connection=errors_connection,
            errors_response=errors_response,
            errors_unknown=errors_unknown,
            errors_timeout=errors_timeout,
            exception_cls=exception_cls,
            exception_args=exception_args,
            destination=destination,
        ),
        marks=pytest.mark.config(
            XSERVICE_CLIENT_QOS={
                '__default__': {'timeout-ms': 10000, 'attempts': attempts},
            },
        ),
    )


@pytest.mark.parametrize(
    'params',
    [
        _make_params(success_code=200, resp_2xx=1, total_ok=1, errors_ok=1),
        _make_params(
            success_code=200,
            attempts=3,
            fails_resp_codes={500: 1, 502: 1},
            resp_2xx=1,
            resp_5xx=2,
            total_ok=1,
            errors_ok=3,
        ),
        _make_params(
            attempts=14,
            fails_resp_codes={500: 2, 502: 3},
            errors_timeout=4,
            errors_connection=5,
            resp_5xx=5,
            total_fail=1,
            errors_ok=5,
            exception_cls=yas_module.ClientException,
            exception_args=(
                'yet-another-service client error: something bad happened',
            ),
        ),
        _make_params(
            attempts=5,
            errors_timeout=5,
            total_fail=1,
            exception_cls=yas_module.ClientException,
            exception_args=('yet-another-service timeout: timeout!',),
        ),
        _make_params(
            attempts=1,
            fails_resp_codes={400: 1},
            resp_4xx=1,
            errors_ok=1,
            total_fail=1,
            exception_cls=yas_module.NotDefinedResponse,
            exception_args=(400, b''),
        ),
        _make_params(
            attempts=3,
            fails_resp_codes={500: 3},
            resp_5xx=3,
            errors_ok=3,
            total_fail=1,
            exception_cls=yas_module.NotDefinedResponse,
            exception_args=(500, b''),
        ),
        _make_params(
            attempts=1,
            total_fail=1,
            errors_unknown=1,
            exception_cls=ValueError,
            exception_args=('unknown error',),
        ),
        _make_params(
            attempts=2,
            errors_payload=2,
            total_fail=1,
            exception_cls=yas_module.ClientException,
            exception_args=('yet-another-service client error: bad payload',),
        ),
        _make_params(
            attempts=7,
            errors_response=7,
            total_fail=1,
            exception_cls=yas_module.ClientException,
            exception_args=(
                'yet-another-service client error: 0, message=\'\'',
            ),
        ),
        _make_params(
            success_code=200,
            resp_2xx=1,
            total_ok=1,
            errors_ok=1,
            destination=PARAM_DESTINATION,
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_ping(
        client, mock_yet_another_service, stats, params, patch, monkeypatch,
):
    assert isinstance(params, Params)

    @patch(
        'generated.clients.yet_another_service.'
        'YetAnotherServiceClient._get_attempt_sleep_time',
    )
    def _get_sleep_time(current_attempt):
        return 0

    timer_it = iter(params.timer_return_values)

    @patch('generated.clients.yet_another_service.timeit.default_timer')
    def _default_timer():
        nonlocal timer_it
        timer_value = next(timer_it)
        return timer_value

    _resps_for_send, _resps_for_mock = itertools.tee(params.handler_responses)
    _original_send = client._session_request

    async def _wrapped_send(*args, **kwargs):
        code = next(_resps_for_send)
        if isinstance(code, int):
            return await _original_send(*args, **kwargs)
        if code == 'timeout':
            raise asyncio.TimeoutError('timeout!')
        if code == 'payload':
            raise aiohttp.ClientPayloadError('bad payload')
        if code == 'connection':
            raise aiohttp.ClientConnectionError('something bad happened')
        if code == 'response':
            raise aiohttp.ClientResponseError(
                None, (),  # type: ignore
            )
        if code == 'unknown':
            raise ValueError('unknown error')
        raise RuntimeError('unreachable code')

    monkeypatch.setattr(client, '_session_request', _wrapped_send)

    if params.destination == PING_DESTINATION:

        @mock_yet_another_service('/ping')
        async def handler(request):
            code = next(_resps_for_mock)
            while not isinstance(code, int):
                code = next(_resps_for_mock)
            return web.Response(status=code)

        if params.success_code:
            response = await client.ping()
            assert response.status == 200
        else:
            with pytest.raises(params.exception_cls) as exc_info:
                await client.ping()
            assert exc_info.value.args == params.exception_args
    elif params.destination == PARAM_DESTINATION:

        @mock_yet_another_service('/path-parameters/{abc}')
        async def handler(request):
            code = next(_resps_for_mock)
            while not isinstance(code, int):
                code = next(_resps_for_mock)
            return web.Response(status=code)

        if params.success_code:
            response = await client.path_parameters_name_get(name='{abc}')
            assert response.status == 200
        else:
            with pytest.raises(params.exception_cls) as exc_info:
                await client.path_parameters_name_get(name='{abc}')
            assert exc_info.value.args == params.exception_args
    else:
        raise RuntimeError('wrong param destination')

    sensors = await _get_sensors(stats)

    all_ping_sensors = list(
        filter(
            lambda x: x['labels'].get('http_destination')
            == params.destination,
            sensors,
        ),
    )
    other_sensors = list(
        filter(
            lambda x: x['labels'].get('http_destination')
            != params.destination,
            sensors,
        ),
    )

    for sensor in other_sensors:
        assert sensor['value'] == 0

    codes_sensors = []
    if params.fails_resp_codes:
        codes_sensors.extend(
            [
                _get_dest_sensor(
                    value=value,
                    sensor_name='httpclient.response',
                    http_code=str(code),
                    http_destination=params.destination,
                )
                for code, value in params.fails_resp_codes.items()
            ],
        )
    if params.success_code:
        codes_sensors.append(
            _get_dest_sensor(
                value=1,
                sensor_name='httpclient.response',
                http_code=str(params.success_code),
                http_destination=params.destination,
            ),
        )

    timings_sensor = _get_dest_sensor(
        kind='HIST',
        value={
            'bounds': params.hist_bounds,
            'buckets': params.hist_buckets,
            'inf': params.hist_inf,
        },
        sensor_name='httpclient.timings',
        http_destination=params.destination,
        timestamp=TIMESTAMP_NOW,
    )

    expected = _sort_sensors(
        [
            *codes_sensors,
            timings_sensor,
            _get_dest_sensor(
                value=params.resp_1xx,
                sensor_name='httpclient.response',
                http_code='1xx',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.resp_2xx,
                sensor_name='httpclient.response',
                http_code='2xx',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.resp_3xx,
                sensor_name='httpclient.response',
                http_code='3xx',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.resp_4xx,
                sensor_name='httpclient.response',
                http_code='4xx',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.resp_5xx,
                sensor_name='httpclient.response',
                http_code='5xx',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=0,
                sensor_name='httpclient.response',
                http_code='other',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.total_fail,
                sensor_name='httpclient.total_response',
                status='fail',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.total_ok,
                sensor_name='httpclient.total_response',
                status='ok',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_ok,
                sensor_name='httpclient.errors',
                http_error='ok',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_connection,
                sensor_name='httpclient.errors',
                http_error='connection-error',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_payload,
                sensor_name='httpclient.errors',
                http_error='payload-error',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_response,
                sensor_name='httpclient.errors',
                http_error='response-error',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_unknown,
                sensor_name='httpclient.errors',
                http_error='unknown-error',
                http_destination=params.destination,
            ),
            _get_dest_sensor(
                value=params.errors_timeout,
                sensor_name='httpclient.errors',
                http_error='timeout',
                http_destination=params.destination,
            ),
        ],
    )

    assert _sort_sensors(all_ping_sensors) == expected

    assert handler.times_called == params.handler_calls
    assert _get_sleep_time.calls == [
        {'current_attempt': i + 1} for i in range(params.attempts - 1)
    ]


async def _get_sensors(stats: Stats):
    await stats.dump()

    assert stats.handler.times_called == 1
    data = stats.handler.next_call()['request'].json

    return data['sensors']


def _sort_sensors(sensors):
    return sorted(sensors, key=lambda x: tuple(sorted(x['labels'].items())))
