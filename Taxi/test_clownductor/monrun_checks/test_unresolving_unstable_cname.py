import pytest

from clownductor.generated.cron import run_monrun


@pytest.fixture(name='clowny_balancers_mock')
def _clowny_balancers_mock(mockserver, mock_clowny_balancer):
    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _handler(_):
        return mockserver.make_response(
            json={'code': '', 'message': ''}, status=404,
        )


@pytest.mark.usefixtures('clowny_balancers_mock')
@pytest.mark.pgsql('clownductor', files=['pg_clownductor.sql'])
async def test_ok(patch):
    @patch('clownductor.internal.unstable_cnames.check_fqdn')
    async def _check_fqdn(unstable_branch, resolver):
        return True, unstable_branch.host

    msg = await run_monrun.run(
        ['clownductor.monrun_checks.check_unresolving_unstable_cname'],
    )
    assert msg == '0; Check done'


@pytest.mark.usefixtures('clowny_balancers_mock')
@pytest.mark.pgsql('clownductor', files=['pg_clownductor.sql'])
async def test_warn(patch):
    @patch('clownductor.internal.unstable_cnames.check_fqdn')
    async def _check_fqdn(unstable_branch, resolver):
        return False, None

    msg = await run_monrun.run(
        ['clownductor.monrun_checks.check_unresolving_unstable_cname'],
    )
    assert (
        msg == '1; Unresolving branches: test-service.yataxi.net -> test-fqdn'
    )
