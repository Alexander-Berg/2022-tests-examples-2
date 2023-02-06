#  pylint: disable=protected-access,unused-variable,too-many-lines

import copy
import datetime

import pytest
import pytz

from taxi.util import dates

from workforce_management.common.jobs.setup import shifts as shifts_job
from workforce_management.common.models import schedule as schedule_module

HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}

V3_SHIFT_SETUP_CONFIG = {
    shifts_job.DEFAULT_CONFIG_KEY: {
        'approach': 'v3',
        'breaks_version': 'v1',
        'minimum_segment_length': 60,
        'maximum_segments_count': 2,
        'plan_demand_multiplier': 1.1,
        'plan_overlap_threshold': 70,
        'multiskill': False,
        'attempts': 5,
    },
}

V3_SHIFT_SETUP_BREAKS_CONFIG = copy.deepcopy(V3_SHIFT_SETUP_CONFIG)
V3_SHIFT_SETUP_BREAKS_CONFIG[shifts_job.DEFAULT_CONFIG_KEY][
    'breaks_version'
] = 'v2'


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'input_data, output_data',
    [
        pytest.param(
            (
                {
                    'starts_at': datetime.datetime(
                        2022, 1, 31, tzinfo=pytz.UTC,
                    ),
                    'expires_at': datetime.datetime(
                        2022, 2, 5, 23, 59, tzinfo=pytz.UTC,
                    ),
                    'first_weekend': False,
                    'rotation_type': 'sequential',
                    'schedule': [2, 2],
                    'start': datetime.time(6),
                    'duration_minutes': 420,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2022, 1, 31, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 13, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2022, 1, 31, 6, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 1, 6, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 4, 6, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 5, 6, tzinfo=pytz.UTC),
            ],
            id='1',
        ),
        pytest.param(
            (
                {
                    'starts_at': datetime.datetime(
                        2022, 2, 7, tzinfo=pytz.UTC,
                    ),
                    'expires_at': None,
                    'first_weekend': True,
                    'rotation_type': 'weekly',
                    'schedule': [4, 3],
                    'start': datetime.time(15),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2022, 1, 31, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 13, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2022, 2, 11, 15, tzinfo=pytz.UTC),
                datetime.datetime(2022, 2, 12, 15, tzinfo=pytz.UTC),
            ],
            id='2',
        ),
        pytest.param(
            (
                {
                    'starts_at': datetime.datetime(
                        2020, 12, 15, tzinfo=pytz.UTC,
                    ),
                    'expires_at': None,
                    'rotation_type': 'weekly',
                    'first_weekend': True,
                    'schedule': [4, 3],
                    'start': datetime.time(12),
                    'duration_minutes': 720,
                    'schedule_by_minutes': [6480, 720, 720, 720, 720, 720, 0],
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2022, 1, 24, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 31, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2022, 1, 28, 12, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 29, 12, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 30, 12, 0, tzinfo=pytz.UTC),
            ],
            id='3',
        ),
        pytest.param(
            (
                {
                    'starts_at': datetime.datetime(
                        2021, 10, 12, tzinfo=pytz.UTC,
                    ),
                    'expires_at': None,
                    'rotation_type': 'sequentially',
                    'first_weekend': False,
                    'schedule': [2, 2],
                    'start': datetime.time(8),
                    'duration_minutes': 540,
                    'schedule_by_minutes': [480, 540, 900, 540, 3300],
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2022, 1, 24, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 31, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2022, 1, 24, 8, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 25, 8, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 28, 8, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 1, 29, 8, 0, tzinfo=pytz.UTC),
            ],
            id='4',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 11, 1, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(21),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 2, 28, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 7, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 2, 28, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 1, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 4, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 5, 21, tzinfo=pytz.UTC),
            ],
            id='5',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2021, 3, 9, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(22),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 3, 7, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 14, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 3, 8, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 9, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 12, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 13, 22, tzinfo=pytz.UTC),
            ],
            id='6',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2021, 3, 9, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 2, 4],
                    'first_weekend': False,
                    'rotation_type': 'weekly',
                    'start': datetime.time(22),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': '123',
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 3, 7, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 14, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 3, 10, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 11, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 12, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 13, 22, tzinfo=pytz.UTC),
            ],
            id='7',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2021, 3, 3, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 2, 4],
                    'first_weekend': False,
                    'rotation_type': 'weekly',
                    'start': datetime.time(22),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 3, 7, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 14, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 3, 7, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 10, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 11, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 12, 22, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 13, 22, tzinfo=pytz.UTC),
            ],
            id='8',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 3, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 3],
                    'first_weekend': True,
                    'start': datetime.time(4),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 10, 20, 21, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 27, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 10, 21, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 22, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 26, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 27, 4, tzinfo=pytz.UTC),
            ],
            id='9',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 5, tzinfo=pytz.UTC,
                    ),
                    'schedule': [3, 2],
                    'first_weekend': False,
                    'start': datetime.time(4),
                    'duration_minutes': 360,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 10, 20, 21, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 27, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 10, 21, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 22, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 26, 4, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 27, 4, tzinfo=pytz.UTC),
            ],
            id='10',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 11, 2, tzinfo=pytz.UTC,
                    ),
                    'schedule': [5, 2],
                    'first_weekend': False,
                    'rotation_type': 'weekly',
                    'start': datetime.time(6),
                    'duration_minutes': 540,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 3, 28, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 3, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 3, 29, 6, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 30, 6, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 31, 6, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 1, 6, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 2, 6, tzinfo=pytz.UTC),
            ],
            id='11',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 11, 20, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 6],
                    'first_weekend': True,
                    'rotation_type': 'weekly',
                    'start': datetime.time(13),
                    'duration_minutes': 480,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 3, 28, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 3, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 3, 30, 13, tzinfo=pytz.UTC),
                datetime.datetime(2021, 3, 31, 13, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 1, 13, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 2, 13, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 3, 13, tzinfo=pytz.UTC),
            ],
            id='12',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2021, 4, 6, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(21),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 4, 4, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 11, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 4, 5, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 6, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 9, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 10, 21, tzinfo=pytz.UTC),
            ],
            id='13',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2021, 3, 23, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 2, 4],
                    'first_weekend': False,
                    'rotation_type': 'weekly',
                    'start': datetime.time(3),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 4, 18, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 25, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 4, 19, 3, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 22, 3, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 23, 3, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 24, 3, tzinfo=pytz.UTC),
                datetime.datetime(2021, 4, 25, 3, tzinfo=pytz.UTC),
            ],
            id='14',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 18, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(13),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 10, 18, 11, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 10, 18, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 19, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 22, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 23, 13, tzinfo=pytz.UTC),
            ],
            id='15',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 18, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(13),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 2,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 10, 18, 11, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 10, 20, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 21, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 24, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 13, tzinfo=pytz.UTC),
            ],
            id='16_test_schedule_offset',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 18, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'start': datetime.time(13),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 123,
                    'schedule_offset': 0,
                    'absolute_start': datetime.datetime(
                        2020, 10, 16, tzinfo=pytz.UTC,
                    ),
                },
                datetime.datetime(2020, 10, 18, 11, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 10, 20, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 21, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 24, 13, tzinfo=pytz.UTC),
                datetime.datetime(2020, 10, 25, 13, tzinfo=pytz.UTC),
            ],
            id='17_test_absolute_start_offset',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 12, 7, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 5, 1],
                    'first_weekend': True,
                    'rotation_type': 'weekly',
                    'start': datetime.time(5),
                    'duration_minutes': 540,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 1,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 12, 6, 21, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 14, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 12, 8, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 9, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 10, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 11, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 12, 5, tzinfo=pytz.UTC),
            ],
            id='18',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 12, 2, tzinfo=pytz.UTC,
                    ),
                    'schedule': [1, 5, 1],
                    'first_weekend': True,
                    'rotation_type': 'weekly',
                    'start': datetime.time(5),
                    'duration_minutes': 540,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 1,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2020, 12, 6, 21, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 14, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2020, 12, 8, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 9, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 10, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 11, 5, tzinfo=pytz.UTC),
                datetime.datetime(2020, 12, 12, 5, tzinfo=pytz.UTC),
            ],
            id='19',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2022, 4, 9, 21, tzinfo=pytz.UTC,
                    ),
                    'schedule': [2, 2],
                    'first_weekend': False,
                    'rotation_type': 'sequentially',
                    'start': datetime.time(0),
                    'duration_minutes': 720,
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 1,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2022, 4, 13, 21, tzinfo=pytz.UTC),
                datetime.datetime(2022, 4, 17, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2022, 4, 14, 0, tzinfo=pytz.UTC),
                datetime.datetime(2022, 4, 15, 0, tzinfo=pytz.UTC),
            ],
            id='20_v3_offset_alignment_bug',
        ),
    ],
)
def test_build(web_context, input_data, output_data):
    data = input_data[0]
    data['schedule_by_minutes'] = schedule_module.format_schedule_v2(
        schedule=data['schedule'],
        start=data['start'],
        first_weekend=data['first_weekend'],
        shift_duration=data['duration_minutes'],
    )
    res = shifts_job.build_shifts_for_operator(*input_data, web_context.config)
    assert [shift['start'] for shift in res] == output_data


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'input_data, output_data',
    [
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 6, tzinfo=pytz.UTC,
                    ),
                    'schedule_by_minutes': [
                        0,
                        720,
                        1485,
                        495,
                        1440,
                        780,
                        660,
                        180,
                    ],
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 1,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 5, 17, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 24, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 5, 17, 21, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 19, 12, 45, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 20, 21, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 21, 21, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 23, 12, 45, tzinfo=pytz.UTC),
            ],
            id='1',
        ),
        pytest.param(
            (
                {
                    'expires_at': None,
                    'starts_at': datetime.datetime(
                        2020, 10, 6, tzinfo=pytz.UTC,
                    ),
                    'schedule_by_minutes': [
                        0,
                        720,
                        1485,
                        495,
                        1440,
                        780,
                        660,
                        180,
                        3000,
                    ],
                    'yandex_uid': '123',
                    'operators_schedule_types_id': 1,
                    'schedule_offset': 0,
                    'absolute_start': None,
                },
                datetime.datetime(2021, 5, 17, 21, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 24, 21, tzinfo=pytz.UTC),
                '',
            ),
            [
                datetime.datetime(2021, 5, 18, 21, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 19, 21, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 22, 2, 0, tzinfo=pytz.UTC),
                datetime.datetime(2021, 5, 23, 14, 45, tzinfo=pytz.UTC),
            ],
            id='2',
        ),
    ],
)
def test_build_difficult(web_context, input_data, output_data):
    res = shifts_job.build_shifts_for_operator(*input_data, web_context.config)
    assert [shift['start'] for shift in res] == output_data


