import pytest

EXTERNAL_ID = '4552995ef815c9bba2dae61d5e0f643a'
FIELD_DATA = 'data'
FIELD_TICKETS = 'tickets'
FIELD_ENDPOINT = 'endpoint'
FIELD_CONSUMER = 'consumer'
FIELD_STATUS_CODE = 'status_code'
REQUESTS_FILE = 'requests.json'
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name, expected_stq_calls_count',
    [
        ('valid', 'send_to_infranaim_success', 2),
        ('valid', 'bulk_salesforce_test_consumer', 4),
        ('valid', 'bulk_either_test_consumer', 6),
        ('valid', 'phone_without_plus', 4),
    ],
)
async def test_tickets_create_simple_requests(
        request_tickets_bulk_create,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        stq_mock,
        request_type,
        request_name,
        expected_stq_calls_count,
):
    # arrange
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')[request_type]
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]

    # act
    response_body = await request_tickets_bulk_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_CONSUMER],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body

    tickets_quantity = len(request_data[FIELD_DATA][FIELD_TICKETS])
    added_tickets = sum(response_body['details']['ticket_statuses'])
    assert added_tickets == tickets_quantity

    assert stq_mock.times_called == expected_stq_calls_count
    assert response_body['details']['external_ids']


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name',
    [('invalid', 'bulk_limit_exceeded'), ('invalid', 'phone_invalid')],
)
async def test_tickets_create_simple_invalid_requests(
        request_tickets_bulk_create,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        request_type,
        request_name,
        stq_mock,
):
    # arrange
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')[request_type]
    hiring_rate_accounting_update_mockserver(
        response_update['bulk_limit_exceeded_test_consumer'],
    )
    hiring_rate_accounting_calculate_mockserver(
        response_calculate['bulk_limit_exceeded_test_consumer'],
    )

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]

    # act
    response_body = await request_tickets_bulk_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_CONSUMER],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == load_json(
        'response_with_too_many_requests_error.json',
    )


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'use_external_id, expected_external_ids',
    [
        (True, [EXTERNAL_ID, EXTERNAL_ID]),
        (False, [X_DELIVERY_ID, X_DELIVERY_ID]),
    ],
)
async def test_tickets_create_check_id(
        request_tickets_bulk_create,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        use_external_id,
        taxi_config,
        expected_external_ids,
):
    # arrange
    taxi_config.set_values(
        {
            'HIRING_API_USE_EXTERNAL_ID_BY_ENDPOINTS': {
                '__default__': {'enabled': use_external_id},
                'endpoints': [],
            },
        },
    )

    response_calculate = load_json('response_calculate.json')['valid']
    response_update = load_json('response_update.json')['valid']
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)['valid']['phone_without_plus']

    # act
    response_body = await request_tickets_bulk_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_CONSUMER],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {
            'external_ids': expected_external_ids,
            'ticket_statuses': [True, True],
        },
    }


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=False)
async def test_tickets_bulk_create_with_disabled_limit_is_error(
        request_tickets_bulk_create, load_json,
):
    # arrange
    request_data = load_json(REQUESTS_FILE)['valid']['phone_without_plus']

    # act
    response_body = await request_tickets_bulk_create(
        request=request_data[FIELD_DATA],
        endpoint=request_data[FIELD_ENDPOINT],
        consumer=request_data[FIELD_CONSUMER],
        status_code=400,
    )

    # assert
    assert response_body == load_json(
        'response_with_disabled_endpoint_error.json',
    )


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
async def test_tickets_bulk_create_with_unable_static_request_is_error(
        request_tickets_bulk_create,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        taxi_config,
):
    # arrange
    accounting_update_mock = hiring_rate_accounting_update_mockserver(
        load_json('response_update.json')['invalid_with_400'],
    )
    accounting_calculate_mock = hiring_rate_accounting_calculate_mockserver(
        load_json('response_calculate.json')['valid'],
    )
    request_data = load_json(REQUESTS_FILE)['valid']['phone_without_plus']

    # act
    response_body = await request_tickets_bulk_create(
        request=request_data[FIELD_DATA],
        endpoint=request_data[FIELD_ENDPOINT],
        consumer=request_data[FIELD_CONSUMER],
        status_code=400,
    )

    # assert
    assert response_body == load_json(
        'response_with_unique_violation_error.json',
    )

    assert accounting_update_mock.times_called == 1
    query_call = accounting_update_mock.next_call()
    request = query_call['request']
    assert request.json == load_json('accounting_update_request.json')

    assert accounting_calculate_mock.times_called == 1
    query_call = accounting_calculate_mock.next_call()
    request = query_call['request']
    assert request.json == load_json('accounting_calculate_request.json')
