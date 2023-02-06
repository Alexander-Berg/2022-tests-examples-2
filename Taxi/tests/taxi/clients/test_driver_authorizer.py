# pylint: disable=protected-access, redefined-outer-name
import pytest

from taxi import config
from taxi.clients import driver_authorizer
from taxi.clients import tvm


DRIVER_AUTHORIZER_URL = 'http://test-driver-authorizer-url'


@pytest.fixture
def tvm_client(simple_secdist, aiohttp_client, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )


@pytest.fixture
async def test_app(test_taxi_app, tvm_client):
    test_taxi_app.driver_authorizer_client = (
        driver_authorizer.DriverAuthorizerClient(
            session=test_taxi_app.session,
            config=test_taxi_app.config,
            tvm_client=tvm_client,
        )
    )
    return test_taxi_app


@pytest.fixture
def mock_request(monkeypatch, mock):
    def _create_dummy_request(response):
        @mock
        async def _dummy_request(*args, **kwargs):
            return response

        monkeypatch.setattr(
            driver_authorizer.DriverAuthorizerClient,
            '_request_json',
            _dummy_request,
        )
        return _dummy_request

    return _create_dummy_request


@pytest.mark.config(DRIVER_AUTHORIZER_URL=DRIVER_AUTHORIZER_URL)
@pytest.mark.parametrize(
    'network_ok,method,url,data,params,expected_result,expected_exception',
    [
        # All OK
        (True, 'POST', '/some_url', {'some': 'data'}, None, {}, None),
        (True, 'GET', '/some_url', None, {'some': 'params'}, {}, None),
        # Wrong auth
        (
            True,
            'GET',
            '/some_url',
            None,
            {'auth': 'wrong'},
            None,
            driver_authorizer.AuthError,
        ),
        # Wrong URL
        (
            True,
            'GET',
            '/wrong_url',
            {'some': 'data'},
            None,
            None,
            driver_authorizer.ClientError,
        ),
        # Network problems
        (
            False,
            'POST',
            '/some_url',
            {'some': 'data'},
            None,
            None,
            driver_authorizer.NetworkError,
        ),
    ],
)
async def test_request(
        test_app,
        monkeypatch,
        mock,
        network_ok,
        method,
        url,
        data,
        params,
        expected_result,
        expected_exception,
):
    @mock
    async def _dummy_session_request(**kwargs):
        class _DummyResponse:
            def __init__(self, status):
                self.status = status

            async def json(self, **kwargs):
                return {}

            async def text(self):
                return '{}'

        if not network_ok:
            raise driver_authorizer.NetworkError('Cannot connect')
        if (
                kwargs['params'] is not None
                and 'auth' in kwargs['params']
                and kwargs['params']['auth'] == 'wrong'
        ):
            return _DummyResponse(401)
        if kwargs['url'] != 'http://test-driver-authorizer-url/some_url':
            return _DummyResponse(418)

        return _DummyResponse(200)

    monkeypatch.setattr(
        test_app.driver_authorizer_client._session,
        'request',
        _dummy_session_request,
    )

    exception = None
    result = None
    try:
        result = await test_app.driver_authorizer_client._request_json(
            'text/html', url, method=method, data=data, params=params,
        )
    except driver_authorizer.BaseError as _e:
        exception = type(_e)

    assert exception == expected_exception
    assert result == expected_result

    if expected_exception is None:
        request_calls = _dummy_session_request.calls
        assert request_calls[0]['kwargs'] == {
            'headers': {'X-Ya-Service-Ticket': 'ticket'},
            'url': 'http://test-driver-authorizer-url/some_url',
            'json': data,
            'method': method,
            'params': params,
        }