SHIFT_URI = 'v2/shifts/values'
JOB_STATUS_URI = 'v1/job/setup/status'
JOB_SET_URI = 'v1/job/setup'


def prepare_data(tst_request, job_id):
    res = tst_request.copy()
    for key, value in tst_request.items():
        if 'datetime' in key:
            res[key] = dates.localize(dates.parse_timestring(value))
        else:
            res[key] = value

    res['id'] = job_id
    res['try_num'] = 1
    return res


@pytest.mark.now('2020-07-02T00:00:00')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG
                ),
            ),
        ),
        pytest.param(
            id='v3_breaks',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_BREAKS_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_break_rules.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_shifts_count, expected_breaks_count',
    [
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2020-07-01 14:00:00 +0300',
                'datetime_to': '2020-10-01 03:00:00 +0300',
                'limit': 10,
            },
            8,
            40,
        ),
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2020-07-01 16:00:00 +0300',
                'datetime_to': '2020-10-01 03:00:00 +0300',
                'limit': 10,
            },
            7,
            35,
        ),
    ],
)
async def test_base(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_shifts_count,
        expected_breaks_count,
        mock_effrat_employees,
):
    mock_effrat_employees()
    #  test that second iteration doesnt add new shifts
    for _ in range(2):
        res = await taxi_workforce_management_web.post(
            JOB_SET_URI,
            json={'data': tst_request, 'job_type': 'shifts'},
            headers=HEADERS,
        )
        assert res.status == 200
        data = await res.json()
        job_id = data['job_id']

        job_data = prepare_data(tst_request, job_id)

        await shifts_job.ShiftSetupJob(
            web_context, **job_data,
        ).fetch_and_do_job()

        res = await taxi_workforce_management_web.post(
            JOB_STATUS_URI, json={'job_id': job_id},
        )
        assert res.status == 200
        data = await res.json()
        assert data['status'] == 'completed'

        res = await taxi_workforce_management_web.post(
            SHIFT_URI, json=tst_request, headers=HEADERS,
        )
        shifts = await res.json()

        assert len(shifts['records']) == expected_shifts_count
        assert (
            len(
                [
                    _break
                    for operator_and_shift in shifts['records']
                    for _break in operator_and_shift['shift'].get('breaks', [])
                ],
            )
            == expected_breaks_count
        )


