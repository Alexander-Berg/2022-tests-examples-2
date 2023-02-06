import datetime
import typing as tp
import uuid

import pytest

from piecework_calculation import calculation
from piecework_calculation import constants


@pytest.mark.parametrize(
    'partial_period, existing_drafts, '
    'expected_drafts, expected_approvals_calls',
    [
        # No drafts
        (
            False,
            [],
            [
                {'country': 'by', 'status': 'need_approval'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {
                'by': {
                    'mode': 'poll',
                    'service_name': 'piecework-calculation',
                    'api_path': 'v1_payments_support-taxi_process',
                    'run_manually': False,
                    'data': {
                        'payment': {
                            'calculation_rule_id': 'some_rule_id',
                            'country': 'by',
                            'start_date': '2022-01-01',
                            'stop_date': '2022-01-16',
                        },
                    },
                    'tickets': {
                        'create_data': {
                            'summary': (
                                'Payment by per 2022-01-01 - 2022-01-16'
                            ),
                            'description': (
                                'Country: by\nPeriod: 2022-01-01 - 2022-01-16'
                            ),
                        },
                    },
                },
                'ru': {
                    'mode': 'poll',
                    'service_name': 'piecework-calculation',
                    'api_path': 'v1_payments_support-taxi_process',
                    'run_manually': False,
                    'data': {
                        'payment': {
                            'calculation_rule_id': 'some_rule_id',
                            'country': 'ru',
                            'start_date': '2022-01-01',
                            'stop_date': '2022-01-16',
                        },
                    },
                    'tickets': {
                        'create_data': {
                            'summary': (
                                'Payment ru per 2022-01-01 - 2022-01-16'
                            ),
                            'description': (
                                'Country: ru\nPeriod: 2022-01-01 - 2022-01-16'
                            ),
                        },
                    },
                },
            },
        ),
        # by failed, ru missing
        (
            False,
            [{'country': 'by', 'status': 'failed'}],
            [
                {'country': 'by', 'status': 'failed'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {
                'ru': {
                    'mode': 'poll',
                    'service_name': 'piecework-calculation',
                    'api_path': 'v1_payments_support-taxi_process',
                    'run_manually': False,
                    'data': {
                        'payment': {
                            'calculation_rule_id': 'some_rule_id',
                            'country': 'ru',
                            'start_date': '2022-01-01',
                            'stop_date': '2022-01-16',
                        },
                    },
                    'tickets': {
                        'create_data': {
                            'summary': (
                                'Payment ru per 2022-01-01 - 2022-01-16'
                            ),
                            'description': (
                                'Country: ru\nPeriod: 2022-01-01 - 2022-01-16'
                            ),
                        },
                    },
                },
            },
        ),
        # by updating, ru missing
        (
            False,
            [{'country': 'by', 'status': 'updating'}],
            [
                {'country': 'by', 'status': 'need_approval'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {
                'ru': {
                    'mode': 'poll',
                    'service_name': 'piecework-calculation',
                    'api_path': 'v1_payments_support-taxi_process',
                    'run_manually': False,
                    'data': {
                        'payment': {
                            'calculation_rule_id': 'some_rule_id',
                            'country': 'ru',
                            'start_date': '2022-01-01',
                            'stop_date': '2022-01-16',
                        },
                    },
                    'tickets': {
                        'create_data': {
                            'summary': (
                                'Payment ru per 2022-01-01 - 2022-01-16'
                            ),
                            'description': (
                                'Country: ru\nPeriod: 2022-01-01 - 2022-01-16'
                            ),
                        },
                    },
                },
            },
        ),
        # by failed, by updating, ru updating
        (
            False,
            [
                {'country': 'by', 'status': 'failed'},
                {'country': 'by', 'status': 'updating'},
                {'country': 'ru', 'status': 'updating'},
            ],
            [
                {'country': 'by', 'status': 'failed'},
                {'country': 'by', 'status': 'need_approval'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {},
        ),
        # by failed, ru updating
        (
            False,
            [
                {'country': 'by', 'status': 'failed'},
                {'country': 'ru', 'status': 'updating'},
            ],
            [
                {'country': 'by', 'status': 'failed'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {},
        ),
        # All drafts updating
        (
            False,
            [
                {'country': 'by', 'status': 'updating'},
                {'country': 'ru', 'status': 'updating'},
            ],
            [
                {'country': 'by', 'status': 'need_approval'},
                {'country': 'ru', 'status': 'need_approval'},
            ],
            {},
        ),
        # Partial period
        (True, [], [], {}),
    ],
)
@pytest.mark.translations(
    piecework={
        'payment_ticket.summary': {
            'ru': 'Payment {country} per {start_date} - {stop_date}',
        },
        'payment_ticket.description': {
            'ru': 'Country: {country}\nPeriod: {start_date} - {stop_date}',
        },
    },
)
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
        'by': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
)
async def test_create_after_calc(
        cron_context,
        mock_create_draft,
        partial_period,
        existing_drafts,
        expected_drafts,
        expected_approvals_calls,
):
    rule = {
        'calculation_rule_id': 'some_rule_id',
        'tariff_type': 'support-taxi',
        'start_date': datetime.date(2022, 1, 1),
        'stop_date': datetime.date(2022, 1, 16),
        'countries': ['ru', 'by'],
    }
    async with cron_context.pg.master_pool.acquire() as conn:
        for approvals_id, draft in enumerate(existing_drafts):
            await conn.execute(
                'INSERT INTO piecework.payment_draft ('
                '  payment_draft_id, tariff_type, calculation_rule_id, '
                '  country, start_date, stop_date, status, approvals_id'
                ') VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
                uuid.uuid4().hex,
                rule['tariff_type'],
                rule['calculation_rule_id'],
                draft['country'],
                rule['start_date'],
                rule['stop_date'],
                draft['status'],
                approvals_id,
            )
        await calculation.create_payment_drafts(
            context=cron_context,
            conn=conn,
            rule=rule,
            partial_period=partial_period,
        )
        updated_drafts = await conn.fetch(
            'SELECT country, status '
            'FROM piecework.payment_draft '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY country, status::varchar',
            rule['calculation_rule_id'],
        )
        updated_drafts = [dict(rec) for rec in updated_drafts]
        assert updated_drafts == expected_drafts

    calls_by_country: tp.Dict[str, dict] = {}
    while mock_create_draft.has_calls:
        create_draft_call = mock_create_draft.next_call()['request'].json
        create_draft_call.pop('request_id')
        create_draft_call['data']['payment'].pop('payment_draft_id')
        calls_by_country[
            create_draft_call['data']['payment']['country']
        ] = create_draft_call
    assert calls_by_country == expected_approvals_calls


@pytest.mark.parametrize(
    'existing_draft_statuses, expected_draft_statuses, '
    'expected_approvals_call',
    [
        (
            [],
            ['updating'],
            {
                'mode': 'poll',
                'service_name': 'piecework-calculation',
                'api_path': 'v1_payments_support-taxi_process',
                'run_manually': False,
                'data': {
                    'payment': {
                        'calculation_rule_id': 'some_rule_id',
                        'country': 'ru',
                        'start_date': '2022-01-01',
                        'stop_date': '2022-01-16',
                    },
                },
                'tickets': {
                    'create_data': {
                        'summary': 'Payment ru per 2022-01-01 - 2022-01-16',
                        'description': (
                            'Country: ru\nPeriod: 2022-01-01 - 2022-01-16'
                        ),
                    },
                },
            },
        ),
        (
            ['failed'],
            ['failed', 'updating'],
            {
                'mode': 'poll',
                'service_name': 'piecework-calculation',
                'api_path': 'v1_payments_support-taxi_process',
                'run_manually': False,
                'data': {
                    'payment': {
                        'calculation_rule_id': 'some_rule_id',
                        'country': 'ru',
                        'start_date': '2022-01-01',
                        'stop_date': '2022-01-16',
                    },
                },
                'tickets': {
                    'create_data': {
                        'summary': 'Payment ru per 2022-01-01 - 2022-01-16',
                        'description': (
                            'Country: ru\nPeriod: 2022-01-01 - 2022-01-16'
                        ),
                    },
                },
            },
        ),
        (['need_approval'], ['updating'], None),
        (['updating'], ['updating'], None),
        (['failed', 'need_approval'], ['failed', 'updating'], None),
        (['failed', 'updating'], ['failed', 'updating'], None),
    ],
)
@pytest.mark.translations(
    piecework={
        'payment_ticket.summary': {
            'ru': 'Payment {country} per {start_date} - {stop_date}',
        },
        'payment_ticket.description': {
            'ru': 'Country: {country}\nPeriod: {start_date} - {stop_date}',
        },
    },
)
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
)
async def test_create_after_correction(
        web_context,
        mock_create_draft,
        existing_draft_statuses,
        expected_draft_statuses,
        expected_approvals_call,
):
    rule = {
        'calculation_rule_id': 'some_rule_id',
        'tariff_type': 'support-taxi',
        'start_date': datetime.date(2022, 1, 1),
        'stop_date': datetime.date(2022, 1, 16),
        'countries': ['ru', 'by'],
    }
    async with web_context.pg.master_pool.acquire() as conn:
        for approvals_id, status in enumerate(existing_draft_statuses):
            await conn.execute(
                'INSERT INTO piecework.payment_draft ('
                '  payment_draft_id, tariff_type, calculation_rule_id, '
                '  country, start_date, stop_date, status, approvals_id'
                ') VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
                uuid.uuid4().hex,
                rule['tariff_type'],
                rule['calculation_rule_id'],
                'ru',
                rule['start_date'],
                rule['stop_date'],
                status,
                approvals_id,
            )
        await calculation.create_payment_draft(
            context=web_context,
            conn=conn,
            rule=rule,
            country='ru',
            status=constants.DRAFT_STATUS_UPDATING,
        )
        updated_drafts = await conn.fetch(
            'SELECT status '
            'FROM piecework.payment_draft '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY status::varchar',
            rule['calculation_rule_id'],
        )
        updated_draft_statuses = [rec['status'] for rec in updated_drafts]
        assert updated_draft_statuses == expected_draft_statuses

        if expected_approvals_call is None:
            assert not mock_create_draft.has_calls
            return
        create_draft_call = mock_create_draft.next_call()['request'].json
        create_draft_call.pop('request_id')
        create_draft_call['data']['payment'].pop('payment_draft_id')
        assert create_draft_call == expected_approvals_call
