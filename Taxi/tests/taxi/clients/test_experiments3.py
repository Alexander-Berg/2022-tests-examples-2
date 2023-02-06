# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=protected-access
import aiohttp
import pytest

from taxi import config
from taxi.clients import experiments3
from taxi.clients import tvm


@pytest.fixture
async def client(loop, db):
    return experiments3.Experiments3Client(
        secdist={
            'settings_override': {'TAXI_EXPERIMENTS3_API_TOKEN': 'secret'},
        },
        config=config.Config(db),
        session=aiohttp.ClientSession(loop=loop),
        retries=5,
        delay=0,
    )


async def test_experiments3_client(client, mockserver):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        json = request.json
        assert json == {
            'consumer': 'launch',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '3.4.5',
                },
            ],
        }

        return {
            'items': [
                {
                    'name': 'experiment_1',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    client_app = experiments3.ClientApplication('android', '3.4.5')

    result = await client.get_values(
        'launch',
        [
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
        ],
        client_application=client_app,
    )
    assert result == [
        experiments3.ExperimentsValue(
            'experiment_1', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1

    await client.session.close()


async def test_experiments3_client_config_values(client, mockserver):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        assert 'v1/configs' in request.url
        json = request.json
        assert json == {
            'consumer': 'launch',
            'config_name': 'test_config',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '3.4.5',
                },
            ],
        }

        return {
            'items': [
                {
                    'name': 'test_config',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    client_app = experiments3.ClientApplication('android', '3.4.5')

    result = await client.get_config_values(
        'test_config',
        'launch',
        [
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
        ],
        client_application=client_app,
    )
    assert result == [
        experiments3.ExperimentsValue(
            'test_config', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1

    await client.session.close()


async def test_experiments3_client_with_user_agent(client, mockserver):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        json = request.json
        assert json == {
            'consumer': 'launch',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
            ],
        }
        assert (
            request.headers.get('X-Request-Application')
            == 'yandex-taxi/3.4.5 Android/6.0 (testenv)'
        )

        return {
            'items': [
                {
                    'name': 'experiment_1',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    result = await client.get_values(
        'launch',
        user_agent='yandex-taxi/3.4.5 Android/6.0 (testenv)',
        experiments_args=[
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
        ],
    )
    assert result == [
        experiments3.ExperimentsValue(
            'experiment_1', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1

    await client.session.close()


async def test_experiments3_client_bulk(client, mockserver):
    @mockserver.json_handler('/experiments3/v1/experiments/bulk', prefix=True)
    def patch_request(request):
        assert (
            request.headers.get('X-Request-Application')
            == 'yandex-taxi/3.4.5 Android/6.0 (testenv)'
        )
        json = request.json
        assert json == {
            'items': [
                {
                    'consumer': 'launch',
                    'args': [
                        {
                            'name': 'user_id',
                            'type': 'string',
                            'value': '8395bc9f652addd8fa174f64a0b4d848',
                        },
                    ],
                },
            ],
        }

        return {
            'results': [
                {
                    'items': [
                        {
                            'name': 'experiment_1',
                            'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                        },
                    ],
                },
            ],
        }

    result = await client.get_bulk_values(
        [
            {
                'consumer': 'launch',
                'experiments_args': [
                    experiments3.ExperimentsArg(
                        'user_id',
                        'string',
                        '8395bc9f652addd8fa174f64a0b4d848',
                    ),
                ],
            },
        ],
        user_agent='yandex-taxi/3.4.5 Android/6.0 (testenv)',
    )
    assert result == [
        experiments3.ExperimentsResponse(
            items=[
                experiments3.ExperimentsValue(
                    'experiment_1', {'key_1': 'value_1', 'key_2': 'value_2'},
                ),
            ],
            version=-1,
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1

    await client.session.close()


async def test_experiments3_client_with_args_transformation(
        client, response_mock, mockserver,
):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        json = request.json
        assert json == {
            'consumer': 'launch',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
                {'name': 'ip', 'type': 'string', 'value': '127.0.0.1'},
            ],
            'kwargs_transformations': [
                {
                    'type': 'country_by_ip',
                    'src_kwargs': ['ip'],
                    'dst_kwarg': 'country',
                    'preserve_src_kwargs': True,
                },
            ],
        }

        return {
            'items': [
                {
                    'name': 'experiment_1',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    result = await client.get_values(
        'launch',
        experiments_args=[
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
            experiments3.ExperimentsArg('ip', 'string', '127.0.0.1'),
        ],
        args_transformations=[
            experiments3.ExperimentsArgTransformation(
                type='country_by_ip',
                src_args=['ip'],
                dst_arg='country',
                preserve_src_args=True,
            ),
        ],
    )
    assert result == [
        experiments3.ExperimentsValue(
            'experiment_1', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1

    await client.session.close()


@pytest.mark.parametrize('failed_number', [4, 6])
async def test_connection_error(client, mockserver, failed_number):
    retries_count = 0

    # pylint: disable=unused-variable
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        nonlocal retries_count
        if retries_count < failed_number:
            retries_count += 1
            raise mockserver.NetworkError()
        else:
            return {
                'items': [
                    {
                        'name': 'experiment_1',
                        'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                    },
                ],
            }

    try:
        await client.get_values(
            'launch',
            [
                experiments3.ExperimentsArg(
                    'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
                ),
            ],
        )
        assert failed_number < 5
    except experiments3.Experiments3RequestError:
        assert failed_number > 5

    await client.session.close()


@pytest.mark.parametrize('use_tvm', [True, False])
async def test_auth(
        simple_secdist, aiohttp_client, patch, mockserver, client, use_tvm,
):
    @mockserver.json_handler('/experiments3', prefix=True)
    def handle(request):
        if use_tvm:
            assert request.headers['X-Ya-Service-Ticket'] == 'ticket'
        else:
            assert request.headers['YaTaxi-Api-Key'] == 'secret'
        return {'items': []}

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    tvm_client = tvm.TVMClient(
        service_name='billing_subventions',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )

    if use_tvm:
        client._tvm = tvm_client

    await client.get_values('launch', [])
    assert handle.times_called == 1

    await client.session.close()


@pytest.fixture
def mock_host_info(monkeypatch):
    monkeypatch.setattr('taxi.settings.is_test_environment', lambda: False)
    monkeypatch.setattr(
        'taxi.util.host_info._get_host_name', lambda: 'host_name',
    )

    def _read_and_parse_file(path, parse_function):
        if 'clownductor' in path:
            return parse_function('pre_stable')
        raise FileNotFoundError

    monkeypatch.setattr(
        'taxi.util.host_info._read_and_parse_file', _read_and_parse_file,
    )


@pytest.mark.usefixtures('mock_host_info')
@pytest.mark.now('2021-01-11T12:00:00+0000')
async def test_get_default_kwargs(client):

    assert client.default_kwargs == [
        experiments3.ExperimentsArg(
            name='host', type='string', value='host_name',
        ),
        experiments3.ExperimentsArg(
            name='cgroups', type='set_string', value=[],
        ),
        experiments3.ExperimentsArg(
            name='ngroups', type='set_string', value=['pre_stable'],
        ),
        experiments3.ExperimentsArg(
            name='is_prestable', type='bool', value=True,
        ),
        experiments3.ExperimentsArg(
            name='request_timestamp', type='int', value=1610366400000,
        ),
        experiments3.ExperimentsArg(
            name='request_timestamp_minutes', type='int', value=26839440,
        ),
    ]
    await client.session.close()


async def test_typed_experiments_values(client, mockserver):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        assert 'v1/typed_experiments' in request.url
        json = request.json
        assert json == {
            'consumer': 'launch',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '3.4.5',
                },
            ],
            'locale': 'en',
        }

        return {
            'items': [
                {
                    'name': 'experiment_1',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    client_app = experiments3.ClientApplication('android', '3.4.5')

    result = await client.get_typed_values(
        'en',
        'launch',
        [
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
        ],
        client_application=client_app,
    )
    assert result == [
        experiments3.ExperimentsValue(
            'experiment_1', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1
    await client.session.close()


async def test_typed_configs_values(client, mockserver):
    @mockserver.json_handler('/experiments3', prefix=True)
    def patch_request(request):
        assert 'v1/typed_configs' in request.url
        json = request.json
        assert json == {
            'consumer': 'launch',
            'args': [
                {
                    'name': 'user_id',
                    'type': 'string',
                    'value': '8395bc9f652addd8fa174f64a0b4d848',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '3.4.5',
                },
            ],
            'locale': 'en',
        }

        return {
            'items': [
                {
                    'name': 'test_config',
                    'value': {'key_1': 'value_1', 'key_2': 'value_2'},
                },
            ],
        }

    client_app = experiments3.ClientApplication('android', '3.4.5')

    result = await client.get_typed_config_values(
        'en',
        'launch',
        [
            experiments3.ExperimentsArg(
                'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
            ),
        ],
        client_application=client_app,
    )
    assert result == [
        experiments3.ExperimentsValue(
            'test_config', {'key_1': 'value_1', 'key_2': 'value_2'},
        ),
    ]
    calls = patch_request.times_called
    assert calls == 1
    await client.session.close()
