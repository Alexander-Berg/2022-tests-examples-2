import pytest


from tests_debt_collector import builders


def cursor(debtor, debt_id):
    return {'debtor': debtor, 'debt_id': debt_id}


@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
@pytest.mark.parametrize(
    'query, response_json',
    [
        # one row
        (
            {
                'debtors': ['yandex/uid/some_uid'],
                'service': 'eats',
                'limit': 2,
            },
            {
                'debts': [
                    builders.debt_info(
                        'with_two_debtors_id',
                        'with_two_debtors_invoice_id',
                        ['taxi/phone_id/some_phone_id', 'yandex/uid/some_uid'],
                    ),
                ],
                'next_cursor': cursor(
                    'yandex/uid/some_uid', 'with_two_debtors_id',
                ),
            },
        ),
        # two rows
        (
            {
                'debtors': ['taxi/phone_id/some_phone_id'],
                'service': 'eats',
                'limit': 2,
            },
            {
                'debts': [
                    builders.debt_info(
                        'first_with_one_debtor_id',
                        'first_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                    builders.debt_info(
                        'second_with_one_debtor_id',
                        'second_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                ],
                'next_cursor': cursor(
                    'taxi/phone_id/some_phone_id', 'second_with_one_debtor_id',
                ),
            },
        ),
        # limit in effect
        (
            {
                'debtors': ['taxi/phone_id/some_phone_id'],
                'service': 'eats',
                'limit': 1,
            },
            {
                'debts': [
                    builders.debt_info(
                        'first_with_one_debtor_id',
                        'first_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                ],
                'next_cursor': cursor(
                    'taxi/phone_id/some_phone_id', 'first_with_one_debtor_id',
                ),
            },
        ),
        # cursor in effect
        (
            {
                'debtors': ['taxi/phone_id/some_phone_id'],
                'service': 'eats',
                'limit': 1,
                'cursor': cursor(
                    'taxi/phone_id/some_phone_id', 'first_with_one_debtor_id',
                ),
            },
            {
                'debts': [
                    builders.debt_info(
                        'second_with_one_debtor_id',
                        'second_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                ],
                'next_cursor': cursor(
                    'taxi/phone_id/some_phone_id', 'second_with_one_debtor_id',
                ),
            },
        ),
        # nothing found
        (
            {
                'debtors': ['taxi/phone_id/unknown_phone_id'],
                'service': 'eats',
                'limit': 10,
            },
            {'debts': []},
        ),
        # several debtors
        (
            {
                'debtors': [
                    'taxi/phone_id/some_phone_id',
                    'yandex/uid/some_uid',
                ],
                'service': 'eats',
                'limit': 10,
            },
            {
                'debts': [
                    builders.debt_info(
                        'first_with_one_debtor_id',
                        'first_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                    builders.debt_info(
                        'second_with_one_debtor_id',
                        'second_with_one_debtor_invoice_id',
                        ['taxi/phone_id/some_phone_id'],
                    ),
                    builders.debt_info(
                        'with_two_debtors_id',
                        'with_two_debtors_invoice_id',
                        ['taxi/phone_id/some_phone_id', 'yandex/uid/some_uid'],
                    ),
                    builders.debt_info(
                        'with_two_debtors_id',
                        'with_two_debtors_invoice_id',
                        ['taxi/phone_id/some_phone_id', 'yandex/uid/some_uid'],
                    ),
                ],
                'next_cursor': cursor(
                    'yandex/uid/some_uid', 'with_two_debtors_id',
                ),
            },
        ),
        # nothing found with cursor
        (
            {
                'debtors': [
                    'taxi/phone_id/some_phone_id',
                    'yandex/uid/some_uid',
                ],
                'service': 'eats',
                'limit': 10,
                'cursor': cursor('yandex/uid/some_uid', 'with_two_debtors_id'),
            },
            {'debts': []},
        ),
    ],
)
async def test_debts_list(taxi_debt_collector, query, response_json):
    response = await taxi_debt_collector.post('/v1/debts/list', query)
    assert response.json() == response_json
