import pytest

from tests_plugins import utils


@pytest.mark.parametrize('check_allowed_classes', [True, False])
@pytest.mark.parametrize('explicit_mapping', [True, False])
@pytest.mark.now('2021-01-01T10:00:00+00:00')
async def test_atlas_metrics(
        taxi_dispatch_airport,
        mockserver,
        testpoint,
        taxi_config,
        load_json,
        now,
        check_allowed_classes,
        explicit_mapping,
):
    @mockserver.json_handler('/atlas-backend/v1/data-access/detailed')
    def _atlas_backend_data_access(request):
        assert request.json['metric_id'] == 'airport_orders_aggregate'

        parameters = request.json['parameters']
        assert 'surge_zone_ids' not in parameters
        assert sorted(parameters['source_geoareas']) == [
            'ekb_airport',
            'svo_airport',
            'unknown_airport',
        ]

        now_ts = int(utils.timestamp(now))
        offset_seconds = 15 * 60
        interval_and_offset_seconds = offset_seconds + 60 * 60
        assert parameters['ts']['from'] == now_ts - interval_and_offset_seconds
        assert parameters['ts']['to'] == now_ts - offset_seconds
        return load_json('atlas_response.json')

    @testpoint('atlas-metrics')
    def atlas_metrics(data):
        return data

    metrics_cfg = {
        'metrics': {
            'airport_orders_aggregate': {
                'interval_length': 60,
                'interval_offset': 15,
            },
        },
    }
    if explicit_mapping:
        mapping_name = 'airport_to_atlas_request_zone_mapping'
        metric = metrics_cfg['metrics']['airport_orders_aggregate']
        metric[mapping_name] = {}
        metric[mapping_name]['ekb'] = 'ekb_airport'
    if check_allowed_classes:
        metric = metrics_cfg['metrics']['airport_orders_aggregate']
        metric['allowed_classes'] = ['comfortplus', 'uberx']
    taxi_config.set_values({'DISPATCH_AIRPORT_ATLAS_METRICS': metrics_cfg})
    await taxi_dispatch_airport.invalidate_caches()

    await taxi_dispatch_airport.run_task(
        'business_metrics_collector.atlas_task',
    )

    atlas_metrics_data = (await atlas_metrics.wait_call())['data']
    etalon = {
        'airport_orders_aggregate': {
            '$meta': {'solomon_children_labels': 'airport_id'},
            'ekb': {
                'uberselect': {'requests_count': 2, 'trips_count': 1},
                'uberx': {'requests_count': 25, 'trips_count': 16},
            },
            'svo': {'comfortplus': {'requests_count': 3, 'trips_count': 3}},
        },
    }
    if check_allowed_classes:
        etalon['airport_orders_aggregate']['ekb'].pop('uberselect')

    assert atlas_metrics_data == etalon


@pytest.mark.now('2021-01-01T10:00:00+00:00')
async def test_atlas_metrics_pins_avg_surge_value(
        taxi_dispatch_airport,
        mockserver,
        testpoint,
        taxi_config,
        load_json,
        now,
):
    @mockserver.json_handler('/atlas-backend/v1/data-access/detailed')
    def _atlas_backend_data_access(request):
        assert request.json['metric_id'] == 'pins_avg_surge_value'

        parameters = request.json['parameters']
        assert 'source_geoareas' not in parameters
        assert sorted(parameters['surge_zone_ids']) == [
            'ekb_airport_surge_id',
            'svo_airport_surge_id',
        ]

        now_ts = int(utils.timestamp(now))
        offset_seconds = 15 * 60
        interval_and_offset_seconds = offset_seconds + 60 * 60
        assert parameters['ts']['from'] == now_ts - interval_and_offset_seconds
        assert parameters['ts']['to'] == now_ts - offset_seconds
        return load_json('atlas_response_pins_avg_surge_value.json')

    @testpoint('atlas-metrics')
    def atlas_metrics(data):
        return data

    metrics_cfg = {
        'metrics': {
            'pins_avg_surge_value': {
                'interval_length': 60,
                'interval_offset': 15,
                'allowed_classes': ['econom'],
                'airports': ['ekb', 'svo'],
                'airport_to_atlas_request_zone_mapping': {
                    'ekb': 'ekb_airport_surge_id',
                    'svo': 'svo_airport_surge_id',
                },
                'atlas_request_zones_field_name': 'surge_zone_ids',
                'atlas_response_zone_field_name': 'surge_id',
            },
        },
    }
    taxi_config.set_values({'DISPATCH_AIRPORT_ATLAS_METRICS': metrics_cfg})
    await taxi_dispatch_airport.invalidate_caches()

    await taxi_dispatch_airport.run_task(
        'business_metrics_collector.atlas_task',
    )

    atlas_metrics_data = (await atlas_metrics.wait_call())['data']
    etalon = {
        'pins_avg_surge_value': {
            '$meta': {'solomon_children_labels': 'airport_id'},
            'ekb': {'econom': {'avg_surge': 1.0}},
            'svo': {'econom': {'avg_surge': 1.0}},
        },
    }

    assert atlas_metrics_data == etalon
