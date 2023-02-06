# pylint: disable=redefined-outer-name
# pylint: disable=C0302
import pytest


import agent.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['agent.generated.service.pytest_plugins']

RESPONSE_V1_OPERATOR = {
    'yandex_uid': '1130000003218796',
    'login': 'rifat4@taxi.auto.connect-test.tk',
    'full_name': 'Gsdf Hsfc',
    'callcenter_id': 'krasnodar_cc',
    'state': 'ready',
    'role_in_telephony': 'ru_disp_operator',
    'phone': 'sdfsdfdsfsdf',
    'employment_date': '2020-08-28',
    'revision_id': '2021-08-24T09:30:20.465315 +0000',
    'skills': ['lavka'],
    'schedules': [
        {
            'record_id': 471,
            'schedule_fixed': False,
            'starts_at': '2021-02-06T00:00:00+03:00',
            'schedule_type_info': {
                'schedule_type_id': 19,
                'revision_id': '2021-06-11T09:06:13.589411 +0000',
                'schedule_alias': '10-20 / 2*5',
                'schedule': [2, 5],
                'first_weekend': False,
                'start': '08:00:00',
                'duration_minutes': 600,
            },
            'revision_id': '2021-02-09T14:07:33.085535 +0000',
            'skills': ['lavka'],
        },
    ],
    'roles': [],
}

RESPONSE_TIMETABLE = {
    'operator': {
        'yandex_uid': '1130000003218796',
        'revision_id': '2021-08-24T09:30:20.465315 +0000',
        'callcenter_id': 'krasnodar_cc',
        'login': 'rifat4@taxi.auto.connect-test.tk',
        'state': 'ready',
        'skills': ['lavka'],
        'full_name': 'Gsdf Hsfc',
        'schedules': [
            {
                'record_id': 471,
                'schedule_fixed': True,
                'starts_at': '2021-02-06T00:00:00+03:00',
                'schedule_type_info': {'schedule_type_id': 19},
                'revision_id': '2021-02-09T14:07:33.085535 +0000',
                'skills': ['lavka'],
            },
        ],
    },
    'shifts': [
        {
            'start': '2021-01-02T10:00:00+03:00',
            'duration_minutes': 540,
            'skill': 'lavka',
            'shift_id': 50394,
            'operators_schedule_types_id': 471,
            'frozen': False,
            'type': 'common',
            'breaks': [
                {
                    'start': '2021-01-02T12:00:00+03:00',
                    'duration_minutes': 30,
                    'id': 29237,
                    'type': 'technical',
                },
                {
                    'start': '2021-01-02T16:00:00+03:00',
                    'duration_minutes': 30,
                    'id': 29238,
                    'type': 'lunchtime',
                },
                {
                    'start': '2021-01-02T17:30:00+03:00',
                    'duration_minutes': 30,
                    'id': 29239,
                    'type': 'technical',
                },
                {
                    'start': '2021-01-02T18:45:00+03:00',
                    'duration_minutes': 15,
                    'id': 29240,
                    'type': 'technical',
                },
            ],
        },
    ],
    'absences': [],
    'actual_shifts': [],
}

RESPONSE_TIMETABLE_ONLYSHIFT = {
    'operator': {
        'yandex_uid': '1130000003218796',
        'revision_id': '2021-08-24T09:30:20.465315 +0000',
        'callcenter_id': 'krasnodar_cc',
        'login': 'rifat4@taxi.auto.connect-test.tk',
        'state': 'ready',
        'skills': ['lavka'],
        'full_name': 'Gsdf Hsfc',
        'schedules': [
            {
                'record_id': 471,
                'schedule_fixed': True,
                'starts_at': '2021-02-06T00:00:00+03:00',
                'schedule_type_info': {'schedule_type_id': 19},
                'revision_id': '2021-02-09T14:07:33.085535 +0000',
                'skills': ['lavka'],
            },
        ],
    },
    'shifts': [
        {
            'start': '2021-01-02T10:00:00+03:00',
            'duration_minutes': 540,
            'skill': 'lavka',
            'shift_id': 50394,
            'operators_schedule_types_id': 471,
            'frozen': False,
            'type': 'common',
        },
    ],
    'absences': [],
    'actual_shifts': [],
}

