# pylint: disable=redefined-outer-name

import datetime

import pytest

from piecework_calculation import constants
from piecework_calculation.generated.cron import run_cron


@pytest.fixture
def mock_drafts_list(mockserver):
    def _wrap(data):
        @mockserver.json_handler('/taxi-approvals/drafts/list/')
        def _mocked_drafts_list(request):
            return [{'id': 1, 'data': data, 'version': 1}]

        return _mocked_drafts_list

    return _wrap


@pytest.mark.parametrize(
    'tariff_type, data, expected_status, expected_payments_call,'
    'expected_rule, expected_db_draft_status, expected_drafts_list_api_path',
    [
        # Payment not found
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-02-01',
                    'stop_date': '2020-02-16',
                },
            },
            'failed',
            None,
            None,
            None,
            'v1_payments_support-taxi_process',
        ),
        # All OK
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            'succeeded',
            {
                'period': '2020-01-01',
                'source': 'piecework_payment_123',
                'data': [
                    {
                        'login': 'ivanov',
                        'summa_br': 10.0,
                        'night_br': 5.0,
                        'holiday_br': 8.0,
                        'holiday_night_br': 1.0,
                        'bonus': 11.0,
                    },
                    {
                        'login': 'petrov',
                        'summa_br': 15.0,
                        'night_br': 7.0,
                        'holiday_br': 10.0,
                        'holiday_night_br': 0.0,
                        'bonus': 16.0,
                    },
                ],
            },
            {
                'start_date': datetime.date(2020, 1, 16),
                'stop_date': datetime.date(2020, 2, 1),
                'repeat': True,
                'countries': ['rus', 'blr'],
                'logins': None,
                'enabled': True,
                'status': 'waiting_agent',
                'description': '',
                'rule_type': constants.CALCULATION_RULE_REGULAR_TYPE,
            },
            'succeeded',
            'v1_payments_support-taxi_process',
        ),
        (
            'call-taxi-unified',
            {
                'payment': {
                    'payment_draft_id': 'dismissal_uuid',
                    'calculation_rule_id': 'dismissal_rule_id',
                    'country': 'rus',
                    'start_date': '2021-01-01',
                    'stop_date': '2021-01-12',
                },
            },
            'succeeded',
            {
                'period': '2021-01-01',
                'data': [
                    {
                        'login': 'sidorova',
                        'summa_br': 15.0,
                        'night_br': 7.0,
                        'holiday_br': 10.0,
                        'holiday_night_br': 2.0,
                        'bonus_br': 16.0,
                        'days_nsz': 5,
                    },
                    {
                        'login': 'smirnova',
                        'summa_br': 0.0,
                        'night_br': 0.0,
                        'holiday_br': 0.0,
                        'holiday_night_br': 0.0,
                        'bonus_br': 0.0,
                        'days_nsz': 6,
                    },
                ],
            },
            {
                'start_date': datetime.date(2021, 1, 1),
                'stop_date': datetime.date(2021, 1, 12),
                'repeat': False,
                'countries': ['rus'],
                'logins': None,
                'enabled': True,
                'status': 'success',
                'description': '',
                'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
            },
            'succeeded',
            'v1_payments_call-taxi-unified_process',
        ),
    ],
)
async def test_process_oebs(
        cron_context,
        mock_drafts_list,
        mock_oebs_payments,
        mock_oebs_dismissal_payments,
        mock_finish_draft,
        mockserver,
        tariff_type,
        data,
        expected_status,
        expected_payments_call,
        expected_rule,
        expected_db_draft_status,
        expected_drafts_list_api_path,
):
    mocked_drafts_list = mock_drafts_list(data)

    await run_cron.main(
        ['piecework_calculation.crontasks.process_payments', '-t', '0'],
    )

    assert mocked_drafts_list.times_called == 8
    mocked_drafts_list = [
        mocked_drafts_list.next_call()['request'].json
        for _ in constants.PAYMENT_DRAFT_API_PATH_BY_TYPE
    ]
    assert (
        list(
            filter(
                lambda x: x['api_path'] == expected_drafts_list_api_path,
                mocked_drafts_list,
            ),
        )[0]
        == {
            'service_name': 'piecework-calculation',
            'api_path': expected_drafts_list_api_path,
            'statuses': ['applying'],
        }
    )

    assert mock_finish_draft.times_called == 8
    mock_finish_draft = [
        mock_finish_draft.next_call()['request'].json
        for _ in constants.PAYMENT_DRAFT_API_PATH_BY_TYPE
    ]
    if expected_status == 'succeeded':
        assert {'final_status': 'succeeded'} in mock_finish_draft
    else:
        assert {'final_status': 'succeeded'} not in mock_finish_draft
        return

    if expected_rule['rule_type'] == constants.CALCULATION_RULE_REGULAR_TYPE:
        oebs_payments_call = mock_oebs_payments.next_call()
        assert (
            oebs_payments_call['request'].headers['Authorization']
            == 'OAuth some_token'
        )
        assert oebs_payments_call['request'].json == expected_payments_call
    else:
        assert (
            mock_oebs_dismissal_payments.next_call()['request'].json
            == expected_payments_call
        )

    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, repeat, countries, '
            'logins, enabled, status, description, rule_type '
            'FROM piecework.calculation_rule ORDER BY updated ASC',
        )

        rule = dict(pg_result[-1])
        del rule['calculation_rule_id']
        assert rule == expected_rule

        pg_result = await conn.fetchrow(
            'SELECT status '
            'FROM piecework.payment_draft '
            'WHERE payment_draft_id = $1',
            data['payment']['payment_draft_id'],
        )
        assert pg_result['status'] == expected_db_draft_status


