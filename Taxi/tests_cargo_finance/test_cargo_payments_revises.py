import pytest


EXPECTED_ORDERS_BEFORE_SENDING = [
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/1',
        {'payload': 1},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/2',
        {'payload': 2},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/3',
        {'payload': 3},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/4',
        {'payload': 4},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/5',
        {'payload': 5},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/6',
        {'payload': 6},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/5',
        {'payload': 5},
        'ndd',
    ),
]

EXPECTED_ORDERS_AFTER_SENDING = [
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/1',
        {'payload': 1},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/2',
        {'payload': 2},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/3',
        {'payload': 3},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/4',
        {'payload': 4},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/5',
        {'payload': 5},
        'ndd',
    ),
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/6',
        {'payload': 6},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/5',
        {'payload': 5},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/2',
        {'payload': 'A'},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/4',
        {'payload': 'B'},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/6',
        {'payload': 'C'},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/1',
        {'payload': 1},
        'ndd',
    ),
]

EXPECTED_ORDERS_AFTER_DELETION = [
    (
        'cargo-finance',
        'taxi/user_on_delivery_payment/6',
        {'payload': 6},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/2',
        {'payload': 'A'},
        'ndd',
    ),
    (
        'cargo-payments',
        'taxi/user_on_delivery_payment/6',
        {'payload': 'C'},
        'ndd',
    ),
]

SENDING_ORDERS = [
    {
        'kind': 'other',
        'payload': 'A',
        'topic': 'taxi/user_on_delivery_payment/2',
    },
    {
        'kind': 'b2b_user_payment',
        'payload': 'B',
        'topic': 'taxi/user_on_delivery_payment/4',
    },
    {
        'kind': 'b2b_user_payment',
        'payload': 'C',
        'topic': 'taxi/user_on_delivery_payment/6',
    },
    {
        'kind': 'b2b_user_payment',
        'payload': 1,
        'topic': 'taxi/user_on_delivery_payment/1',
    },
]

REVISE_TESTPOINT_CASE_NO_OPPOSITE = [
    {
        'order': {
            'source': 'cargo-payments',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/2',
            'migration_name': 'ndd',
        },
    },
    {
        'order': {
            'source': 'cargo-payments',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/3',
            'migration_name': 'ndd',
        },
    },
]

REVISE_TESTPOINT_CASE_EQUAL = [
    {
        'order': {
            'source': 'cargo-finance',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/1',
            'migration_name': 'ndd',
        },
        'opposite_order': {
            'source': 'cargo-payments',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/1',
            'migration_name': 'ndd',
        },
    },
    {
        'order': {
            'source': 'cargo-payments',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/5',
            'migration_name': 'ndd',
        },
        'opposite_order': {
            'source': 'cargo-finance',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/5',
            'migration_name': 'ndd',
        },
    },
]

REVISE_TESTPOINT_CASE_MISMATCH = [
    {
        'order': {
            'source': 'cargo-finance',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/4',
            'migration_name': 'ndd',
        },
        'opposite_order': {
            'source': 'cargo-payments',
            'kind': 'b2b_user_payment',
            'topic': 'taxi/user_on_delivery_payment/4',
            'migration_name': 'ndd',
        },
    },
]

DIFFERENT_CONFLICTING_ORDERS = [
    {
        'kind': 'b2b_user_payment',
        'payload': 'A',
        'topic': 'taxi/user_on_delivery_payment/0',
    },
    {
        'kind': 'b2b_user_payment',
        'payload': 'B',
        'topic': 'taxi/user_on_delivery_payment/0',
    },
]

SAME_CONFLICTING_ORDERS = [
    {
        'kind': 'b2b_user_payment',
        'payload': 'A',
        'topic': 'taxi/user_on_delivery_payment/0',
    },
    {
        'kind': 'b2b_user_payment',
        'payload': 'A',
        'topic': 'taxi/user_on_delivery_payment/0',
    },
]


def _write_docs(pgsql, request):
    cursor = pgsql['cargo_finance'].cursor()
    cursor.execute(request)


