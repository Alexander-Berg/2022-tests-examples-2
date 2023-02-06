import typing as tp

JSON = tp.Dict[str, tp.Any]
FIRST_AUDIT = {'updated_at': '2020-06-26T00:00:00+03:00'}

FIRST_SCHEDULE_TYPE = {
    'schedule_type_id': 1,
    'duration_minutes': 720,
    'first_weekend': False,
    'revision_id': '2020-08-26T09:00:00.000000 +0000',
    'schedule': [2, 2],
    'start': '12:00:00',
}
FIRST_SCHEDULE_TYPE_SIMPLE = {'schedule_type_id': 1}
SECOND_SCHEDULE_TYPE = {
    'schedule_type_id': 2,
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedule_alias': '5x2/10:00-00:00',
    'schedule': [5, 2],
    'start': '10:00:00',
}
SECOND_SCHEDULE_TYPE_SIMPLE = {'schedule_type_id': 2}
THIRD_SCHEDULE_TYPE_SIMPLE = {'schedule_type_id': 3}
FOURTH_SCHEDULE_TYPE = {
    'schedule_type_id': 4,
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2023-07-31T21:00:00.000000 +0000',
    'schedule': [5, 2],
    'schedule_alias': '5x2/10:00-00:00',
    'start': '10:00:00',
}
FOURTH_SCHEDULE_TYPE_SIMPLE = {'schedule_type_id': 4}

FIRST_SCHEDULE = {
    'record_id': 1,
    'expires_at': '2020-08-01T03:00:00+03:00',
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': FIRST_SCHEDULE_TYPE,
    'starts_at': '2020-07-01T03:00:00+03:00',
    'skills': ['hokage', 'tatarin'],
    'schedule_offset': 0,
    'audit': FIRST_AUDIT,
}
FIRST_SCHEDULE_SIMPLE: tp.Dict = {
    **FIRST_SCHEDULE,
    'schedule_type_info': FIRST_SCHEDULE_TYPE_SIMPLE,
}
SECOND_SCHEDULE = {
    'record_id': 2,
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': SECOND_SCHEDULE_TYPE,
    'starts_at': '2020-08-01T03:00:00+03:00',
    'skills': ['pokemon', 'tatarin'],
    'schedule_offset': 0,
    'audit': FIRST_AUDIT,
}
SECOND_SCHEDULE_SIMPLE: tp.Dict = {
    **SECOND_SCHEDULE,
    'schedule_type_info': SECOND_SCHEDULE_TYPE_SIMPLE,
}
THIRD_SCHEDULE = {
    'record_id': 3,
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': FOURTH_SCHEDULE_TYPE,
    'starts_at': '2023-08-01T03:00:00+03:00',
    'skills': ['hokage'],
    'schedule_offset': 0,
    'audit': FIRST_AUDIT,
}
THIRD_SCHEDULE_SIMPLE: tp.Dict = {
    **THIRD_SCHEDULE,
    'schedule_type_info': FOURTH_SCHEDULE_TYPE_SIMPLE,
}
FOURTH_SCHEDULE_SIMPLE = {
    'record_id': 4,
    'expires_at': '2020-08-01T03:00:00+03:00',
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': FIRST_SCHEDULE_TYPE_SIMPLE,
    'starts_at': '2020-07-01T03:00:00+03:00',
    'skills': [],
    'schedule_offset': 0,
    'audit': FIRST_AUDIT,
}

FIRST_OPERATOR_REVISION = '2020-08-25T21:00:00.000000 +0000'
FIRST_OPERATOR_SIMPLE = {
    'yandex_uid': 'uid1',
    'login': 'abd-damir',
    'full_name': 'Abdullin Damir',
    'state': 'ready',
    'phone': '111',
    'mentor_login': 'supervisor@unit.test',
    'supervisor_login': 'aladin227',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'skills': ['hokage', 'tatarin'],
    'tags': ['naruto'],
    'schedules': [{**FIRST_SCHEDULE_SIMPLE, 'secondary_skills': ['tatarin']}],
    'roles': [{'name': 'group1'}, {'name': 'group2'}],
}

