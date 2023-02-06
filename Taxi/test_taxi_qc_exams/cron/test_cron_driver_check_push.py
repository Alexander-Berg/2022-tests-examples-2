# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron
from taxi_qc_exams.helpers import consts
from test_taxi_qc_exams import utils


@pytest.mark.now('2020-12-18T12:00:06.000+0000')
@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_check_push=utils.job_settings()),
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=False,
    ),
)
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', consts.qc.Exam.BIOMETRY, status='new'),
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, status='pending'),
        utils.make_pass('1_1', consts.qc.Exam.STS, status='canceled'),
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
        [
            'taxi_qc_exams.crontasks.communications.driver_check_push',
            '-t',
            '0',
        ],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0]['skipped'] == 1


@pytest.mark.now('2020-12-18T12:00:06.000+0000')
@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_check_push=utils.job_settings()),
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=False,
    ),
)
@pytest.mark.parametrize(
    'resolved, expired',
    [
        ('2020-12-18T12:00:00.000+0000', False),
        ('2020-12-18T11:30:00.000+0000', False),
        ('2020-12-18T11:00:00.000+0000', True),
        ('2020-12-18T10:30:00.000+0000', True),
    ],
)
async def test_expiration(
        mongo,
        mock_quality_control_py3,
        mock_communications,
        resolved,
        expired,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    def api_v1_pass_list(request):
        assert request.method == 'GET'
        pass_ = utils.make_pass('1_1')
        pass_['resolution']['resolved'] = resolved

        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    @mock_communications('/driver/notification/bulk-push')
    def bulk_push(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [
            'taxi_qc_exams.crontasks.communications.driver_check_push',
            '-t',
            '0',
        ],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    if expired:
        assert not bulk_push.times_called
        assert stats[0] == dict(skipped=1, expired=1, drivers_to_notify=0)
    else:
        assert bulk_push.times_called == 1
        assert stats[0] == dict(succeeded=1, drivers_to_notify=1)


@pytest.mark.now('2020-12-18T12:00:06.000+0000')
@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_check_push=utils.job_settings()),
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=False,
    ),
)
async def test_car_push(
        mongo,
        mock_quality_control_py3,
        mock_communications,
        mock_driver_profiles,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    def api_v1_pass_list(request):
        assert request.method == 'GET'
        pass_ = utils.make_pass('1_1', exam=consts.qc.Exam.STS)
        pass_['resolution']['resolved'] = '2020-12-18T12:00:00.000+0000'

        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    @mock_communications('/driver/notification/bulk-push')
    def bulk_push(request):
        return web.json_response(data={})

    @mock_driver_profiles(
        '/v1/vehicle_bindings/drivers/retrieve_by_park_id_car_id',
    )
    def retrieve_by_park_id_car_id(request):
        return web.json_response(
            data=dict(
                profiles_by_park_id_car_id=[
                    dict(
                        park_id_car_id='1_1',
                        profiles=[
                            dict(park_driver_profile_id='1_2'),
                            dict(park_driver_profile_id='1_3'),
                            dict(park_driver_profile_id='1_4'),
                        ],
                    ),
                ],
            ),
        )

    # crontask
    await run_cron.main(
        [
            'taxi_qc_exams.crontasks.communications.driver_check_push',
            '-t',
            '0',
        ],
    )

    assert api_v1_pass_list.times_called == 1
    assert retrieve_by_park_id_car_id.times_called == 1
    assert bulk_push.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert bulk_push.times_called == 1
    assert stats[0] == dict(succeeded=1, drivers_to_notify=3)


@pytest.mark.now('2020-12-18T12:00:06.000+0000')
@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_check_push=utils.job_settings()),
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=True,
    ),
)
@pytest.mark.parametrize(
    'resolved, expired',
    [
        ('2020-12-18T12:00:00.000+0000', False),
        ('2020-12-18T11:30:00.000+0000', False),
        ('2020-12-18T11:00:00.000+0000', True),
        ('2020-12-18T10:30:00.000+0000', True),
    ],
)
async def test_expiration_client_notify(
        mongo, mock_quality_control_py3, mock_client_notify, resolved, expired,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    def api_v1_pass_list(request):
        assert request.method == 'GET'
        pass_ = utils.make_pass('1_1')
        pass_['resolution']['resolved'] = resolved

        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    @mock_client_notify('/v2/bulk-push')
    def bulk_push(request):
        return web.json_response(data={'notifications': []})

    # crontask
    await run_cron.main(
        [
            'taxi_qc_exams.crontasks.communications.driver_check_push',
            '-t',
            '0',
        ],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    if expired:
        assert not bulk_push.times_called
        assert stats[0] == dict(skipped=1, expired=1, drivers_to_notify=0)
    else:
        assert bulk_push.times_called == 1
        assert stats[0] == dict(succeeded=1, drivers_to_notify=1)


@pytest.mark.now('2020-12-18T12:00:06.000+0000')
@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_check_push=utils.job_settings()),
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=True,
    ),
)
async def test_car_push_client_notify(
        mongo,
        mock_quality_control_py3,
        mock_client_notify,
        mock_driver_profiles,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    def api_v1_pass_list(request):
        assert request.method == 'GET'
        pass_ = utils.make_pass('1_1', exam=consts.qc.Exam.STS)
        pass_['resolution']['resolved'] = '2020-12-18T12:00:00.000+0000'

        return web.json_response(
            data=dict(
                modified=dates.timestring(), cursor='next', items=[pass_],
            ),
        )

    @mock_client_notify('/v2/bulk-push')
    def bulk_push(request):
        return web.json_response(data={'notifications': []})

    @mock_driver_profiles(
        '/v1/vehicle_bindings/drivers/retrieve_by_park_id_car_id',
    )
    def retrieve_by_park_id_car_id(request):
        return web.json_response(
            data=dict(
                profiles_by_park_id_car_id=[
                    dict(
                        park_id_car_id='1_1',
                        profiles=[
                            dict(park_driver_profile_id='1_2'),
                            dict(park_driver_profile_id='1_3'),
                            dict(park_driver_profile_id='1_4'),
                        ],
                    ),
                ],
            ),
        )

    # crontask
    await run_cron.main(
        [
            'taxi_qc_exams.crontasks.communications.driver_check_push',
            '-t',
            '0',
        ],
    )

    assert api_v1_pass_list.times_called == 1
    assert retrieve_by_park_id_car_id.times_called == 1
    assert bulk_push.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert bulk_push.times_called == 1
    assert stats[0] == dict(succeeded=1, drivers_to_notify=3)
