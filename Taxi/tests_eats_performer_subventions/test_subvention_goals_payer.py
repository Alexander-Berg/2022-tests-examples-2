import pytest


ADJ_REASON_ID = 198
RETENTION_ADJ_REASON_ID = 293


async def get_paid_goals(cursor):
    cursor.execute(
        """
SELECT
    psog.id, psog.performer_id, sp.amount, sp.currency, sp.external_payment_id
FROM eats_performer_subventions.performer_subvention_order_goals psog
INNER JOIN eats_performer_subventions.subvention_payments sp
    on psog.id=sp.goal_id
WHERE psog.status='paid'
        """,
    )

    return cursor.fetchall()


def get_db_paid_goal(performer_id, amount, currency, external_payment_id):
    return {
        'performer_id': performer_id,
        'amount': amount,
        'currency': currency,
        'external_payment_id': external_payment_id,
    }


def get_create_adjustment_response(
        external_payment_id,
        courier_id,
        amount,
        comment,
        date,
        reason_id=ADJ_REASON_ID,
):
    return {
        'isSuccess': True,
        'adjustment': {
            'id': external_payment_id,
            'courierId': courier_id,
            'reasonId': reason_id,
            'amount': amount,
            'comment': comment,
            'date': date,
        },
    }


@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_SUBVENTION_GOALS_PAYER_SETTINGS={
        'period_sec': 600,
        'is_enabled': True,
        'db_read_chunk_size': 2,
        'delay_to_pay': 24 * 60 * 60,
        'max_adjustment_creation_fails_count': 2,
        'adjustment': {
            'reason_id': ADJ_REASON_ID,
            'comment_tanker_key': 'subvention_adjustment_comment',
        },
        'adjustments': {
            'retention': {
                'reason_id': ADJ_REASON_ID,
                'comment_tanker_key': 'subvention_adjustment_comment',
            },
        },
    },
)
@pytest.mark.parametrize(
    'payments,adjustment_responses',
    [
        pytest.param(
            [],
            {},
            marks=[pytest.mark.now('2022-12-20T15:34:00+03:00')],
            id='nothing to pay (database is empty)',
        ),
        pytest.param(
            [],
            {},
            marks=[
                pytest.mark.now('2022-01-01 00:00:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals.sql'],
                ),
            ],
            id='nothing to pay (time isn\'t up)',
        ),
        pytest.param(
            {
                '3': get_db_paid_goal(3, 6793, 'rub', '30'),
                '4': get_db_paid_goal(4, 6795, 'rub', '40'),
                '7': get_db_paid_goal(7, 6796, 'byn', '70'),
                '8': get_db_paid_goal(8, 20388, 'byn', '80'),
                '9': get_db_paid_goal(9, 7000, 'rub', '30'),
            },
            {
                3: get_create_adjustment_response(
                    30, 3, 6793, 'Personal goal', '2022-01-02',
                ),
                4: get_create_adjustment_response(
                    40, 4, 6795, 'Personal goal', '2022-01-02',
                ),
                7: get_create_adjustment_response(
                    70, 7, 6796, 'Personal goal', '2022-01-02',
                ),
                8: get_create_adjustment_response(
                    80, 8, 20388, 'Personal goal', '2022-01-02',
                ),
                9: get_create_adjustment_response(
                    30,
                    9,
                    7000,
                    'Personal goal',
                    '2022-01-02',
                    RETENTION_ADJ_REASON_ID,
                ),
            },
            marks=[
                pytest.mark.now('2022-01-02T00:00:00+00:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals.sql'],
                ),
            ],
            id='London courier is ignored',
        ),
        pytest.param(
            {
                '2': get_db_paid_goal(2, 8233, 'rub', '20'),
                '3': get_db_paid_goal(3, 6793, 'rub', '30'),
                '4': get_db_paid_goal(4, 6795, 'rub', '40'),
                '7': get_db_paid_goal(7, 6796, 'byn', '70'),
                '8': get_db_paid_goal(8, 20388, 'byn', '80'),
                '9': get_db_paid_goal(9, 7000, 'rub', '30'),
            },
            {
                2: get_create_adjustment_response(
                    20, 2, 8233, 'Personal goal', '2022-01-02',
                ),
                3: get_create_adjustment_response(
                    30, 3, 6793, 'Personal goal', '2022-01-02',
                ),
                4: get_create_adjustment_response(
                    40, 4, 6795, 'Personal goal', '2022-01-02',
                ),
                7: get_create_adjustment_response(
                    70, 7, 6796, 'Personal goal', '2022-01-02',
                ),
                8: get_create_adjustment_response(
                    80, 8, 20388, 'Personal goal', '2022-01-02',
                ),
                9: get_create_adjustment_response(
                    30,
                    9,
                    7000,
                    'Personal goal',
                    '2022-01-02',
                    RETENTION_ADJ_REASON_ID,
                ),
            },
            marks=[
                pytest.mark.now('2022-01-02T03:00:00+00:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals.sql'],
                ),
            ],
            id='all payed',
        ),
    ],
)
async def test_subvention_goals_importer(
        taxi_eats_performer_subventions,
        pgsql,
        mockserver,
        payments,
        adjustment_responses,
):
    @mockserver.json_handler(
        '/eats-core-courier-salary/server/api/v1/courier-salary/adjustments',
    )
    def _mock_handler(request):
        return adjustment_responses[request.json['courierId']]

    cursor = pgsql['eats_performer_subventions'].dict_cursor()

    await taxi_eats_performer_subventions.run_periodic_task(
        'subvention-goals-payer-periodic',
    )

    assert _mock_handler.times_called == len(adjustment_responses)

    db_payments = await get_paid_goals(cursor)

    assert len(db_payments) == len(payments)

    for db_payment in db_payments:
        assert db_payment['performer_id'] in payments

        expected_payment = payments[db_payment['performer_id']]

        assert db_payment['amount'] == expected_payment['amount']
        assert db_payment['currency'] == expected_payment['currency']
        assert (
            db_payment['external_payment_id']
            == expected_payment['external_payment_id']
        )