@pytest.mark.parametrize(
    'db,session,expected_uuid',
    [
        ('some_park_id', 'some_session_id', 'some_uuid'),
        ('bad_park_id', 'some_session_id', None),
        ('some_park_id', 'bad_session_id', None),
    ],
)
async def test_driver_session(
        monkeypatch, mock, test_app, db, session, expected_uuid,
):
    @mock
    async def _dummy_request(*_, **kwargs):
        if (
                kwargs['params']['db'] == 'some_park_id'
                and kwargs['params']['session'] == 'some_session_id'
        ):
            return {'uuid': 'some_uuid'}

        raise driver_authorizer.AuthError('Not authorized')

    monkeypatch.setattr(
        test_app.driver_authorizer_client, '_request_json', _dummy_request,
    )

    try:
        driver_uuid = await test_app.driver_authorizer_client.driver_session(
            db=db, session=session,
        )
    except driver_authorizer.AuthError:
        driver_uuid = None

    request_calls = _dummy_request.calls
    assert request_calls
    assert 'kwargs' in request_calls[0]
    assert request_calls[0]['kwargs'] == {
        'method': 'GET',
        'url': '/driver_session',
        'params': {'db': db, 'session': session},
        'log_extra': None,
    }

    assert driver_uuid == expected_uuid


@pytest.mark.parametrize(
    'client_id,park_id,uuid,expected_token,expected_exception',
    [
        ('good_client_id', 'good_park_id', 'good_uuid', 'some_token', None),
        (
            'good_client_id',
            'good_park_id',
            'bad_uuid',
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'good_client_id',
            'bad_park_id',
            'good_uuid',
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'bad_client_id',
            'good_park_id',
            'good_uuid',
            None,
            driver_authorizer.NotFoundError,
        ),
    ],
)
async def test_get_driver_sessions(
        monkeypatch,
        mock,
        test_app,
        client_id,
        park_id,
        uuid,
        expected_token,
        expected_exception,
):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, headers):
                self.headers = headers

        params = kwargs['params']
        if (
                params
                and 'client_id' in params
                and 'park_id' in params
                and 'uuid' in params
        ):
            if (
                    params['client_id'] == 'good_client_id'
                    and params['park_id'] == 'good_park_id'
                    and params['uuid'] == 'good_uuid'
            ):
                return _DummyResponse({'X-Driver-Session': 'some_token'})

            raise driver_authorizer.NotFoundError

        raise driver_authorizer.ClientError

    monkeypatch.setattr(
        test_app.driver_authorizer_client, '_request', _dummy_request,
    )

    token = None
    exception = None

    try:
        token = await test_app.driver_authorizer_client.get_driver_sessions(
            client_id, park_id, uuid,
        )
    except driver_authorizer.BaseError as _e:
        exception = type(_e)

    request_calls = _dummy_request.calls
    assert request_calls
    assert 'kwargs' in request_calls[0]
    assert request_calls[0]['kwargs'] == {
        'method': 'GET',
        'url': '/driver/sessions',
        'params': {'client_id': client_id, 'park_id': park_id, 'uuid': uuid},
        'log_extra': None,
    }

    assert token == expected_token
    assert exception == expected_exception


@pytest.mark.parametrize(
    'client_id,park_id,uuid,ttl,expected_token,expected_exception',
    [
        (
            'good_client_id',
            'good_park_id',
            'good_uuid',
            42,
            'some_token',
            None,
        ),
        (
            'good_client_id',
            'good_park_id',
            'bad_uuid',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'good_client_id',
            'bad_park_id',
            'good_uuid',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'bad_client_id',
            'good_park_id',
            'good_uuid',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'good_client_id',
            'good_park_id',
            'good_uuid',
            0,
            None,
            driver_authorizer.NotFoundError,
        ),
    ],
)
async def test_put_driver_sessions(
        monkeypatch,
        mock,
        test_app,
        client_id,
        park_id,
        uuid,
        ttl,
        expected_token,
        expected_exception,
):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, headers):
                self.headers = headers

        params = kwargs['params']
        data = kwargs['data']
        is_correct_params_format = (
            params
            and 'client_id' in params
            and 'park_id' in params
            and 'uuid' in params
        )
        is_correct_data_format = data and 'ttl' in data
        if is_correct_params_format and is_correct_data_format:
            if (
                    params['client_id'] == 'good_client_id'
                    and params['park_id'] == 'good_park_id'
                    and params['uuid'] == 'good_uuid'
                    and data['ttl'] == 42
            ):
                return _DummyResponse({'X-Driver-Session': 'some_token'})

            raise driver_authorizer.NotFoundError

        raise driver_authorizer.ClientError

    monkeypatch.setattr(
        test_app.driver_authorizer_client, '_request', _dummy_request,
    )

    token = None
    exception = None

    try:
        token = await test_app.driver_authorizer_client.put_driver_sessions(
            client_id, park_id, uuid, ttl,
        )
    except driver_authorizer.BaseError as _e:
        exception = type(_e)

    request_calls = _dummy_request.calls
    assert request_calls
    assert 'kwargs' in request_calls[0]
    assert request_calls[0]['kwargs'] == {
        'method': 'PUT',
        'url': '/driver/sessions',
        'params': {'client_id': client_id, 'park_id': park_id, 'uuid': uuid},
        'data': {'ttl': ttl},
        'log_extra': None,
    }

    assert token == expected_token
    assert exception == expected_exception


