import json

import pytest

ENDPOINT_URL = 'fleet/work-modes/v1/contractor/unblock'


@pytest.mark.parametrize(
    ['blocklist_code', 'blocklist_response', 'dwm_code', 'dwm_response'],
    [
        (200, {}, 204, None),
        (204, {}, 204, None),
        (
            400,
            {'code': 'PERMISSION_DENIED', 'message': 'Permission denied'},
            400,
            {'code': 'PERMISSION_DENIED', 'message': 'Permission denied'},
        ),
        (
            404,
            {'code': 'BLOCK_NOT_FOUND', 'message': 'Block not found'},
            404,
            {'code': 'BLOCK_NOT_FOUND', 'message': 'Block not found'},
        ),
    ],
)
async def test_contractor_block(
        taxi_driver_work_modes,
        mockserver,
        blocklist_code,
        blocklist_response,
        dwm_code,
        dwm_response,
):
    @mockserver.json_handler('/blocklist/internal/blocklist/v1/delete')
    def _blocklist_add(request):
        assert request.json == {
            'block': {
                'block_id': '00000000-0000-0000-0000-000000000000',
                'comment': '',
            },
            'identity': {'name': 'driver-work-modes', 'type': 'service'},
        }
        return mockserver.make_response(
            json.dumps(blocklist_response), blocklist_code,
        )

    dwm_request = {'block_id': '00000000-0000-0000-0000-000000000000'}

    headers = {
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '123',
        'Content-Type': 'application/json',
        'X-Park-Id': 'park_id1',
    }

    response = await taxi_driver_work_modes.post(
        ENDPOINT_URL, json=dwm_request, headers=headers,
    )

    assert response.status_code == dwm_code
    if dwm_code != 204:
        assert response.json() == dwm_response
