import pytest

from tests_qc_executors import utils


REQUIRED_FIELDS = {'number', 'color', 'brand', 'resolution'}


@pytest.mark.config(
    QC_EXECUTORS_FETCH_CAR_DATA_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'projection': ['data.brand', 'data.number', 'data.color'],
    },
)
@pytest.mark.parametrize(
    'passes_,ids_',
    [
        (
            [
                utils.make_pass('id1', 'dkk', status='new'),
                utils.make_pass('id2', 'dkk', status='pending'),
                utils.make_pass('id3', 'sts', entity_type='car'),
            ],
            ['entity_car_id1', 'entity_car_id2', 'entity_id3'],
        ),
    ],
)
async def test_simple_scenario(
        taxi_qc_executors, taxi_config, testpoint, mockserver, passes_, ids_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles_api_v1_vehicle_retrieve(request):
        assert request.method == 'POST'
        config = taxi_config.get('QC_EXECUTORS_FETCH_CAR_DATA_SETTINGS')
        assert set(request.json['id_in_set']) == set(ids_)
        assert set(request.json['projection']) == set(config['projection'])
        data_ = [utils.make_vehicle_item(id) for id in ids_]
        for item in data_:
            if 'data' in item:
                item['data'] = {
                    k: v
                    for k, v in item['data'].items()
                    if 'data.' + k in config['projection']
                }
        return mockserver.make_response(json={'vehicles': data_}, status=200)

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        got_fields = set()
        for val in request.json['items']:
            for dat in val['data']:
                got_fields.add(dat['field'])
        assert not got_fields - REQUIRED_FIELDS
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-car-data'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _fleet_vehicles_api_v1_vehicle_retrieve.times_called == 1
    assert _internal_qc_pools_v1_pool_push.times_called == 1


@pytest.mark.config(
    QC_EXECUTORS_FETCH_CAR_DATA_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'projection': ['data.brand', 'data.number', 'data.color'],
    },
)
@pytest.mark.parametrize(
    'passes_,ids_,data_,not_empty_ids_,empty_ids_',
    [
        (
            [
                utils.make_pass('id1', 'dkk', status='new'),
                utils.make_pass('id2', 'dkk', status='pending'),
                utils.make_pass('id3', status='resolved'),
            ],
            ['entity_car_id1', 'entity_car_id2', 'entity_car_id3'],
            [
                utils.make_vehicle_item('entity_car_id1', False),
                utils.make_vehicle_item('entity_car_id2'),
                utils.make_vehicle_item(
                    'entity_car_id3',
                    True,
                    {
                        'park_id': 'park_id',
                        'car_id': 'car_id',
                        'color': 'blue',
                        'number': 'A134BC163',
                    },
                ),
            ],
            ['entity_id2', 'entity_id3'],
            ['entity_id1'],
        ),
    ],
)
async def test_vehicle_without_items(
        taxi_qc_executors,
        taxi_config,
        testpoint,
        mockserver,
        passes_,
        ids_,
        data_,
        not_empty_ids_,
        empty_ids_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles_api_v1_vehicle_retrieve(request):
        assert request.method == 'POST'
        assert set(request.json['id_in_set']) == set(ids_)
        config = taxi_config.get('QC_EXECUTORS_FETCH_CAR_DATA_SETTINGS')
        assert set(request.json['projection']) == set(config['projection'])
        for item in data_:
            if 'data' in item:
                item['data'] = {
                    k: v
                    for k, v in item['data'].items()
                    if 'data.' + k in config['projection']
                }

        return mockserver.make_response(json={'vehicles': data_}, status=200)

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        got_fields = set()
        good_ids = set()
        bad_ids = set()
        for val in request.json['items']:
            for dat in val['data']:
                got_fields.add(dat['field'])
                if dat['field'] == 'resolution':
                    if dat['value'] == 'SUCCESS':
                        good_ids.add(val['entity_id'])
                    else:
                        bad_ids.add(val['entity_id'])
        assert good_ids == set(not_empty_ids_)
        assert bad_ids == set(empty_ids_)
        assert set(got_fields) == set(REQUIRED_FIELDS)
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-car-data'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _fleet_vehicles_api_v1_vehicle_retrieve.times_called == 1
    assert _internal_qc_pools_v1_pool_push.times_called == 1


@pytest.mark.config(
    QC_EXECUTORS_FETCH_CAR_DATA_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
    },
)
async def test_vehicle_all_items(
        taxi_qc_executors, taxi_config, testpoint, mockserver,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={
                'items': [
                    utils.make_pass(
                        'id1', 'dkk', status='new', with_data=False,
                    ),
                ],
                'cursor': 'next',
            },
            status=200,
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles_api_v1_vehicle_retrieve(request):
        assert request.method == 'POST'
        assert set(request.json['id_in_set']) == set()
        assert 'projection' not in request.json
        return mockserver.make_response(json={'vehicles': []}, status=200)

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        got_fields = set()
        good_ids = set()
        bad_ids = set()
        for val in request.json['items']:
            for dat in val['data']:
                got_fields.add(dat['field'])
                if dat['field'] == 'resolution':
                    if dat['value'] == 'SUCCESS':
                        good_ids.add(val['entity_id'])
                    else:
                        bad_ids.add(val['entity_id'])
        assert good_ids == set()
        assert bad_ids == set(['entity_id1'])
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-car-data'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
