import dataclasses
from typing import List
from typing import Optional

import pytest


@dataclasses.dataclass()
class AwacsRequest:
    backends_in_update: Optional[List[dict]] = None


def param(
        name: str,
        input_data: dict,
        payload: Optional[dict] = None,
        extras: Optional[dict] = None,
        awacs_request: Optional[AwacsRequest] = None,
        id_: Optional[str] = None,
):
    return pytest.param(
        name, input_data, payload, extras or {}, awacs_request, id=id_,
    )


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras, awacs_request',
    [
        param(
            'AwacsL3GetBalancer',
            {'namespace_id': 'ns_1'},
            {'l3_balancer_id': 'abc', 'l3mgr_service_id': '123'},
        ),
        param(
            'AwacsL3AddBackend',
            {
                'namespace_id': 'ns_1',
                'balancer_id': 'abc',
                'backend_id': 'abc',
            },
            awacs_request=AwacsRequest(
                backends_in_update=[{'id': 'some'}, {'id': 'abc'}],
            ),
        ),
        param(
            'AwacsL3AddBackend',
            {
                'namespace_id': 'ns_1',
                'balancer_id': 'abc',
                'backend_id': 'some',
            },
            awacs_request=AwacsRequest(backends_in_update=[{'id': 'some'}]),
        ),
    ],
)
async def test_cube(
        mockserver,
        call_cube,
        cube_name,
        input_data,
        payload,
        extras,
        awacs_request,
):
    @mockserver.json_handler('/client-awacs/api/ListL3Balancers/')
    def _l3_list_handler(request):
        assert request.json['fieldMask'] == 'meta.id,spec.l3mgrServiceId'
        return {
            'l3Balancers': [
                {'meta': {'id': 'abc'}, 'spec': {'l3mgrServiceId': '123'}},
            ],
        }

    @mockserver.json_handler('/client-awacs/api/GetL3Balancer/')
    def _l3_get_handler(request):
        assert request.json == {'namespaceId': 'ns_1', 'id': 'abc'}
        return {
            'l3Balancer': {
                'meta': {'id': 'abc'},
                'spec': {'realServers': {'backends': [{'id': 'some'}]}},
            },
        }

    @mockserver.json_handler('/client-awacs/api/UpdateL3Balancer/')
    def _l3_update_handler(request):
        assert (
            request.json['spec']['realServers']['backends']
            == awacs_request.backends_in_update
        )
        return {}

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(extras)
    assert response == result
