import pytest

PARK_ID = 'park_id_1'
DRIVER_ID = 'driver_id_1'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}

ENDPOINT = '/driver/v1/order-misc/v1/check/digital-pass'

TOKEN_TEMPLATE = {
    'access_token': '835eec7a-0075-3754-8e4d-2a75f38a1e28',
    'scope': 'am_application_scope default',
    'token_type': 'Bearer',
    'expires_in': 3600,
}
TICKET_INFO_TEMPLATE = {
    '_id': '5e9f02bfc6195830aa5c2b5f',
    'id': '30047eam65kam2xx',
    'source': 1,
    'data': {'DATE_BEGIN': '21.04.2020', 'DATE_END': '30.04.2020'},
    'date_create': '2020-04-21T14:27:11.887Z',
}
MO_TOKENS_TEMPLATE = {
    'accessToken': {
        'value': 'access_token',
        'expires': '2020-05-01T00:00:00.000000',
    },
    'refreshToken': {
        'value': 'refresh_token',
        'expires': '2020-05-01T00:00:00.000000',
    },
}
MO_TICKET_INFO_TEMPLATE = {'valid': 1, 'type': 1, 'parameters': []}


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.now('2020-04-25T11:30:00+0300')
@pytest.mark.parametrize(
    'token,ticket_info,code,expected_output',
    [
        pytest.param(
            None,
            {'result': TICKET_INFO_TEMPLATE},
            500,
            {
                'code': 'unable_to_check',
                'message': '',
                'details': {
                    'available_actions': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                },
            },
            id='Invalid token',
        ),
        pytest.param(
            TOKEN_TEMPLATE,
            None,
            500,
            {
                'code': 'unable_to_check',
                'message': '',
                'details': {
                    'available_actions': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                },
            },
            id='Invalid ticket info',
        ),
        pytest.param(
            TOKEN_TEMPLATE,
            {'result': TICKET_INFO_TEMPLATE},
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '2020-04-21T00:00:00.000000Z',
                'date_end': '2020-05-01T00:00:00.000000Z',
            },
            id='Valid ticket',
        ),
        pytest.param(
            TOKEN_TEMPLATE,
            {
                'result': {
                    **TICKET_INFO_TEMPLATE,
                    **{
                        'data': {
                            'DATE_BEGIN': '24.04.2020',
                            'DATE_END': '24.04.2020',
                        },
                    },
                },
            },
            200,
            {
                'is_valid': False,
                'available_actions': ['cancel_ride', 'retry_check'],
            },
            id='Expired ticket',
        ),
        pytest.param(
            TOKEN_TEMPLATE,
            {'result': False},
            200,
            {
                'is_valid': False,
                'available_actions': ['cancel_ride', 'retry_check'],
            },
            id='Invalid ticket',
        ),
    ],
)
async def test_check_digital_pass_dit(
        taxi_driver_order_misc,
        dit_efp,
        driver_trackstory,
        token,
        ticket_info,
        code,
        expected_output,
):
    dit_efp.set_token(token)
    dit_efp.set_ticket_info(ticket_info)
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit_mo'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.now('2020-04-25T11:30:00+0300')
@pytest.mark.parametrize(
    'token,ticket_info,code,expected_output',
    [
        pytest.param(
            None,
            MO_TICKET_INFO_TEMPLATE,
            500,
            {
                'code': 'unable_to_check',
                'message': '',
                'details': {
                    'available_actions': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                },
            },
            id='Invalid token',
        ),
        pytest.param(
            None,
            MO_TICKET_INFO_TEMPLATE,
            500,
            {
                'code': 'unable_to_check',
                'message': '',
                'details': {
                    'available_actions': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                },
            },
            id='Invalid ticket info',
        ),
        pytest.param(
            MO_TOKENS_TEMPLATE,
            MO_TICKET_INFO_TEMPLATE,
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '',
                'date_end': '',
            },
            id='Valid ticket',
        ),
        pytest.param(
            MO_TOKENS_TEMPLATE,
            {**MO_TICKET_INFO_TEMPLATE, **{'valid': 0}},
            200,
            {
                'is_valid': False,
                'available_actions': ['cancel_ride', 'retry_check'],
            },
            id='Invalid ticket',
        ),
    ],
)
async def test_check_digital_pass_dit_mo(
        taxi_driver_order_misc,
        dit_mo,
        driver_trackstory,
        token,
        ticket_info,
        code,
        expected_output,
):
    dit_mo.set_tokens(token)
    dit_mo.set_ticket_info(ticket_info)
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit', 'dit_mo'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.now('2020-04-25T11:30:00+0300')
@pytest.mark.parametrize(
    'dit_ticket_info,dit_mo_ticket_info,code,expected_output',
    [
        pytest.param(
            None,
            None,
            500,
            {
                'code': 'unable_to_check',
                'message': '',
                'details': {
                    'available_actions': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                },
            },
            id='Invalid ticket info',
        ),
        pytest.param(
            {'result': TICKET_INFO_TEMPLATE},
            None,
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '2020-04-21T00:00:00.000000Z',
                'date_end': '2020-05-01T00:00:00.000000Z',
            },
            id='Valid ticket',
        ),
        pytest.param(
            {'result': False},
            MO_TICKET_INFO_TEMPLATE,
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '',
                'date_end': '',
            },
            id='dit_mo valid ticket',
        ),
    ],
)
async def test_check_digital_pass_both(
        taxi_driver_order_misc,
        dit_efp,
        dit_mo,
        driver_trackstory,
        dit_ticket_info,
        dit_mo_ticket_info,
        code,
        expected_output,
):
    dit_efp.set_ticket_info(dit_ticket_info)
    dit_mo.set_ticket_info(dit_mo_ticket_info)

    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit', 'dit_mo'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.now('2020-04-21T00:00:01+0300')
