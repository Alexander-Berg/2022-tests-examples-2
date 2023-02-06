import pytest

from tests_subventions_candidates_reader import common


@pytest.fixture(name='billing_subventions', autouse=True)
def mock_billing_subventions(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {
            'subventions': [
                {
                    'tariff_zones': ['moscow'],
                    'geoareas': ['subv_zone1'],
                    'status': 'enabled',
                    'start': '2018-08-01T12:59:23.231000+00:00',
                    'end': '2018-08-10T12:59:23.231000+00:00',
                    'type': 'geo_booking',
                    'is_personal': False,
                    'taxirate': 'TAXIRATE-21',
                    'subvention_rule_id': '_id/1',
                    'cursor': '1',
                    'tags': ['tag1'],
                    'time_zone': {'id': 'Europe/Moscow', 'offset': '+03'},
                    'currency': 'RUB',
                    'updated': '2018-08-01T12:59:23.231000+00:00',
                    'visible_to_driver': True,
                    'week_days': ['mon'],
                    'hours': [],
                    'log': [],
                    'workshift': {'start': '08:00', 'end': '18:00'},
                    'payment_type': 'add',
                    'profile_payment_type_restrictions': 'none',
                    'min_online_minutes': 0,
                    'rate_free_per_minute': '1.23',
                    'rate_on_order_per_minute': '1.23',
                    'is_relaxed_order_time_matching': False,
                    'is_relaxed_income_matching': False,
                },
            ],
        }


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
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
                    'payment_methods': ['card', 'cash', 'coupon'],
                },
                {
                    'uuid': 'uuid2',
                    'dbid': 'dbid2',
                    'position': [37.642772, 55.735456],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid2',
                    'payment_methods': ['card', 'cash'],
                },
                {
                    'uuid': 'uuid3',
                    'dbid': 'dbid3',
                    'position': [37.642772, 55.735456],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid3',
                    'payment_methods': ['corp', 'coupon', 'card', 'cash'],
                },
            ],
        }


@pytest.fixture(name='driver-metrics-storage', autouse=True)
def mock_driver_metrics_storage(mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _list(request):
        doc = request.json
        ids = doc['unique_driver_ids']
        response_items = []
        for udid in ids:
            response_items.append({'unique_driver_id': udid, 'value': 77})
        return {'items': response_items}


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.config(
    SUBVENTIONS_CANDIDATES_READER_SETTINGS={
        'bs_rules_select_active_from_now': 60,
        'bs_rules_select_limit': 1000,
        'bs_tags_based_rule_types': ['geo_booking'],
        'service_enabled': True,
        'scheduler_settings': {
            'scheduler_enabled': True,
            'schedule_interval_ms': 1,
            'max_execute_duration_ms': 1000,
        },
        'logbroker_producer_settings': {
            'max_in_fly_messages': 11,
            'commit_timeout': 100,
            'partitions_number': 1,
        },
        'enable_filtering_by_tags': True,
    },
)
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='uuid1', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='dbid2', uuid='uuid2', tags=['tag2'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_filter_by_tags(
        taxi_subventions_candidates_reader, pgsql, testpoint, logbroker,
):
    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        [common.ReaderTask('subv_zone1', 'tags_based')],
    )

    messages_by_zone = common.get_published_messages_by_zones(logbroker)
    assert list(messages_by_zone.keys()) == ['subv_zone1']
    messages = messages_by_zone['subv_zone1']

    assert messages == [
        {
            'classes': ['econom'],
            'billing_types': ['geo_booking'],
            'drivers': [
                {
                    'activity': 77,
                    'dbid': 'dbid1',
                    'unique_driver_id': 'udid1',
                    'uuid': 'uuid1',
                },
            ],
            'geoarea': 'subv_zone1',
            'timestamp': '2019-10-11T10:38:07+00:00',
            'tags': ['tag1'],
            'payment_type_restrictions': 'none',
        },
    ]
