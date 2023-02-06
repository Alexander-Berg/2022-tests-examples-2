import pytest

from clownductor.generated.cron import run_cron


@pytest.mark.now('2020-02-21T19:00:00.0Z')
@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.config(
    CLOWNDUCTOR_REMOVE_SUSPENDED_PODS={
        'max_age_in_hours': 24,
        'yp_regions': ['sas', 'vla', 'man'],
        'skip_for_services': [],
        'skip_for_branches': [],
        'enabled': True,
        'only_search': False,
    },
)
async def test_old_pods(
        mockserver,
        nanny_yp_mockserver,
        nanny_mockserver,
        add_service,
        add_nanny_branch,
):
    service = await add_service(
        'test', 'test_old_pods', direct_link='test_old_pods',
    )
    await add_nanny_branch(
        service['id'], 'test-branch', direct_link='test_old_pods',
    )

    service2 = await add_service(
        'test', 'test-service', direct_link='test-service',
    )
    await add_nanny_branch(
        service2['id'], 'test-branch-2', direct_link='test-service',
    )

    nanny_yp_mockserver()

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/RemovePod/')
    async def _handler(request):
        assert request.method == 'POST'
        data = request.json
        assert data['podId'] == 'qqbyrftajycoh7q2'
        return {}

    await run_cron.main(
        ['clownductor.crontasks.remove_old_suspended_pods', '-t', '0'],
    )
    assert _handler.times_called == 2
