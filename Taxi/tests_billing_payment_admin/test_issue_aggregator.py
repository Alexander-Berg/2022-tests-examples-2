import operator

import pytest


TICKET_KEY = 'TICKET-1'

ISSUE_AGGREGATION_TASK = 'distlock/issue-aggregation'


@pytest.mark.parametrize(
    'expected, issue_exists',
    [
        pytest.param(  # отправка тикетов включена, тикета нет, тикет появился
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': True,
                    'ticket': TICKET_KEY,
                },
            ],
            False,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=True,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '100',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': ['$big_sum'],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            # отправка тикетов включена, тикета в стартреке нет,
            # тикет не появился. Не сматчилось по payload.status
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': True,
                    'ticket': None,
                },
            ],
            False,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=True,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '100',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': [
                                    '$big_sum',
                                    {
                                        'kind': 'status',
                                        'statuses': ['hold_pending'],
                                    },
                                ],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            # отправка тикетов включена, тикет есть,
            # к тикету привязался комментарий
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': True,
                    'ticket': TICKET_KEY,
                },
            ],
            True,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=True,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '100',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': ['$big_sum'],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(  # отправка тикетов включена, тикета нет (не сматчилось)
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': True,
                    'ticket': None,
                },
            ],
            False,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=True,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '1000',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': ['$big_sum'],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            # отправка тикетов выключена, тикета нет, крон не работает
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': None,
                    'ticket': None,
                },
            ],
            False,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=False,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '1000',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': ['$big_sum'],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(  # отправка тикетов включена, тикета нет (не сматчилось)
            [
                {
                    'invoice_id': 'invoice_id',
                    'namespace_id': 'namespace_id',
                    'processed': True,
                    'ticket': None,
                },
            ],
            False,
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_ENABLED=True,
                    BILLING_PAYMENT_ADMIN_ISSUE_AGGREGATION_SETTINGS={
                        'vars': {
                            'big_sum': {
                                'kind': 'amount',
                                'amount': {
                                    '__default__': '1000',
                                    'RUB': '1000',
                                },
                            },
                        },
                        'rules': [
                            {
                                'matchers': ['$big_sum'],
                                'actions': [
                                    {
                                        'kind': 'create_ticket',
                                        'options': {'queue': 'TESTQUEUE'},
                                    },
                                ],
                            },
                        ],
                    },
                ),
                pytest.mark.now('2019-09-17T10:31:00+00:00'),
            ],
        ),
    ],
)
@pytest.mark.ydb(files=['fill_issues.sql'])
async def test_issue_aggregation(
        taxi_billing_payment_admin, ydb, expected, api_tracker, issue_exists,
):
    if issue_exists:
        api_tracker.set_error(
            handler='v2/issues',
            status=409,
            headers={'X-Ticket-Key': TICKET_KEY},
        )
        api_tracker.set_response(
            handler='v2/issues/{issue}/comments', response=dict(id=123500),
        )
    else:
        api_tracker.set_response(
            handler='v2/issues', response={'key': TICKET_KEY, 'id': 'some_id'},
        )

    await taxi_billing_payment_admin.run_task(ISSUE_AGGREGATION_TASK)

    cursor = ydb.execute(
        f"""
        --!syntax_v1
        SELECT
            CAST(invoice_id_hash as Uint64) AS invoice_id_hash,
            CAST(invoice_id as Utf8) AS invoice_id,
            CAST(namespace_id as Utf8) AS namespace_id,
            CAST(kind as Utf8) AS kind,
            CAST(target as Utf8) AS target,
            CAST(external_id as Utf8?) AS external_id,
            payload,
            CAST(description as Utf8) AS description,
            created,
            payload_updated,
            CAST(description_updated as Utf8) AS description_updated,
            updated,
            counter,
            amount,
            currency,
            processed,
            CAST(ticket AS Utf8) AS ticket
        FROM issues
    """,
    )
    assert len(cursor) == 1
    actual_rows = []
    columns = list(expected[0].keys())
    # extract fields by first line
    fields_getter = operator.itemgetter(*columns)
    for actual_row in cursor[0].rows:
        actual_rows.append(dict(zip(columns, fields_getter(actual_row))))
    sorted(actual_rows, key=lambda item: item['invoice_id'])
    assert actual_rows == expected
