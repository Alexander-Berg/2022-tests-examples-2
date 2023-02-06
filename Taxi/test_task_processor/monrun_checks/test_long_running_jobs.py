import freezegun
import pytest

from task_processor.generated.cron import run_monrun


@pytest.mark.parametrize(
    'expected_msg',
    [
        pytest.param(
            '0; Check done',
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 30, 'warn': 25}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='no_old_jobs',
        ),
        pytest.param(
            (
                '1; Dummy job #1(job_id=1, recipe_id=1), '
                'Dummy job #2(job_id=4, recipe_id=2) '
                'jobs are running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 30, 'warn': 15}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='two_old_jobs_warn',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1), '
                'Dummy job #2(job_id=4, recipe_id=2), '
                'Dummy job #2(job_id=6, recipe_id=2) '
                'jobs are running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 14, 'warn': 12}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='three_old_jobs_crit',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1) '
                'job is running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 19, 'warn': 17}},
                    'jobs': [],
                    'ignored_jobs': [],
                },
            ),
            id='one_old_job_crit',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1) '
                'job is running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 18, 'warn': 10}},
                    'jobs': [],
                    'ignored_jobs': ['Dummy job #2'],
                },
            ),
            id='one_old_job_crit_for_exclusion',
        ),
        pytest.param(
            '0; Check done',
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 12, 'warn': 10}},
                    'jobs': [
                        {'name': 'Dummy job #1', 'excluded': [1]},
                        {'name': 'Dummy job #2', 'excluded': [4, 6, 9]},
                    ],
                    'ignored_jobs': [],
                },
            ),
            id='no_old_jobs_for_excluded_ids',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1) '
                'job is running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 15, 'warn': 12}},
                    'jobs': [{'name': 'Dummy job #2', 'excluded': [4, 6]}],
                    'ignored_jobs': [],
                },
            ),
            id='one_old_job_crit_for_ids_exclusion',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1) '
                'job is running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 12, 'warn': 10}},
                    'jobs': [
                        {
                            'name': 'Dummy job #2',
                            'age_levels': {'warn': 20, 'crit': 30},
                        },
                    ],
                    'ignored_jobs': [],
                },
            ),
            id='crit_for_both_cause_Dummy_job_#2_is_critical',
        ),
        pytest.param(
            (
                '2; Dummy job #1(job_id=1, recipe_id=1), '
                'Dummy job #2(job_id=4, recipe_id=2) '
                'jobs are running for too long'
            ),
            marks=pytest.mark.config(
                TASK_PROCESSOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
                    'common': {'age_levels': {'crit': 20, 'warn': 15}},
                    'jobs': [
                        {'name': 'Dummy job #1', 'age_levels': {'crit': 15}},
                    ],
                    'ignored_jobs': [],
                },
            ),
            id=(
                'crit_for_both_cause_'
                'Dummy_job_#1_is_critical_for_explicit_time_settings'
            ),
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['init_data.sql'])
@freezegun.freeze_time('1998-11-22 8:35:00')
async def test_long_running_jobs(expected_msg):
    msg = await run_monrun.run(
        ['task_processor.monrun_checks.long_running_jobs'],
    )
    assert msg == expected_msg
