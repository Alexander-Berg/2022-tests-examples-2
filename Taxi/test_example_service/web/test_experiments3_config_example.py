import pytest


@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    config_name='example_exp3_config',
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
    config_name='example_exp3_config',
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
    config_name='example_exp3_config',
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
    ],
)
async def test_who_are_you(phone, answer, code, web_app_client):
    if phone is None:
        url = '/who_are_you_config'
    else:
        url = f'/who_are_you_config?phone={phone}'
    response = await web_app_client.get(
        url, headers={'X-Remote-IP': '127.0.0.1'},
    )
    assert response.status == code

    if code == 200:
        assert (await response.text()) == answer
    else:
        body = await response.json()
        assert body['code'] == answer
