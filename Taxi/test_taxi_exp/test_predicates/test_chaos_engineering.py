# pylint: disable=W0212
import datetime

import pytest

from taxi_exp import util
from taxi_exp.util import chaos_engineering as chaos


@pytest.mark.parametrize(
    'tag_name,is_chaos',
    [
        ('taxi_phone_id', False),
        ('chaos_fallback_routestats', True),
        ('chaos', False),
        ('routestats_chaos', False),
    ],
)
async def test_is_chaos_tag(tag_name, is_chaos):
    assert chaos.is_chaos_tag_name(tag_name) == is_chaos


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={'features': {'backend': {'chaos_tags_enabled': True}}},
    TAXI_EXP_CHAOS_ENGINEERING_TAGS={
        'chaos_fallback_routestats': {
            'rotate_hours': 2,
            'percent': 5,
            'salt': 'salt1',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
        'chaos_fallback_totw': {
            'rotate_hours': 5,
            'percent': 10,
            'salt': 'salt2',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
    },
)
async def test_build_chaos_tags(web_context):
    chaos_tags = chaos.build_chaos_tags(web_context.config, True)
    assert len(chaos_tags) == 2
    assert chaos_tags['chaos_fallback_routestats'] == chaos.ChaosTag(
        tag_name='chaos_fallback_routestats',
        arg_name='phone_id',
        percent=5,
        rotate_hours=2,
        base_tag='taxi_phone_id',
        salt='salt1',
    )
    assert chaos_tags['chaos_fallback_totw'] == chaos.ChaosTag(
        tag_name='chaos_fallback_totw',
        arg_name='phone_id',
        percent=10,
        rotate_hours=5,
        base_tag='taxi_phone_id',
        salt='salt2',
    )


@pytest.mark.parametrize(
    'rotate,expected',
    [
        pytest.param(
            8,
            'routestats_4_5',
            marks=[pytest.mark.now('2021-04-02T18:30:00+00:00')],
        ),
        pytest.param(
            7,
            'routestats_4_6',
            marks=[pytest.mark.now('2021-04-02T18:30:00+00:00')],
        ),
        pytest.param(
            6,
            'routestats_5_7',
            marks=[pytest.mark.now('2021-05-02T18:30:00+00:00')],
        ),
        pytest.param(
            4,
            'routestats_4_10',
            marks=[pytest.mark.now('2021-04-02T18:30:00+00:00')],
        ),
        pytest.param(
            1,
            'routestats_4_41',
            marks=[pytest.mark.now('2021-04-02T17:30:00+00:00')],
        ),
    ],
)
async def test_gen_salt(rotate, expected):
    tag = chaos.ChaosTag(
        tag_name='chaos_fallback_routestats',
        arg_name='phone_id',
        percent=5,
        rotate_hours=rotate,
        base_tag='taxi_phone_id',
        salt='routestats',
    )

    salt = chaos._generate_salt(tag)
    assert salt == expected


@pytest.mark.now('2021-04-02T17:30:00+00:00')
async def test_gen_chaos_segmentation():
    tag = chaos.ChaosTag(
        tag_name='chaos_fallback_routestats',
        arg_name='phone_id',
        percent=5,
        rotate_hours=4,
        base_tag='taxi_phone_id',
        salt='routestats',
    )

    base_tag = chaos.predicates.FileTag(
        tag_name='taxi_phone_id', mds_id='mds_id', file_type='uid', version=1,
    )

    res = chaos.generate_chaos_predicate(tag, base_tag)
    predicates = res['init']['predicates']

    assert res['type'] == 'all_of'

    assert len(predicates) == 2
    assert predicates[0] == {
        'type': 'segmentation',
        'init': {
            'arg_name': 'phone_id',
            'divisor': 100,
            'range_from': 0,
            'range_to': 5,
            'salt': 'routestats_4_10',
        },
    }

    assert predicates[1] == {
        'type': 'in_file',
        'init': {
            'arg_name': 'phone_id',
            'file': 'mds_id',
            'set_elem_type': 'uid',
        },
    }


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={'features': {'backend': {'chaos_tags_enabled': True}}},
    TAXI_EXP_CHAOS_ENGINEERING_TAGS={
        'chaos_fallback_routestats': {
            'rotate_hours': 2,
            'percent': 5,
            'salt': 'salt1',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
            'schedule': [
                {
                    'intervals_msc': [
                        {'from': '12:00', 'to': '18:00'},
                        {'from': '19:00', 'to': '23:00'},
                    ],
                    'weekdays': ['tue', 'wed'],
                },
            ],
        },
    },
)
async def test_build_chaos_tags_schedule(web_context):
    chaos_tags = chaos.build_chaos_tags(web_context.config, True)
    assert len(chaos_tags) == 1
    assert chaos_tags['chaos_fallback_routestats'] == chaos.ChaosTag(
        tag_name='chaos_fallback_routestats',
        arg_name='phone_id',
        percent=5,
        rotate_hours=2,
        base_tag='taxi_phone_id',
        salt='salt1',
        schedule=[
            chaos.ScheduleItem(
                weekdays={'tue', 'wed'},
                intervals_msc=[
                    chaos.IntervalItem(from_time='12:00', to_time='18:00'),
                    chaos.IntervalItem(from_time='19:00', to_time='23:00'),
                ],
            ),
        ],
    )


@pytest.mark.parametrize(
    'in_interval',
    [
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-02T12:10:00+00:00')],
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-02T18:00:00+00:00')],
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-05-02T12:00:00+00:00')],
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-02T11:50:00+00:00')],
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-02T18:10:00+00:00')],
        ),
    ],
)
async def test_chaos_tags_intervals(web_context, in_interval):
    dttm = datetime.datetime.now()
    interval = chaos.IntervalItem(from_time='12:00', to_time='18:00')
    assert interval.is_in_interval(dttm) == in_interval


@pytest.mark.parametrize(
    'in_schedule',
    [
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-12T12:10:00+00:00')],  # mon
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-13T18:00:00+00:00')],  # tue
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2021-05-14T12:00:00+00:00')],  # wed
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-15T11:50:00+00:00')],  # thu
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-16T18:10:00+00:00')],  # fri
        ),
    ],
)
async def test_chaos_tags_weekdays(web_context, in_schedule):
    dttm = datetime.datetime.now()
    schedule = chaos.ScheduleItem(intervals_msc=[], weekdays={'tue', 'thu'})
    assert schedule.is_in_schedule(dttm) == in_schedule


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={'features': {'backend': {'chaos_tags_enabled': True}}},
    TAXI_EXP_CHAOS_ENGINEERING_TAGS={
        'chaos_fallback_routestats': {
            'rotate_hours': 2,
            'percent': 5,
            'salt': 'salt1',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
            'schedule': [
                {
                    'intervals_msc': [
                        {'from': '12:00', 'to': '18:00'},
                        {'from': '19:00', 'to': '23:00'},
                    ],
                    'weekdays': ['tue', 'wed', 'fri'],
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    'in_schedule',
    [
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-12T12:10:00+00:00')],  # mon
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-13T18:00:00+00:00')],  # tue
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-05-14T12:00:00+00:00')],  # wed
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2021-04-15T11:50:00+00:00')],  # thu
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2021-04-16T19:10:00+00:00')],  # fri
        ),
    ],
)
async def test_chaos_tags_full_schedule_check(web_context, in_schedule):
    chaos_tags = chaos.build_chaos_tags(web_context.config, True)
    dttm = util.now()

    tag = chaos_tags['chaos_fallback_routestats']
    assert tag.is_active_by_schedule(dttm) == in_schedule
