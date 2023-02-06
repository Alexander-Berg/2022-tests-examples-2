import copy
import datetime

import pytest

from piecework_calculation import calculation_rules
from piecework_calculation import constants
from piecework_calculation.stq import stq_tasks


NOW = datetime.datetime(2021, 1, 15, 11, 11, 11)
START_NOW = datetime.datetime(2021, 1, 16, 11, 11, 11)

AGENT_EMPLOYEES_RESP_MAPPING = {
    'calldelivery_ru': {
        'items': [
            {'login': 'ivanov', 'team': 'general', 'country': 'ru'},
            {'login': 'petrov', 'team': 'general', 'country': 'ru'},
            {'login': 'asmirnoff', 'team': 'general', 'country': 'ru'},
            {'login': 'test1', 'team': 'general', 'country': 'ru'},
            {'login': 'test2', 'team': 'general', 'country': 'ru'},
        ],
    },
    'calltaxi_ru': {
        'items': [
            {'login': 'ivanov', 'team': 'general', 'country': 'ru'},
            {'login': 'popov', 'team': 'general', 'country': 'ru'},
            {'login': 'bsidorov', 'team': 'general', 'country': 'ru'},
            {'login': 'test3', 'team': 'general', 'country': 'ru'},
            {'login': 'test4', 'team': 'general', 'country': 'ru'},
        ],
    },
    'calltaxi_by': {
        'items': [
            {'login': 'by_ivanov', 'team': 'general', 'country': 'by'},
            {'login': 'by_popov', 'team': 'general', 'country': 'by'},
            {'login': 'by_test3', 'team': 'general', 'country': 'by'},
            {'login': 'by_test4', 'team': 'general', 'country': 'by'},
        ],
    },
    'calldelivery_by': {
        'items': [
            {'login': 'by_ivanov', 'team': 'general', 'country': 'by'},
            {'login': 'by_petrov', 'team': 'general', 'country': 'by'},
            {'login': 'by_asmirnoff', 'team': 'general', 'country': 'by'},
            {'login': 'by_test1', 'team': 'general', 'country': 'by'},
            {'login': 'by_test2', 'team': 'general', 'country': 'by'},
        ],
    },
    'edasupport_ru': {'items': []},
    'edasupport_by': {'items': []},
}

EXPECTED_AGENT_CALLS = [
    {
        'project': 'calldelivery',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'ru',
    },
    {
        'project': 'calldelivery',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'by',
    },
    {
        'project': 'calltaxi',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'ru',
    },
    {
        'project': 'calltaxi',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'by',
    },
    {
        'project': 'edasupport',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'ru',
    },
    {
        'project': 'edasupport',
        'start_date': '2021-01-01',
        'stop_date': '2021-01-15',
        'country': 'by',
    },
]

DEFAULT_IN_DB_CALC_RULES = [
    {
        'start_date': datetime.date(2021, 1, 1),
        'stop_date': datetime.date(2021, 1, 13),
        'repeat': False,
        'countries': {'ru'},
        'logins': {'asmirnoff'},
        'enabled': True,
        'status': calculation_rules.STATUS_WAITING_AGENT,
        'description': '',
        'payment_draft_ids': None,
        'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
        'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
        'n_login': 'asmirnoff',
        'number_nsz_days': 4,
        'term_date': datetime.date(2021, 1, 16),
        'n_updated': datetime.datetime(2021, 1, 13, 0, 0, 0),
    },
    {
        'start_date': datetime.date(2021, 1, 1),
        'stop_date': datetime.date(2021, 1, 13),
        'repeat': False,
        'countries': {'ru'},
        'logins': {'bsidorov'},
        'enabled': True,
        'status': calculation_rules.STATUS_WAITING_AGENT,
        'description': '',
        'payment_draft_ids': None,
        'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
        'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
        'n_login': 'bsidorov',
        'number_nsz_days': 5,
        'term_date': datetime.date(2021, 1, 17),
        'n_updated': datetime.datetime(2021, 1, 13, 0, 0, 0),
    },
]