@pytest.mark.now('2020-07-14T23:59:59')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG
                ),
            ),
        ),
        pytest.param(
            id='v3_breaks',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_BREAKS_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_break_rules.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_shifts_count, expected_breaks_count',
    [
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2020-07-14 14:00:00 +0300',
                'datetime_to': '2020-10-01 03:00:00 +0300',
                'limit': 10,
            },
            1,
            5,
        ),
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2020-07-14 16:00:00 +0300',
                'datetime_to': '2020-10-01 03:00:00 +0300',
                'limit': 10,
            },
            0,
            0,
        ),
    ],
)
async def test_base_schedule_skills(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_shifts_count,
        expected_breaks_count,
        mock_effrat_employees,
):
    mock_effrat_employees()
    #  test that second iteration doesnt add new shifts
    for _ in range(2):
        res = await taxi_workforce_management_web.post(
            JOB_SET_URI,
            json={'data': tst_request, 'job_type': 'shifts'},
            headers=HEADERS,
        )
        assert res.status == 200
        data = await res.json()
        job_id = data['job_id']

        job_data = prepare_data(tst_request, job_id)

        await shifts_job.ShiftSetupJob(
            web_context, **job_data,
        ).fetch_and_do_job()

        res = await taxi_workforce_management_web.post(
            JOB_STATUS_URI, json={'job_id': job_id},
        )
        assert res.status == 200
        data = await res.json()
        assert data['status'] == 'completed'
        res = await taxi_workforce_management_web.post(
            SHIFT_URI, json=tst_request, headers=HEADERS,
        )
        shifts = await res.json()

        assert len(shifts['records']) == expected_shifts_count
        assert (
            len(
                [
                    _break
                    for operator_and_shift in shifts['records']
                    for _break in operator_and_shift['shift'].get('breaks', [])
                ],
            )
            == expected_breaks_count
        )


