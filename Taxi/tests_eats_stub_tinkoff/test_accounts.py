import datetime
import math

import pytz

HEADERS = {'Authorization': 'Bearer TestToken'}


async def test_accounts_get_200(taxi_eats_stub_tinkoff, create_account):
    account1 = '123'
    account2 = '456'
    create_account(number=account1)
    create_account(number=account2)

    response = await taxi_eats_stub_tinkoff.get(
        '/api/v3/bank-accounts', headers=HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]['accountNumber'] == account1
    assert body[1]['accountNumber'] == account2


async def test_accounts_get_401(taxi_eats_stub_tinkoff, create_account):
    account1 = '123'
    account2 = '456'
    create_account(number=account1)
    create_account(number=account2)

    response = await taxi_eats_stub_tinkoff.get('/api/v3/bank-accounts')

    assert response.status_code == 401


async def test_accounts_post_200(taxi_eats_stub_tinkoff, get_account):
    account_number = '123'

    response = await taxi_eats_stub_tinkoff.post(
        '/api/v3/bank-accounts',
        headers=HEADERS,
        json={
            'account': {
                'accountNumber': account_number,
                'name': 'Account Name',
                'currency': 'RUB',
                'bankBik': '12345678',
                'accountType': 'Current',
                'activationDate': (
                    datetime.datetime.utcnow()
                    .replace(tzinfo=pytz.UTC)
                    .strftime('%Y-%m-%d')
                ),
                'balance': {
                    'otb': 10000,
                    'authorized': 0,
                    'pendingPayments': 0,
                    'pendingRequisitions': 0,
                },
            },
        },
    )

    assert response.status_code == 200
    account = get_account(account_number)
    assert account
    assert account['number'] == account_number


async def test_accounts_get_balance_200(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    balance = 123456.78
    create_account(number=account_number, balance=balance)

    response = await taxi_eats_stub_tinkoff.get(
        '/internal/api/v1/account/balance',
        headers=HEADERS,
        params={'account_number': account_number},
    )

    assert response.status_code == 200
    body = response.json()
    assert 'balance' in body
    assert math.isclose(body['balance'], balance, abs_tol=0.000001)


async def test_accounts_get_balance_401(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    balance = 123456.78
    create_account(number=account_number, balance=balance)

    response = await taxi_eats_stub_tinkoff.get(
        '/internal/api/v1/account/balance',
        params={'account_number': account_number},
    )

    assert response.status_code == 401


async def test_accounts_get_balance_404(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    balance = 123456.78
    create_account(number=account_number, balance=balance)

    response = await taxi_eats_stub_tinkoff.get(
        '/internal/api/v1/account/balance',
        headers=HEADERS,
        params={'account_number': '456'},
    )

    assert response.status_code == 404


async def test_accounts_set_balance_200(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    old_balance = 123456.78
    create_account(number=account_number, balance=old_balance)

    new_balance = 876543.21

    response = await taxi_eats_stub_tinkoff.post(
        '/internal/api/v1/account/balance',
        headers=HEADERS,
        json={'account_number': account_number, 'balance': new_balance},
    )

    assert response.status_code == 200

    response = await taxi_eats_stub_tinkoff.get(
        '/internal/api/v1/account/balance',
        headers=HEADERS,
        params={'account_number': account_number},
    )

    assert response.status_code == 200
    assert math.isclose(
        response.json()['balance'], new_balance, abs_tol=0.000001,
    )


async def test_accounts_set_balance_401(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    old_balance = 123456.78
    create_account(number=account_number, balance=old_balance)

    new_balance = 876543.21

    response = await taxi_eats_stub_tinkoff.post(
        '/internal/api/v1/account/balance',
        json={'account_number': account_number, 'balance': new_balance},
    )

    assert response.status_code == 401


async def test_accounts_set_balance_404(
        taxi_eats_stub_tinkoff, create_account,
):
    account_number = '123'
    old_balance = 123456.78
    create_account(number=account_number, balance=old_balance)

    new_balance = 876543.21

    response = await taxi_eats_stub_tinkoff.post(
        '/internal/api/v1/account/balance',
        headers=HEADERS,
        json={'account_number': '456', 'balance': new_balance},
    )

    assert response.status_code == 404
