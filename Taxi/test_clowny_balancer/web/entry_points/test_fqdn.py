from typing import Optional

import pytest


def case(
        *,
        service_id: Optional[int] = None,
        env: Optional[str] = None,
        branch_id: Optional[int] = None,
        response_status: int,
        response_json: dict,
        is_external: Optional[bool] = None,
):
    params = {
        'service_id': service_id,
        'env': env,
        'branch_id': branch_id,
        'is_external': is_external,
    }
    params = {key: val for key, val in params.items() if val is not None}
    return params, response_status, response_json


@pytest.mark.parametrize(
    'params, response_status, response_json',
    [
        case(
            service_id=1,
            env='stable',
            response_status=200,
            response_json={'fqdns': ['ext-test.net', 'test.net']},
        ),
        case(
            service_id=1,
            env='stable',
            response_status=200,
            response_json={'fqdns': ['test.net']},
            is_external=False,
        ),
        case(
            service_id=1,
            env='stable',
            response_status=200,
            response_json={'fqdns': ['ext-test.net']},
            is_external=True,
        ),
        case(
            service_id=2,
            env='stable',
            response_status=200,
            response_json={'fqdns': []},
        ),
        case(
            branch_id=2,
            response_status=200,
            response_json={'fqdns': ['ext-test.net', 'test.net']},
        ),
        case(
            service_id=1,
            branch_id=1,
            response_status=400,
            response_json={
                'code': 'REQUEST_ERROR',
                'message': (
                    'Only one group is required: [\'service_id\', \'env\'] OR '
                    '[\'branch_id\']'
                ),
            },
        ),
        case(
            service_id=1,
            response_status=400,
            response_json={
                'code': 'REQUEST_ERROR',
                'message': 'Param "env" is required',
            },
        ),
        case(
            branch_id=1,
            env='stable',
            response_status=400,
            response_json={
                'code': 'REQUEST_ERROR',
                'message': (
                    'Only one group is required: [\'service_id\', \'env\'] OR '
                    '[\'branch_id\']'
                ),
            },
        ),
        case(
            service_id=1,
            env='stable',
            branch_id=1,
            response_status=400,
            response_json={
                'code': 'REQUEST_ERROR',
                'message': (
                    'Only one group is required: [\'service_id\', \'env\'] OR '
                    '[\'branch_id\']'
                ),
            },
        ),
    ],
)
async def test_fqdn_search(
        taxi_clowny_balancer_web, params, response_status, response_json,
):
    response = await taxi_clowny_balancer_web.get(
        '/v1/entry-points/fqdn/search/', params=params,
    )
    assert response.status == response_status
    assert await response.json() == response_json
