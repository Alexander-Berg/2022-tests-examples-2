# pylint: disable=redefined-outer-name
import pytest

from clownductor.generated.cron import run_monrun


@pytest.mark.parametrize(
    ['service_names', 'expected'],
    [
        (['test_service_1'], '0; Check done'),
        (
            [
                'test_service_1',
                'test_service_2',
                'test_service_3',
                'test_service_4',
                'test_service_5',
            ],
            '2; CRIT: '
            'service test_service_2 is suspicious, '
            'owner of service test_service_3 is robot, '
            'no owner for service test_service_4, '
            'non-Taxi owner of service test_service_5',
        ),
    ],
)
async def test_abc_owners_check(
        cron_context,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        service_names,
        expected,
):
    abc_mockserver()
    login_mockserver()
    staff_mockserver()

    project = await add_project('taxi')
    for service_name in service_names:
        await cron_context.service_manager.services.add(
            {
                'project_id': project['id'],
                'name': service_name,
                'artifact_name': '-',
                'cluster_type': 'nanny',
                'st_task': '',
                'abc_service': service_name,
            },
        )

    msg = await run_monrun.run(['clownductor.monrun_checks.abc_owners_check'])
    assert msg == expected
