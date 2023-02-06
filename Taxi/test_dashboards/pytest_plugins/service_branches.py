import pytest

from dashboards.internal import types
from dashboards.internal.models import service_branches


ADD_SERVICE_BRANCH_QUERY = """
INSERT INTO dashboards.service_branches (
    clown_branch_id,
    project_name,
    service_name,
    branch_name,
    hostnames,
    group_info
)
VALUES (
    '{clown_branch_id}',
    '{project_name}',
    '{service_name}',
    '{branch_name}',
    ARRAY{hostnames},
    ROW('{group_info_name}', '{group_info_type}')
)
RETURNING id;
"""


@pytest.fixture(name='service_branch_mock')
def _service_branch_mock():
    return service_branches.BareServiceBranch(
        clown_branch_id=123,
        project_name='taxi-devops',
        service_name='test_service',
        branch_name='stable',
        hostnames=['test_service.taxi.yandex.net'],
        group_info=service_branches.GroupInfo(
            name='test_service_stable',
            type=service_branches.GroupType('nanny'),
        ),
        awacs_namespace=None,
    )


@pytest.fixture(name='add_service_branch')
def _add_service_branch():
    async def _wrapper(
            context: types.AnyContext,
            service_branch: service_branches.BareServiceBranch,
    ) -> int:
        query = ADD_SERVICE_BRANCH_QUERY.format(
            clown_branch_id=service_branch.clown_branch_id,
            project_name=service_branch.project_name,
            service_name=service_branch.service_name,
            branch_name=service_branch.branch_name,
            hostnames=service_branch.hostnames,
            group_info_name=service_branch.group_info.name,
            group_info_type=service_branch.group_info.type.value,
        )

        record = await context.pg.primary.fetchrow(query)
        return record['id']

    return _wrapper
