from aiohttp import web

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron


async def test_happy_path(
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

    @mock_taximeter_xservice('/utils/qc/car/update-branding-data')
    async def _taximeter_xservice_car_update_branding_data(request):
        assert request.json['values'] == {'sticker': 'True'}
        return web.Response(status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.car_branding_data', '-t', '0'],
    )

    assert _api_v1_pass_list.times_called == 1
    assert _taximeter_xservice_car_update_branding_data.times_called == 1
