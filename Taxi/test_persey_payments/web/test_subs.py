import pytest


PERSEY_PAYMENTS_SUBS_BASE = {
    'from_string': 'Помощь рядом &lt;donation@yandex-team.ru&gt;',
    'default_subs_period': '1M',
    'default_subs_retry_charging_limit': '7D',
    'default_subs_retry_charging_delay': '1D',
    'personal_account_link': 'link_stub',
    'show_started_duration': 1800,
}


@pytest.mark.now('2020-05-01T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(PERSEY_PAYMENTS_SUBS=PERSEY_PAYMENTS_SUBS_BASE)
@pytest.mark.parametrize(
    [
        'request_update',
        'send_new_subs',
        'exp_period',
        'exp_retry_charging_limit',
        'exp_retry_charging_delay',
        'exp_resp_code',
        'exp_reject_newsletter',
        'exp_application',
        'exp_list_response',
    ],
    [
        (
            {'reject_newsletter': True},
            False,
            '1M',
            '7D',
            '1D',
            200,
            True,
            None,
            'expected_list_response_empty.json',
        ),
        (
            {'reject_newsletter': True},
            True,
            '1M',
            '7D',
            '1D',
            200,
            True,
            None,
            'expected_list_response.json',
        ),
        pytest.param(
            {
                'reject_newsletter': False,
                'subs_settings': {
                    'period': '180S',
                    'retry_charging_limit': '50S',
                    'retry_charging_delay': '5S',
                },
                'application': 'go_android',
            },
            False,
            '180S',
            '50S',
            '5S',
            200,
            False,
            'go_android',
            'expected_list_response_empty.json',
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_SUBS={
                    **PERSEY_PAYMENTS_SUBS_BASE,
                    **{'custom_settings_allowed_uids': ['123']},
                },
            ),
        ),
        pytest.param(
            {
                'reject_newsletter': False,
                'subs_settings': {
                    'period': '180S',
                    'retry_charging_limit': '50S',
                    'retry_charging_delay': '5S',
                },
                'application': 'go_android',
            },
            True,
            '180S',
            '50S',
            '5S',
            200,
            False,
            'go_android',
            'expected_list_response_app.json',
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_SUBS={
                    **PERSEY_PAYMENTS_SUBS_BASE,
                    **{'custom_settings_allowed_uids': ['123']},
                },
            ),
        ),
        (
            {
                'subs_settings': {
                    'period': '180S',
                    'retry_charging_limit': '50S',
                    'retry_charging_delay': '5S',
                },
            },
            False,
            None,
            None,
            None,
            403,
            None,
            None,
            None,
        ),
    ],
)
async def test_subs_simple(
        web_app_client,
        pgsql,
        stq,
        mock_uuid,
        trust_create_basket_success,
        trust_pay_basket_success,
        mockserver,
        load_json,
        request_update,
        send_new_subs,
        exp_period,
        exp_retry_charging_limit,
        exp_retry_charging_delay,
        exp_resp_code,
        exp_reject_newsletter,
        exp_application,
        exp_list_response,
):
    mock_uuid(1)

    @mockserver.json_handler('/trust-payments/v2/products/')
    def mock_products(request):
        assert request.json['subs_renewal_cancel_notify'] == 1
        assert request.json['subs_period'] == exp_period
        assert (
            request.json['subs_retry_charging_limit']
            == exp_retry_charging_limit
        )
        assert (
            request.json['subs_retry_charging_delay']
            == exp_retry_charging_delay
        )

        return {'status': 'success'}

    @mockserver.json_handler('/trust-payments/v2/subscriptions/', prefix=True)
    def mock_subscriptions(request):
        assert (
            request.json['notify_url']
            == '$mockserver/persey-payments/v1/charity/subs/back_url/'
        )

        return {'status': 'success', 'status_code': 'success'}

    create_mock = trust_create_basket_success('create_basket_simple.json')
    pay_mock = trust_pay_basket_success()

    request = {
        'fund_id': 'some_fund',
        'sum': '777.777',
        'return_path': 'some_return_path',
        'user': {'email': 'some_email'},
    }
    request.update(request_update)
    headers = {'X-Yandex-UID': '123'}
    response = await web_app_client.post(
        '/payments/v1/charity/subs/start', json=request, headers=headers,
    )
    assert response.status == exp_resp_code

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT amount, period, retry_charging_limit, retry_charging_delay '
        'FROM persey_payments.subs_product',
    )

    if exp_resp_code != 200:
        assert mock_subscriptions.times_called == 0
        assert mock_products.times_called == 0
        assert create_mock.times_called == 0
        assert pay_mock.times_called == 0
        assert stq.persey_payments_donation.times_called == 0
        assert list(cursor) == []

        return

    assert await response.json() == load_json('expected_response.json')
    assert mock_subscriptions.times_called == 1
    assert mock_products.times_called == 1
    assert create_mock.times_called == 1
    assert pay_mock.times_called == 1
    assert stq.persey_payments_donation.times_called == 0
    assert list(cursor) == [
        (
            '777.777',
            exp_period,
            exp_retry_charging_limit,
            exp_retry_charging_delay,
        ),
    ]

    cursor.execute(
        'SELECT reject_newsletter, application FROM persey_payments.donation',
    )
    assert list(cursor) == [(exp_reject_newsletter, exp_application)]

    list_params = {}
    if send_new_subs:
        list_params = {'new_subs': '2104653bdac343e39ac57869d0bd738d'}

    response = await web_app_client.get(
        '/payments/v1/charity/subs/list', headers=headers, params=list_params,
    )
    assert response.status == 200
    assert await response.json() == load_json(exp_list_response)

    request = {'subs_id': '2104653bdac343e39ac57869d0bd738d'}
    response = await web_app_client.post(
        '/payments/v1/charity/subs/cancel', json=request, headers=headers,
    )
    assert response.status == 400
    expected_status = 'promoted' if send_new_subs else 'started'
    assert await response.json() == {
        'code': 'WRONG_STATUS',
        'message': f'Subscription is in wrong status: {expected_status}',
    }


