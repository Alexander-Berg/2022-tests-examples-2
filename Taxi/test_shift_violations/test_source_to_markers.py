import pytest

from workforce_management.common.models import (
    shift_violations as violations_module,
)
from workforce_management.storage.postgresql import db as db_module
from . import data


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {'start': data.add_minutes(0), 'end': data.add_minutes(0.5)},
            data.MARKERS_SHIFT_START,
            id='one_shift_start',
        ),
        pytest.param(
            {'start': data.add_minutes(0), 'end': data.add_minutes(120.5)},
            data.MARKERS_CONSECUTIVE_SHIFTS,
            id='multiple_shifts',
        ),
    ],
)
async def test_shifts_to_markers(stq3_context, kwargs, expected_res):
    operators_db = db_module.OperatorsRepo(stq3_context)

    async with operators_db.master.acquire() as conn:
        shifts = await operators_db.get_shifts_no_cursor(
            conn,
            yandex_uids=['uid1'],
            datetime_from=kwargs['start'],
            datetime_to=kwargs['end'],
        )

    res = violations_module.convert.shifts_to_markers(shifts, **kwargs)
    res = data.expected_fields(res, expected_res)

    assert res == expected_res


@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(0.5),
            },
            [],
            id='empty',
        ),
        pytest.param(
            {
                'events': data.EVENTS_CONNECT,
                'start': data.add_minutes(0),
                'end': data.add_minutes(60.5),
            },
            data.MARKERS_CONNECT,
            id='connect',
        ),
        pytest.param(
            {
                'events': data.EVENTS_ALL_TYPES,
                'start': data.add_minutes(0),
                'end': data.add_minutes(60.5),
            },
            [
                {'marker_type': 'disconnect', 'start': data.add_minutes(5)},
                {'marker_type': 'connect', 'start': data.add_minutes(15)},
                {
                    'marker_type': 'pause',
                    'start': data.add_minutes(25),
                    'subtype': 'toilet',
                },
            ],
            id='all_types',
        ),
    ],
)
async def test_events_to_markers(stq3_context, kwargs, expected_res):
    res = violations_module.convert.events_to_markers(
        **kwargs, valid_queues={'pokemon'},
    )
    res = data.expected_fields(res, expected_res)
    assert res == expected_res


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'shift_event_break.sql'],
)
async def test_shifts_to_markers_reverse(stq3_context):
    kwargs = {'start': data.add_minutes(0), 'end': data.add_minutes(120.5)}
    expected_res = data.MARKERS_REVERSE
    await test_shifts_to_markers(stq3_context, kwargs, expected_res)
