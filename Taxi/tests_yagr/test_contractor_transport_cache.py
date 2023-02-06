import time

import pytest


@pytest.mark.config(
    CONTRACTOR_TRANSPORT_CACHE_SETTINGS={
        'yagr': {
            'cache_enabled': True,
            'batch_size': 1,
            'only_active_contractors': True,
        },
    },
)
async def test_cache_server_cycle(taxi_yagr_adv, mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '1234567_4':
            return {
                'contractors_transport': [
                    {
                        'contractor_id': 'park3_driver2',
                        'is_deleted': False,
                        'revision': '1234567_2',
                        'transport_active': {'type': 'pedestrian'},
                    },
                ],
                'cursor': '1234567_3',
            }
        return {
            'contractors_transport': [
                {
                    'contractor_id': 'park4_driver4',
                    'is_deleted': False,
                    'revision': '1234567_4',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car4'},
                },
            ],
            'cursor': '1234567_4',
        }

    await taxi_yagr_adv.invalidate_caches()


@pytest.mark.config(
    CONTRACTOR_TRANSPORT_CACHE_SETTINGS={
        'yagr': {
            'cache_enabled': True,
            'batch_size': 1,
            'only_active_contractors': True,
            'max_update_time_seconds': 1,
        },
    },
)
async def test_kill_update(taxi_yagr_adv, mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        time.sleep(5)
        return {
            'contractors_transport': [
                {
                    'contractor_id': 'park3_driver2',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'pedestrian'},
                },
            ],
            'cursor': request.query.get('cursor', '') + '9',
        }

    await taxi_yagr_adv.invalidate_caches()
