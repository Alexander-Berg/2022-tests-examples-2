# pylint: disable=protected-access
from workforce_management.common import constants
# pylint: disable=import-only-modules
from workforce_management.generated.web.operators_cache.plugin import (
    _operators_states_default_dict,
)


OPERATORS_LIST_CHANGES = [
    [
        {
            'unique_operator_id': 1,
            'yandex_uid': 'uid1',
            'employee_uid': '00000000-0000-0000-0000-000000000001',
            'login': 'abd-damir',
            'staff_login': 'abd-damir',
            'departments': ['1'],
            'subdepartments': ['1', '2', '3'],
            'full_name': 'Abdullin Damir',
            'employment_status': 'fired',
            'phone_pd_id': '111',
            'supervisor_login': 'aladin227',
            'mentor_login': 'supervisor@unit.test',
            'employment_datetime': '2020-07-21T00:00:00+03:00',
            'positions': ['nokia'],
            'source': 'taxi',
            'tags': ['tag1', 'tag2'],
            'organization': {'name': 'Google', 'country_code': 'vacanda'},
            'timezone': 'Europe/Saratov',
            'hr_ticket': 'some_ticket',
        },
    ],
    '1',
]
EMPLOYEES_CACHE_INFO = {
    'not-existing': {
        'callcenter_id': '666',
        'subdepartments': None,
        'employment_date': '2020-07-21',
        'full_name': 'Anonymous Anonymous',
        'first_name': 'Anonymous',
        'last_name': 'Anonymous',
        'middle_name': '',
        'login': 'unknown',
        'mentor_login': 'supervisor@unit.test',
        'phone_number': None,
        'roles': ['super-role', 'super2'],
        'staff_login': 'unknown',
        'parent_state': 'staff',
        'state': 'ready',
        'supervisor_login': 'anonym222',
        'telegram_login': None,
        'domain': 'taxi',
        'timezone': None,
        'unique_operator_id': 4,
        'yandex_uid': 'not-existing',
        'employee_uid': 'deadbeef-0000-0000-0000-000000000000',
        'tags': None,
        'organization': None,
        'hr_ticket': None,
    },
    'uid1': {
        'callcenter_id': '1',
        'subdepartments': ['1', '2', '3'],
        'employment_date': '2020-07-21',
        'full_name': 'Abdullin Damir',
        'first_name': 'Damir',
        'last_name': 'Abdullin',
        'middle_name': '',
        'login': 'abd-damir',
        'mentor_login': 'supervisor@unit.test',
        'phone_number': '111',
        'roles': ['nokia', 'nokia2'],
        'staff_login': 'abd-damir',
        'state': 'ready',
        'parent_state': 'staff',
        'supervisor_login': 'aladin227',
        'telegram_login': None,
        'domain': 'taxi',
        'unique_operator_id': 1,
        'yandex_uid': 'uid1',
        'employee_uid': '00000000-0000-0000-0000-000000000001',
        'tags': ['naruto'],
        'organization': {'name': 'Google', 'country_code': 'vacanda'},
        'timezone': 'Europe/Saratov',
        'hr_ticket': 'some_ticket',
    },
    'uid2': {
        'callcenter_id': '2',
        'subdepartments': ['2', '3'],
        'employment_date': '2020-07-21',
        'full_name': 'Gilgenberg Valeria',
        'first_name': 'Valeria',
        'last_name': 'Gilgenberg',
        'middle_name': '',
        'login': 'chakchak',
        'mentor_login': 'mentor@unit.test',
        'phone_number': None,
        'roles': ['nokia', 'nokia2'],
        'staff_login': 'chakchak',
        'state': 'ready',
        'parent_state': 'staff',
        'supervisor_login': 'abd-damir',
        'telegram_login': 'vasya_iz_derevni',
        'domain': 'taxi',
        'timezone': None,
        'unique_operator_id': 2,
        'yandex_uid': 'uid2',
        'employee_uid': '00000000-0000-0000-0000-000000000002',
        'tags': ['naruto', 'driver'],
        'organization': None,
        'hr_ticket': None,
    },
    'uid3': {
        'callcenter_id': '999',
        'subdepartments': None,
        'employment_date': '2020-07-21',
        'full_name': 'Minihanov Minihanov',
        'first_name': 'Minihanov',
        'last_name': 'Minihanov',
        'middle_name': '',
        'login': 'tatarstan',
        'mentor_login': 'supervisor@unit.test',
        'phone_number': None,
        'roles': ['iphone', 'iphone2'],
        'staff_login': 'tatarstan',
        'state': 'ready',
        'parent_state': 'staff',
        'supervisor_login': 'abd-damir',
        'domain': 'taxi',
        'telegram_login': 'morozhenka',
        'timezone': None,
        'unique_operator_id': 3,
        'yandex_uid': 'uid3',
        'employee_uid': '00000000-0000-0000-0000-000000000003',
        'tags': None,
        'organization': None,
        'hr_ticket': None,
    },
    'uid5': {
        'callcenter_id': '666',
        'subdepartments': None,
        'employment_date': '2020-07-21',
        'full_name': 'Deleted Deleted',
        'first_name': 'Deleted',
        'last_name': 'Deleted',
        'middle_name': '',
        'login': 'deleted',
        'mentor_login': 'admin@unit.test',
        'phone_number': None,
        'domain': 'taxi',
        'roles': ['super-role'],
        'staff_login': 'deleted',
        'state': 'deleted',
        'parent_state': 'staff',
        'supervisor_login': 'anonym222',
        'telegram_login': 'Dota2Lover',
        'timezone': None,
        'unique_operator_id': 5,
        'yandex_uid': 'uid5',
        'employee_uid': '00000000-0000-0000-0000-000000000005',
        'tags': None,
        'organization': None,
        'hr_ticket': None,
    },
    'uid10': {
        'callcenter_id': '1',
        'subdepartments': None,
        'domain': 'taxi',
        'employment_date': '2020-07-21',
        'first_name': 'Malevich',
        'full_name': 'Kazimir Malevich',
        'last_name': 'Kazimir',
        'login': 'kazimir_black_square',
        'mentor_login': 'admin@unit.test',
        'middle_name': '',
        'phone_number': None,
        'roles': ['artist'],
        'staff_login': 'kazimir_black_square',
        'state': 'preprofile_approved',
        'parent_state': 'preprofile',
        'supervisor_login': 'tatarstan',
        'tags': None,
        'telegram_login': 'alphabet',
        'timezone': None,
        'unique_operator_id': 6,
        'yandex_uid': 'uid10',
        'employee_uid': '00000000-0000-0000-0000-000000000010',
        'organization': None,
        'hr_ticket': None,
    },
}