RESPONSE_PIECEWORK_CALCULATION = {
    'calculation': {'commited': False},
    'logins': [
        {
            'login': 'webalex',
            'bo': {
                'daytime_cost': 2046.0,
                'night_cost': 2092.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 0.0,
            'benefit_details': {
                'hour_cost': 99,
                'workshifts_duration_sec': 50,
                'plan_workshifts_duration_sec': 100,
            },
        },
        {
            'login': 'mikh-vasily',
            'bo': {
                'daytime_cost': 10.0,
                'night_cost': 20.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 0.0,
            'benefit_details': {},
        },
        {
            'login': 'calltaxi_chief',
            'bo': {
                'daytime_cost': 30.0,
                'night_cost': 30.0,
                'holidays_daytime_cost': 1.0,
                'holidays_night_cost': 1.5,
            },
            'benefits': 0.0,
            'benefit_details': {},
        },
        {
            'login': 'lavkasupport_chief',
            'bo': {
                'daytime_cost': 10.0,
                'night_cost': 20.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 0.0,
            'benefit_details': {
                'workshifts_duration_sec': 50,
                'min_hour_cost': 100,
            },
        },
        {
            'login': 'lavkasupport_user',
            'bo': {
                'daytime_cost': 30.0,
                'night_cost': 30.0,
                'holidays_daytime_cost': 1.0,
                'holidays_night_cost': 1.5,
            },
            'benefits': 0.0,
            'benefit_details': {
                'workshifts_duration_sec': 50,
                'min_hour_cost': 100,
            },
        },
        {
            'login': 'taxisupport_cc_chief',
            'bo': {
                'daytime_cost': 10.0,
                'night_cost': 20.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 0.0,
            'benefit_details': {
                'workshifts_duration_sec': 50,
                'min_hour_cost': 100,
            },
        },
        {
            'login': 'taxisupport_cc_user',
            'bo': {
                'daytime_cost': 30.0,
                'night_cost': 30.0,
                'holidays_daytime_cost': 1.0,
                'holidays_night_cost': 1.5,
            },
            'benefits': 0.0,
            'benefit_details': {
                'workshifts_duration_sec': 50,
                'min_hour_cost': 100,
            },
        },
    ],
}

RESPONSE_PIECEWORK_CALCULATION_RU = {
    'calculation': {'commited': False},
    'logins': [
        {
            'login': 'webalex',
            'bo': {
                'daytime_cost': 10000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 97.5,
                'rating_pos': 1,
                'benefits_per_bo': 0.5,
            },
        },
        {
            'login': 'liambaev',
            'bo': {
                'daytime_cost': 10000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 90,
                'rating_pos': 2,
                'benefits_per_bo': 0.5,
            },
        },
        {
            'login': 'piskarev',
            'bo': {
                'daytime_cost': 10000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 81,
                'rating_pos': 3,
                'benefits_per_bo': 0.2,
            },
        },
    ],
}

RESPONSE_PIECEWORK_CALCULATION_BY = {
    'calculation': {'commited': False},
    'logins': [
        {
            'login': 'akozhevina',
            'bo': {
                'daytime_cost': 10000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 71,
                'rating_pos': 4,
                'benefits_per_bo': 0.2,
            },
        },
        {
            'login': 'simon',
            'bo': {
                'daytime_cost': 0.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 0.0,
            'benefit_details': {
                'rating': 5,
                'rating_pos': 5,
                'benefits_per_bo': 0.0,
            },
        },
    ],
}

TOPALYAN_RESPONSE = {
    'calculation': {'commited': False},
    'logins': [
        {
            'login': 'a-topalyan',
            'bo': {
                'daytime_cost': 10000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 0.975,
                'rating_pos': 1,
                'benefits_per_bo': 0.5,
            },
        },
    ],
}


WEBALEXBOT_RESPONSE = {
    'calculation': {'commited': False},
    'logins': [
        {
            'login': 'webalexbot',
            'bo': {
                'daytime_cost': 20000.0,
                'night_cost': 0.0,
                'holidays_daytime_cost': 0.0,
                'holidays_night_cost': 0.0,
            },
            'benefits': 5000.0,
            'benefit_details': {
                'rating': 0.975,
                'rating_pos': 1,
                'benefits_per_bo': 0.5,
            },
        },
    ],
}

RESPONSE_MOE_FIRST_PAGE = {
    'count': 5,
    'next': 2,
    'previous': None,
    'results': [
        {
            'login': 'agent_1',
            'total_result': {'points': 1, 'max_points': 2, 'percent': 50},
            'clessons': [
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 0,
                        'max_points': 10,
                        'percent': 0,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 5,
                        'max_points': 10,
                        'percent': 50,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 10,
                        'max_points': 10,
                        'percent': 100,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
            ],
        },
        {
            'login': 'agent_2',
            'total_result': {'points': 0, 'max_points': 0, 'percent': 0},
            'clessons': [],
        },
        {
            'login': 'agent_3',
            'total_result': {'points': 0, 'max_points': 0, 'percent': 0},
            'clessons': [],
        },
    ],
}


RESPONSE_MOE_SECOND_PAGE = {
    'count': 5,
    'next': None,
    'previous': 1,
    'results': [
        {
            'login': 'agent_4',
            'total_result': {'points': 1, 'max_points': 2, 'percent': 50},
            'clessons': [
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 10,
                        'max_points': 10,
                        'percent': 80,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
            ],
        },
        {
            'login': 'agent_5',
            'total_result': {'points': 1, 'max_points': 10, 'percent': 10},
            'clessons': [
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 1,
                        'max_points': 10,
                        'percent': 10,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 1,
                        'max_points': 10,
                        'percent': 10,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
                {
                    'clesson_id': 1,
                    'result': {
                        'points': 1,
                        'max_points': 10,
                        'percent': 10,
                        'last_modified': '2021-01-01T00:00:00Z',
                    },
                },
            ],
        },
    ],
}

WFM_OPERATOR_URL = 'workforce-management-py3/v1/operator'
WFM_TIMETABLE_URL = 'workforce-management-py3/v1/operators/timetable/values'
PIECEWORK_CALCULATION_URL = 'piecework-calculation/v1/calculation/load'
PIECEWORK_CALCULATION_DETAILS_URL = (
    'piecework-calculation/v1/calculation/detail/load'
)
PIECEWORK_RESERVE_CURRENT_URL = 'piecework-calculation/v1/reserve/current'

PIECEWORK_MAPPING_LOGINS_PAYDAY = (
    'piecework-calculation/v1/payday/mapping-logins'
)

BILLING_BALANCE_URL = 'billing-reports/v1/balances/select'
BILLING_ORDERS_URL = 'billing-orders/v2/execute'
PIECEWORK_CALCULATION_DAYLY_LOAD = (
    'piecework-calculation/v1/calculation/daily/load'
)
MOE_COURSE_RESULTS_URL = 'moe/api/v3/courses/1474/students_results/'
PERSONAL_URL_BULK_STORE_PHONE = 'personal/v2/phones/bulk_store'
PERSONAL_URL_BULK_STORE_TELEGRAM = 'personal/v2/telegram_logins/bulk_store'
PERSONAL_URL_BULK_RETRIEVE = 'personal/v1/phones/bulk_retrieve'
PERSONAL_URL_BULK_RETRIEVE_TELEGRAMS = (
    'personal/v1/telegram_logins/bulk_retrieve'
)
PERSONAL_STORE_PHONES_URL = 'personal/v1/phones/store'
PAYDAY_EMPLOYEE_URL = 'payday/api/employee'
OEBS_PRIMERY_URL = 'oebs/rest/primaryAssg'

PERSONAL_FIND_URL = '/personal/v1/phones/find'


def billing_response(login: str, project: str, balance: int):
    return {
        'entries': [
            {
                'account': {
                    'account_id': 61460104,
                    'entity_external_id': 'staff/%s' % login,
                    'agreement_id': project,
                    'currency': 'XXX',
                    'sub_account': 'deposit',
                },
                'balances': [
                    {
                        'accrued_at': '2021-10-19T00:00:00.000000+00:00',
                        'balance': str(balance),
                        'last_entry_id': 1302710104,
                        'last_created': '2021-10-18T08:41:56.867066+00:00',
                    },
                ],
            },
        ],
    }


@pytest.fixture(autouse=False)
def mock_wfm_operators(mockserver):
    @mockserver.json_handler(WFM_OPERATOR_URL, prefix=False)
    def _fetch(request):
        return RESPONSE_V1_OPERATOR

    return _fetch


@pytest.fixture(autouse=False)
def mock_wfm_timetable(mockserver):
    @mockserver.json_handler(WFM_TIMETABLE_URL, prefix=False)
    def _fetch(request):
        assert request.query.get('datetime_from') in [
            '2021-01-02T00:00:00+03:00',
            '2021-01-02T16:00:00+03:00',
        ]
        assert request.query.get('datetime_to') == '2021-01-03T00:00:00+03:00'

        return RESPONSE_TIMETABLE

    return _fetch


@pytest.fixture(autouse=False)
def mock_wfm_timetable_onlyshift(mockserver):
    @mockserver.json_handler(WFM_TIMETABLE_URL, prefix=False)
    def _fetch(request):
        assert (
            request.query.get('datetime_from') == '2021-01-02T00:00:00+03:00'
        )
        assert request.query.get('datetime_to') == '2021-01-03T00:00:00+03:00'
        return RESPONSE_TIMETABLE_ONLYSHIFT

    return _fetch


@pytest.fixture(autouse=False)
async def mock_wfm_operators_fail(mockserver):
    @mockserver.json_handler(WFM_OPERATOR_URL, prefix=False)
    def _fetch(reqeust):
        return mockserver.make_response(
            status=404,
            json={
                'message': 'Operator not found in system',
                'code': 'not_found',
            },
        )


@pytest.fixture(autouse=False)
async def mock_wfm_timetable_fail(mockserver):
    @mockserver.json_handler(WFM_TIMETABLE_URL, prefix=False)
    def _fetch(reqeust):
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_piecework_calc_load(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_URL, prefix=False)
    def _fetch(request):
        return RESPONSE_PIECEWORK_CALCULATION

    return _fetch


@pytest.fixture(autouse=False)
def mock_piecework_rating(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_URL, prefix=False)
    def _fetch(request):
        body = request.json
        if body['country'] == 'ru':
            return RESPONSE_PIECEWORK_CALCULATION_RU
        return RESPONSE_PIECEWORK_CALCULATION_BY

    return _fetch


@pytest.fixture(autouse=False)
def mock_piecework_response(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_URL, prefix=False)
    def _fetch(request):
        body = request.json
        assert body['tariff_type'] == 'call-taxi-unified'
        if body['logins'] == ['a-topalyan']:
            assert body['country'] == 'by'
            return TOPALYAN_RESPONSE
        if body['logins'] == ['webalexbot']:
            assert body['country'] == 'ru'
            return mockserver.make_response(status=500, json={})
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_piecework_details(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_DETAILS_URL, prefix=False)
    def _fetch(request):
        body = request.json
        if body['login'] == 'webalex':
            return {
                'login': body['login'],
                'start_date': body['start_date'],
                'stop_date': body['stop_date'],
                'details': [
                    {
                        'line': 'first',
                        'actions': [
                            {
                                'cost_condition_key': 'close',
                                'cost': 10,
                                'count': 11,
                            },
                        ],
                    },
                ],
            }
        if body['login'] == 'liambaev':
            return {
                'login': body['login'],
                'start_date': body['start_date'],
                'stop_date': body['stop_date'],
                'details': [
                    {
                        'line': 'urgent',
                        'actions': [
                            {
                                'cost_condition_key': 'close',
                                'cost': 10,
                                'count': 10,
                            },
                            {
                                'cost_condition_key': 'comment',
                                'cost': 6.125,
                                'count': 10,
                            },
                        ],
                    },
                ],
            }
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_piecework_calculation_load(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_URL, prefix=False)
    def _fetch(request):
        body = request.json
        if body['logins'] == ['webalex']:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {
                            'login': 'webalex',
                            'bo': {
                                'daytime_cost': 12.12123,
                                'night_cost': 13.13123,
                                'holidays_daytime_cost': 14.14123,
                                'holidays_night_cost': 15.15123,
                            },
                            'benefit_details': {
                                'rating_prcnt': 12.12123,
                                'discipline_ratio': 13.13123,
                                'benefits_per_bo': 0.14123,
                                'workshifts_duration_sec': 10,
                                'plan_workshifts_duration_sec': 2,
                                'min_hour_cost': 13,
                            },
                            'benefits': 12,
                            'extra_costs': [
                                {
                                    'source': 'tracker',
                                    'daytime_bo': 1.0,
                                    'night_bo': 1.0,
                                    'holidays_daytime_bo': 1.0,
                                    'holidays_night_bo': 1.0,
                                },
                                {
                                    'source': 'angryspace',
                                    'daytime_bo': 2.0,
                                    'night_bo': 2.0,
                                    'holidays_daytime_bo': 2.0,
                                    'holidays_night_bo': 2.0,
                                },
                            ],
                            'corrections': {
                                'intermediate': {
                                    'daytime_bo': 10,
                                    'night_bo': 10,
                                    'holidays_daytime_bo': 10,
                                    'holidays_night_bo': 10,
                                },
                            },
                        },
                    ],
                },
            )
        if body['logins'] == ['liambaev']:
            return mockserver.make_response(
                json={'calculation': {'commited': True}, 'logins': []},
            )
        if body['logins'] == ['cargo_callcenter_user']:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {
                            'login': 'cargo_callcenter_user',
                            'bo': {
                                'daytime_cost': 9.12123,
                                'night_cost': 19.13123,
                                'holidays_daytime_cost': 11.14123,
                                'holidays_night_cost': 12.15123,
                            },
                            'benefit_details': {
                                'rating_prcnt': 12.12123,
                                'discipline_ratio': 13.13123,
                                'benefits_per_bo': 0.14123,
                                'workshifts_duration_sec': 10,
                                'plan_workshifts_duration_sec': 2,
                            },
                            'benefits': 12,
                            'extra_costs': [
                                {
                                    'source': 'tracker',
                                    'daytime_bo': 1.0,
                                    'night_bo': 1.0,
                                    'holidays_daytime_bo': 1.0,
                                    'holidays_night_bo': 1.0,
                                },
                                {
                                    'source': 'angryspace',
                                    'daytime_bo': 2.0,
                                    'night_bo': 2.0,
                                    'holidays_daytime_bo': 2.0,
                                    'holidays_night_bo': 2.0,
                                },
                            ],
                        },
                    ],
                },
            )
        if set(body['logins']) == {'justmark0', 'support_taxi_user'}:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {
                            'login': 'justmark0',
                            'bo': {
                                'daytime_cost': 11.12123,
                                'night_cost': 12.13123,
                                'holidays_daytime_cost': 13.14123,
                                'holidays_night_cost': 14.15123,
                            },
                            'benefit_details': {
                                'rating_prcnt': 12.12123,
                                'discipline_ratio': 13.13123,
                                'benefits_per_bo': 0.14123,
                                'workshifts_duration_sec': 10,
                                'plan_workshifts_duration_sec': 2,
                            },
                            'benefits': 12,
                            'extra_costs': [
                                {
                                    'source': 'tracker',
                                    'daytime_bo': 1.0,
                                    'night_bo': 1.0,
                                    'holidays_daytime_bo': 1.0,
                                    'holidays_night_bo': 1.0,
                                },
                                {
                                    'source': 'angryspace',
                                    'daytime_bo': 2.0,
                                    'night_bo': 2.0,
                                    'holidays_daytime_bo': 2.0,
                                    'holidays_night_bo': 2.0,
                                },
                            ],
                        },
                        {
                            'login': 'support_taxi_user',
                            'bo': {
                                'daytime_cost': 10.12123,
                                'night_cost': 11.13123,
                                'holidays_daytime_cost': 12.14123,
                                'holidays_night_cost': 13.15123,
                            },
                            'benefit_details': {
                                'rating_prcnt': 12.12123,
                                'discipline_ratio': 13.13123,
                                'benefits_per_bo': 0.14123,
                                'workshifts_duration_sec': 10,
                                'plan_workshifts_duration_sec': 2,
                            },
                            'benefits': 12,
                            'extra_costs': [
                                {
                                    'source': 'tracker',
                                    'daytime_bo': 1.0,
                                    'night_bo': 1.0,
                                    'holidays_daytime_bo': 1.0,
                                    'holidays_night_bo': 1.0,
                                },
                                {
                                    'source': 'angryspace',
                                    'daytime_bo': 2.0,
                                    'night_bo': 2.0,
                                    'holidays_daytime_bo': 2.0,
                                    'holidays_night_bo': 2.0,
                                },
                            ],
                        },
                    ],
                },
            )
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_picework_reserve_current(mockserver):
    @mockserver.json_handler(PIECEWORK_RESERVE_CURRENT_URL, prefix=False)
    def _fetch(request):
        body = request.json
        if set(body['logins']) == {'cargo_callcenter_user', 'justmark0'}:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {'login': 'justmark0', 'value': 100},
                        {'login': 'cargo_callcenter_user', 'value': 150},
                    ],
                },
            )
        if set(body['logins']) == {
                'absent_login',
                'disabled_login',
                'login_with_minimum_info',
                'not_compendium_user',
                'not_on_piece_login',
                'not_use_reserves_login',
                'regular_login',
                'returned_after_dismiss_user',
                'use_reserves_login',
        }:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {'login': 'absent_login', 'value': 10},
                        {'login': 'disabled_login', 'value': 10},
                        {'login': 'not_on_piece_login', 'value': 10},
                        {'login': 'not_use_reserves_login', 'value': -10},
                        {'login': 'regular_login', 'value': 12},
                        {'login': 'use_reserves_login', 'value': -10},
                    ],
                },
            )
        if body['logins'] == ['a-topalyan']:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [{'login': 'a-topalyan', 'value': 1234.0}],
                },
            )
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_billing_balance(mockserver):
    @mockserver.json_handler(BILLING_BALANCE_URL, prefix=False)
    def _fetch(reqeust):
        body = reqeust.json
        if body['accounts'][0]['entity_external_id'] == 'staff/mikh-vasily':
            return billing_response('staff/mikh-vasily', 'calltaxi', 120)
        if body['accounts'][0]['entity_external_id'] == 'staff/webalex':
            return billing_response('staff/webalex', 'calltaxi', 220)
        if body['accounts'][0]['entity_external_id'] == 'staff/slon':
            return billing_response('staff/slon', 'taxisupport', 0)
        if body['accounts'][0]['entity_external_id'] == 'staff/korol':
            return billing_response('staff/korol', 'taxisupport', 0)
        if body['accounts'][0]['entity_external_id'] == 'staff/meetka':
            return billing_response('staff/meetka', 'taxisupport', 0)
        return mockserver.make_response(status=500, json={})


