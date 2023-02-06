# pylint: disable=redefined-outer-name
import pytest

from clownductor.internal import balancers


@pytest.fixture
def balancer(web_context):
    return balancers.Balancers(web_context)


@pytest.mark.usefixtures('mocks_for_service_creation')
async def test_add_and_search(add_service, add_nanny_branch, balancer):
    service = await add_service('test_project', 'test_service')
    await add_nanny_branch(service['id'], 'test_branch_1')
    await add_nanny_branch(service['id'], 'test_branch_2')

    await balancer.add(1, 'test-name')
    _balancers = await balancer.get_by_service_id(1)
    assert len(_balancers) == 1
    assert _balancers[0] == balancers.Balancer(1, 'test-name', False, False)