FIRST_OPERATOR: tp.Dict[str, tp.Any] = {
    **FIRST_OPERATOR_SIMPLE,
    'employment_date': '2020-07-21',
    'callcenter_id': '1',
    'role_in_telephony': 'nokia',
    'rate': 0.5,
    'schedules': [{**FIRST_SCHEDULE, 'secondary_skills': ['tatarin']}],
}

SECOND_OPERATOR_SIMPLE_SCHEDULES: tp.List[tp.Dict] = [
    {**FOURTH_SCHEDULE_SIMPLE, 'secondary_skills': []},
    {**SECOND_SCHEDULE_SIMPLE, 'secondary_skills': ['pokemon']},
]

SECOND_OPERATOR_SIMPLE = {
    'yandex_uid': 'uid2',
    'login': 'chakchak',
    'full_name': 'Gilgenberg Valeria',
    'state': 'ready',
    'mentor_login': 'mentor@unit.test',
    'supervisor_login': 'abd-damir',
    'supervisor': {
        'full_name': 'Abdullin Damir',
        'login': 'abd-damir',
        'yandex_uid': 'uid1',
        'state': 'ready',
    },
    'telegram': 'vasya_iz_derevni',
    'revision_id': '2020-08-26T22:00:00.000000 +0000',
    'skills': ['pokemon', 'tatarin'],
    'tags': ['naruto', 'driver'],
    'schedules': SECOND_OPERATOR_SIMPLE_SCHEDULES,
    'roles': [{'name': 'group1'}],
}

SECOND_OPERATOR_EXTRA = {
    'yandex_uid': 'uid2',
    'login': 'chakchak',
    'full_name': 'Gilgenberg Valeria',
    'state': 'ready',
    'mentor_login': 'mentor@unit.test',
    'supervisor_login': 'abd-damir',
    'supervisor': {
        'full_name': 'Abdullin Damir',
        'login': 'abd-damir',
        'yandex_uid': 'uid1',
        'state': 'ready',
    },
    'telegram': 'vasya_iz_derevni',
    'revision_id': '2020-08-26T22:00:00.000000 +0000',
    'tags': ['naruto', 'driver'],
    'schedules': SECOND_OPERATOR_SIMPLE_SCHEDULES,
    'roles': [{'name': 'group1'}],
    'skills': ['pokemon', 'tatarin'],
}

SECOND_OPERATOR_SCHEDULES: tp.List[tp.Dict] = [
    {**SECOND_SCHEDULE, 'secondary_skills': ['pokemon']},
]

SECOND_OPERATOR = {
    **SECOND_OPERATOR_SIMPLE,
    'employment_date': '2020-07-21',
    'callcenter_id': '2',
    'role_in_telephony': 'nokia',
    'schedules': SECOND_OPERATOR_SCHEDULES,
    'rate': 1.0,
    'skills': [],
}

SECOND_OPERATOR_WITH_SKILLS: tp.Dict[str, tp.Any] = {
    **SECOND_OPERATOR_SIMPLE,
    'employment_date': '2020-07-21',
    'callcenter_id': '2',
    'role_in_telephony': 'nokia',
    'schedules': SECOND_OPERATOR_SCHEDULES,
    'rate': 1.0,
    'skills': ['pokemon', 'tatarin'],
}

THIRD_OPERATOR_SIMPLE = {
    'yandex_uid': 'uid3',
    'login': 'tatarstan',
    'full_name': 'Minihanov Minihanov',
    'state': 'ready',
    'mentor_login': 'supervisor@unit.test',
    'supervisor_login': 'abd-damir',
    'supervisor': {
        'full_name': 'Abdullin Damir',
        'login': 'abd-damir',
        'yandex_uid': 'uid1',
        'state': 'ready',
    },
    'telegram': 'morozhenka',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedules': [{**THIRD_SCHEDULE_SIMPLE, 'secondary_skills': []}],
    'roles': [{'name': 'group1'}],
    'skills': ['hokage'],
}

