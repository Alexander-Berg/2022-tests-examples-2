import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.parametrize(
    [
        'headers',
        'user_data',
        'expected_uid',
        'expected_create_basket',
        'expected_name',
        'expected_email',
        'expected_reject_newsletter',
        'expected_application',
    ],
    [
        (
            {},
            {
                'user': {'name': 'username', 'email': 'useremail'},
                'reject_newsletter': True,
            },
            None,
            'create_basket_simple.json',
            'username',
            'useremail',
            True,
            None,
        ),
        (
            {'X-Yandex-UID': '123'},
            {
                'user': {'name': 'username', 'email': 'useremail'},
                'reject_newsletter': False,
                'application': 'go_ios',
            },
            '123',
            'create_basket_uid.json',
            'username',
            'useremail',
            False,
            'go_ios',
        ),
        pytest.param(
            {},
            {'user': {'name': 'username', 'email': 'useremail'}},
            None,
            'create_basket_timeout.json',
            'username',
            'useremail',
            False,
            None,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_FUNDS={
                    'operator_uid': '1',
                    'funds': [],
                    'payment_timeout': 123,
                },
            ),
        ),
        (
            {},
            {'user': {'email': 'useremail'}},
            None,
            'create_basket_no_user_name.json',
            None,
            'useremail',
            False,
            None,
        ),
        (
            {},
            {},
            None,
            'create_basket_no_user_data.json',
            None,
            None,
            False,
            None,
        ),
        (
            {},
            {},
            None,
            'create_basket_no_user_data.json',
            None,
            None,
            False,
            None,
        ),
    ],
)
async def test_simple(
        web_app_client,
        stq,
        mock_uuid,
        pgsql,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_pay_basket_success,
        headers,
        user_data,
        expected_uid,
        expected_create_basket,
        expected_name,
        expected_email,
        expected_reject_newsletter,
        expected_application,
):
    mock_uuid(1)

    order_mock = fill_service_orders_success('create_orders_simple.json')
    create_mock = trust_create_basket_success(expected_create_basket)
    pay_mock = trust_pay_basket_success()

    request = {
        'fund_id': 'some_fund',
        'sum': '777.777',
        'return_path': 'some_return_path',
    }
    request.update(user_data)

    response = await web_app_client.post(
        '/payments/v1/charity/start', json=request, headers=headers,
    )

    assert response.status == 200
    assert await response.json() == {'payment_url': 'trust-payment-url'}

    assert order_mock.times_called == 1
    assert create_mock.times_called == 1
    assert pay_mock.times_called == 1

    assert stq.persey_payments_donation.times_called == 1
    call = stq.persey_payments_donation.next_call()
    assert call['args'] == [1, 'create_donation']

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id, purchase_token, status, yandex_uid, sum, '
        'user_name, user_email, reject_newsletter, application '
        'FROM persey_payments.donation',
    )
    rows = list(cursor)
    assert rows == [
        (
            'some_fund',
            'trust-basket-token',
            'started',
            expected_uid,
            '777.777',
            expected_name,
            expected_email,
            expected_reject_newsletter,
            expected_application,
        ),
    ]


async def test_not_found(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/payments/v1/charity/start',
        json={
            'fund_id': 'nonexistent',
            'sum': '777.777',
            'user': {'name': 'username', 'email': 'useremail'},
            'return_path': 'some_return_path',
        },
        headers={},
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'FUND_NOT_FOUND',
        'message': 'No fund_id=nonexistent in db',
    }
