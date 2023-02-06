import datetime
import json

import pytest

from taxi.core import arequests
from taxi.external import crons


@pytest.fixture(autouse=True)
def _reduce_api_retries(monkeypatch):
    monkeypatch.setattr(crons, 'CRON_API_RETRIES', 2)
    monkeypatch.setattr(crons, 'CRON_API_RETRY_DELAY', .1)


@pytest.mark.parametrize(
    'network_err,status_code,response,expected_return_val,failure',
    [
        (
            False, 200, {'is_enabled': True}, True, False,
        ),
        (
            True, None, None, None, True,
        ),
        (
            False, 500, None, None, True,
        ),
        (
            False, 400, None, None, True,
        ),
    ]
)
@pytest.inline_callbacks
def test_is_enabled(
        areq_request,
        network_err, status_code, response, expected_return_val, failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert (
            url == 'http://crons.taxi.dev.yandex.net/v1/task/test/is-enabled/'
        )
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps(response))

    if network_err or failure:
        with pytest.raises(crons.BaseError):
            yield crons.is_enabled('test')
    else:
        if expected_return_val:
            assert (yield crons.is_enabled('test')) == expected_return_val
        else:
            with pytest.raises(crons.IsEnabledRequestError):
                yield crons.is_enabled('test')


@pytest.mark.parametrize(
    'network_err,status_code,expected_return_val,failure',
    [
        (
            False, 200, True, False,
        ),
        (
            False, 423, False, False,
        ),
        (
            True, None, None, True,
        ),
        (
            False, 500, None, True,
        ),
        (
            False, 400, None, True,
        ),
    ]
)
@pytest.inline_callbacks
def test_lock_aquire(
        areq_request,
        network_err, status_code, expected_return_val, failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert (
            url == 'http://crons.taxi.dev.yandex.net/v1/task/test/lock/aquire/'
        )
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps({}))

    def defer():
        return crons.lock_aquire(
            task_name='test',
            owner='1',
            key='test',
            now=datetime.datetime.now(),
            till=datetime.datetime.now(),
        )

    if network_err or failure:
        with pytest.raises(crons.BaseError):
            yield defer()
    else:
        if expected_return_val is not None:
            assert (yield defer()) == expected_return_val
        else:
            with pytest.raises(crons.LockAquireRequestError):
                yield defer()


@pytest.mark.parametrize(
    'network_err,status_code,expected_return_val,failure',
    [
        (
            False, 200, True, False,
        ),
        (
            False, 404, False, False,
        ),
        (
            True, None, None, True,
        ),
        (
            False, 500, None, True,
        ),
        (
            False, 400, None, True,
        ),
    ]
)
@pytest.inline_callbacks
def test_lock_prolong(
        areq_request,
        network_err, status_code, expected_return_val, failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert (
            url == 'http://crons.taxi.dev.yandex.net/v1/task/test/lock/prolong/'
        )
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps({}))

    def defer():
        return crons.lock_prolong(
            task_name='test',
            owner='1',
            key='test',
            till=datetime.datetime.now(),
        )

    if network_err or failure:
        with pytest.raises(crons.BaseError):
            yield defer()
    else:
        if expected_return_val is not None:
            assert (yield defer()) == expected_return_val
        else:
            with pytest.raises(crons.LockProlongRequestError):
                yield defer()


@pytest.mark.parametrize(
    'network_err,status_code,expected_return_val,failure',
    [
        (
            False, 200, True, False,
        ),
        (
            False, 404, False, False,
        ),
        (
            True, None, None, True,
        ),
        (
            False, 500, None, True,
        ),
        (
            False, 400, None, True,
        ),
    ]
)
@pytest.inline_callbacks
def test_lock_release(
        areq_request,
        network_err, status_code, expected_return_val, failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert (
            url == 'http://crons.taxi.dev.yandex.net/v1/task/test/lock/release/'
        )
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps({}))

    def defer():
        return crons.lock_release(
            task_name='test',
            owner='1',
            key='test',
        )

    if network_err or failure:
        with pytest.raises(crons.BaseError):
            yield defer()
    else:
        if expected_return_val is not None:
            assert (yield defer()) == expected_return_val
        else:
            with pytest.raises(crons.LockReleaseRequestError):
                yield defer()


@pytest.mark.parametrize(
    'network_err,status_code,expected_err,client_failure,service_failure',
    [
        (
            False, 200, False, False, False,
        ),
        (
            True, None, None, None, None,
        ),
        (
            False, 409, True, False, False,
        ),
        (
            False, 500, False, False, True,
        ),
        (
            False, 400, False, True, False,
        )
    ]
)
@pytest.inline_callbacks
def test_task_start(
        areq_request,
        network_err, status_code,
        expected_err, client_failure, service_failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert url == 'http://crons.taxi.dev.yandex.net/v1/task/test/start/'
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps({}))

    def defer():
        return crons.start(
            task_name='test',
            run_id='123',
            hostname='',
            start_time=datetime.datetime.now(),
            features=[],
        )

    if network_err or service_failure:
        with pytest.raises(crons.BaseError):
            yield defer()
    else:
        if not expected_err and not client_failure:
            assert (yield defer()) is None
        else:
            with pytest.raises(crons.StartTaskError):
                yield defer()


@pytest.mark.parametrize(
    'network_err,status_code,expected_err,client_failure,service_failure',
    [
        (
            False, 200, False, False, False,
        ),
        (
            True, None, None, None, None,
        ),
        (
            False, 409, True, False, False,
        ),
        (
            False, 500, False, False, True,
        ),
        (
            False, 400, False, True, False,
        )
    ]
)
@pytest.inline_callbacks
def test_task_finish(
        areq_request,
        network_err, status_code,
        expected_err, client_failure, service_failure,
):
    @areq_request
    def requests_request(method, url, *args, **kwargs):
        assert url == 'http://crons.taxi.dev.yandex.net/v1/task/test/finish/'
        if network_err:
            raise arequests.TimeoutError('timeout')
        return areq_request.response(status_code, body=json.dumps({}))

    def defer():
        return crons.finish(
            task_name='test',
            run_id='123',
            status='finished',
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now(),
            execution_time=10.0,
            clock_time=0.1,
        )

    if network_err or service_failure:
        with pytest.raises(crons.BaseError):
            yield defer()
    else:
        if not expected_err and not client_failure:
            assert (yield defer()) is None
        else:
            with pytest.raises(crons.FinishTaskError):
                yield defer()
