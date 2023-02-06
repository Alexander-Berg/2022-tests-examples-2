import datetime

import pytest

from clownductor.internal.utils import postgres


class DatetimeNearNow:
    def __init__(self, epsilon_seconds: float):
        self._eps = datetime.timedelta(seconds=epsilon_seconds)

    def __repr__(self):
        return f'DatetimeNearNow({self._eps})'

    def __eq__(self, other):
        if not isinstance(other, datetime.datetime):
            return False
        now = datetime.datetime.now()
        return (now - self._eps) <= other <= now


@pytest.mark.dontfreeze
async def test_delete_service(web_app_client, web_context):
    response = await web_app_client.post(
        '/permissions/v1/idm/add-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={
            'login': 'd1mbas',
            'path': (
                '/project/taxi/role/service/service_role/'
                'clownductor/service_role/deploy_approve_programmer/'
            ),
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'code': 0}

    async with postgres.get_connection(web_context) as conn:
        await conn.fetch('delete from clownductor.services where id = 1')
        roles = await conn.fetch(
            'select * from permissions.roles where deleted_service = 1',
        )

    assert len(roles) == 1
    assert dict(roles[0]) == {
        'created_at': DatetimeNearNow(1),
        'deleted_at': DatetimeNearNow(0.5),
        'deleted_project': None,
        'deleted_service': 1,
        'fired': False,
        'id': 2,
        'is_deleted': True,
        'login': 'd1mbas',
        'project_id': None,
        'role': 'deploy_approve_programmer',
        'service_id': None,
        'updated_at': DatetimeNearNow(1),
        'is_super': False,
    }