def _fetch_orders_divergences(pgsql):
    cursor = pgsql['cargo_finance'].cursor()
    cursor.execute(
        """
        SELECT cargo_finance_doc, cargo_payments_doc, mismatch_hint
        FROM cargo_finance.billing_orders_divergences
        ORDER BY id
        """,
    )
    return cursor.fetchall()


def _fetch_orders(pgsql):
    cursor = pgsql['cargo_finance'].cursor()
    cursor.execute(
        """
        SELECT source, topic, order_document, migration_name
        FROM cargo_finance.billing_orders_revise_queue
        ORDER BY id
        """,
    )
    return cursor.fetchall()


@pytest.mark.config(
    CARGO_FINANCE_BILLING_ORDERS_REVISE_JOB_SETTINGS={
        'revise_job_settings': {
            'enabled': True,
            'allow_log_stats': True,
            'allow_do_fetch': True,
            'allow_do_revise': True,
            'allow_do_delete': True,
        },
    },
)
@pytest.mark.pgsql('cargo_finance', files=['insert_billing_orders.sql'])
async def test_worker(taxi_cargo_finance, run_infinite_task, pgsql, testpoint):
    # Revise cases testpoints

    @testpoint('revise: no opposite document')
    def revise_tespoint_no_opposite(data):
        assert data in REVISE_TESTPOINT_CASE_NO_OPPOSITE

    @testpoint('revise: equal')
    def revise_tespoint_equal(data):
        assert data in REVISE_TESTPOINT_CASE_EQUAL

    @testpoint('revise: mismatch')
    def revise_tespoint_mismatch(data):
        assert data in REVISE_TESTPOINT_CASE_MISMATCH

    # Step 0 - initials conditions

    assert _fetch_orders(pgsql) == EXPECTED_ORDERS_BEFORE_SENDING

    # Step 1 - send orders from cargo-payments

    for order in SENDING_ORDERS:
        response = await taxi_cargo_finance.post(
            '/internal/cargo-finance/ndd/billing-order/revise',
            json={'orders': [order]},
        )
    assert response.status_code == 200
    assert _fetch_orders(pgsql) == EXPECTED_ORDERS_AFTER_SENDING

    # Step 2 - do revise job iteration

    await run_infinite_task('cargo-finance-cargo-payments-reviser')

    assert _fetch_orders(pgsql) == EXPECTED_ORDERS_AFTER_DELETION

    # Check tespoints calls

    assert revise_tespoint_no_opposite.times_called == len(
        REVISE_TESTPOINT_CASE_NO_OPPOSITE,
    )
    assert revise_tespoint_equal.times_called == len(
        REVISE_TESTPOINT_CASE_EQUAL,
    )
    assert revise_tespoint_mismatch.times_called == len(
        REVISE_TESTPOINT_CASE_MISMATCH,
    )