@pytest.fixture(autouse=False)
def mock_billing_orders(mockserver):
    @mockserver.json_handler(BILLING_ORDERS_URL, prefix=False)
    def _fetch(request):
        return {
            'doc_id': 11223344,
            'kind': request.json['kind'],
            'topic': request.json['topic'],
            'external_ref': request.json['external_ref'],
            'event_at': request.json['event_at'],
            'data': request.json['data'],
            'created': '2021-10-11T10:01:02.0+00:00',
        }

    return _fetch


@pytest.fixture(autouse=False)
async def mock_billing_not_coins(mockserver):
    @mockserver.json_handler(BILLING_ORDERS_URL, prefix=False)
    def _fetch(reqeust):
        return mockserver.make_response(
            status=409,
            json={'message': 'Not enough coins', 'code': 'execute_error'},
        )


@pytest.fixture(autouse=False)
async def mock_billing_bad_request(mockserver):
    @mockserver.json_handler(BILLING_ORDERS_URL, prefix=False)
    def _fetch(request):
        if request.json['topic'] == 'agent/coins/404':
            return mockserver.make_response(
                json={'message': 'Bad kind', 'code': 'value_error'},
                status=404,
            )
        return mockserver.make_response(
            'The event was rejected because it had '
            'occurred more than 240 hours ago',
            status=400,
        )