@pytest.mark.parametrize(
    'tariff_type, data, oebs_status, oebs_raw_response, oebs_response, '
    'expected_finish_draft, expected_db_draft_status',
    [
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            400,
            None,
            {'status': 'error', 'message': 'oh shi~'},
            {'final_status': 'failed', 'errors': [{'message': 'oh shi~'}]},
            'failed',
        ),
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            400,
            None,
            {
                'errors': [
                    {
                        'login': 'some_login',
                        'code': 'some_code',
                        'message': 'some_message',
                    },
                    {
                        'login': 'other_login',
                        'code': 'other_code',
                        'message': 'other_message',
                    },
                ],
            },
            {
                'final_status': 'failed',
                'errors': [
                    {
                        'login': 'some_login',
                        'code': 'some_code',
                        'message': 'some_message',
                    },
                    {
                        'login': 'other_login',
                        'code': 'other_code',
                        'message': 'other_message',
                    },
                ],
            },
            'failed',
        ),
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            200,
            None,
            {
                'errors': [
                    {
                        'login': 'ivanov',
                        'code': 'some_code',
                        'message': 'some_message',
                    },
                ],
            },
            {
                'final_status': 'failed',
                'errors': [
                    {
                        'login': 'ivanov',
                        'code': 'some_code',
                        'message': 'some_message',
                    },
                ],
            },
            'failed',
        ),
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            200,
            b'',
            None,
            {
                'final_status': 'failed',
                'errors': [{'message': 'Invalid response: b\'\''}],
            },
            'failed',
        ),
    ],
)
async def test_oebs_errors(
        cron_context,
        mock_drafts_list,
        mock_finish_draft,
        mockserver,
        tariff_type,
        data,
        oebs_status,
        oebs_raw_response,
        oebs_response,
        expected_finish_draft,
        expected_db_draft_status,
):
    mock_drafts_list(data)

    @mockserver.json_handler('/oebs/rest/loadSdelNonstd')
    def _load_sdel_nonstd(request):
        if oebs_raw_response is not None:
            return mockserver.make_response(
                oebs_raw_response, status=oebs_status,
            )
        return mockserver.make_response(json=oebs_response, status=oebs_status)

    await run_cron.main(
        ['piecework_calculation.crontasks.process_payments', '-t', '0'],
    )

    finish_draft_call = mock_finish_draft.next_call()
    assert finish_draft_call['request'].json == expected_finish_draft

    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status '
            'FROM piecework.payment_draft WHERE payment_draft_id = $1',
            data['payment']['payment_draft_id'],
        )
        assert pg_result['status'] == expected_db_draft_status


@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'rus': {
            'destination': 'startrack',
            'benefits_bo_ratio': 1.0,
            'locale': 'ru',
        },
    },
)
@pytest.mark.parametrize(
    'tariff_type, data, expected_status',
    [
        (
            'support-taxi',
            {
                'payment': {
                    'payment_draft_id': 'uuid',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'rus',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            'succeeded',
        ),
    ],
)
async def test_process_startrack(
        cron_context,
        mock_drafts_list,
        mock_finish_draft,
        mock_oebs_payments,
        tariff_type,
        data,
        expected_status,
):
    mock_drafts_list(data)

    await run_cron.main(
        ['piecework_calculation.crontasks.process_payments', '-t', '0'],
    )

    finish_draft_call = mock_finish_draft.next_call()
    assert finish_draft_call['request'].json['final_status'] == expected_status
    if expected_status != 'succeeded':
        return

    assert not mock_oebs_payments.has_calls
