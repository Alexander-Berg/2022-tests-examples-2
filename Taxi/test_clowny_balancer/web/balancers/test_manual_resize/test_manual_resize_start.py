from typing import Optional
import uuid

import pytest

from clowny_balancer.pytest_plugins import (
    manual_resize as manual_resize_plugin,
)


DEFAULT_ALLOCATION_REQUEST = {
    'replicas': {'sas': 2, 'vla': 2},
    'preset': 'NANO',
    'io_intensity': 'HIGH',
    'network_macro': '_TEST_NETS_',
}


@pytest.fixture(autouse=True)
def _autoinit_db(fill_default_manual_resize):
    pass


@pytest.fixture(name='manual_resize_start_request')
def _manual_resize_start_request(taxi_clowny_balancer_web):
    async def _wrapper(
            namespace_id: str,
            allocation_request: dict,
            token: Optional[str] = None,
    ):
        response = await taxi_clowny_balancer_web.post(
            '/balancers/v1/manual_resize/start/',
            json={
                'meta': {'namespace_id': namespace_id},
                'allocation_request': allocation_request,
            },
            headers={'X-Idempotency-Token': token or uuid.uuid4().hex},
        )
        return response

    return _wrapper


@pytest.mark.parametrize(
    ['namespace_id'],
    [
        pytest.param('new-namespace', id='new_namespace'),
        pytest.param(
            manual_resize_plugin.RECORD_2.namespace_id,
            id='not_in_progress_namespace',
        ),
    ],
)
async def test_start_manual_resize(manual_resize_start_request, namespace_id):
    response = await manual_resize_start_request(
        namespace_id=namespace_id,
        allocation_request=DEFAULT_ALLOCATION_REQUEST,
    )
    assert response.status == 200
    content = await response.json()
    assert content.keys() == {'resize_id'}
    assert len(content.pop('resize_id')) == 22


async def test_already_in_progress_resize(manual_resize_start_request):
    response = await manual_resize_start_request(
        namespace_id=manual_resize_plugin.RECORD_1.namespace_id,
        allocation_request=DEFAULT_ALLOCATION_REQUEST,
    )
    assert response.status == 409
    content = await response.json()
    resize_id = manual_resize_plugin.RECORD_1.resize_id
    namespace_id = manual_resize_plugin.RECORD_1.namespace_id
    assert content == {
        'code': 'RESIZE_ALREADY_STARTED',
        'details': {'resize_id': resize_id},
        'message': (
            f'There is already active resize with id {resize_id} for '
            f'namespace {namespace_id}'
        ),
    }


async def test_idempotency_token(manual_resize_start_request):
    response = await manual_resize_start_request(
        namespace_id=manual_resize_plugin.RECORD_1.namespace_id,
        allocation_request=DEFAULT_ALLOCATION_REQUEST,
        token=manual_resize_plugin.RECORD_1.idempotency_token,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'resize_id': manual_resize_plugin.RECORD_1.resize_id}
