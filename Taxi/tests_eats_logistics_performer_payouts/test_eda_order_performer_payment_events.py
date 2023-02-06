import pytest


def create_payment_event(
        courier_id: str,
        order_nr: str,
        amount: str,
        currency: str,
        payment_type: str,
        direction: str,
        time_point_at: str,
):
    return {
        'courier_id': int(courier_id),
        'order_nr': order_nr,
        'amount': amount,
        'currency': currency,
        'type': payment_type,
        'direction': direction,
        'time_point_at': time_point_at,
    }


def create_expected_payment(
        courier_id: str,
        order_nr: str,
        amount_factor_name: str,
        amount,
        currency,
        currency_factor_name: str,
):
    return {
        'courier_id': int(courier_id),
        'order_nr': order_nr,
        'factor_name': amount_factor_name,
        'amount': amount,
        'currency': currency,
        'currency_factor_name': currency_factor_name,
    }


async def get_decimal_value_for_subject(
        cursor, external_id: str, factor_name: str,
):
    cursor.execute(
        """
select value from eats_logistics_performer_payouts.factor_decimal_values fdv
where subject_id = (SELECT id from eats_logistics_performer_payouts.subjects
    where external_id = '{}' AND subject_type_id = 8 LIMIT 1)
AND factor_id = (SELECT id from eats_logistics_performer_payouts.factors
    where name = '{}' AND subject_type_id = 8 LIMIT 1);
    """.format(
            external_id, factor_name,
        ),
    )

    result = cursor.fetchone()

    return str(result['value']) if result is not None else None


async def get_string_value_for_subject(
        cursor, external_id: str, factor_name: str,
):
    cursor.execute(
        """
select value from eats_logistics_performer_payouts.factor_string_values fsv
where subject_id = (SELECT id from eats_logistics_performer_payouts.subjects
    where external_id = '{}' AND subject_type_id = 8 LIMIT 1)
AND factor_id = (SELECT id from eats_logistics_performer_payouts.factors
    where name = '{}' AND subject_type_id = 8 LIMIT 1);
    """.format(
            external_id, factor_name,
        ),
    )

    result = cursor.fetchone()

    return result['value'] if result is not None else None


async def get_integer_value_for_subject(
        cursor, external_id: str, factor_name: str,
):
    cursor.execute(
        """
select value from eats_logistics_performer_payouts.factor_integer_values fsv
where subject_id = (SELECT id from eats_logistics_performer_payouts.subjects
    where external_id = '{}' AND subject_type_id = 8 LIMIT 1)
AND factor_id = (SELECT id from eats_logistics_performer_payouts.factors
    where name = '{}' AND subject_type_id = 8 LIMIT 1);
    """.format(
            external_id, factor_name,
        ),
    )

    result = cursor.fetchone()

    return bool(result['value']) if result is not None else False


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_orders_subjects.sql'],
)
@pytest.mark.parametrize(
    'payment_events,expected_payments,expected_surged_orders',
    [
        pytest.param(
            [
                create_payment_event(
                    '43',
                    '43-70',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [],
            [],
            id='unknown order, unknown performer',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-76',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-76',
                    'payment_fee',
                    '50.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
            ],
            [],
            id='unknown order, performer exist',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '40.00',
                    'RUB',
                    'surge_bonus',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_fee',
                    '149.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_tips',
                    '49.0000',
                    'RUB',
                    'payment_tips_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'surge_bonus',
                    '40.0000',
                    'RUB',
                    'surge_bonus_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': True}],
            id='order doesn\'t have time_point_at, factors were added',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_fee',
                    '149.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_tips',
                    '49.0000',
                    'RUB',
                    'payment_tips_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': False}],
            id='order doesn\'t have time_point_at, without surge',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '5.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_fee',
                    '154.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_tips',
                    '49.0000',
                    'RUB',
                    'payment_tips_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': False}],
            id='order doesn\'t have time_point_at, multiple delivery payments',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'refund',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '5.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'refund',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_fee',
                    '54.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_tips',
                    '0.0000',
                    'RUB',
                    'payment_tips_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': False}],
            id='order doesn\'t have time_point_at, multiple'
            ' delivery payments and refunds',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'RUB',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '49.00',
                    'RUB',
                    'tips',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '40.00',
                    'RUB',
                    'surge_bonus',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '40.00',
                    'RUB',
                    'surge_bonus',
                    'refund',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_fee',
                    '149.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'payment_tips',
                    '49.0000',
                    'RUB',
                    'payment_tips_currency',
                ),
                create_expected_payment(
                    '42',
                    '42-73',
                    'surge_bonus',
                    '0.0000',
                    'RUB',
                    'surge_bonus_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': True}],
            id='order doesn\'t have time_point_at, refund on surged order',
        ),
        pytest.param(
            [
                create_payment_event(
                    '42',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '42',
                    '42-73',
                    '99.00',
                    'KZT',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '123',
                    '42-73',
                    'payment_fee',
                    '50.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
            ],
            [{'order_nr': '42-73', 'is_surge': False}],
            id='order doesn\'t have time_point_at, different currencies',
        ),
        pytest.param(
            [
                create_payment_event(
                    '123',
                    '42-73',
                    '50.00',
                    'RUB',
                    'assembly',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '123',
                    '42-74',
                    '99.00',
                    'KZT',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
                create_payment_event(
                    '123',
                    '42-75',
                    '99.00',
                    'KZT',
                    'delivery',
                    'payment',
                    '2021-12-24T17:05:46+00:00',
                ),
            ],
            [
                create_expected_payment(
                    '123',
                    '42-73',
                    'payment_fee',
                    '50.0000',
                    'RUB',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '123',
                    '42-74',
                    'payment_fee',
                    '99.0000',
                    'KZT',
                    'payment_fee_currency',
                ),
                create_expected_payment(
                    '123',
                    '42-75',
                    'payment_fee',
                    '99.0000',
                    'KZT',
                    'payment_fee_currency',
                ),
            ],
            [
                {'order_nr': '42-73', 'is_surge': False},
                {'order_nr': '42-74', 'is_surge': False},
                {'order_nr': '42-75', 'is_surge': False},
            ],
            id='order doesn\'t have time_point_at, finished order',
        ),
    ],
)
async def test_handle_eda_order_performer_payment_events(
        stq,
        stq_runner,
        pgsql,
        payment_events,
        expected_payments,
        expected_surged_orders,
):
    cursor = pgsql['eats_logistics_performer_payouts'].dict_cursor()

    for payment_event in payment_events:
        await stq_runner.eda_order_performer_payment_events.call(
            task_id='dummy_task', kwargs=payment_event,
        )

    for expected_payment in expected_payments:
        amount = await get_decimal_value_for_subject(
            cursor,
            expected_payment['order_nr'],
            expected_payment['factor_name'],
        )
        assert amount == expected_payment['amount']
        currency = await get_string_value_for_subject(
            cursor,
            expected_payment['order_nr'],
            expected_payment['currency_factor_name'],
        )
        assert currency == expected_payment['currency']

    for expected_surged_order in expected_surged_orders:
        is_surge = await get_integer_value_for_subject(
            cursor, expected_surged_order['order_nr'], 'is_surge',
        )

        assert is_surge == expected_surged_order['is_surge']