@pytest.fixture
def mock_piecework_daily_load(mockserver):
    def _wrap(response):
        @mockserver.json_handler(
            PIECEWORK_CALCULATION_DAYLY_LOAD, prefix=False,
        )
        def _piecework_daily(request):
            return response

        return _piecework_daily

    return _wrap


@pytest.fixture(autouse=False)
def mock_staff_gap_api(mockserver):
    @mockserver.json_handler(
        'staff/gap-api/api/export_gaps.json', prefix=False,
    )
    def _fetch(request):
        return mockserver.make_response(
            status=200,
            json={
                'persons': {
                    'absent_login': [
                        {
                            'id': 430968,
                            'workflow': 'vacation',
                            'date_from': '2016-05-23T00:00:00',
                            'date_to': '2016-05-24T00:00:00',
                            'comment': '',
                            'work_in_absence': False,
                        },
                    ],
                    'webalex': [
                        {
                            'id': 430968,
                            'workflow': 'vacation',
                            'date_from': '2016-05-23T00:00:00',
                            'date_to': '2016-05-24T00:00:00',
                            'comment': '',
                            'work_in_absence': False,
                        },
                    ],
                    'liambaev': [
                        {
                            'id': 430968,
                            'workflow': 'duty',
                            'date_from': '2016-05-23T00:00:00',
                            'date_to': '2016-05-24T00:00:00',
                            'comment': '',
                            'work_in_absence': False,
                        },
                    ],
                },
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_staff_groups_api(mockserver):
    @mockserver.json_handler('staff-production/v3/groups', prefix=False)
    def _fetch(request):
        if 'page=1' in request.url:
            return mockserver.make_response(
                json={
                    'links': {'next': 'next_page'},
                    'result': [
                        {
                            'type': 'department',
                            'url': 'ext',
                            'is_deleted': False,
                            'name': 'Внешние консультанты',
                            'level': 0,
                        },
                    ],
                },
            )
        if 'page=2' in request.url:
            return mockserver.make_response(
                json={
                    'links': {'prev': 'prev_page'},
                    'result': [
                        {
                            'type': 'department',
                            'url': 'taxi_dep72956_dep20857',
                            'is_deleted': False,
                            'name': 'Внешние консультанты дочерний элемент',
                            'level': 1,
                            'parent': {'url': 'ext'},
                            'department': {
                                'heads': [
                                    {
                                        'role': 'chief',
                                        'person': {'login': 'webalex'},
                                    },
                                    {
                                        'role': 'chief',
                                        'person': {'login': 'no_login'},
                                    },
                                ],
                            },
                        },
                    ],
                },
            )
        return mockserver.json_response({})

    return _fetch


STAFF_PERSONS = {
    'piskarev': {'login': 'piskarev'},
    'webalex': {
        'phones': [
            {
                'kind': 'common',
                'protocol': 'voice',
                'description': '',
                'number': '+7 495 000 00 00',
                'for_digital_sign': False,
                'type': 'home',
                'is_main': True,
            },
        ],
        'login': 'webalex',
        'uid': '12345',
        'guid': '12345',
        'personal': {'birthday': '1980-11-21'},
        'name': {
            'first': {'ru': 'Александр', 'en': 'Alexandr'},
            'last': {'ru': 'Иванов', 'en': 'Ivanov'},
        },
        'official': {
            'affiliation': 'yandex',
            'is_dismissed': True,
            'join_at': '2016-06-02',
            'quit_at': None,
            'organization': {'name': 'Яндекс'},
            'is_robot': False,
        },
        'department_group': {'url': 'something_dep'},
        'yandex': {'login': 'ssaneka'},
    },
    'liambaev': {
        'login': 'liambaev',
        'phones': [
            {
                'kind': 'common',
                'protocol': 'voice',
                'description': '',
                'number': '+7 495 000 00 00',
                'for_digital_sign': False,
                'type': 'home',
                'is_main': True,
            },
        ],
        'uid': '12347',
        'guid': '12347',
        'personal': {'birthday': '1981-11-21'},
        'name': {
            'first': {'ru': 'Лиам', 'en': 'LIAM'},
            'last': {'ru': 'Баев', 'en': 'BAEV'},
        },
        'official': {
            'affiliation': 'yandex',
            'is_dismissed': True,
            'join_at': '2016-06-02',
            'quit_at': None,
            'organization': {'name': 'Яндекс'},
            'is_robot': False,
        },
        'department_group': {'url': 'something_dep'},
        'yandex': {'login': 'liambaev'},
    },
    'orangevl': {
        'login': 'orangevl',
        'phones': [
            {
                'kind': 'common',
                'protocol': 'voice',
                'description': '',
                'number': '+7 495 000 00 00',
                'for_digital_sign': False,
                'type': 'home',
                'is_main': True,
            },
        ],
        'uid': '141111',
        'guid': '141111',
        'personal': {'birthday': '1982-11-21'},
        'name': {
            'first': {'ru': 'Семён', 'en': 'Simon'},
            'last': {'ru': 'Решетняк', 'en': 'Reshetnyak'},
        },
        'official': {
            'affiliation': 'external',
            'is_dismissed': True,
            'join_at': '2010-01-01',
            'quit_at': None,
            'organization': {'name': 'Яндекс Деньги'},
            'is_robot': False,
        },
        'department_group': {'url': 'something_dep'},
        'yandex': {'login': None},
    },
    'robot-support-taxi': {
        'login': 'robot-support-taxi',
        'phones': [
            {
                'kind': 'common',
                'protocol': 'voice',
                'description': '',
                'number': '+7 495 000 00 00',
                'for_digital_sign': False,
                'type': 'home',
                'is_main': True,
            },
        ],
        'uid': '15',
        'guid': '15',
        'personal': {'birthday': '1983-11-21'},
        'name': {
            'first': {'ru': 'robot', 'en': 'robot'},
            'last': {'ru': 'robot', 'en': 'robot'},
        },
        'official': {
            'affiliation': 'external',
            'is_dismissed': True,
            'join_at': '2000-01-01',
            'quit_at': None,
            'organization': {'name': 'Яндекс Драйв'},
            'is_robot': True,
        },
        'department_group': {'url': 'yandex'},
        'telegram_accounts': [{'id': 1, 'value': 'telegram_login'}],
    },
    'dismissed_user': {
        'login': 'dismissed_user',
        'phones': [
            {
                'kind': 'common',
                'protocol': 'voice',
                'description': '',
                'number': '+7 495 000 00 00',
                'for_digital_sign': False,
                'type': 'home',
                'is_main': True,
            },
        ],
        'uid': '15',
        'guid': '15',
        'name': {
            'first': {'ru': 'Dismissed_user', 'en': 'Dismissed_user'},
            'last': {'ru': 'Dismissed_user', 'en': 'Dismissed_user'},
        },
        'official': {
            'affiliation': 'yandex',
            'is_dismissed': True,
            'join_at': '2000-01-01',
            'quit_at': '2021-01-01',
            'organization': {'name': 'Яндекс Драйв'},
            'is_robot': False,
        },
        'department_group': {'url': 'yandex'},
        'telegram_accounts': [{'id': 1, 'value': 'telegram_login'}],
    },
}


@pytest.fixture(autouse=False)
def mock_staff_persons_api(mockserver):
    @mockserver.json_handler('staff-production/v3/persons', prefix=False)
    def _fetch(request):
        if '_page=1' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('webalex')],
                    'pages': len(STAFF_PERSONS),
                    'page': 1,
                },
            )
        if '_page=2' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('liambaev')],
                    'pages': len(STAFF_PERSONS),
                    'page': 2,
                },
            )
        if '_page=3' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('orangevl')],
                    'pages': len(STAFF_PERSONS),
                    'page': 3,
                },
            )
        if '_page=4' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('robot-support-taxi')],
                    'pages': len(STAFF_PERSONS),
                    'page': 4,
                },
            )
        if '_page=5' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('piskarev')],
                    'pages': len(STAFF_PERSONS),
                    'page': 5,
                },
            )
        if '_page=6' in request.url:
            return mockserver.make_response(
                json={
                    'result': [STAFF_PERSONS.get('dismissed_user')],
                    'pages': len(STAFF_PERSONS),
                    'page': 5,
                },
            )
        return mockserver.make_response(json={})

    return _fetch


