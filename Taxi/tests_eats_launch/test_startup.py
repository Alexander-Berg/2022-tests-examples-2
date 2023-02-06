import pytest

LAUNCH_STARTUP = '/eats/v1/launch/v1/startup'


def build_headers(common_values):
    return {'X-Ya-Service-Ticket': common_values['mock_service_ticket']}


def build_exp30_startup(is_enabled_mobile_webview: bool):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_launch_startup',
        consumers=['eats-launch/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'is_enabled_mobile_webview': is_enabled_mobile_webview},
    )


def build_exp30_qos(value):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_launch_frontend_qos',
        consumers=['eats-launch/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


@pytest.mark.parametrize(
    ['expected_response_payload'],
    [
        pytest.param(
            {'is_webview': True},
            marks=[build_exp30_startup(True)],
            id='is_webview',
        ),
        pytest.param({}, marks=[build_exp30_startup(False)], id='is_native'),
    ],
)
async def test_happy_path(
        taxi_eats_launch, common_values, expected_response_payload,
):
    response = await taxi_eats_launch.post(
        LAUNCH_STARTUP,
        headers=build_headers(common_values),
        json={'urls_block_id': 'block1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_enabled_urls_block': True,
        'payload': expected_response_payload,
    }


async def test_empty_config(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.post(
        LAUNCH_STARTUP,
        headers=build_headers(common_values),
        json={'urls_block_id': 'block1'},
    )
    assert response.status_code == 200
    assert response.json() == {'is_enabled_urls_block': True, 'payload': {}}


@pytest.mark.parametrize(
    ['expected_response_qos'],
    [
        pytest.param(
            (
                [
                    {'attempts': 2, 'timeout_ms': 10000},
                    {
                        'url': '/api/v2/orders/tracking',
                        'attempts': 1,
                        'timeout_ms': 2000,
                    },
                ]
            ),
            marks=[
                build_exp30_qos(
                    {
                        'default': {'attempts': 2, 'timeout_ms': 10000},
                        '/api/v2/orders/tracking': {
                            'attempts': 1,
                            'timeout_ms': 2000,
                        },
                    },
                ),
            ],
            id='default_and_url',
        ),
        pytest.param(
            ([{'attempts': 2, 'timeout_ms': 10000}]),
            marks=[
                build_exp30_qos(
                    {'default': {'attempts': 2, 'timeout_ms': 10000}},
                ),
            ],
            id='only_default',
        ),
        pytest.param(
            (
                [
                    {
                        'url': '/api/v2/orders/tracking',
                        'attempts': 1,
                        'timeout_ms': 2000,
                    },
                ]
            ),
            marks=[
                build_exp30_qos(
                    {
                        '/api/v2/orders/tracking': {
                            'attempts': 1,
                            'timeout_ms': 2000,
                        },
                    },
                ),
            ],
            id='only_url',
        ),
    ],
)
async def test_qos(taxi_eats_launch, common_values, expected_response_qos):
    response = await taxi_eats_launch.post(
        LAUNCH_STARTUP,
        headers=build_headers(common_values),
        json={'urls_block_id': 'block1'},
    )
    assert response.status_code == 200
    assert response.json()['payload']['qos'] == expected_response_qos