THIRD_OPERATOR: tp.Dict[str, tp.Any] = {
    **THIRD_OPERATOR_SIMPLE,
    'employment_date': '2020-07-21',
    'callcenter_id': '999',
    'role_in_telephony': 'iphone',
    'schedules': [{**THIRD_SCHEDULE, 'secondary_skills': []}],
    'rate': 1.0,
    'skills': [],
}
THIRD_OPERATOR_EFFRAT: JSON = {
    'yandex_uid': 'uid3',
    'login': 'tatarstan',
    'employee_uid': '00000000-0000-0000-0000-000000000003',
    'staff_login': 'tatarstan',
    'departments': ['1'],
    'full_name': 'Minihanov Minihanov',
    'employment_status': 'in_staff',
    'phone_pd_id': '111',
    'supervisor_login': 'abd-damir',
    'mentor_login': 'supervisor@unit.test',
    'employment_datetime': '2020-07-21T00:00:00+03:00',
    'positions': [],
    'source': 'taxi',
}

FOURTH_OPERATOR: tp.Dict[str, tp.Any] = {
    'yandex_uid': 'not-existing',
    'login': 'unknown',
    'mentor_login': 'supervisor@unit.test',
    'employment_date': '2020-07-21',
    'callcenter_id': '666',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'full_name': 'Anonymous Anonymous',
    'state': 'ready',
    'supervisor_login': 'anonym222',
    'role_in_telephony': 'super-role',
    'skills': [],
    'schedules': [],
    'roles': [],
}

FIRST_BREAK = {
    'id': 1,
    'start': '2020-07-26T15:00:00+03:00',
    'duration_minutes': 30,
    'type': 'technical',
}
SECOND_BREAK = {
    'id': 2,
    'start': '2020-07-26T15:35:00+03:00',
    'duration_minutes': 15,
    'type': 'technical',
}

FIRST_OPERATOR_EVENT = {
    'id': 1,
    'description': 'technical',
    'start': '2020-07-28T19:00:00+03:00',
    'duration_minutes': 30,
    'event_id': 1,
}
SECOND_OPERATOR_EVENT = {
    'id': 2,
    'description': 'technical',
    'start': '2020-07-28T19:35:00+03:00',
    'duration_minutes': 15,
    'event_id': 2,
}
THIRD_OPERATOR_EVENT = {
    'id': 3,
    'description': 'technical',
    'start': '2020-08-03T18:10:00+03:00',
    'duration_minutes': 15,
    'event_id': 2,
}

ZEROTH_SHIFT = {
    'shift': {
        'shift_id': 0,
        'type': 'common',
        'description': 'empty',
        'start': '2020-07-26T15:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'hokage',
        'breaks': [FIRST_BREAK],
    },
    'operator': FIRST_OPERATOR_SIMPLE,
}
FIRST_SHIFT = {
    'shift': {
        'shift_id': 1,
        'type': 'common',
        'description': 'empty',
        'start': '2020-07-26T15:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'hokage',
        'breaks': [FIRST_BREAK, SECOND_BREAK],
    },
    'operator': FIRST_OPERATOR_SIMPLE,
}
SECOND_SHIFT = {
    'shift': {
        'shift_id': 2,
        'type': 'common',
        'description': 'empty',
        'start': '2020-07-26T16:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'pokemon',
    },
    'operator': THIRD_OPERATOR_SIMPLE,
}
THIRD_SHIFT = {
    'shift': {
        'shift_id': 3,
        'type': 'common',
        'description': 'empty',
        'start': '2020-07-26T17:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'pokemon',
    },
    'operator': THIRD_OPERATOR_SIMPLE,
}
FOURTH_SHIFT = {
    'shift': {
        'shift_id': 4,
        'type': 'common',
        'description': 'empty',
        'start': '2020-08-03T18:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'pokemon',
        'events': [THIRD_OPERATOR_EVENT],
    },
    'operator': SECOND_OPERATOR_SIMPLE,
}
FIFTH_SHIFT = {
    'shift': {
        'shift_id': 5,
        'type': 'common',
        'description': 'empty',
        'start': '2020-07-26T19:00:00+03:00',
        'duration_minutes': 60,
        'skill': 'pokemon',
    },
    'operator': THIRD_OPERATOR_SIMPLE,
}
SIXTH_SHIFT = {
    'shift': {
        'shift_id': 6,
        'type': 'additional',
        'start': '2020-07-28T19:00:00+03:00',
        'description': 'empty',
        'duration_minutes': 60,
        'skill': 'pokemon',
        'events': [FIRST_OPERATOR_EVENT, SECOND_OPERATOR_EVENT],
    },
    'operator': THIRD_OPERATOR_SIMPLE,
}
