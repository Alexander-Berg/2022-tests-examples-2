# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={
        'dkk': {
            '__default__': [
                dict(
                    date_begin='01-01',
                    date_end='12-31',
                    ranges=[dict(time_begin='10:00', time_end='10:00')],
                ),
            ],
        },
        'branding': {
            '__default__': [
                dict(
                    date_begin='01-01',
                    date_end='12-31',
                    ranges=[dict(time_begin='12:00', time_end='12:00')],
                ),
            ],
            'pgd': [
                dict(
                    date_begin='01-01',
                    date_end='12-31',
                    ranges=[dict(time_begin='1:00', time_end='1:00')],
                ),
            ],
        },
    },
)
@pytest.mark.parametrize(
    'entity_id, code, future',
    [
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'dkk',
            [
                dict(begin='2018-12-15T15:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T03:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'branding',
            [
                dict(begin='2018-12-20T17:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-21T05:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'dkk',
            [
                dict(begin='2018-12-13T23:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-14T11:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'branding',
            [
                dict(begin='2018-12-15T14:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T02:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000002',
            'dkvu',
            None,
        ),
    ],
)
async def test_setup_exam_deadline_old_config(  # pylint: disable=invalid-name
        mock_qc_exams_admin, db, entity_id, code, future,
):
    # setup initial state
    await db.qc_entities.update_one(
        {
            'entity_type': 'driver',
            'entity_id': entity_id,
            'state.exams.code': code,
        },
        {'$set': {'state.exams.$.need_future': True}},
    )

    @mock_qc_exams_admin('/api/v1/schedule')
    def mock_schedule(request):
        assert request.query == dict(id=entity_id, type='driver', exam=code)
        assert request.json == dict(future=future)
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert mock_schedule.times_called == 0 if future is None else 1


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={
        'dkk': [
            {
                'date_ranges': [
                    dict(
                        date_begin='01-01',
                        date_end='12-31',
                        ranges=[dict(time_begin='10:00', time_end='10:00')],
                    ),
                ],
            },
        ],
        'branding': [
            {
                'date_ranges': [
                    dict(
                        date_begin='01-01',
                        date_end='12-31',
                        ranges=[dict(time_begin='12:00', time_end='12:00')],
                    ),
                ],
            },
            {
                'zones': ['pgd'],
                'date_ranges': [
                    dict(
                        date_begin='01-01',
                        date_end='12-31',
                        ranges=[dict(time_begin='1:00', time_end='1:00')],
                    ),
                ],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'entity_id, code, future',
    [
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'dkk',
            [
                dict(begin='2018-12-15T15:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T03:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'branding',
            [
                dict(begin='2018-12-20T17:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-21T05:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'dkk',
            [
                dict(begin='2018-12-13T23:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-14T11:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'branding',
            [
                dict(begin='2018-12-15T14:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T02:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000002',
            'dkvu',
            None,
        ),
    ],
)
async def test_setup_exam_deadline(
        mock_qc_exams_admin, db, entity_id, code, future,
):
    # setup initial state
    await db.qc_entities.update_one(
        {
            'entity_type': 'driver',
            'entity_id': entity_id,
            'state.exams.code': code,
        },
        {'$set': {'state.exams.$.need_future': True}},
    )

    @mock_qc_exams_admin('/api/v1/schedule')
    def mock_schedule(request):
        assert request.query == dict(id=entity_id, type='driver', exam=code)
        assert request.json == dict(future=future)
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert mock_schedule.times_called == 0 if future is None else 1


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.parametrize(
    'entity_id, code, future',
    [
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'biometry',
            [
                dict(begin='2018-12-15T14:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T02:00:00+03:00',
                    can_pass=True,
                    sanctions=['biometry'],
                ),
            ],
        ),
    ],
)
async def test_setup_biometry_exam_deadline(
        mock_qc_exams_admin, db, entity_id, code, future,
):
    # setup initial state
    where = {
        'entity_type': 'driver',
        'entity_id': entity_id,
        'state.exams.code': code,
    }
    update = {'$set': {'state.exams.$.need_future': True}}
    await db.qc_entities.update_one(where, update)

    lower = dates.parse_timestring('2018-12-14T21:00:00Z', 'UTC')
    upper = dates.parse_timestring('2018-12-16T21:00:00Z', 'UTC')

    @mock_qc_exams_admin('/api/v1/schedule')
    def mock_schedule(request):
        assert request.query == dict(id=entity_id, type='driver', exam=code)
        exam_begin = dates.parse_timestring(
            request.json['future'][0]['begin'], 'UTC',
        )
        assert lower < exam_begin < upper
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert mock_schedule.times_called == 0 if future is None else 1


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(QC_EXAMS_DEADLINE_WINDOWS={})
@pytest.mark.parametrize(
    'entity_id, code, future',
    [
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'dkk',
            [
                dict(begin='2018-12-15T12:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T00:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000000_7d7a94a3fee84eda95de736b5e000000',
            'branding',
            [
                dict(begin='2018-12-20T12:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-21T00:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'dkk',
            [
                dict(begin='2018-12-13T12:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-14T00:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkk'],
                ),
            ],
        ),
        (
            '596348f157c8e64565000001_7d7a94a3fee84eda95de736b5e000001',
            'branding',
            [
                dict(begin='2018-12-15T12:00:00+03:00', can_pass=True),
                dict(
                    begin='2018-12-16T00:00:00+03:00',
                    can_pass=True,
                    sanctions=['dkb'],
                ),
            ],
        ),
    ],
)
async def test_park_period(mock_qc_exams_admin, db, entity_id, code, future):
    # setup initial state
    await db.qc_entities.update_one(
        {
            'entity_type': 'driver',
            'entity_id': entity_id,
            'state.exams.code': code,
        },
        {'$set': {'state.exams.$.need_future': True}},
    )

    @mock_qc_exams_admin('/api/v1/schedule')
    def mock_schedule(request):
        assert request.query == dict(id=entity_id, type='driver', exam=code)
        assert request.json == dict(future=future)
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert mock_schedule.times_called == 0 if future is None else 1
