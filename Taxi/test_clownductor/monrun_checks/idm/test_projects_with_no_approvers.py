import pytest

from clownductor.generated.cron import run_monrun


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param('0; Ok'),
        pytest.param(
            '1; Missing roles: project eda roles deploy_approve_manager',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=['projects.sql', 'eda_has_no_manager_approve.sql'],
                ),
            ],
        ),
        pytest.param(
            '1; Missing roles: project eda roles deploy_approve_programmer',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=['projects.sql', 'eda_has_no_dev_approve.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                '1; '
                'Missing roles: project taxi roles deploy_approve_manager, '
                'project eda roles deploy_approve_programmer'
            ),
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'projects.sql',
                        'eda_has_no_dev-taxi_has_no_manager.sql',
                    ],
                ),
            ],
        ),
    ],
)
async def test_monrun(expected):
    msg = await run_monrun.run(
        ['clownductor.monrun_checks.idm.projects_with_no_approvers'],
    )
    assert msg == expected
