import pytest

from tests_subventions_candidates_reader import common


@pytest.fixture(name='shuttle_control', autouse=True)
def mock_shuttle_control(mockserver):
    class Context:
        def __init__(self):
            self.driver_protos = []
            self.last_request = None
            self.list_drivers_in_geoarea = None

    ctx = Context()

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control'
        '/v1/subventions/list-drivers-in-geoarea',
    )
    def _list_drivers_in_geoarea(request):
        doc = request.json
        assert 'subvention_geoarea' in doc
        ctx.last_request = request.json

        drivers = []
        for num, status in ctx.driver_protos:
            drivers.append(
                {
                    'park_id': 'dbid' + str(num),
                    'driver_profile_id': 'uuid' + str(num),
                    'shuttle_descriptor': {
                        'shuttle_id': 'shuttle_id' + str(num),
                        'started_at': '2021-01-01T12:00:00+0300',
                    },
                    'shuttle_state': {
                        'status': status,
                        'position': [37.643, 55.735],
                    },
                },
            )

        return {'drivers': drivers}

    ctx.list_drivers_in_geoarea = _list_drivers_in_geoarea
    return ctx


@pytest.fixture(name='driver_metrics_storage', autouse=True)
def mock_driver_metrics_storage(mockserver):
    class Context:
        def __init__(self):
            self.activity_by_udid = {}

    ctx = Context()

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _list(request):
        doc = request.json

        items = []
        for udid in doc['unique_driver_ids']:
            itm = {'unique_driver_id': udid}
            if udid in ctx.activity_by_udid:
                itm['value'] = ctx.activity_by_udid[udid]
            items.append(itm)

        return {'items': items}

    return ctx


@pytest.fixture(name='unique_drivers', autouse=True)
def mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.udid_by_dbid_uuid = {}

    ctx = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        doc = request.json

        response_items = []
        for dbid_uuid in doc['profile_id_in_set']:
            itm = {'park_driver_profile_id': dbid_uuid}
            if dbid_uuid in ctx.udid_by_dbid_uuid:
                itm['data'] = {
                    'unique_driver_id': ctx.udid_by_dbid_uuid[dbid_uuid],
                }
            response_items.append(itm)

        return {'uniques': response_items}

    return ctx


def _make_joint_settings(tags_topics=None):
    settings = {}
    if tags_topics is not None:
        settings['tags_topics'] = tags_topics
    return settings


@pytest.mark.now('2021-01-01T14:00:01+0000')
@pytest.mark.config(
    SUBVENTIONS_CANDIDATES_READER_SETTINGS={
        'bs_rules_select_active_from_now': 60,
        'bs_rules_select_limit': 1000,
        'bs_tags_based_rule_types': ['geo_booking'],
        'bs_workmode_based_rule_types': ['driver_fix'],
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
        'activity_fallback_value': 11,
        'fetch_payment_types_from': 'candidates',
    },
    SUBVENTIONS_CANDIDATES_READER_SHUTTLE_SPECIFIC={
        'enabled': True,
        'bs_shuttle_rule_classes': ['shuttle'],
        'default_payment_type': 'none',
    },
)
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='uuid1', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='dbid2', uuid='uuid2', tags=['tag2'])
@pytest.mark.driver_tags_match(dbid='dbid3', uuid='uuid3', tags=['tag3'])
async def test_read_shuttle_drivers(
        taxi_subventions_candidates_reader,
        pgsql,
        logbroker,
        load_json,
        shuttle_control,
        driver_metrics_storage,
        unique_drivers,
):
    shuttle_control.driver_protos = [
        (1, 'active'),
        (2, 'blocked'),
        (3, 'active'),
        (4, 'active'),
    ]

    driver_metrics_storage.activity_by_udid = {
        'udid1': 77,
        'udid2': 88,
        'udid3': 99,
    }

    unique_drivers.udid_by_dbid_uuid = {
        'dbid1_uuid1': 'udid1',
        'dbid2_uuid2': 'udid2',
        'dbid3_uuid3': 'udid3',
    }

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        [common.ReaderTask('geoarea1', 'shuttle')],
    )

    messages = logbroker.publish['data']
    expected_messages = load_json('expected_messages.json')
    assert messages == expected_messages
