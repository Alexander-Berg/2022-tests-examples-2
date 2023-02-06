import pytest

from clownductor.generated.cron import run_monrun


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param('0; Ok'),
        pytest.param(
            '2; Missing roles: service taxi_srv1 roles deploy_approve_manager',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'projects.sql',
                        'services.sql',
                        'taxi-srv1-has-no-manager.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            (
                '2; '
                'Missing roles: '
                'service taxi_srv1 roles deploy_approve_manager, '
                'service eda_srv3 roles '
                'deploy_approve_manager,deploy_approve_programmer'
                # 'Service taxi_srv1 '
                # 'has no roles at all deploy_approve_manager; '
                # 'Service eda_srv3 has no roles at all '
                # 'deploy_approve_manager, deploy_approve_programmer'
            ),
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'projects.sql',
                        'services.sql',
                        'taxi-srv1-has-no-manager_eda-srv3-has-no-all.sql',
                    ],
                ),
            ],
        ),
    ],
)
async def test_monrun(expected):
    msg = await run_monrun.run(
        ['clownductor.monrun_checks.idm.services_with_no_approvers_at_all'],
    )
    assert msg == expected