@pytest.fixture(autouse=False)
def mock_moe_students_results(mockserver):
    @mockserver.json_handler(MOE_COURSE_RESULTS_URL, prefix=False)
    def _fetch(request):
        if request.query.get('page') == '1':
            return mockserver.make_response(json=RESPONSE_MOE_FIRST_PAGE)
        if request.query.get('page') == '2':
            return mockserver.make_response(json=RESPONSE_MOE_SECOND_PAGE)

        return mockserver.make_response(json={})

    return _fetch


@pytest.fixture(autouse=False)
def mock_chatterbox_available_lines(mockserver):
    @mockserver.json_handler(
        '/chatterbox-py3/v1/lines/available_by_logins/', prefix=False,
    )
    def _fetch(request):
        if set(request.json['logins']) == {'login_1', 'login_2'}:
            return mockserver.make_response(
                json=[
                    {'login': 'login_2', 'lines': ['line_2', 'line_3']},
                    {'login': 'login_3', 'lines': ['line_2']},
                ],
            )
        return mockserver.make_response(status=500)

    return _fetch


@pytest.fixture(autouse=False)
def mock_chatterbox_lines_info(mockserver):
    @mockserver.json_handler('/chatterbox-py3/v1/lines/info/', prefix=False)
    def _fetch(request):
        if set(request.json['lines']) == {'line_3', 'line_2'}:
            return mockserver.make_response(
                json=[
                    {
                        'line': 'line_2',
                        'line_tanker_key': 'line_2_tanker_key',
                        'mode': 'offline',
                        'open_chats': 12,
                    },
                    {
                        'line': 'line_3',
                        'line_tanker_key': 'line_3_tanker_key',
                        'mode': 'offline',
                        'open_chats': 13,
                    },
                ],
            )
        return mockserver.make_response(status=500)

    return _fetch


