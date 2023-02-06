import json

import pytest

ENDPOINT_URL = 'fleet/work-modes/v1/contractor/block/temporary'


PROFILES_GOOD_RESPONSE = {
    'profiles': [
        {
            'data': {'license': {'pd_id': 'license_pd_id1'}},
            'park_driver_profile_id': 'park_id1_contractor_id1',
        },
    ],
}
PROFILES_NO_DRIVER = {
    'profiles': [{'park_driver_profile_id': 'park_id1_contractor_id1'}],
}
PROFILES_NO_LICENSE = {
    'profiles': [
        {
            'data': {'license': None},
            'park_driver_profile_id': 'park_id1_contractor_id1',
        },
    ],
}


@pytest.mark.parametrize(
    [
        'profiles_response',
        'blocklist_code',
        'blocklist_response',
        'dwm_code',
        'dwm_response',
    ],
    [
        (
            PROFILES_GOOD_RESPONSE,
            200,
            {'block_id': '68188f40-f665-4403-b237-9d91c22b15c6'},
            200,
            {'block_id': '68188f40-f665-4403-b237-9d91c22b15c6'},
        ),
        (
            PROFILES_NO_DRIVER,
            None,
            None,
            400,
            {
                'code': 'DRIVER_NOT_FOUND_OR_NO_LICENSE',
                'message': 'Driver not found or has no license',
            },
        ),
        (
            PROFILES_NO_LICENSE,
            None,
            None,
            400,
            {
                'code': 'DRIVER_HAS_NO_LICENSE',
                'message': 'Driver has no license',
            },
        ),
        (
            PROFILES_GOOD_RESPONSE,
            400,
            {
                'code': 'REASON_SUBSTITUTE_ERROR',
                'message': (
                    'Failed to substitude key\'s arguments: Translation '
                    '[taximeter_backend_driver_messages]'
                    '[blocklist.reasons.yango_temporary_block.default] '
                    'failed: No substitution for key unblock_date when '
                    'formatting template Вы временно заблокированы '
                    'парком до {unblock_date}'
                ),
            },
            400,
            {
                'code': 'REASON_SUBSTITUTE_ERROR',
                'message': (
                    'Failed to substitude key\'s arguments: Translation '
                    '[taximeter_backend_driver_messages]'
                    '[blocklist.reasons.yango_temporary_block.default] '
                    'failed: No substitution for key unblock_date when '
                    'formatting template Вы временно заблокированы '
                    'парком до {unblock_date}'
                ),
            },
        ),
    ],
)
async def test_contractor_block(
        taxi_driver_work_modes,
        mockserver,
        profiles_response,
        blocklist_code,
        blocklist_response,
        dwm_code,
        dwm_response,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['park_id1_contractor_id1'],
            'projection': ['data.license.pd_id'],
        }
        return profiles_response

    @mockserver.json_handler('/blocklist/internal/blocklist/v1/add')
    def _blocklist_add(request):
        assert request.json == {
            'block': {
                'comment': '',
                'expires': '2022-01-01T12:00:00+00:00',
                'kwargs': {
                    'license_id': 'license_pd_id1',
                    'park_id': 'park_id1',
                },
                'mechanics': 'yango_temporary_block',
                'predicate_id': '44444444-4444-4444-4444-444444444444',
                'reason': {
                    'key': 'blocklist.reasons.yango_temporary_block.default',
                },
            },
            'identity': {'name': 'driver-work-modes', 'type': 'service'},
        }
        return mockserver.make_response(
            json.dumps(blocklist_response), blocklist_code,
        )

    dwm_request = {
        'contractor_id': 'contractor_id1',
        'expires': '2022-01-01T15:00:00+03:00',
    }

    headers = {
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '123',
        'Content-Type': 'application/json',
        'Accept-Language': 'ru_RU',
        'X-Idempotency-Token': '1111',
        'X-Park-Id': 'park_id1',
    }

    response = await taxi_driver_work_modes.post(
        ENDPOINT_URL, json=dwm_request, headers=headers,
    )

    assert response.status_code == dwm_code
    assert response.json() == dwm_response