@pytest.mark.now('2021-08-02T14:00:00 +0300')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_break_rules.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_shifts',
    [
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2021-08-02 14:00:00 +0300',
                'datetime_to': '2021-08-04 17:00:00 +0300',
                'limit': 10,
            },
            [
                {
                    'duration_minutes': 840,
                    'operators_schedule_types_id': 2,
                    'shift_id': 1,
                    'skill': 'pokemon',
                    'start': '2021-08-03T13:00:00+03:00',
                    'type': 'common',
                    'yandex_uid': 'uid2',
                },
                {
                    'duration_minutes': 840,
                    'operators_schedule_types_id': 2,
                    'shift_id': 2,
                    'skill': 'pokemon',
                    'start': '2021-08-04T13:00:00+03:00',
                    'type': 'common',
                    'yandex_uid': 'uid2',
                },
            ],
        ),
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2021-07-29 14:00:00 +0300',
                'datetime_to': '2021-08-02 17:00:00 +0300',
                'limit': 10,
            },
            [
                {
                    'duration_minutes': 840,
                    'operators_schedule_types_id': 2,
                    'shift_id': 1,
                    'skill': 'pokemon',
                    'start': '2021-08-02T13:00:00+03:00',
                    'type': 'common',
                    'yandex_uid': 'uid2',
                },
            ],
        ),
        (
            {
                'skill': 'pokemon',
                'skill_type': 'any',
                'datetime_from': '2021-08-02 14:00:00 +0300',
                'datetime_to': '2021-08-04 17:00:00 +0300',
                'limit': 10,
            },
            [
                {
                    'duration_minutes': 840,
                    'operators_schedule_types_id': 2,
                    'shift_id': 1,
                    'skill': 'pokemon',
                    'start': '2021-08-03T13:00:00+03:00',
                    'type': 'common',
                    'yandex_uid': 'uid2',
                },
                {
                    'duration_minutes': 840,
                    'operators_schedule_types_id': 2,
                    'shift_id': 2,
                    'skill': 'pokemon',
                    'start': '2021-08-04T13:00:00+03:00',
                    'type': 'common',
                    'yandex_uid': 'uid2',
                },
            ],
        ),
    ],
)
async def test_schedule_id_inserting(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_shifts,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        JOB_SET_URI,
        json={'data': tst_request, 'job_type': 'shifts'},
        headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    job_id = data['job_id']

    job_data = prepare_data(tst_request, job_id)

    await shifts_job.ShiftSetupJob(web_context, **job_data).fetch_and_do_job()

    await taxi_workforce_management_web.post(
        JOB_STATUS_URI, json={'job_id': job_id},
    )

    res = await taxi_workforce_management_web.post(
        SHIFT_URI, json=tst_request, headers=HEADERS,
    )
    shifts = await res.json()

    for operator_and_shift in shifts['records']:
        del operator_and_shift['operator']['revision_id']
    assert pop_fields(shifts['records']) == expected_shifts


def pop_fields(shifts):
    res = []
    for operator_and_shift in shifts:
        operator_and_shift['shift'].pop('breaks', None)
        operator_and_shift['shift'].pop('audit', None)
        res.append(operator_and_shift['shift'])
    return res


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_SHIFT_SETUP_CONFIG,
                ),
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_shifts_count',
    [
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2020-07-14 11:00:00Z',
                'datetime_to': '2020-10-01 00:00:00Z',
                'limit': 10,
            },
            0,
        ),
    ],
)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
async def test_error(
        web_context,
        taxi_workforce_management_web,
        patch,
        pgsql,
        tst_request,
        expected_shifts_count,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        JOB_SET_URI,
        json={'data': tst_request, 'job_type': 'shifts'},
        headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    job_id = data['job_id']
    assert job_id == 1

    @patch('workforce_management.common.models.shift.save_shifts')
    async def save_shifts_mock(*args, **kwargs):
        raise Exception()

    with pytest.raises(Exception):
        await shifts_job.ShiftSetupJob(web_context).fetch_and_do_job()

    res = await taxi_workforce_management_web.post(
        JOB_STATUS_URI, json={'job_id': job_id},
    )
    assert res.status == 200
    data = await res.json()
    assert data['status'] == 'not_started'
    res = await taxi_workforce_management_web.post(
        SHIFT_URI, json=tst_request, headers=HEADERS,
    )
    shifts = await res.json()

    assert len(shifts['records']) == expected_shifts_count
