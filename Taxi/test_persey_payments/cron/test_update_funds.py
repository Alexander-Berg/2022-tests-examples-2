import decimal

import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_FUNDS={
        'operator_uid': 'some_operator',
        'funds': [
            {
                'fund_id': 'new_fund',
                'name': 'Имя фонда',
                'balance_client_id': 'some_client',
                'offer_link': 'some_link',
                'exclude_from_sampling': True,
                'applepay': {
                    'merchant_ids': ['some_merchant_id'],
                    'country_code': 'ru',
                    'item_title_tanker_key': 'new_tanker_key',
                },
            },
            {
                'fund_id': 'updated_fund',
                'name': 'Новое имя',
                'balance_client_id': 'nonexistent',
                'offer_link': 'new_offer_link',
                'exclude_from_sampling': True,
                'applepay': {
                    'merchant_ids': ['some_merchant_id'],
                    'country_code': 'ru',
                    'item_title_tanker_key': 'new_tanker_key',
                },
            },
        ],
    },
)
async def test_simple(
        cron_runner,
        pgsql,
        trust_create_partner_success,
        trust_create_product_success,
        mock_balance,
):
    partner_mock = trust_create_partner_success('create_partner_simple.json')
    product_mock = trust_create_product_success('create_product_simple.json')
    balance_mock = mock_balance(
        {
            'Balance2.FindClient': 'find_client_simple.xml',
            'Balance2.ListClientPassports': 'list_client_passports_simple.xml',
        },
    )

    await cron_runner.update_funds()

    assert partner_mock.times_called == 1
    assert product_mock.times_called == 1
    assert balance_mock.times_called == 2

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id, name, offer_link, is_hidden, balance_client_id, '
        'trust_partner_id, trust_product_id, available_amount, '
        'exclude_from_sampling, applepay_country_code, applepay_item_title '
        'FROM persey_payments.fund ORDER BY fund_id',
    )
    rows = list(cursor)
    assert rows == [
        (
            'deleted_fund',
            'Имя удаленного фонда',
            'http://fund.com',
            True,
            'client1',
            'partner_id1',
            'product_id1',
            decimal.Decimal(0),
            False,
            None,
            None,
        ),
        (
            'new_fund',
            'Имя фонда',
            'some_link',
            False,
            'some_client',
            'some_partner_id',
            'new_fund_persey_charity',
            decimal.Decimal(0),
            True,
            'ru',
            'new_tanker_key',
        ),
        (
            'updated_fund',
            'Новое имя',
            'new_offer_link',
            False,
            'client2',
            'partner_id2',
            'product_id2',
            decimal.Decimal(0),
            True,
            'ru',
            'new_tanker_key',
        ),
    ]


@pytest.mark.pgsql('persey_payments', files=['available_amount.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_FUNDS={
        'operator_uid': 'some_operator',
        'funds': [
            {
                'fund_id': 'new_fund',
                'name': 'Имя фонда',
                'balance_client_id': 'some_client',
                'offer_link': 'some_link',
                'available_amount': [
                    {'time': '2019-01-11T22:49:56+0300', 'amount': '50'},
                    {'time': '2019-01-11T23:49:56+0300', 'amount': '500'},
                    {'time': '2019-01-12T23:49:56+0300', 'amount': '890'},
                ],
            },
            {
                'fund_id': 'invalid_fund',
                'name': 'Имя фонда',
                'balance_client_id': 'some_client',
                'offer_link': 'some_link',
                'available_amount': [
                    {'time': '2019-01-11T22:49:56+0300', 'amount': '123'},
                ],
            },
            {
                'fund_id': 'updated_fund',
                'name': 'Новое имя',
                'balance_client_id': 'nonexistent',
                'offer_link': 'new_offer_link',
                'available_amount': [
                    {'time': '2019-01-11T22:49:56+0300', 'amount': '50'},
                    {'time': '2019-01-11T23:49:56+0300', 'amount': '500'},
                    {'time': '2019-01-12T23:49:56+0300', 'amount': '505'},
                ],
            },
        ],
    },
)
async def test_available_amount(
        cron_runner,
        pgsql,
        trust_create_partner_success,
        trust_create_product_success,
        mock_balance,
):
    partner_mock = trust_create_partner_success('create_partner_simple.json')
    product_mock = trust_create_product_success('create_product_simple.json')
    balance_mock = mock_balance(
        {
            'Balance2.FindClient': 'find_client_simple.xml',
            'Balance2.ListClientPassports': 'list_client_passports_simple.xml',
        },
    )

    await cron_runner.update_funds()

    assert partner_mock.times_called == 1
    assert product_mock.times_called == 1
    assert balance_mock.times_called == 2

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id, name, offer_link, is_hidden, balance_client_id, '
        'trust_partner_id, trust_product_id, available_amount, '
        'exclude_from_sampling FROM persey_payments.fund ORDER BY fund_id',
    )
    rows = list(cursor)
    assert rows == [
        (
            'invalid_fund',
            'Имя невалидного фонда',
            'http://fund.com',
            False,
            'client1',
            'partner_id1',
            'product_id1',
            decimal.Decimal(777),
            False,
        ),
        (
            'new_fund',
            'Имя фонда',
            'some_link',
            False,
            'some_client',
            'some_partner_id',
            'new_fund_persey_charity',
            decimal.Decimal(890),
            False,
        ),
        (
            'updated_fund',
            'Новое имя',
            'new_offer_link',
            False,
            'client2',
            'partner_id2',
            'product_id2',
            decimal.Decimal(505),
            False,
        ),
    ]
