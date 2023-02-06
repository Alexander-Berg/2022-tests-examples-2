import datetime

import freezegun
import pytest

from clownductor.generated.cron import run_monrun


@pytest.mark.parametrize(
    'expected_msg, create_branch',
    [
        pytest.param(
            '0; Check done',
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 15, 'warn': 30}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='no_old_jobs',
        ),
        pytest.param(
            (
                '1; CreateNannyService(job_id=1, service_id=1), '
                'CreateFullNannyBranch(job_id=2, service_id=1) '
                'jobs are running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 30, 'warn': 5}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='two_old_jobs_warn',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1), '
                'CreateFullNannyBranch(job_id=2, service_id=1) '
                'jobs are running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='two_old_jobs_crit',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1) '
                'job is running for too long'
            ),
            False,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='one_old_job_crit',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1) '
                'job is running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [],
                    'ignored_jobs': ['CreateFullNannyBranch'],
                },
            ),
            id='one_old_job_crit_for_exclusion',
        ),
        pytest.param(
            '0; Check done',
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [
                        {'name': 'CreateFullNannyBranch', 'excluded': [2]},
                        {'name': 'CreateNannyService', 'excluded': [1]},
                    ],
                    'ignored_jobs': [],
                },
            ),
            id='no_old_jobs_for_excluded_ids',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1) '
                'job is running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [
                        {'name': 'CreateFullNannyBranch', 'excluded': [2]},
                    ],
                    'ignored_jobs': [],
                },
            ),
            id='one_old_job_crit_for_ids_exclusion',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1), '
                'CreateFullNannyBranch(job_id=2, service_id=1) '
                'jobs are running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 5, 'warn': 1}},
                    'jobs': [
                        {
                            'name': 'CreateFullNannyBranch',
                            'age_levels': {'crit': 120},
                        },
                    ],
                    'ignored_jobs': [],
                },
            ),
            id='crit_for_both_cause_CreateNannyService_is_critical',
        ),
        pytest.param(
            (
                '2; CreateNannyService(job_id=1, service_id=1), '
                'CreateFullNannyBranch(job_id=2, service_id=1) '
                'jobs are running for too long'
            ),
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 120, 'warn': 1}},
                    'jobs': [
                        {
                            'name': 'CreateFullNannyBranch',
                            'age_levels': {'crit': 5},
                        },
                    ],
                    'ignored_jobs': [],
                },
            ),
            id=(
                'crit_for_both_cause_'
                'branch_job_is_critical_for_explicit_time_settings'
            ),
        ),
    ],
)
async def test_long_running_jobs(
        web_app_client,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_service_jobs,
        expected_msg,
        create_branch,
):
    login_mockserver()
    staff_mockserver()
    await add_project('project-1')
    service = await add_service('project-1', 'service-1')
    if create_branch:
        response = await web_app_client.post(
            f'/v2/create_nanny_branch/',
            params={'service_id': service['id']},
            json={
                'name': 'testing',
                'env': 'testing',
                'preset': 'x2pico',
                'disk_profile': 'default',
            },
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200

    with freezegun.freeze_time() as timer:
        timer.tick(delta=datetime.timedelta(minutes=10))
        msg = await run_monrun.run(
            ['clownductor.monrun_checks.long_running_jobs'],
        )
        assert msg == expected_msg

    jobs = await get_service_jobs(service['id'])
    if create_branch:
        assert len(jobs) == 2
        assert {x['job']['name'] for x in jobs} == {
            'CreateNannyService',
            'CreateFullNannyBranch',
        }
    else:
        assert len(jobs) == 1
        assert jobs[0]['job']['name'] == 'CreateNannyService'