@pytest.mark.now('2020-05-01T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    ['share_trust_products'],
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_SUBS=PERSEY_PAYMENTS_SUBS_BASE,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_SUBS={
                    **PERSEY_PAYMENTS_SUBS_BASE,
                    **{'share_trust_products': False},
                },
            ),
        ),
    ],
)
async def test_share_trust_products(
        web_app_client,
        pgsql,
        stq,
        mock_uuid,
        trust_create_basket_success,
        trust_pay_basket_success,
        mockserver,
        load_json,
        share_trust_products,
):
    mock_uuid(1)

    @mockserver.json_handler('/trust-payments/v2/products/')
    def mock_products(request):
        return {'status': 'success'}

    @mockserver.json_handler('/trust-payments/v2/subscriptions/', prefix=True)
    def mock_subscriptions(request):
        return {'status': 'success', 'status_code': 'success'}

    trust_create_basket_success('create_basket_simple.json')
    trust_pay_basket_success()

    request = {
        'fund_id': 'some_fund',
        'sum': '777.777',
        'return_path': 'some_return_path',
        'user': {'email': 'some_email'},
    }
    headers = {'X-Yandex-UID': '123'}
    expected_sub_products = [
        ('777.777', '1M', '7D', '1D', share_trust_products),
    ]
    db = pgsql['persey_payments']
    cursor = db.cursor()

    async def _start_subs():
        response = await web_app_client.post(
            '/payments/v1/charity/subs/start', json=request, headers=headers,
        )
        assert response.status == 200
        cursor.execute(
            'SELECT amount, period, retry_charging_limit, '
            'retry_charging_delay, shared '
            'FROM persey_payments.subs_product',
        )
        got_sub_products = list(cursor)
        assert got_sub_products == expected_sub_products

    expected_products_times_called = 1
    await _start_subs()
    assert mock_products.times_called == expected_products_times_called
    assert mock_subscriptions.times_called == 1

    if not share_trust_products:
        expected_sub_products *= 2
        expected_products_times_called += 1

    await _start_subs()
    assert mock_products.times_called == expected_products_times_called
    assert mock_subscriptions.times_called == 2


async def test_no_user_email(taxi_persey_payments_web):
    request = {
        'fund_id': 'some_fund',
        'sum': '777.777',
        'return_path': 'some_return_path',
    }
    headers = {'X-Yandex-UID': '123'}
    response = await taxi_persey_payments_web.post(
        '/payments/v1/charity/subs/start', json=request, headers=headers,
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'NO_EMAIL',
        'message': 'user.email is required',
    }
