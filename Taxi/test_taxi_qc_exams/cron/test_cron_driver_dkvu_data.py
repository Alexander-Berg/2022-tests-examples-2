from aiohttp import web

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron


async def test_mismatch(
        mongo, mock_quality_control_py3, mock_taximeter_xservice, load_json,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=load_json('pass_list.json'),
            ),
        )

    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'
        assert request.json['filter'] == {'id': 'park_driver3'}
        assert request.json['direction'] == 'desc'
        return web.json_response(
            data=dict(cursor='end', items=load_json('pass_history_3_1.json')),
        )

    @mock_taximeter_xservice('/utils/qc/driver/update-dkvu-data')
    async def _taximeter_xservice_driver_update_dkvu_data(request):
        return web.Response(status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_dkvu_data', '-t', '0'],
    )

    assert _api_v1_pass_list.times_called == 1
    assert _api_v1_pass_history.times_called == 1
    assert _taximeter_xservice_driver_update_dkvu_data.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert stats[0]['skipped'] == 3
    assert stats[0]['fields_mismatch'] == 1
    assert stats[0]['changed'] == 1


async def test_empty_field(
        mongo, mock_quality_control_py3, mock_taximeter_xservice, load_json,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=load_json('pass_list_one.json'),
            ),
        )

    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'
        assert request.json['filter'] == {'id': 'park_driver3'}
        assert request.json['direction'] == 'desc'
        return web.json_response(
            data=dict(cursor='end', items=load_json('pass_history_3_2.json')),
        )

    @mock_taximeter_xservice('/utils/qc/driver/update-dkvu-data')
    async def _taximeter_xservice_driver_update_dkvu_data(request):
        assert request.json['values'] == {
            'driver_license_pd_id': 'lpd_3_4',
            'first_name': 'Petr',
            'last_name': 'Petrov',
        }
        return web.Response(status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_dkvu_data', '-t', '0'],
    )

    assert _api_v1_pass_list.times_called == 1
    assert _api_v1_pass_history.times_called == 1
    assert _taximeter_xservice_driver_update_dkvu_data.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert stats[0]['fields_mismatch'] == 1
    assert stats[0]['changed'] == 1


async def test_uniq(
        mongo,
        mock_quality_control_py3,
        mock_taximeter_xservice,
        mock_unique_drivers,
        load_json,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def _api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=load_json('pass_list.json'),
            ),
        )

    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'
        assert request.json['filter'] == {'id': 'park_driver3'}
        assert request.json['direction'] == 'desc'
        return web.json_response(
            data=dict(cursor='end', items=load_json('pass_history_3_2.json')),
        )

    @mock_unique_drivers('/service/v1/uniques/merge')
    async def _uniques_merge(request):
        assert request.json['new_license_pd_id'] == 'lpd_3_4'
        assert request.json['old_license_pd_id'] == 'lpd_3_2'
        return web.Response(status=200)

    @mock_taximeter_xservice('/utils/qc/driver/update-dkvu-data')
    async def _taximeter_xservice_driver_update_dkvu_data(request):
        return web.Response(status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_dkvu_data', '-t', '0'],
    )

    assert _api_v1_pass_list.times_called == 1
    assert _api_v1_pass_history.times_called == 1
    assert _uniques_merge.times_called == 1
    assert _taximeter_xservice_driver_update_dkvu_data.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert stats[0]['skipped'] == 3
    assert stats[0]['uniques'] == {'merged': 1}
    assert stats[0]['changed'] == 1
