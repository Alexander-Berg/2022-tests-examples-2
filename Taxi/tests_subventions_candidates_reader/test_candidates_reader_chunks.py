import pytest

from tests_subventions_candidates_reader import common


@pytest.fixture(name='candidates')
def _mock_candidates(mockserver):
    @mockserver.json_handler('/candidates/list-profiles')
    def _list_profiles(request):
        return {
            'drivers': [
                {
                    'uuid': 'uuid1',
                    'dbid': 'dbid1',
                    'position': [37.642772, 55.735456],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid1',
                },
                {
                    'uuid': 'uuid2',
                    'dbid': 'dbid2',
                    'position': [37.642772, 55.735456],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid2',
                },
                {
                    'uuid': 'uuid3',
                    'dbid': 'dbid3',
                    'position': [37.642772, 55.735456],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid3',
                },
            ],
        }

    return _list_profiles


@pytest.fixture(name='driver_metrics_storage')
def _mock_driver_metrics_storage(mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _list(request):
        doc = request.json
        ids = doc['unique_driver_ids']
        assert ids in [['udid1', 'udid2'], ['udid3']]
        response_items = []
        for udid in ids:
            response_items.append({'unique_driver_id': udid, 'value': 77})
        return {'items': response_items}

    return _list


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.config(
    SUBVENTIONS_CANDIDATES_READER_SETTINGS={
        'bs_rules_select_active_from_now': 60,
        'bs_rules_select_limit': 1000,
        'bs_tags_based_rule_types': ['geo_booking', 'driver_fix'],
        'service_enabled': True,
        'scheduler_settings': {
            'scheduler_enabled': True,
            'schedule_interval_ms': 1,
            'max_execute_duration_ms': 1000,
        },
        'chunk_sizes': {'payment_type': 2, 'tags': 2, 'activity': 2},
    },
)
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='uuid1', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='dbid2', uuid='uuid2', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='dbid3', uuid='uuid3', tags=['tag1'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_chunk_requests(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        candidates,
        driver_metrics_storage,
):
    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    assert candidates.times_called > 0
    assert driver_metrics_storage.times_called > 0