@pytest.mark.parametrize(
    'client_id,park_id,uuid,expected_exception',
    [
        ('good_client_id', 'good_park_id', 'good_uuid', None),
        (
            'good_client_id',
            'good_park_id',
            'bad_uuid',
            driver_authorizer.NotFoundError,
        ),
        (
            'good_client_id',
            'bad_park_id',
            'good_uuid',
            driver_authorizer.NotFoundError,
        ),
        (
            'bad_client_id',
            'good_park_id',
            'good_uuid',
            driver_authorizer.NotFoundError,
        ),
    ],
)
async def test_delete_driver_sessions(
        monkeypatch,
        mock,
        test_app,
        client_id,
        park_id,
        uuid,
        expected_exception,
):
    @mock
    async def _dummy_request(**kwargs):
        params = kwargs['params']
        if (
                params
                and 'client_id' in params
                and 'park_id' in params
                and 'uuid' in params
        ):
            if (
                    params['client_id'] == 'good_client_id'
                    and params['park_id'] == 'good_park_id'
                    and params['uuid'] == 'good_uuid'
            ):
                return

            raise driver_authorizer.NotFoundError

        raise driver_authorizer.ClientError

    monkeypatch.setattr(
        test_app.driver_authorizer_client, '_request', _dummy_request,
    )

    exception = None

    try:
        await test_app.driver_authorizer_client.delete_driver_sessions(
            client_id, park_id, uuid,
        )
    except driver_authorizer.BaseError as _e:
        exception = type(_e)

    request_calls = _dummy_request.calls
    assert request_calls
    assert 'kwargs' in request_calls[0]
    assert request_calls[0]['kwargs'] == {
        'method': 'DELETE',
        'url': '/driver/sessions',
        'params': {'client_id': client_id, 'park_id': park_id, 'uuid': uuid},
        'log_extra': None,
    }

    assert exception == expected_exception


@pytest.mark.parametrize(
    'token,client_id,park_id,ttl,expected_response,expected_exception',
    [
        (
            'good_token',
            'good_client_id',
            'good_park_id',
            42,
            {'uuid': 'some_uuid', 'ttl': 42},
            None,
        ),
        (
            'good_token',
            'good_client_id',
            'good_park_id',
            0,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'good_token',
            'good_client_id',
            'bad_park_id',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'good_token',
            'bad_client_id',
            'good_park_id',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
        (
            'bad_token',
            'good_client_id',
            'good_park_id',
            42,
            None,
            driver_authorizer.NotFoundError,
        ),
    ],
)
async def test_check_driver_sessions(
        monkeypatch,
        mock,
        test_app,
        token,
        client_id,
        park_id,
        ttl,
        expected_response,
        expected_exception,
):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, json):
                self._json = json

            async def json(self, **_):
                return self._json

        headers = kwargs['headers']
        data = kwargs['data']
        is_correct_headers_format = headers and 'X-Driver-Session' in headers
        is_correct_data_format = (
            data
            and 'client_id' in data
            and 'park_id' in data
            and 'ttl' in data
        )
        if is_correct_headers_format and is_correct_data_format:
            if (
                    data['client_id'] == 'good_client_id'
                    and data['park_id'] == 'good_park_id'
                    and data['ttl'] == 42
                    and headers['X-Driver-Session'] == 'good_token'
            ):
                return _DummyResponse({'uuid': 'some_uuid', 'ttl': 42})

            raise driver_authorizer.NotFoundError

        raise driver_authorizer.ClientError

    monkeypatch.setattr(
        test_app.driver_authorizer_client, '_request', _dummy_request,
    )

    response = None
    exception = None

    try:
        response = await (
            test_app.driver_authorizer_client.check_driver_sessions(
                token, client_id, park_id, ttl,
            )
        )
    except driver_authorizer.BaseError as _e:
        exception = type(_e)

    request_calls = _dummy_request.calls
    assert request_calls
    assert 'kwargs' in request_calls[0]
    assert request_calls[0]['kwargs'] == {
        'method': 'POST',
        'url': '/driver/sessions/check',
        'headers': {'X-Driver-Session': token},
        'data': {'client_id': client_id, 'park_id': park_id, 'ttl': ttl},
        'log_extra': None,
    }

    assert response == expected_response
    assert exception == expected_exception


