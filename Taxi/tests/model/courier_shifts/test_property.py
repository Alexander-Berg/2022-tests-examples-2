from datetime import datetime

import pytest


async def test_duration(tap, dataset):
    with tap.plan(2, 'Плановая продолжительность смены'):
        store = await dataset.store()
        shift = await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 1, 1, 12, 30, 0),
            closes_at=datetime(2021, 1, 1, 13, 0, 0),
        )
        tap.ok(shift, 'Объект создан')
        tap.eq(shift.duration, 30 * 60, 'продолжительность')


@pytest.mark.parametrize('data', [
    {
        'shift_events': [
            {'type': 'started', 'created': datetime(2021, 1, 1, 11, 30, 0)},
            {'type': 'stopped', 'created': datetime(2021, 1, 1, 13, 30, 0)},
        ],
        'result': 2 * 60 * 60,
    },
    {
        'shift_events': [
            {'type': 'started', 'created': datetime(2021, 1, 1, 11, 30, 0)},
        ],
        'result': None,
    },
    {
        'shift_events': [
            {'type': 'stopped', 'created': datetime(2021, 1, 1, 13, 30, 0)},
        ],
        'result': None,
    },
    {
        'shift_events': [],
        'result': None,
    },
])
async def test_duration_real(tap, dataset, data):
    with tap.plan(3, 'Реальная продолжительность смены'):
        store = await dataset.store()

        shift = await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 1, 1, 12, 30, 0),
            closes_at=datetime(2021, 1, 1, 13, 0, 0),
            shift_events=data['shift_events'],
        )
        tap.ok(shift, 'Объект создан')
        tap.eq(shift.duration, 30 * 60, 'продолжительность')
        tap.eq(
            shift.duration_real,
            data['result'],
            'реальная продолжительность'
        )
