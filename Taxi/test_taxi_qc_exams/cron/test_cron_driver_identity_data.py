from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron
from taxi_qc_exams.helpers import consts
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T16:40:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, status='new'),
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, status='pending'),
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, status='canceled'),
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, success=False),
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
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0]['skipped'] == 1


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
@pytest.mark.now('2020-05-01T16:40:00Z')
@pytest.mark.parametrize(
    'pass_',
    [
        utils.make_pass('1_1', consts.qc.Exam.IDENTITY, data=[]),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[dict(field='field', value='value')],
        ),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[dict(field='field', value='')],
        ),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[dict(field='identity_number', value='')],
        ),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[
                dict(
                    field='identity_number',
                    value='8fd1ee166d8140499a529feb469e1892',
                ),
            ],
        ),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[
                dict(
                    field='identity_number',
                    value='8fd1ee166d8140499a529feb469e1892',
                ),
                dict(field='identity_id', value=''),
            ],
        ),
        utils.make_pass(
            '1_1',
            consts.qc.Exam.IDENTITY,
            data=[
                dict(field='identity_number', value=''),
                dict(field='identity_id', value='passport_rus'),
            ],
        ),
    ],
)
async def test_missing_data(mongo, mock_quality_control_py3, pass_):
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
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0].pop('succeeded') == 1
    assert stats[0].pop('resolution') == dict(SUCCESS=1)
    assert stats[0].pop('no_fields', None) or stats[0].pop('no_data', None)


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
@pytest.mark.parametrize(
    'providers',
    [
        ['taxi', 'taxi_walking_courier', 'lavka', 'eda'],
        ['taxi', 'taxi_walking_courier', 'lavka'],
        ['taxi', 'taxi_walking_courier', 'eda'],
        ['taxi', 'taxi_walking_courier'],
        ['taxi', 'lavka', 'eda'],
        ['taxi', 'lavka'],
        ['taxi', 'eda'],
        ['taxi'],
    ],
)
async def test_taxi_profile(
        mongo,
        mock_quality_control_py3,
        mock_driver_profiles,
        personal,
        providers,
        mockserver,
):
    orders_provider = {
        x: bool(x in providers)
        for x in [
            'taxi',
            'taxi_walking_courier',
            'lavka',
            'eda',
            'cargo',
            'retail',
        ]
    }

    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=[
                    utils.make_pass(
                        '1_1',
                        consts.qc.Exam.IDENTITY,
                        data=[
                            dict(
                                field='identity_number',
                                value='identity_number_pd_id',
                            ),
                            dict(
                                field='identity_data',
                                value='identity_data_pd_id',
                            ),
                            dict(field='identity_id', value='passport_rus'),
                        ],
                    ),
                ],
            ),
        )

    @mock_driver_profiles('/v1/driver/profiles/proxy-retrieve')
    async def profile(request):
        return web.json_response(
            data=dict(
                profiles=[
                    dict(
                        park_driver_profile_id=x,
                        data=dict(
                            orders_provider=orders_provider,
                            license=dict(pd_id='current'),
                        ),
                    )
                    for x in request.json['id_in_set']
                ],
            ),
        )

    @mock_driver_profiles('/v1/driver/identity')
    async def update_identity(request):
        return mockserver.make_response('', status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert profile.times_called == 1
    assert update_identity.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0] == dict(
        succeeded=1, not_changed=1, taxi_profile=1, resolution=dict(SUCCESS=1),
    )


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
@pytest.mark.parametrize('mode', ['no_profile', 'no_license', 'taxi_profile'])
async def test_missing_profile_data(
        mongo,
        mock_quality_control_py3,
        mock_driver_profiles,
        personal,
        mode,
        mockserver,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=[
                    utils.make_pass(
                        '1_1',
                        consts.qc.Exam.IDENTITY,
                        data=[
                            dict(
                                field='identity_number',
                                value='identity_number_pd_id',
                            ),
                            dict(
                                field='identity_data',
                                value='identity_data_pd_id',
                            ),
                            dict(field='identity_id', value='passport_rus'),
                        ],
                    ),
                ],
            ),
        )

    @mock_driver_profiles('/v1/driver/profiles/proxy-retrieve')
    async def profile(request):
        profile = dict(park_driver_profile_id='1_1')
        if mode != 'no_profile':
            data = {}
            if mode != 'no_license':
                data['license'] = dict(pd_id='current')
            if mode != 'taxi_profile':
                data['orders_provider'] = dict(taxi=False)
            profile['data'] = data
        return web.json_response(data=dict(profiles=[profile]))

    @mock_driver_profiles('/v1/driver/identity')
    async def update_identity(request):
        assert request.json == {
            'author': {
                'consumer': 'qc',
                'identity': {
                    'job_name': 'driver_identity_data',
                    'type': 'job',
                },
            },
            'identity': {
                'data_pd_id': 'identity_data_pd_id',
                'number_pd_id': 'identity_number_pd_id',
                'type': 'passport_rus',
            },
        }
        return mockserver.make_response('', status=200)

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert profile.times_called == 1
    assert update_identity.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    result_stats = dict(succeeded=1, not_changed=1, resolution=dict(SUCCESS=1))
    result_stats[mode] = 1
    assert stats[0] == result_stats


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
async def test_unchanged_license(
        mongo,
        mock_quality_control_py3,
        mock_driver_profiles,
        personal,
        mockserver,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=[
                    utils.make_pass(
                        '1_1',
                        consts.qc.Exam.IDENTITY,
                        data=[
                            dict(
                                field='identity_number',
                                value='8fd1ee166d8140499a529feb469e1892',
                            ),
                            dict(field='identity_id', value='passport_rus'),
                        ],
                    ),
                ],
            ),
        )

    @mock_driver_profiles('/v1/driver/profiles/proxy-retrieve')
    async def profile(request):
        return web.json_response(
            data=dict(
                profiles=[
                    dict(
                        park_driver_profile_id=x,
                        data=dict(
                            orders_provider=dict(taxi=False),
                            license=dict(pd_id='current'),
                        ),
                    )
                    for x in request.json['id_in_set']
                ],
            ),
        )

    personal.add(
        pd_type='license',
        number='COURIERF0F607D8EF9AF7FA6ABA6D8BEF486A1F',
        pd_id='current',
    )

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert profile.times_called == 1

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1
    assert stats[0] == dict(
        succeeded=1,
        not_changed=1,
        resolution=dict(SUCCESS=1),
        fields=dict(identity_data=dict(missing=1)),
    )


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(driver_identity_data=utils.job_settings()),
)
@pytest.mark.parametrize(
    'mode', ['new', 'exists', 'unique_already_exists', 'unique_not_found'],
)
async def test_changed_license(
        mongo,
        mock_quality_control_py3,
        mock_driver_profiles,
        mock_unique_drivers,
        personal,
        mode,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                modified=dates.timestring(),
                cursor='next',
                items=[
                    utils.make_pass(
                        '1_1',
                        consts.qc.Exam.IDENTITY,
                        data=[
                            dict(
                                field='identity_number',
                                value='8fd1ee166d8140499a529feb469e1892',
                            ),
                            dict(field='identity_id', value='passport_rus'),
                        ],
                    ),
                ],
            ),
        )

    @mock_driver_profiles('/v1/driver/profiles/proxy-retrieve')
    async def profile(request):
        return web.json_response(
            data=dict(
                profiles=[
                    dict(
                        park_driver_profile_id=x,
                        data=dict(
                            orders_provider=dict(taxi=False),
                            license=dict(pd_id='current'),
                        ),
                    )
                    for x in request.json['id_in_set']
                ],
            ),
        )

    @mock_unique_drivers('/service/v1/uniques/merge')
    async def uniques_merge(request):
        if mode not in ['unique_already_exists', 'unique_not_found']:
            return web.json_response(data={})

        return web.json_response(
            status=400,
            data=dict(code=mode.upper(), message=' '.join(mode.split('_'))),
        )

    @mock_driver_profiles('/v1/courier/license')
    async def update_license(request):
        return web.json_response(data={})

    number = 'COURIERF0F607D8EF9AF7FA6ABA6D8BEF486A1F'
    if mode in ['exists', 'unique_already_exists', 'unique_not_found']:
        personal.add('license', number=number, pd_id='exists')

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.driver_identity_data', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 1
    assert profile.times_called == 1
    assert update_license.times_called == 1
    assert uniques_merge.times_called == 1

    # check if stored to personal service
    new_license_pd_id = personal.get('license', number=number)
    assert new_license_pd_id

    # check uniques merge request
    assert uniques_merge.next_call()['request'].json == dict(
        new_license_pd_id=new_license_pd_id, old_license_pd_id='current',
    )

    assert update_license.next_call()['request'].json == dict(
        license=dict(number=number),
        author=dict(
            consumer='qc',
            identity=dict(job_name='driver_identity_data', type='job'),
        ),
    )

    job_data = await mongo.qc_jobs_data.find_one({})
    stats = list(job_data['statistics'].values())
    assert len(stats) == 1

    assert stats[0].pop('license_pd_id') == (
        dict(stored=1) if mode == 'new' else dict(exists=1)
    )

    if mode in ['unique_already_exists', 'unique_not_found']:
        assert stats[0].pop('uniques') == dict(not_merged=1)
    else:
        assert stats[0].pop('uniques') == dict(merged=1)

    assert stats[0] == dict(
        succeeded=1,
        changed=1,
        resolution=dict(SUCCESS=1),
        fields=dict(identity_data=dict(missing=1)),
    )
