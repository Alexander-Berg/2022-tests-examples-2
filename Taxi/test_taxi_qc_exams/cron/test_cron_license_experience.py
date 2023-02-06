import datetime

from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron
from taxi_qc_exams.helpers import consts
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(license_experience=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T16:40:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', consts.qc.Exam.DKVU, status='new'),
        utils.make_pass('1_1', consts.qc.Exam.DKVU, status='pending'),
        utils.make_pass('1_1', consts.qc.Exam.DKVU, status='canceled'),
        utils.make_pass('1_1', consts.qc.Exam.DKVU, success=False),
    ],
)
async def test_license_experience_skipped(
        mongo, mock_quality_control_py3, pass_,
):
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
        ['taxi_qc_exams.crontasks.license_experience', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0]['skipped'] == 1


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(license_experience=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T00:00:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass(
            '1_1',
            consts.qc.Exam.DKVU,
            data=[
                {
                    'field': 'license_experience_confirmation',
                    'value': '<confirmation_id>',
                },
            ],
        ),
    ],
)
@pytest.mark.parametrize('experience_months', [10, 35, 36])
async def test_license_experience_ok(
        mongo,
        mock_quality_control_py3,
        mock_driver_profiles,
        mock_fleet_parks,
        pass_,
        experience_months,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    await mongo.confirmations.insert_one(
        {
            '_id': '<confirmation_id>',
            'pass_id': pass_['id'],
            'park_id': '1',
            'driver_profile_id': '1',
            'offer_id': 'license_experience_confirmation',
            'offer_link': 'http://dl_offer',
            'created': datetime.datetime(2020, 1, 1, 0, 0, 0),
        },
    )

    @mock_fleet_parks('/v1/parks/list')
    def _fleet_parks_handler(request):
        return {
            'parks': [
                {
                    'city_id': 'Москва',
                    'country_id': 'rus',
                    'demo_mode': True,
                    'id': '1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'locale': 'ru',
                    'login': 'sample_park',
                    'name': 'Sample Park',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_driver_profiles('/v1/driver/license-experience')
    async def dp_lic_exp(request):
        assert request.method == 'PATCH'
        assert request.args == {'park_id': '1', 'driver_profile_id': '1'}
        return {}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def dp_retrieve(request):
        assert request.method == 'POST'
        assert request.json == {
            'id_in_set': ['1_1'],
            'projection': ['data.license_experience'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': '1_1',
                    'data': {
                        'license_experience': {
                            'total': (
                                consts.LICENSE_EXPERIENCE_INITIAL_DATE
                                - consts.ONE_MONTH * experience_months
                            ).isoformat(),
                        },
                    },
                },
            ],
        }

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.license_experience', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert dp_retrieve.times_called == 1
    assert dp_lic_exp.times_called == int(experience_months < 36)

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0].pop('succeeded') == 1