@pytest.mark.parametrize(
    'user_agent,expected_result',
    [
        ('Taximeter 8.89 (550)', 'taximeter'),
        ('Taximeter-Uber 8.89 (550)', 'uberdriver'),
        ('Taximeter-Vezet 8.89 (550)', 'vezet'),
        ('Taximeter-beta 8.89 (550)', 'taximeter'),
        ('Taximeter-rubbish 8.89 (550)', 'taximeter'),
    ],
)
def test_parse_client_by_user_agent(user_agent, expected_result):
    result = driver_authorizer.parse_client_by_user_agent(user_agent)
    assert result == expected_result


@pytest.mark.parametrize(
    'retries_num,response_status,excepted_calls,excepted_exception',
    [
        (1, 500, 1, driver_authorizer.ServerError),
        (1, 400, 1, driver_authorizer.ClientError),
        (1, 401, 1, driver_authorizer.AuthError),
        (1, 200, 1, None),
        (2, 500, 2, driver_authorizer.ServerError),
        (3, 400, 1, driver_authorizer.ClientError),
        (5, 401, 1, driver_authorizer.AuthError),
        (3, 200, 1, None),
    ],
)
async def test_retry_request(
        test_taxi_app,
        tvm_client,
        patch_aiohttp_session,
        response_mock,
        retries_num,
        response_status,
        excepted_calls,
        excepted_exception,
):
    test_app.driver_authorizer_client = (
        driver_authorizer.DriverAuthorizerClient(
            session=test_taxi_app.session,
            config=test_taxi_app.config,
            tvm_client=tvm_client,
            retries_num=retries_num,
        )
    )

    @patch_aiohttp_session(DRIVER_AUTHORIZER_URL, 'POST')
    def _dummy_session_request(*args, **kwargs):
        return response_mock(json={}, status=response_status)

    async def make_request():
        await test_app.driver_authorizer_client._request(
            url='/some_url',
            method='POST',
            data={'some': 'data'},
            params={'some_params': 'some'},
        )

    if excepted_exception:
        with pytest.raises(excepted_exception):
            await make_request()
    else:
        await make_request()

    request_calls = _dummy_session_request.calls
    assert len(request_calls) == excepted_calls


@pytest.mark.config(CONFIG_RETRY_ONE=1, CONFIG_RETRY_FOUR=4)
@pytest.mark.parametrize(
    'config_name,excepted_calls',
    [
        ('CONFIG_RETRY_ONE', 1),
        ('CONFIG_RETRY_FOUR', 4),
        ('CONFIG_RETRY_SOME', 1),
    ],
)
@pytest.mark.config(DRIVER_AUTHORIZER_URL=DRIVER_AUTHORIZER_URL)
async def test_retry_config(
        test_taxi_app,
        patch_aiohttp_session,
        tvm_client,
        response_mock,
        config_name,
        excepted_calls,
):
    test_app.driver_authorizer_client = (
        driver_authorizer.DriverAuthorizerClient(
            session=test_taxi_app.session,
            config=test_taxi_app.config,
            tvm_client=tvm_client,
            retries_num_conf_name=config_name,
        )
    )

    @patch_aiohttp_session(DRIVER_AUTHORIZER_URL, 'POST')
    def _dummy_session_request(*args, **kwargs):
        return response_mock(json={}, status=500)

    with pytest.raises(driver_authorizer.BaseError):
        await test_app.driver_authorizer_client._request(
            url='/some_url',
            method='POST',
            data={'status': 'some'},
            params={'some_params': 'some'},
        )

    request_calls = _dummy_session_request.calls
    assert len(request_calls) == excepted_calls
