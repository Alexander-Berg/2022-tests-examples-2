# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest
from contractor_fts_receiver_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def contractor_transport_request(mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '123456_6':
            return {'contractors_transport': [], 'cursor': '1234567_6'}
        data = {
            'contractors_transport': [
                {
                    'contractor_id': 'park3_driver2',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'berty_qwerty1',
                    'is_deleted': False,
                    'revision': '1234567_3',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
                {
                    'contractor_id': 'park3_driver3',
                    'is_deleted': False,
                    'revision': '1234567_3',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
                {
                    'contractor_id': 'park4_driver4',
                    'is_deleted': False,
                    'revision': '1234567_4',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car4'},
                },
                {
                    'contractor_id': 'dbid_uuidpedestrian',
                    'is_deleted': False,
                    'revision': '1234567_5',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'dbid_uuiddriver',
                    'is_deleted': False,
                    'revision': '1234567_6',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
            ],
            'cursor': '1234567_6',
        }
        return mockserver.make_response(response=json.dumps(data))