@pytest.mark.parametrize(
    'token,ticket_info,code,expected_output',
    [
        (
            TOKEN_TEMPLATE,
            {'result': TICKET_INFO_TEMPLATE},
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '2020-04-21T00:00:00.000000Z',
                'date_end': '2020-05-01T00:00:00.000000Z',
            },
        ),
    ],
)
async def test_check_start_borderline_case(
        taxi_driver_order_misc,
        dit_efp,
        driver_trackstory,
        token,
        ticket_info,
        code,
        expected_output,
):
    dit_efp.set_token(token)
    dit_efp.set_ticket_info(ticket_info)
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.now('2020-04-30T23:59:59+0300')
@pytest.mark.parametrize(
    'token,ticket_info,code,expected_output',
    [
        (
            TOKEN_TEMPLATE,
            {'result': TICKET_INFO_TEMPLATE},
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '2020-04-21T00:00:00.000000Z',
                'date_end': '2020-05-01T00:00:00.000000Z',
            },
        ),
    ],
)
async def test_check_end_borderline_case(
        taxi_driver_order_misc,
        dit_efp,
        driver_trackstory,
        token,
        ticket_info,
        code,
        expected_output,
):
    dit_efp.set_token(token)
    dit_efp.set_ticket_info(ticket_info)
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'title': 'For everyone',
            'value': {
                'providers': ['dit_mo_gos'],
                'available_actions': {
                    'valid': ['continue_ride'],
                    'invalid': ['cancel_ride', 'retry_check'],
                    'unable_to_check': [
                        'cancel_ride',
                        'continue_ride',
                        'retry_check',
                    ],
                    'unsupported_geoarea': ['continue_ride'],
                },
            },
        },
    ],
)
@pytest.mark.parametrize(
    'token,token_format,formatted_token,code,expected_output',
    [
        pytest.param(
            'SOME-DATA-FROM-USER',
            '-',
            'SOMEDATAFROMUSER',
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '',
                'date_end': '',
            },
            id='Replace dash',
        ),
        pytest.param(
            'http://some-host/some-handler/?id=SOME-DATA-FROM-USER',
            r'http:\/\/some-host\/some-handler\/\?id=',
            'SOME-DATA-FROM-USER',
            200,
            {
                'is_valid': True,
                'available_actions': ['continue_ride'],
                'date_start': '',
                'date_end': '',
            },
            id='Replace link',
        ),
    ],
)
async def test_check_token_formatter(
        taxi_driver_order_misc,
        driver_trackstory,
        taxi_config,
        mockserver,
        token,
        token_format,
        formatted_token,
        code,
        expected_output,
):
    taxi_config.set_values(
        {
            'DRIVER_ORDER_MISC_PROVIDER_TOKEN_FORMAT': {
                'dit_mo_gos': token_format,
            },
        },
    )

    @mockserver.json_handler(
        '/dit-mo-gos/api/qr/v2/getMos/{}'.format(formatted_token),
    )
    def _get_mos(request):
        return {'valid': 1, 'type': 1, 'parameters': []}

    response = await taxi_driver_order_misc.post(
        ENDPOINT, headers=AUTHORIZED_HEADERS, json={'pass': token},
    )
    assert response.status_code == code
    assert response.json() == expected_output


@pytest.mark.experiments3(
    name='digital_pass_check_settings',
    consumers=['driver_order_misc/check_digital_pass'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {'predicate': {'type': 'false'}, 'title': 'For everyone', 'value': {}},
    ],
)
async def test_check_missed_experiment(
        taxi_driver_order_misc, driver_trackstory,
):
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'unsupported_geoarea',
        'message': '',
        'details': {'available_actions': ['continue_ride']},
    }


async def test_check_disabled_experiment(
        taxi_driver_order_misc, driver_trackstory,
):
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'pass': 'SOME-DATA-FROM-USER'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'unsupported_geoarea',
        'message': '',
        'details': {'available_actions': ['continue_ride']},
    }
