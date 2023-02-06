import pytest


@pytest.mark.parametrize(
    'tariff_type, data, expected_status, expected_response',
    [
        # Wrong request
        ('support-taxi', {}, 400, None),
        # Payment not found
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-02-01',
                    'stop_date': '2020-02-16',
                },
            },
            409,
            None,
        ),
        # Country not configured
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'not_configured_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            409,
            None,
        ),
        # All OK
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            200,
            {
                'data': {
                    'payment': {
                        'payment_draft_id': 'uuid',
                        'calculation_rule_id': 'some_rule_id',
                        'country': 'rus',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                    },
                },
            },
        ),
    ],
)
async def test_check(
        web_app_client, tariff_type, data, expected_status, expected_response,
):
    response = await web_app_client.post(
        '/v1/payments/{}/check'.format(tariff_type), json=data,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_status != 200:
        return

    assert content == expected_response


@pytest.mark.parametrize(
    [
        'tariff_type',
        'payment_draft_id',
        'expected_status',
        'expected_response',
    ],
    [
        (
            'support-taxi',
            'rus_draft_id',
            200,
            {
                'payment_draft': {
                    'payment_draft_id': 'rus_draft_id',
                    'approvals_id': 123,
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'status': 'need_approval',
                    'stop_date': '2020-01-16',
                    'tariff_type': 'support-taxi',
                },
                'payment': {
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                    'country': 'rus',
                    'logins': [
                        {
                            'login': 'ivanov',
                            'daytime_cost': 10.0,
                            'night_cost': 5.0,
                            'holidays_daytime_cost': 8.0,
                            'holidays_night_cost': 1.0,
                            'benefits': 11.0,
                            'extra_costs': [
                                {
                                    'source': 'tracker',
                                    'daytime_bo': 10.0,
                                    'night_bo': 15.0,
                                    'holidays_daytime_bo': 5.0,
                                    'holidays_night_bo': 0.0,
                                    'total_bo': 20.0,
                                },
                            ],
                            'correction': {
                                'intermediate': {
                                    'daytime_bo': 3.0,
                                    'night_bo': 3.0,
                                    'holidays_daytime_bo': 3.0,
                                    'holidays_night_bo': 3.0,
                                },
                                'final': {'daytime_bo': 2.0, 'night_bo': 2.0},
                            },
                        },
                        {
                            'login': 'petrov',
                            'daytime_cost': 15.0,
                            'night_cost': 7.0,
                            'holidays_daytime_cost': 10.0,
                            'holidays_night_cost': 0.0,
                            'benefits': 16.0,
                            'extra_costs': [],
                        },
                    ],
                },
            },
        ),
        ('support-taxi', 'missing_draft_id', 404, None),
        ('call-taxi', 'rus_draft_id', 404, None),
    ],
)
async def test_get_payment(
        web_app_client,
        tariff_type,
        payment_draft_id,
        expected_status,
        expected_response,
):
    response = await web_app_client.get(
        '/v1/payment/{}/{}'.format(tariff_type, payment_draft_id),
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    [
        'tariff_type',
        'payment_draft_id',
        'expected_status',
        'expected_response',
    ],
    [
        (
            'support-taxi',
            'rus_draft_id',
            200,
            'login,daytime_cost,night_cost,holidays_daytime_cost,'
            'holidays_night_cost,benefits\r\n'
            'ivanov,10.0,5.0,8.0,1.0,11.0\r\n'
            'petrov,15.0,7.0,10.0,0.0,16.0\r\n',
        ),
        ('support-taxi', 'missing_draft_id', 404, None),
        ('call-taxi', 'rus_draft_id', 404, None),
    ],
)
async def test_get_csv(
        web_app_client,
        tariff_type,
        payment_draft_id,
        expected_status,
        expected_response,
):
    response = await web_app_client.get(
        '/v1/payment/{}/{}/csv'.format(tariff_type, payment_draft_id),
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    response_data = await response.text()
    assert response_data == expected_response


@pytest.mark.parametrize(
    ['data', 'expected_response'],
    [
        (
            {},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        (
            {'tariff_type': 'support-taxi'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        ({'tariff_type': 'call-taxi'}, {'payment_drafts': []}),
        (
            {'calculation_rule_id': 'some_rule_id'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        ({'calculation_rule_id': 'missing_rule_id'}, {'payment_drafts': []}),
        (
            {'date': '2020-01-10'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        ({'date': '2020-01-20'}, {'payment_drafts': []}),
        (
            {'date': '2020-01-10'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        ({'date': '2020-01-20'}, {'payment_drafts': []}),
        (
            {'country': 'rus'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        (
            {'status': 'need_approval'},
            {
                'payment_drafts': [
                    {
                        'payment_draft_id': 'blr_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'blr',
                        'status': 'need_approval',
                        'approvals_id': 456,
                    },
                    {
                        'payment_draft_id': 'rus_draft_id',
                        'tariff_type': 'support-taxi',
                        'calculation_rule_id': 'some_rule_id',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                        'country': 'rus',
                        'status': 'need_approval',
                        'approvals_id': 123,
                    },
                ],
            },
        ),
        ({'status': 'failed'}, {'payment_drafts': []}),
    ],
)
async def test_payments_list(web_app_client, data, expected_response):
    response = await web_app_client.post('/v1/payments/list', json=data)
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response
