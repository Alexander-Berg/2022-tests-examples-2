# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron

EXP_NAME = 'biometry_deadline_settings'
EXP_ARGS = dict(
    consumer='qc/setup_exam_deadlines',
    config_name=EXP_NAME,
    args=[
        dict(name='park_id', type='string', value='596348f157c8e64565000003'),
        dict(
            name='driver_profile_id',
            type='string',
            value='7d7a94a3fee84eda95de736b5e000000',
        ),
        dict(name='tags', type='set_string', value=['some_tag']),
        dict(name='city', type='string', value='Екатеринодар'),
    ],
)


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period=10)),
)
async def test_integer_period(mock_qc_exams_admin):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert schedule.times_called == 1

    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-21T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period='3d')),
)
async def test_delta_period(mock_qc_exams_admin):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert schedule.times_called == 1

    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-14T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period=dict(lower='4d', upper='8d'))),
)
async def test_random_period(mock_qc_exams_admin):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert schedule.times_called == 1

    result = schedule.next_call()['request'].json

    futures = result.pop('future')
    assert not result
    assert len(futures) == 1
    future = futures[0]
    begin = dates.parse_timestring(future.pop('begin'), 'UTC')
    lower = dates.parse_timestring('2018-12-14T21:00:00Z')
    upper = dates.parse_timestring('2018-12-18T21:00:00Z')

    assert lower < begin < upper
    assert future == dict(can_pass=True, sanctions=['biometry'])


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(
        biometry=dict(period=10, park_period='biometry_period'),
    ),
)
async def test_park_period(mock_qc_exams_admin):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert schedule.times_called == 1
    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-12T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period='3d', ready_gap='15m')),
)
async def test_ready_gap(mock_qc_exams_admin):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert schedule.times_called == 1

    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(begin='2018-12-13T23:45:00+03:00', can_pass=True),
            dict(
                begin='2018-12-14T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period=1, exp_period=EXP_NAME)),
)
@pytest.mark.client_experiments3(
    value=dict(enabled=True, period=10), **EXP_ARGS,
)
async def test_exp_integer_period(mock_qc_exams_admin, mock_tags):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    @mock_tags('/v1/bulk_match')
    async def v1_bulk_match(request):
        id_ = '596348f157c8e64565000003_7d7a94a3fee84eda95de736b5e000000'
        return web.json_response(
            data=dict(entities=[dict(id=id_, tags=['some_tag'])]),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert v1_bulk_match.times_called == 1
    assert schedule.times_called == 1
    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-21T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period=1, exp_period=EXP_NAME)),
)
@pytest.mark.client_experiments3(
    value=dict(enabled=True, period='3d'), **EXP_ARGS,
)
async def test_exp_delta_period(mock_qc_exams_admin, mock_tags):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    @mock_tags('/v1/bulk_match')
    async def v1_bulk_match(request):
        id_ = '596348f157c8e64565000003_7d7a94a3fee84eda95de736b5e000000'
        return web.json_response(
            data=dict(entities=[dict(id=id_, tags=['some_tag'])]),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert v1_bulk_match.times_called == 1
    assert schedule.times_called == 1

    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-14T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(biometry=dict(period=1, exp_period=EXP_NAME)),
)
@pytest.mark.client_experiments3(
    value=dict(enabled=True, period=dict(lower='4d', upper='8d')), **EXP_ARGS,
)
async def test_exp_random_period(mock_qc_exams_admin, mock_tags):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    @mock_tags('/v1/bulk_match')
    async def v1_bulk_match(request):
        id_ = '596348f157c8e64565000003_7d7a94a3fee84eda95de736b5e000000'
        return web.json_response(
            data=dict(entities=[dict(id=id_, tags=['some_tag'])]),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert v1_bulk_match.times_called == 1
    assert schedule.times_called == 1

    result = schedule.next_call()['request'].json

    futures = result.pop('future')
    assert not result
    assert len(futures) == 1
    future = futures[0]
    begin = dates.parse_timestring(future.pop('begin'), 'UTC')
    lower = dates.parse_timestring('2018-12-14T21:00:00Z')
    upper = dates.parse_timestring('2018-12-18T21:00:00Z')

    assert lower < begin < upper
    assert future == dict(can_pass=True, sanctions=['biometry'])


@pytest.mark.now('2018-12-10T21:00:00.000Z')
@pytest.mark.config(
    QC_EXAMS_DEADLINE_WINDOWS={},
    QC_PERIODIC_EXAMS=dict(
        biometry=dict(
            period=1, exp_period=EXP_NAME, park_period='biometry_period',
        ),
    ),
)
@pytest.mark.client_experiments3(
    value=dict(enabled=True, period=10), **EXP_ARGS,
)
async def test_exp_park_period(mock_qc_exams_admin, mock_tags):
    @mock_qc_exams_admin('/api/v1/schedule')
    def schedule(request):
        return web.json_response(data={})

    @mock_tags('/v1/bulk_match')
    async def v1_bulk_match(request):
        id_ = '596348f157c8e64565000003_7d7a94a3fee84eda95de736b5e000000'
        return web.json_response(
            data=dict(entities=[dict(id=id_, tags=['some_tag'])]),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.setup_exam_deadlines', '-t', '0'],
    )

    assert v1_bulk_match.times_called == 1
    assert schedule.times_called == 1
    assert schedule.next_call()['request'].json == dict(
        future=[
            dict(
                begin='2018-12-12T00:00:00+03:00',
                can_pass=True,
                sanctions=['biometry'],
            ),
        ],
    )