@pytest.mark.parametrize(
    'orders_count, expected_code', [(0, 500), (1, 200), (2, 500), (3, 500)],
)
async def test_incorrect_orders_to_send(
        taxi_cargo_finance, orders_count, expected_code,
):
    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/ndd/billing-order/revise',
        json={'orders': SENDING_ORDERS[0:orders_count]},
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'write_docs, expected_divergence_in_db',
    (
        pytest.param(
            """
            INSERT INTO
                cargo_finance.billing_orders_revise_queue (
                    id,
                    received,
                    source,
                    kind,
                    topic,
                    order_document
                )
            VALUES
                (-8, now() - '1 day'::interval, 'cargo-payments',
                'b2b_user_payment', 'taxi/user_on_delivery_payment/2',
                '{"payload": 2}')
            """,
            [(None, {'payload': 2}, 'One doc is missing')],
            id='Missing document from cargo-finance',
        ),
        pytest.param(
            """
            INSERT INTO
                cargo_finance.billing_orders_revise_queue (
                    id,
                    received,
                    source,
                    kind,
                    topic,
                    order_document
                )
            VALUES
                (-6, now() - '1 day'::interval, 'cargo-finance',
                'b2b_user_payment', 'taxi/user_on_delivery_payment/4',
                '{"payload": 3}')
            """,
            [({'payload': 3}, None, 'One doc is missing')],
            id='Missing document from cargo-payments',
        ),
        pytest.param(
            """
            INSERT INTO
                cargo_finance.billing_orders_revise_queue (
                    id,
                    received,
                    source,
                    kind,
                    topic,
                    order_document
                )
            VALUES
                (-6, now() - '1 day'::interval, 'cargo-finance',
                'b2b_user_payment', 'taxi/user_on_delivery_payment/4',
                '{"payload": 3}'),
                (-7, now() - '1 day'::interval, 'cargo-payments',
                'b2b_user_payment', 'taxi/user_on_delivery_payment/4',
                '{"payload": 4}')
            """,
            [({'payload': 3}, {'payload': 4}, 'Docs mismatch')],
            id='Mismatch in documents',
        ),
    ),
)
@pytest.mark.config(
    CARGO_FINANCE_BILLING_ORDERS_REVISE_JOB_SETTINGS={
        'revise_job_settings': {
            'enabled': True,
            'allow_log_stats': True,
            'allow_do_fetch': True,
            'allow_do_revise': True,
            'allow_do_delete': True,
        },
    },
)
async def test_log_divergences(
        taxi_cargo_finance,
        run_infinite_task,
        pgsql,
        write_docs,
        expected_divergence_in_db,
):

    _write_docs(pgsql, write_docs)

    await run_infinite_task('cargo-finance-cargo-payments-reviser')

    assert _fetch_orders_divergences(pgsql) == expected_divergence_in_db


@pytest.mark.config(
    CARGO_FINANCE_BILLING_ORDERS_REVISE_JOB_SETTINGS={
        'revise_job_settings': {
            'enabled': True,
            'allow_log_stats': True,
            'allow_do_fetch': True,
            'allow_do_revise': True,
            'allow_do_delete': True,
        },
    },
)
async def test_delete_old_devergences(
        taxi_cargo_finance, run_infinite_task, pgsql,
):
    _write_docs(
        pgsql,
        """
        INSERT INTO
            cargo_finance.billing_orders_divergences (
                id,
                received,
                kind,
                topic,
                cargo_finance_doc,
                cargo_payments_doc,
                mismatch_hint
            )
        VALUES
            (-1, now() - '10 days'::interval, 'b2b_user_payment',
            'taxi/user_on_delivery_payment/1', '{"payload": 1}',
            '{"payload": 2}', 'hint')
        """,
    )

    await run_infinite_task('cargo-finance-cargo-payments-reviser')

    assert _fetch_orders_divergences(pgsql) == []


async def test_attempt_to_insert_existing_document_different_docs(
        taxi_cargo_finance, pgsql,
):
    for order in DIFFERENT_CONFLICTING_ORDERS:
        response = await taxi_cargo_finance.post(
            '/internal/cargo-finance/ndd/billing-order/revise',
            json={'orders': [order]},
        )
        assert response.status_code == 200
    assert _fetch_orders_divergences(pgsql) == [
        (None, {'payload': 'A'}, 'Insertion conflict: Existing document'),
        (None, {'payload': 'B'}, 'Insertion conflict: New document'),
    ]

    assert _fetch_orders(pgsql) == [
        (
            'cargo-payments',
            'taxi/user_on_delivery_payment/0',
            {'payload': 'A'},
            'ndd',
        ),
    ]


async def test_attempt_to_insert_existing_document_same_docs(
        taxi_cargo_finance, pgsql,
):
    for order in SAME_CONFLICTING_ORDERS:
        response = await taxi_cargo_finance.post(
            '/internal/cargo-finance/ndd/billing-order/revise',
            json={'orders': [order]},
        )
        assert response.status_code == 200
    assert _fetch_orders_divergences(pgsql) == []
    assert _fetch_orders(pgsql) == [
        (
            'cargo-payments',
            'taxi/user_on_delivery_payment/0',
            {'payload': 'A'},
            'ndd',
        ),
    ]
