import pytest


@pytest.mark.now('2020-09-02T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'test_data_json', ['valid_request.json', 'rule_not_found.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_open_shift',
    tariff_settings='for_test_open_shift',
)
async def test_open_shift_for_provided_subscription(
        db,
        billing_subventions_client,
        request_headers,
        patch,
        stq_client_patched,
        load_json,
        test_data_json,
):
    @patch('random.randint')
    def _randint(left, right):
        return 2

    actual_shift_ended = []

    @patch('taxi.billing.clients.billing_docs.BillingDocsApiClient.create')
    async def _create(data, log_extra=None):
        nonlocal actual_shift_ended
        actual_shift_ended.append(data)
        return {'doc_id': 2, 'process_at': '2100-01-01T00:00:00+00:00'}

    test_data = load_json(test_data_json)

    request = test_data['request']
    response = await billing_subventions_client.post(
        '/v1/shifts/open', json=request, headers=request_headers,
    )

    expected_response = test_data['expected_response']
    assert await response.json() == expected_response

    expected_shift_ended = test_data['expected_shift_ended']
    assert actual_shift_ended == expected_shift_ended


@pytest.mark.now('2020-09-02T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'test_data_json',
    [
        'valid_request.json',
        'subscription_not_found.json',
        'not_driver_fix_subscription.json',
    ],
)
@pytest.mark.filldb(
    subvention_rules='for_test_open_shift',
    tariff_settings='for_test_open_shift',
)
async def test_open_shift_for_unknown_subscription(
        db,
        billing_subventions_client,
        request_headers,
        patch,
        stq_client_patched,
        load_json,
        test_data_json,
):
    test_data = load_json(test_data_json)

    @patch('random.randint')
    def _randint(left, right):
        return 2

    @patch('taxi.billing.clients.billing_docs.BillingDocsApiClient.search')
    async def _search(query, log_extra=None):
        return test_data['subscription']

    actual_shift_ended = []

    @patch('taxi.billing.clients.billing_docs.BillingDocsApiClient.create')
    async def _create(data: dict, log_extra=None) -> dict:
        nonlocal actual_shift_ended
        actual_shift_ended.append(data)
        return {'doc_id': 2, 'process_at': '2120-01-01T00:00:00+00:00'}

    request = test_data['request']
    response = await billing_subventions_client.post(
        '/v1/shifts/open', json=request, headers=request_headers,
    )
    expected_response = test_data['expected_response']
    assert await response.json() == expected_response

    expected_shift_ended = test_data['expected_shift_ended']
    assert actual_shift_ended == expected_shift_ended


@pytest.mark.now('2020-09-02T00:00:00.000000+00:00')
@pytest.mark.parametrize('test_data_json', ['old_as_of.json'])
@pytest.mark.config(BILLING_SUBVENTIONS_SHIFT_OPEN_MAX_REQUEST_AGE_HRS=1)
async def test_bad_requests(
        test_data_json,
        *,
        billing_subventions_client,
        request_headers,
        load_json,
):
    test_data = load_json(test_data_json)
    request = test_data['request']
    response = await billing_subventions_client.post(
        '/v1/shifts/open', json=request, headers=request_headers,
    )
    expected_response = test_data['expected_response']
    assert await response.json() == expected_response
