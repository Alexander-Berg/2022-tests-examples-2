from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(medcard_issue_date=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T16:40:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', status='new'),
        utils.make_pass('1_1', status='pending'),
        utils.make_pass('1_1', status='canceled'),
        utils.make_pass('1_1', success=False),
    ],
)
async def test_skipped(mongo, mock_quality_control_py3, pass_):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.medcard_issue_date', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0]['skipped'] == 1


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(medcard_issue_date=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T16:40:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', data=[]),
        utils.make_pass('1_1', data=[dict(field='field', value='value')]),
        utils.make_pass('1_1', data=[dict(field='field', value='')]),
        utils.make_pass(
            '1_1',
            data=[
                dict(
                    field='medical_card.issue_date',
                    value='2020-05-01T16:30:00Z',
                ),
            ],
        ),
    ],
)
async def test_unchanged(mongo, mock_quality_control_py3, pass_):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.medcard_issue_date', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0].pop('succeeded') == 1


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(medcard_issue_date=utils.job_settings()),
)
async def test_changed(mongo, mock_quality_control_py3, mock_driver_profiles):
    items = [
        utils.make_pass(
            '1_1',
            data=[
                dict(
                    field='medical_card.issue_date',
                    prev_value='',
                    value='2020-05-01T16:30:00Z',
                ),
            ],
        ),
        utils.make_pass(
            '2_2',
            data=[
                dict(
                    field='medical_card.issue_date',
                    prev_value='2020-04-01T16:30:00Z',
                    value='2020-05-01T16:30:00Z',
                ),
            ],
        ),
    ]

    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(modified=dates.timestring(), cursor='next', items=items),
        )

    @mock_driver_profiles('/v1/driver/medical-card')
    async def medical_card(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.medcard_issue_date', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert medical_card.times_called == len(items)

    author = dict(
        consumer='qc',
        identity=dict(job_name='medcard_issue_date', type='job'),
    )
    for item in items:
        park_id, driver_profile_id = item['entity_id'].split('_', 2)
        request = medical_card.next_call()['request']
        assert request.json == dict(
            author=author,
            medical_card=dict(issue_date='2020-05-01T19:30:00+03:00'),
        )
        assert request.query == dict(
            driver_profile_id=driver_profile_id, park_id=park_id,
        )

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0] == dict(succeeded=2, changed=2, resolution=dict(SUCCESS=2))