async def test_operators_cache(web_context, mock_effrat_employees):
    mock_effrat_employees()

    await web_context.operators_cache.refresh_cache()

    assert dict(web_context.operators_cache._operators_by_yuid['taxi']) == {
        state.value: {
            key: value
            for key, value in EMPLOYEES_CACHE_INFO.items()
            if value['state'] == state.value
        }
        for state in constants.OperatorStates
    }

    mock_next = mock_effrat_employees(
        operators_list=OPERATORS_LIST_CHANGES[0],
        cursor=OPERATORS_LIST_CHANGES[1],
    )

    await web_context.operators_cache.refresh_cache()
    assert mock_next.employees_list.next_call()['request'].json == {
        'cursor': '0',
        'limit': 1000,
    }

    assert (
        web_context.operators_cache.get_by_yuid(
            domain='taxi', yandex_uid='uid1',
        )
        == {
            'callcenter_id': '1',
            'subdepartments': ['1', '2', '3'],
            'domain': 'taxi',
            'employment_date': '2020-07-21',
            'first_name': 'Damir',
            'full_name': 'Abdullin Damir',
            'last_name': 'Abdullin',
            'login': 'abd-damir',
            'mentor_login': 'supervisor@unit.test',
            'middle_name': '',
            'phone_number': '111',
            'roles': ['nokia'],
            'staff_login': 'abd-damir',
            'state': 'deleted',
            'parent_state': 'staff',
            'supervisor_login': 'aladin227',
            'telegram_login': None,
            'unique_operator_id': 1,
            'yandex_uid': 'uid1',
            'employee_uid': '00000000-0000-0000-0000-000000000001',
            'tags': ['tag1', 'tag2'],
            'organization': {'name': 'Google', 'country_code': 'vacanda'},
            'timezone': 'Europe/Saratov',
            'hr_ticket': 'some_ticket',
        }
    )
    assert not web_context.operators_cache.is_operator_ready('uid1')
    assert web_context.operators_cache.effrat_request.cursor == '1'

    await web_context.operators_cache.refresh_cache()

    assert mock_next.employees_list.next_call()['request'].json == {
        'cursor': '1',
        'limit': 1000,
    }


async def test_effrat_cache(web_context):
    cache = web_context.operators_cache
    cache._operators_by_yuid.clear()
    cache._operators_by_login.clear()
    cache._operators_by_euid = _operators_states_default_dict()

    await cache.refresh_cache()

    assert dict(cache._operators_by_yuid['taxi']) == {
        state.value: {
            key: value
            for key, value in EMPLOYEES_CACHE_INFO.items()
            if value['state'] == state.value
        }
        for state in constants.OperatorStates
    }
    assert dict(cache._operators_by_login['taxi']) == {
        state.value: {
            value['login']: value
            for key, value in EMPLOYEES_CACHE_INFO.items()
            if value['state'] == state.value
        }
        for state in constants.OperatorStates
    }
    assert dict(cache._operators_by_euid) == {
        state.value: {
            value['employee_uid']: value
            for key, value in EMPLOYEES_CACHE_INFO.items()
            if value['state'] == state.value
        }
        for state in constants.OperatorStates
    }


async def test_several_domains(web_context, mock_effrat_employees):
    mock_effrat_employees()
    await web_context.operators_cache.refresh_cache()
    mock_effrat_employees(
        operators_list=OPERATORS_LIST_CHANGES[0],
        cursor=OPERATORS_LIST_CHANGES[1],
    )
    await web_context.operators_cache.refresh_cache()
    mock_effrat_employees(
        operators_list=[
            {
                **OPERATORS_LIST_CHANGES[0][0],
                'employment_status': 'in_staff',
                'source': 'eats',
            },
        ],
    )
    await web_context.operators_cache.refresh_cache()

    assert web_context.operators_cache.get_by_yuid('taxi', 'uid1') == {
        **EMPLOYEES_CACHE_INFO['uid1'],
        'state': 'deleted',
        'domain': 'taxi',
        'roles': ['nokia'],
        'tags': ['tag1', 'tag2'],
    }
    assert web_context.operators_cache.get_by_yuid('eats', 'uid1') == {
        **EMPLOYEES_CACHE_INFO['uid1'],
        'state': 'ready',
        'domain': 'eats',
        'roles': ['nokia'],
        'tags': ['tag1', 'tag2'],
    }