EXPECTED_AGENT_CALLS_2 = copy.deepcopy(EXPECTED_AGENT_CALLS)
for item in EXPECTED_AGENT_CALLS_2:
    item['start_date'] = '2021-01-16'
    item['stop_date'] = '2021-01-16'


async def _check_data(
        stq3_context,
        create_rule_date: datetime.date,
        mock_yandex_calendar,
        mock_oebs_get_sdel_term,
        mock_agent_employees_by_project,
        calendar_data,
        oebs_response,
        expected_calendar_calls,
        expected_oebs_calls,
        expected_agent_calls,
        expected_rules,
        expected_rules_amount,
):
    mocked_yandex_calendar = mock_yandex_calendar(calendar_data)
    mocked_oebs_get_sdel_term = mock_oebs_get_sdel_term(oebs_response)
    mocked_agent_employees = mock_agent_employees_by_project(
        AGENT_EMPLOYEES_RESP_MAPPING,
    )

    await stq_tasks.save_dismissal_rule(
        stq3_context, create_rule_date.strftime(constants.OEBS_DATE_FORMAT),
    )
    calendar_calls = [
        dict(mocked_yandex_calendar.next_call()['request'].args)
        for _ in expected_calendar_calls
    ]
    assert calendar_calls == expected_calendar_calls

    oebs_calls = [
        mocked_oebs_get_sdel_term.next_call()['request'].json
        for _ in expected_oebs_calls
    ]
    assert oebs_calls == expected_oebs_calls

    agent_employees_calls = [
        mocked_agent_employees.next_call()['request'].json
        for _ in expected_agent_calls
    ]
    agent_employees_calls = sorted(
        agent_employees_calls, key=lambda x: x['project'],
    )
    assert agent_employees_calls == expected_agent_calls

    async with stq3_context.pg.slave_pool.acquire() as conn:
        pg_rules = await conn.fetch(
            'SELECT start_date, '
            '   stop_date,'
            '   repeat,'
            '   countries,'
            '   logins,'
            '   enabled,'
            '   status,'
            '   description,'
            '   payment_draft_ids,'
            '   tariff_type, '
            '   rule_type, '
            '   n.login as n_login, '
            '   n.number_nsz_days, '
            '   n.term_date, '
            '   n.updated as n_updated '
            'FROM piecework.calculation_rule as c '
            '   LEFT JOIN piecework.dismissal_nsz_days as n '
            '   ON c.calculation_rule_id = n.calculation_rule_id '
            'ORDER BY n_login, tariff_type, countries',
        )
        pg_rules = [dict(rule) for rule in pg_rules]
        for rule in pg_rules:
            for key in rule:
                if isinstance(rule[key], list):
                    rule[key] = set(rule[key])
        assert pg_rules == expected_rules

        rules_count = await conn.fetchrow(
            'SELECT COUNT(calculation_rule_id) as amount '
            'FROM piecework.calculation_rule',
        )
        assert rules_count['amount'] == expected_rules_amount


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    PIECEWORK_CALCULATION_OEBS_DISMISSAL_DELTA_DAYS={'ru': 5, 'by': 4},
)
@pytest.mark.parametrize(
    'oebs_response, expected_oebs_calls, calendar_data, '
    'expected_calendar_calls, expected_rules,'
    'expected_agent_calls, expected_rules_amount',
    [
        (
            {'data': [{'login': 'ivanov', 'term_date': '15.01.2021'}]},
            [],
            {
                '2021-01-20+225': {
                    'holidays': [{'date': '2021-01-15', 'type': 'holiday'}],
                },
                '2021-01-19+149': {
                    'holidays': [{'date': '2021-01-15', 'type': 'holiday'}],
                },
            },
            [
                {
                    'from': '2021-01-15',
                    'to': '2021-01-20',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-19',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            DEFAULT_IN_DB_CALC_RULES,
            [],
            2,
        ),
        (
            {'data': []},
            [
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-23'},
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-19'},
            ],
            {
                '2021-01-20+225': {
                    'holidays': [
                        {'date': '2021-01-16', 'type': 'holiday'},
                        {'date': '2021-01-17', 'type': 'weekend'},
                    ],
                },
                '2021-01-22+225': {
                    'holidays': [
                        {'date': '2021-01-16', 'type': 'holiday'},
                        {'date': '2021-01-17', 'type': 'weekend'},
                        {'date': '2021-01-22', 'type': 'weekend'},
                    ],
                },
                '2021-01-23+225': {
                    'holidays': [
                        {'date': '2021-01-16', 'type': 'holiday'},
                        {'date': '2021-01-17', 'type': 'weekend'},
                        {'date': '2021-01-22', 'type': 'weekend'},
                    ],
                },
                '2021-01-19+149': {'holidays': []},
            },
            [
                {
                    'from': '2021-01-15',
                    'to': '2021-01-20',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-22',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-23',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-19',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            DEFAULT_IN_DB_CALC_RULES,
            [],
            2,
        ),
        (
            {'data': None},
            [
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-21'},
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-19'},
            ],
            {
                '2021-01-20+225': {
                    'holidays': [{'date': '2021-01-16', 'type': 'holiday'}],
                },
                '2021-01-21+225': {
                    'holidays': [{'date': '2021-01-16', 'type': 'holiday'}],
                },
                '2021-01-19+149': {'holidays': []},
            },
            [
                {
                    'from': '2021-01-15',
                    'to': '2021-01-20',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-21',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-19',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            DEFAULT_IN_DB_CALC_RULES,
            [],
            2,
        ),
        (
            {
                'data': [
                    {'login': 'ivanov', 'term_date': '15.01.2021'},
                    {'login': 'petrov', 'term_date': '16.01.2021'},
                    {'login': 'by_ivanov', 'term_date': '16.01.2021'},
                    {'login': 'by_petrov', 'term_date': '17.01.2021'},
                ],
            },
            [
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-20'},
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-19'},
            ],
            {
                '2021-01-20+225': {'holidays': []},
                '2021-01-19+149': {'holidays': []},
            },
            [
                {
                    'from': '2021-01-15',
                    'to': '2021-01-20',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-19',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            DEFAULT_IN_DB_CALC_RULES
            + [
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'by'},
                    'logins': {'by_ivanov', 'by_petrov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'by_ivanov',
                    'number_nsz_days': 1,
                    'term_date': datetime.date(2021, 1, 16),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'by'},
                    'logins': {'by_ivanov', 'by_petrov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'by_petrov',
                    'number_nsz_days': 1,
                    'term_date': datetime.date(2021, 1, 17),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'ivanov', 'petrov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'ivanov',
                    'number_nsz_days': 1,
                    'term_date': datetime.date(2021, 1, 15),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'ivanov', 'petrov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'petrov',
                    'number_nsz_days': 1,
                    'term_date': datetime.date(2021, 1, 16),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'by'},
                    'logins': {'by_ivanov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': None,
                    'number_nsz_days': None,
                    'term_date': None,
                    'n_updated': None,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'ivanov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': None,
                    'number_nsz_days': None,
                    'term_date': None,
                    'n_updated': None,
                },
            ],
            EXPECTED_AGENT_CALLS,
            6,
        ),
        (
            {
                'data': [
                    {'login': 'asmirnoff', 'term_date': '16.01.2021'},
                    {'login': 'bsidorov', 'term_date': '19.01.2021'},
                    {'login': 'popov', 'term_date': '20.01.2021'},
                    {'login': 'not_agent_login', 'term_date': '20.01.2021'},
                ],
            },
            [
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-20'},
                {'Date_from': '2021-01-15', 'Date_to': '2021-01-19'},
            ],
            {
                '2021-01-20+225': {'holidays': []},
                '2021-01-19+149': {'holidays': []},
            },
            [
                {
                    'from': '2021-01-15',
                    'to': '2021-01-20',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-15',
                    'to': '2021-01-19',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            [
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 13),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'asmirnoff'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_AGENT,
                    'description': '',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'asmirnoff',
                    'number_nsz_days': 4,
                    'term_date': datetime.date(2021, 1, 16),
                    'n_updated': datetime.datetime(2021, 1, 13, 0, 0, 0),
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'bsidorov', 'popov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'bsidorov',
                    'number_nsz_days': 3,
                    'term_date': datetime.date(2021, 1, 19),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 15),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'bsidorov', 'popov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'popov',
                    'number_nsz_days': 2,
                    'term_date': datetime.date(2021, 1, 20),
                    'n_updated': NOW,
                },
                {
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 13),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'bsidorov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_AGENT,
                    'description': '',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CALL_TAXI_UNIFIED,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': None,
                    'number_nsz_days': None,
                    'term_date': None,
                    'n_updated': None,
                },
            ],
            EXPECTED_AGENT_CALLS,
            3,
        ),
    ],
)
async def test_save_dismissal_rule(
        stq3_context,
        stq,
        mock_oebs_get_sdel_term,
        mock_uuid4_list,
        mock_agent_employees_by_project,
        mock_yandex_calendar,
        oebs_response,
        expected_oebs_calls,
        calendar_data,
        expected_calendar_calls,
        expected_rules,
        expected_agent_calls,
        expected_rules_amount,
):
    mock_uuid4_list()
    await _check_data(
        stq3_context,
        datetime.date(2021, 1, 15),
        mock_yandex_calendar,
        mock_oebs_get_sdel_term,
        mock_agent_employees_by_project,
        calendar_data,
        oebs_response,
        expected_calendar_calls,
        expected_oebs_calls,
        expected_agent_calls,
        expected_rules,
        expected_rules_amount,
    )


@pytest.mark.now(START_NOW.isoformat())
@pytest.mark.config(
    PIECEWORK_CALCULATION_OEBS_DISMISSAL_DELTA_DAYS={'ru': 5, 'by': 4},
)
@pytest.mark.parametrize(
    'oebs_response, expected_oebs_calls, calendar_data, '
    'expected_calendar_calls, expected_rules,'
    'expected_agent_calls, expected_rules_amount',
    [
        (
            {'data': [{'login': 'petrov', 'term_date': '18.01.2021'}]},
            [
                {'Date_from': '2021-01-16', 'Date_to': '2021-01-21'},
                {'Date_from': '2021-01-16', 'Date_to': '2021-01-20'},
            ],
            {
                '2021-01-21+225': {'holidays': []},
                '2021-01-20+149': {'holidays': []},
            },
            [
                {
                    'from': '2021-01-16',
                    'to': '2021-01-21',
                    'for': '225',
                    'outMode': 'holidays',
                },
                {
                    'from': '2021-01-16',
                    'to': '2021-01-20',
                    'for': '149',
                    'outMode': 'holidays',
                },
            ],
            DEFAULT_IN_DB_CALC_RULES
            + [
                {
                    'start_date': datetime.date(2021, 1, 16),
                    'stop_date': datetime.date(2021, 1, 16),
                    'repeat': False,
                    'countries': {'ru'},
                    'logins': {'petrov'},
                    'enabled': True,
                    'status': calculation_rules.STATUS_WAITING_RESTART,
                    'description': 'Created',
                    'payment_draft_ids': None,
                    'tariff_type': constants.TARIFF_TYPE_CARGO_CALLCENTER,
                    'rule_type': constants.CALCULATION_RULE_DISMISSAL_TYPE,
                    'n_login': 'petrov',
                    'number_nsz_days': 1,
                    'term_date': datetime.date(2021, 1, 18),
                    'n_updated': START_NOW,
                },
            ],
            EXPECTED_AGENT_CALLS_2,
            3,
        ),
    ],
)
async def test_save_dismissal_rule_start_date(
        stq3_context,
        stq,
        mock_oebs_get_sdel_term,
        mock_uuid4_list,
        mock_agent_employees_by_project,
        mock_yandex_calendar,
        oebs_response,
        expected_oebs_calls,
        calendar_data,
        expected_calendar_calls,
        expected_rules,
        expected_agent_calls,
        expected_rules_amount,
):
    mock_uuid4_list()
    await _check_data(
        stq3_context,
        datetime.date(2021, 1, 16),
        mock_yandex_calendar,
        mock_oebs_get_sdel_term,
        mock_agent_employees_by_project,
        calendar_data,
        oebs_response,
        expected_calendar_calls,
        expected_oebs_calls,
        expected_agent_calls,
        expected_rules,
        expected_rules_amount,
    )
