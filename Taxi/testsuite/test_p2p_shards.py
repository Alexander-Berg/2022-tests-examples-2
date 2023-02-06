import asyncio
import pytest


DUMMY_DRIVER_FOR_ORDER_REQUEST = {
    'aliases': [],
    'allowed_classes': ['courier'],
    'excluded_car_numbers': [],
    'excluded_ids': [],
    'excluded_license_ids': [],
    'lookup': {'generation': 1, 'version': 1, 'wave': 1},
    'order_id': 'taxi-order',
}


@pytest.fixture
def dummy_candidates(mockserver):
    def wrapper(*, chain_info=None):
        @mockserver.json_handler('/candidates/order-search')
        def order_search(request):
            response = {
                'candidates': [
                    {
                        'car_id': 'd08b0e4d8360010cb27f19659ea3f96e',
                        'car_number': 'Н792ВР76',
                        'classes': ['courier'],
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838473',
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_d0000000000000000000000000000001',
                        'license_id': '1677495cbb1a41b38ab3d71813c2569e',
                        'metadata': {},
                        'position': [37.632745, 55.774532],
                        'position_info': {
                            'timestamp': '2021-11-29T16:58:12+00:00',
                        },
                        'route_info': {
                            'approximate': False,
                            'distance': 10,
                            'properties': {'toll_roads': False},
                            'time': 20,
                        },
                        'status': {
                            'driver': 'free',
                            'orders': [],
                            'status': 'online',
                            'taximeter': 'free',
                        },
                        'transport': {'type': 'car'},
                        'unique_driver_id': '5a201c5751baddbf5b24469b',
                        'uuid': 'd0000000000000000000000000000001',
                    },
                    {
                        'car_id': 'd08b0e4d8360010cb27f19659ea3f96e',
                        'car_number': 'Н792ВР76',
                        'classes': ['courier'],
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838479',
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_d0000000000000000000000000000002',
                        'license_id': '1677495cbb1a41b38ab3d71813c2569e',
                        'metadata': {},
                        'position': [37.632745, 55.774532],
                        'position_info': {
                            'timestamp': '2021-11-29T16:58:12+00:00',
                        },
                        'route_info': {
                            'approximate': False,
                            'distance': 10,
                            'properties': {'toll_roads': False},
                            'time': 20,
                        },
                        'status': {
                            'driver': 'free',
                            'orders': [],
                            'status': 'online',
                            'taximeter': 'free',
                        },
                        'transport': {'type': 'car'},
                        'unique_driver_id': '5a201c5751baddbf5b24469b',
                        'uuid': 'd0000000000000000000000000000002',
                    },
                ],
            }
            if chain_info is not None:
                for candidate in response['candidates']:
                    candidate['chain_info'] = chain_info
            return response

        @mockserver.json_handler('/candidates/profiles')
        def profiles(request):
            return {
                'drivers': [
                    {
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_d0000000000000000000000000000001',
                        'uuid': 'd0000000000000000000000000000001',
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838473',
                        'position': [37.632745, 55.774532],
                        'classes': ['courier'],
                    },
                    {
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_d0000000000000000000000000000002',
                        'uuid': 'd0000000000000000000000000000002',
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838479',
                        'position': [37.632745, 55.774532],
                        'classes': ['courier'],
                    },
                ],
            }

    return wrapper


@pytest.mark.skip(reason="not finished yet")
async def test_conflict(
        create_segment,
        rt_robot_execute,
        dummy_candidates,
        mock_waybill_propose,
        propositions_manager,
        logistic_dispatcher_client,
        mockserver,
        testpoint,
):
    @testpoint('ld::p2p::before_apply_propositions')
    async def before_apply_propositions(data):
        # await asyncio.sleep(5)
        print(data)
        
    dummy_candidates()
    segment1 = create_segment(zone_id='moscow')
    segment2 = create_segment(zone_id='spb')
    segment3 = create_segment(zone_id='spb')
    await rt_robot_execute('segments_journal')
    task1 = rt_robot_execute('p2p_allocation')
    task2 = rt_robot_execute('p2p_allocation_sadovoe')
    
    await asyncio.gather(task1, task2)
    
    await rt_robot_execute('propositions_notifier')
    await rt_robot_execute('operator_commands_executor')

    assert len(propositions_manager.propositions) == 2
    assert propositions_manager.propositions[0]['segments'] == [
        {'segment_id': segment1, 'waybill_building_version': 1},
    ]

    @mockserver.json_handler('/internal/order/info')
    def order_info(request):
        assert request.json == {'order_id': 'taxi-order'}
        return {
            'waybill_ref': propositions_manager.propositions[0][
                'external_ref'
            ],
        }

    response = await logistic_dispatcher_client.post(
        '/driver-for-order', json=DUMMY_DRIVER_FOR_ORDER_REQUEST,
    )
    assert response.status_code == 200
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert (
        candidates[0]['id']
        == '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
    )
    assert order_info.times_called == 1
