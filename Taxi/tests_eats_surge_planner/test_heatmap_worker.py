# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint:disable= unused-variable, redefined-builtin, invalid-name
# pylint:disable= global-statement, no-else-return
import pytest

from . import conftest

count = 0
alive_ids = []


@pytest.fixture(name='heatmap_handlers')
def _mock_heatmap_handlers(mockserver):
    @mockserver.json_handler('/eats-surge-resolver/api/v1/surge-level')
    def _mock_surge_resolver(request):
        body = request.json
        if len(body['params']['placeIds']) == 1:
            return {'jsonrpc': '2.0', 'id': body['params']['placeIds'][0]}

        global count
        global alive_ids
        count += 1

        if count == 1:
            first_place_id = body['params']['placeIds'][0]
            second_place_id = body['params']['placeIds'][1]
            alive_ids.append(first_place_id)
            alive_ids.append(second_place_id)
            return {
                'jsonrpc': '2.0',
                'id': 1,
                'result': [
                    {
                        'placeId': first_place_id,
                        'nativeInfo': {
                            'surgeLevel': first_place_id,
                            'loadLevel': first_place_id,
                            'deliveryFee': float(first_place_id),
                        },
                    },
                    {
                        'placeId': second_place_id,
                        'nativeInfo': {
                            'surgeLevel': second_place_id,
                            'loadLevel': second_place_id,
                            'deliveryFee': float(second_place_id),
                        },
                    },
                ],
            }

        if count == 2:
            first_place_id = body['params']['placeIds'][0]
            second_place_id = body['params']['placeIds'][1]
            alive_ids.append(second_place_id)
            return {
                'jsonrpc': '2.0',
                'id': 2,
                'result': [
                    {'placeId': first_place_id},
                    {
                        'placeId': second_place_id,
                        'nativeInfo': {
                            'surgeLevel': second_place_id,
                            'loadLevel': second_place_id,
                            'deliveryFee': float(second_place_id),
                        },
                    },
                ],
            }

        assert False
        return None

    @mockserver.json_handler('/heatmap-sample-storage/v1/add_samples')
    def _mock_heatmap_sample_storage(request):
        body = request.json
        sample = body['samples'][0]
        if sample['map_name'] == 'default/default':
            if sample['value'] in alive_ids:
                return {'timestamp': '2021-05-11T00:00:00+00:00'}
        if sample['map_name'] == 'surge_level/default':
            if sample['meta']['fee'] is not None:
                return {'timestamp': '2021-05-11T00:00:00+00:00'}

        assert False
        return None


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_surge_planner_enable_surge_level',
    consumers=['eats-surge-planner/surge-level'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enable': False},
)
@pytest.mark.eats_catalog_storage_cache(conftest.PLACES)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
async def test_heatmap(taxi_eats_surge_planner, heatmap_handlers):
    await taxi_eats_surge_planner.run_distlock_task('heatmap-worker')
    assert count != 0