@pytest.fixture(autouse=False)
def bulk_personal_store_phone(mockserver):
    @mockserver.json_handler(PERSONAL_URL_BULK_STORE_PHONE, prefix=False)
    def _fetch(request):

        return mockserver.make_response(
            json={
                'items': [
                    {
                        'id': '26fe660e100e45c897225fc8637edfff',
                        'value': '+74950000000',
                    },
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def bulk_personal_store_telegram(mockserver):
    @mockserver.json_handler(PERSONAL_URL_BULK_STORE_TELEGRAM, prefix=False)
    def _fetch(request):

        return mockserver.make_response(
            json={
                'items': [
                    {
                        'id': 'ab7326daa774233d779c2e015d2c9e0c',
                        'value': 'telegram_login',
                    },
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_payday_piecework_load(mockserver):
    @mockserver.json_handler(PIECEWORK_CALCULATION_URL, prefix=False)
    def _fetch(request):
        body = request.json
        if set(body['logins']) == set(
                [
                    'calltaxi_support',
                    'calltaxi_support_wrong_status',
                    'calltaxi_support_too_much_money',
                ],
        ):
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {
                            'login': 'calltaxi_support',
                            'bo': {
                                'daytime_cost': 10.01,
                                'night_cost': 10.01,
                                'holidays_daytime_cost': 10.01,
                                'holidays_night_cost': 10.01,
                            },
                            'benefit_details': {},
                            'benefits': 0,
                        },
                        {
                            'login': 'calltaxi_support_wrong_status',
                            'bo': {
                                'daytime_cost': 11,
                                'night_cost': 11,
                                'holidays_daytime_cost': 11,
                                'holidays_night_cost': 11,
                            },
                            'benefit_details': {},
                            'benefits': 0,
                        },
                        {
                            'login': 'calltaxi_support_too_much_money',
                            'bo': {
                                'daytime_cost': 1000000,
                                'night_cost': 1000000,
                                'holidays_daytime_cost': 1000000,
                                'holidays_night_cost': 1000000,
                            },
                            'benefit_details': {},
                            'benefits': 0,
                        },
                    ],
                },
            )
        if body['logins'] == ['directsupport_support']:
            return mockserver.make_response(
                json={
                    'calculation': {'commited': True},
                    'logins': [
                        {
                            'login': 'directsupport_support',
                            'bo': {
                                'daytime_cost': 15.51,
                                'night_cost': 15.51,
                                'holidays_daytime_cost': 15.51,
                                'holidays_night_cost': 15.51,
                            },
                            'benefit_details': {},
                            'benefits': 0,
                        },
                    ],
                },
            )
        return mockserver.make_response(status=500, json={})

    return _fetch


@pytest.fixture(autouse=False)
def mock_payday_employee_balance(mockserver):
    @mockserver.json_handler('/payday/api/employee/balance', prefix=False)
    def _fetch(request):
        return mockserver.make_response(status=200)

    return _fetch


@pytest.fixture(autouse=False)
def mock_retrieve_personal(mockserver):
    @mockserver.json_handler(PERSONAL_URL_BULK_RETRIEVE, prefix=False)
    def _fetch(request):
        return mockserver.make_response(
            json={
                'items': [
                    {
                        'id': '26fe660e100e45c897225fc8637edfff',
                        'value': '+74950000000',
                    },
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_retrieve_telegrams(mockserver):
    @mockserver.json_handler(
        PERSONAL_URL_BULK_RETRIEVE_TELEGRAMS, prefix=False,
    )
    def _fetch(request):
        return mockserver.make_response(
            json={
                'items': [
                    {
                        'id': '1e55e7049fc543dc9ebbb63c8fc4d7ed',
                        'value': '@telegram_account',
                    },
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_personal_store_phones(mockserver):
    @mockserver.json_handler(PERSONAL_STORE_PHONES_URL, prefix=False)
    def _fetch(request):
        if request.json['value'] == '79000000000':
            return mockserver.make_response(status=400)
        if request.json['value'] in ['+79000000000', '+79000000001']:
            return mockserver.make_response(
                json={
                    'value': request.json['value'],
                    'id': 'fc4029bd2293d37d8e1609628ee67efd',
                },
            )
        if request.json['value'] == '+79858011671':
            return mockserver.make_response(
                json={
                    'value': request.json['value'],
                    'id': '08d7d29ac9cb46cdb35f72c304ad16f6',
                },
            )
        return mockserver.make_response(status=400)

    return _fetch


@pytest.fixture(autouse=False)
def mock_payday_employee_ok(mockserver):
    @mockserver.json_handler(PAYDAY_EMPLOYEE_URL, prefix=False)
    def _fetch(request):
        if request.json['employeeInfo']['phoneNumber'] == '77777777777':
            return mockserver.make_response(
                status=400, json={'code': 1, 'message': 'Error'},
            )

        return mockserver.make_response(status=200)

    return _fetch


@pytest.fixture(autouse=False)
def mock_oebs_primary(mockserver):
    @mockserver.json_handler(OEBS_PRIMERY_URL, prefix=False)
    def _fetch(request):

        return mockserver.make_response(
            json={
                'logins': [
                    {
                        'login': 'webalex',
                        'hireDate': '2021-03-09',
                        'hrOrg': {'id': 230805, 'name': 'Сектор поддержки'},
                        'managementOrg': {
                            'id': 230365,
                            'name': 'Сектор поддержки',
                        },
                        'job': {
                            'id': 657950,
                            'name': 'Специалист поддержки сервиса.',
                        },
                        'hrKladr': {
                            'id': '3571696',
                            'code': None,
                            'region': None,
                            'district': None,
                            'city': None,
                            'village': None,
                        },
                        'addrReg': {
                            'code': None,
                            'zip': None,
                            'house': None,
                            'bld': None,
                            'flat': None,
                            'str': None,
                        },
                        'addrRes': {
                            'code': None,
                            'zip': None,
                            'house': None,
                            'bld': None,
                            'flat': None,
                            'str': None,
                        },
                        'salaryBasis': {'name': 'RUB (часовая ставка сделка)'},
                        'sdelDate': {'name': '2021-03-09'},
                        'isNonStdSchedule': {'name': 'Y'},
                        'legislationCode': {'code': 'RU'},
                    },
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_hrms_events(mockserver):
    @mockserver.json_handler(
        '/hrms/external/api/agent/v1/calendar/events', prefix=False,
    )
    def _fetch(request):
        if (
                request.query['start'] == '2020-01-01'
                and request.query['end'] == '2020-01-02'
                and request.headers['X-Ya-User-Ticket'] == 'webalex_ticket'
        ):
            return mockserver.make_response(
                json=[
                    {
                        'date': '2020-01-01',
                        'category': 'WORK',
                        'events': [
                            {
                                'code': '1',
                                'isPrimary': True,
                                'title': 'перерыв',
                                'description': 'описание',
                                'timeBound': {
                                    'start': '2020-01-01T07:00:00Z+03:00',
                                    'end': '2020-01-01T08:00:00Z+03:00',
                                },
                            },
                            {
                                'code': '2',
                                'isPrimary': True,
                                'title': 'работа',
                                'description': 'описание',
                                'timeBound': {
                                    'start': '2020-01-01T08:00:00Z+03:00',
                                    'end': '2020-01-01T20:00:00Z+03:00',
                                },
                            },
                        ],
                    },
                    {
                        'date': '2020-01-02',
                        'category': 'HOLIDAY',
                        'events': [
                            {
                                'code': '3',
                                'isPrimary': True,
                                'title': 'отпуск',
                                'description': 'описание',
                                'timeBound': {
                                    'start': '2020-01-02T06:00:00Z+03:00',
                                    'end': '2020-01-02T19:00:00Z+03:00',
                                },
                            },
                        ],
                    },
                    {
                        'date': '2020-01-03',
                        'category': 'UNSPECIFIED',
                        'events': [
                            {
                                'code': '4',
                                'isPrimary': True,
                                'title': 'отпуск',
                            },
                        ],
                    },
                ],
            )
        return mockserver.make_response(status=500)

    return _fetch


@pytest.fixture(autouse=False)
def mock_hrms_finances_one_person(mockserver):
    @mockserver.json_handler(
        '/hrms/external/api/agent/v1/finances/bonus', prefix=True,
    )
    def _fetch(request):

        return mockserver.make_response(
            json={
                'perDay': [
                    {
                        'date': '2022-01-15',
                        'bonus': 746.60,
                        'bonusFact': 447,
                        'qualityFactor': 0.6,
                        'qualityFactorReductionComment': (
                            'Коэффициент снижен из-за допущенных ошибок'
                        ),
                        'efficiencyFactor': 1,
                        'violations': [
                            {
                                'title': 'Товар удален',
                                'cost': 2,
                                'key': 'FFMISTAKES-43489',
                            },
                        ],
                        'operations': [
                            {
                                'amount': 259,
                                'operationTitle': 'Отбор, мезонин 2-5',
                                'unit': 'штуки',
                                'cost': 1.1,
                            },
                            {
                                'amount': 36,
                                'operationTitle': 'Отбор товаров',
                                'unit': 'штуки',
                                'cost': 1.1,
                            },
                            {
                                'amount': 13,
                                'operationTitle': 'Отбор товаров КГТ',
                                'unit': 'штуки',
                                'cost': 3.3,
                            },
                            {
                                'amount': 395,
                                'operationTitle': 'Отбор, мезонин 1',
                                'unit': 'штуки',
                                'cost': 0.96,
                            },
                        ],
                    },
                ],
                'total': 447,
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def personal_phones_fine_mock(mockserver):
    @mockserver.json_handler(PERSONAL_FIND_URL, prefix=False)
    def _fetch(request):
        if request.json['value'] == 'dc6732e6-834e-4cea-9be2-2cbc3e5864f5':

            return mockserver.make_response(
                json={
                    'id': 'a7f95295-c932-4b93-a2ca-9cb1edddf816',
                    'value': '+79000000000',
                },
            )
        return mockserver.make_response(json={})

    return _fetch


@pytest.fixture(autouse=False)
def mock_piecework_reserve_users(mockserver):
    @mockserver.json_handler(PIECEWORK_RESERVE_CURRENT_URL, prefix=False)
    def _fetch(request):

        assert request.json == {
            'logins': ['mikh-vasily', 'webalex', 'akozhevina', 'slon'],
        }

        return mockserver.make_response(
            json={
                'logins': [
                    {'login': 'webalex', 'value': 1000},
                    {'login': 'mikh-vasily', 'value': 2000},
                    {'login': 'akozhevina', 'value': 3000},
                ],
            },
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_hrms_categories(mockserver):
    @mockserver.json_handler(
        '/hrms/external/api/agent/v1/calendar/categories', prefix=False,
    )
    def _fetch(request):
        if (
                request.query['start'] == '2022-01-01'
                and request.query['end'] == '2022-01-07'
                and request.headers['X-Ya-User-Ticket']
                == 'calltaxi_user_ticket'
        ):
            return mockserver.make_response(
                json=[
                    {'date': '2022-01-01', 'categories': ['WORK']},
                    {'date': '2022-01-02', 'categories': ['HOLIDAY']},
                    {
                        'date': '2022-01-03',
                        'categories': [
                            'WORK',
                            'HOLIDAY',
                            'SCHEDULED_ABSENCE',
                            'TRUANCY',
                            'UNSPECIFIED',
                        ],
                    },
                ],
            )
        return mockserver.make_response(status=200, json=[])

    return _fetch


@pytest.fixture(autouse=False)
def mock_lavka1c(mockserver):
    @mockserver.json_handler(
        'lavka-1c/hs/employee_cursor/GetEmployee', prefix=False,
    )
    def _fetch(request):
        if request.query.get('cursor') == '0':
            return mockserver.make_response(
                json={
                    'users': [
                        {
                            'employee_code': 'webalex_external',
                            'employee_first_name': 'Александр',
                            'employee_middle_name': 'Игоревич',
                            'employee_last_name': 'Иванов',
                            'divison_membership': '72554',
                            'division_name': 'МСК Духовской переулок, 14',
                            'division_head': [{'division_code': '72554'}],
                            'job_title': 'Директор склада',
                            'roles': ['lavkastorekeeper_director'],
                            'updated': '2022-06-28T12:23:19',
                            'is_active': True,
                        },
                    ],
                    'cursor': 63792015799540,
                },
            )
        if request.query.get('cursor') == '63792015799540':
            return mockserver.make_response(
                json={
                    'users': [
                        {
                            'employee_code': 'liambaev',
                            'employee_first_name': 'Лиам',
                            'employee_middle_name': 'Александрович',
                            'employee_last_name': 'Баев',
                            'divison_membership': '72554',
                            'division_name': 'МСК Духовской переулок, 14',
                            'division_head': [{'division_code': '72554'}],
                            'job_title': 'Заместитель директора склада',
                            'roles': [],
                            'updated': '2022-06-28T12:23:19',
                            'is_active': True,
                        },
                    ],
                    'cursor': 63792015799541,
                },
            )
        return mockserver.make_response(
            json={'users': [], 'cursor': 63792015799541},
        )

    return _fetch


@pytest.fixture(autouse=False)
def mock_piecework_mapping_payday(mockserver):
    @mockserver.json_handler(PIECEWORK_MAPPING_LOGINS_PAYDAY, prefix=False)
    def _fetch(request):
        return mockserver.make_response(status=200)

    return _fetch
