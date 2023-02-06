from pytest import mark
from datetime import datetime, timezone
import pytest

from callcenter_etl.layer.yt.ods.workforce_management.shift.impl import mapper


@mark.parametrize(
    'input_data, expected_data', [
        pytest.param(
            {
                'shift_id': 'shift1',
                'type': 'additional',
                'start': '2022-05-19T21:00:00+03:00',
                'duration_minutes': 720,
                'yandex_uid': 'op1',
                'description': 'тестовый коммент',
                'skill': 'lavka',
                'operators_schedule_types_id': 'type1',
                'events': [
                    {
                        'event_id': 'qweqe',
                        'start': '2022-05-19T21:00:00+03:00',
                        'duration_minutes': 75,
                        'id': 'event1',
                        'description': 'комментарий для ПА'
                    }
                ],
                'breaks': [
                    {
                        'start': '2022-05-20T00:00:00+03:00',
                        'duration_minutes': 15,
                        'id': 'break1',
                        'type': 'technical'
                    },
                    {
                        'start': '2022-05-20T04:00:00+03:00',
                        'duration_minutes': 30,
                        'id': 'break2',
                        'type': 'lunchtime'
                    }
                ],
                'segments': [
                    {
                        'id': 'segment1',
                        'skill': 'lavka',
                        'start': '2022-05-21T10:30:00+03:00',
                        'duration_minutes': 15,
                        'description': 'lox'
                    }
                ],
                'shift_violations': [
                    {
                        'id': 'shift_violation1',
                        'type': 'absent',
                        'start': '2022-05-21T10:30:00+03:00',
                        'duration_minutes': 120,
                    }
                ],
                'actual_shifts': [
                    {
                        'duration_minutes': 2,
                        'id': 'actual_shift1',
                        'skill': 'qwe',
                        'start': '2022-05-19T11:47:59.545738+03:00',
                        'events': [
                            {
                                'duration_minutes': 1,
                                'type': 'pause',
                                'sub_type': 'tech',
                                'start': '2022-05-19T12:47:59.545738+03:00',
                            }
                        ]
                    }
                ],
                'audit': {
                        'updated_at': '2022-05-19T11:47:59.545738+03:00',
                        'author_yandex_uid': 'auditor1'
                },
                'utc_updated_dttm': '2022-05-16 11:47:59.545738',
                'is_deleted': False
            },
            [
{
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'segment1',
                    'activity_code': 'work',
                    'activity_desc': 'lox',
                    'activity_duration_mnt': 15,
                    'activity_subtype': None,
                    'activity_type': 'lavka',
                    'utc_activity_start_dttm': '2022-05-21 07:30:00.000000'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'break1',
                    'activity_code': 'break',
                    'activity_desc': None,
                    'activity_duration_mnt': 15,
                    'activity_subtype': None,
                    'activity_type': 'technical',
                    'utc_activity_start_dttm': '2022-05-19 21:00:00.000000'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'break2',
                    'activity_code': 'break',
                    'activity_desc': None,
                    'activity_duration_mnt': 30,
                    'activity_subtype': None,
                    'activity_type': 'lunchtime',
                    'utc_activity_start_dttm': '2022-05-20 01:00:00.000000'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'shift_violation1',
                    'activity_code': 'violation',
                    'activity_desc': None,
                    'activity_duration_mnt': 120,
                    'activity_subtype': None,
                    'activity_type': 'absent',
                    'utc_activity_start_dttm': '2022-05-21 07:30:00.000000'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'event1',
                    'activity_code': 'event',
                    'activity_desc': 'комментарий для ПА',
                    'activity_duration_mnt': 75,
                    'activity_subtype': None,
                    'activity_type': 'qweqe',
                    'utc_activity_start_dttm': '2022-05-19 18:00:00.000000'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'actual_shift1',
                    'activity_code': 'fact_shift',
                    'activity_desc': None,
                    'activity_duration_mnt': 2,
                    'activity_subtype': None,
                    'activity_type': 'qwe',
                    'utc_activity_start_dttm': '2022-05-19 08:47:59.545738'
                },
                {
                    'shift_id': 'shift1',
                    'shift_type': 'additional',
                    'shift_desc': 'тестовый коммент',
                    'utc_shift_finish_dttm': '2022-05-20 06:00:00.000000',
                    'utc_shift_start_dttm': '2022-05-19 18:00:00.000000',
                    'utc_shift_updated_dttm': '2022-05-16 11:47:59.545738',
                    'shift_duration_mnt': 720,
                    'skill_code': 'lavka',
                    'auditor_yandex_uid': 'auditor1',
                    'deleted_flg': False,
                    'operator_schedule_type_id': 'type1',
                    'yandex_uid': 'op1',
                    'activity_id': 'actual_shift1',
                    'activity_code': 'fact_status',
                    'activity_desc': None,
                    'activity_duration_mnt': 1,
                    'activity_subtype': 'tech',
                    'activity_type': 'pause',
                    'utc_activity_start_dttm': '2022-05-19 09:47:59.545738'
                }
            ]
        ),
    ]
)
def test_workforce_management_shift_mapper(input_data, expected_data):
    actual_data = [row for row in mapper(input_data)]
    assert actual_data == expected_data
