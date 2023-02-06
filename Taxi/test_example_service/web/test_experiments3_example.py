import pytest


@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79219201566'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='taxi',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79219201666'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='yandex',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79219202666'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='regular',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79219202611'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
        {'name': 'is_prestable', 'type': 'bool', 'value': True},
        {'name': 'request_timestamp', 'type': 'int', 'value': 1610366400000},
        {
            'name': 'request_timestamp_minutes',
            'type': 'int',
            'value': 26839440,
        },
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='regular',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79229202611'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
        {'name': 'is_prestable', 'type': 'bool', 'value': True},
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='taxi',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[
        {'name': 'phone', 'type': 'string', 'value': '+79239202611'},
        {'name': 'remote_ip', 'type': 'string', 'value': '127.0.0.1'},
        {'name': 'is_prestable', 'type': 'bool', 'value': False},
        {'name': 'host', 'type': 'string', 'value': 'test.host'},
        {'name': 'ngroups', 'type': 'set_string', 'value': []},
        {'name': 'cgroups', 'type': 'set_string', 'value': []},
    ],
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='taxi',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    file_args='args_in_file.json',
    args_transformations=[
        {
            'type': 'country_by_ip',
            'src_args': ['remote_ip'],
            'dst_arg': 'country_by_ip',
            'preserve_src_args': True,
        },
    ],
    value='regular',
)
@pytest.mark.usefixtures('territories_mock')
@pytest.mark.parametrize(
    'phone,answer,code',
    [
        ('79219201566', 'taxi', 200),
        ('79219201666', 'yandex', 200),
        ('79219202666', 'regular', 200),
        ('7', 'unknown', 200),
        ('aaaa', 'REQUEST_VALIDATION_ERROR', 400),
        ('', 'REQUEST_VALIDATION_ERROR', 400),
        (None, 'REQUEST_VALIDATION_ERROR', 400),
        pytest.param(
            '79219202611',
            'regular',
            200,
            marks=(
                pytest.mark.client_experiments3(
                    default_args=[
                        {
                            'name': 'is_prestable',
                            'type': 'bool',
                            'value': True,
                        },
                    ],
                ),
                pytest.mark.now('2021-01-11T12:00:00+0000'),
            ),
            id='success check if host is prestable',
        ),
        pytest.param(
            '79219202611',
            'unknown',
            200,
            marks=(
                pytest.mark.client_experiments3(
                    default_args=[
                        {
                            'name': 'is_prestable',
                            'type': 'bool',
                            'value': False,
                        },
                    ],
                ),
                pytest.mark.now('2021-01-11T12:00:00+0000'),
            ),
            id='fail check if host is not prestable',
        ),
        pytest.param(
            '79229202611',
            'taxi',
            200,
            marks=(
                pytest.mark.client_experiments3(
                    default_args=[
                        {
                            'name': 'is_prestable',
                            'type': 'bool',
                            'value': True,
                        },
                    ],
                    disable_request_timestamp=True,
                ),
            ),
            id='disable send request_timestamp* args',
        ),
        pytest.param(
            '79239202611',
            'taxi',
            200,
            marks=(
                pytest.mark.client_experiments3(
                    default_args=True, disable_request_timestamp=True,
                ),
                pytest.mark.now('2021-01-11T12:00:00+0000'),
            ),
            id='use default default_args',
        ),
        pytest.param(
            '79249202611',
            'regular',
            200,
            marks=(
                pytest.mark.client_experiments3(
                    default_args='default_args.json',
                    disable_request_timestamp=True,
                ),
                pytest.mark.now('2021-01-11T12:00:00+0000'),
            ),
            id='load default args from file',
        ),
    ],
)
async def test_who_are_you(phone, answer, code, web_app_client):
    if phone is None:
        url = '/who_are_you'
    else:
        url = f'/who_are_you?phone={phone}'
    response = await web_app_client.get(
        url, headers={'X-Remote-IP': '127.0.0.1'},
    )
    assert response.status == code

    if code == 200:
        assert (await response.text()) == answer
    else:
        body = await response.json()
        assert body['code'] == answer
