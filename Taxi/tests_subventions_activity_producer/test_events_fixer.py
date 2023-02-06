import pytest

from tests_subventions_activity_producer import common
from tests_subventions_activity_producer import pg_helpers


@pytest.fixture(name='dms', autouse=True)
def mock_dms(mockserver):
    class DMSContext:
        def __init__(self):
            self.activity_value = None

        def set_activity_value(self, activity_value):
            self.activity_value = activity_value

    ctx = DMSContext()

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _v2_activity_values_list(request):
        if ctx.activity_value is None:
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'error_msg'},
            )

        return {
            'items': [
                {'unique_driver_id': 'udid1', 'value': ctx.activity_value},
            ],
        }

    return ctx


@pytest.fixture(name='driver_tags', autouse=True)
def mock_driver_tags(mockserver):
    class DMSContext:
        def __init__(self):
            self.tags = None
            self.topics_requested = []

        def set_tags(self, tags):
            self.tags = tags

        def get_topics_requested(self):
            return self.topics_requested

    ctx = DMSContext()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _mock_v1_match_profiles(request):
        if ctx.tags is None:
            return mockserver.make_response(status=500)

        response_drivers = []
        for driver in request.json['drivers']:
            dbid = driver['dbid']
            uuid = driver['uuid']
            response_drivers.append(
                {'dbid': dbid, 'uuid': uuid, 'tags': list(ctx.tags)},
            )

        if 'topics' in request.json:
            ctx.topics_requested.append(request.json['topics'])

        return {'drivers': response_drivers}

    return ctx


@pytest.fixture(name='unique_drivers')
def mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.unique_driver_id = None

        def set_unique_driver_id(self, unique_driver_id):
            self.unique_driver_id = unique_driver_id

    ctx = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        if ctx.unique_driver_id is None:
            return mockserver.make_response(status=500)

        response_items = []
        for dbid_uuid in request.json['profile_id_in_set']:
            itm = {'park_driver_profile_id': dbid_uuid}
            itm['data'] = {'unique_driver_id': ctx.unique_driver_id}
            response_items.append(itm)

        return {'uniques': response_items}

    return ctx


def _check_activity_events_unsent(
        load_json, pgsql, datafiles_expected_by_shard,
):
    for i, datafile in enumerate(datafiles_expected_by_shard):
        expected = load_json(datafile)
        schema = 'shard{}'.format(i)
        actual = pg_helpers.get_activity_events_unsent(pgsql, schema)
        assert expected == actual, 'Unexpected data for shard #{}'.format(i)


@pytest.mark.now('2020-02-03T10:39:00+00:00')
@pytest.mark.parametrize(
    'tags_in_mock,activity_in_mock,udid_in_mock,init_incomplete_event_groups,'
    'expected_activity_events_docs,expected_incomplete_event_groups',
    [
        pytest.param(
            # tags_in_mock
            ['fixer'],
            # activity_in_mock
            99,
            # udid_in_mock
            None,
            # init_incomplete_event_groups
            [
                'incomplete_events_no_activity.json',
                'incomplete_events_no_activity.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_full.json',
                'activity_events_expected_full.json',
            ],
            # expected_incomplete_event_groups
            None,
        ),
        pytest.param(
            # tags_in_mock
            ['fixer'],
            # activity_in_mock
            99,
            # udid_in_mock
            None,
            # init_incomplete_event_groups
            [
                'incomplete_events_no_tags.json',
                'incomplete_events_no_tags.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_full.json',
                'activity_events_expected_full.json',
            ],
            # expected_incomplete_event_groups
            None,
        ),
        pytest.param(
            # tags_in_mock
            None,
            # activity_in_mock
            None,
            # udid_in_mock
            'udid1',
            # init_incomplete_event_groups
            [
                'incomplete_events_no_unique_driver_id.json',
                'incomplete_events_no_unique_driver_id.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_full.json',
                'activity_events_expected_full.json',
            ],
            # expected_incomplete_event_groups
            None,
        ),
        pytest.param(
            # tags_in_mock
            ['fixer'],
            # activity_in_mock
            99,
            # udid_in_mock
            None,
            # init_incomplete_event_groups
            [
                'incomplete_events_no_tags_and_activity.json',
                'incomplete_events_no_tags_and_activity.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_full.json',
                'activity_events_expected_full.json',
            ],
            # expected_incomplete_event_groups
            None,
        ),
        pytest.param(
            # tags_in_mock
            ['fixer'],
            # activity_in_mock
            99,
            # udid_in_mock
            'udid1',
            # init_incomplete_event_groups
            [
                'incomplete_events_no_tags_activity_udid.json',
                'incomplete_events_no_tags_activity_udid.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_full.json',
                'activity_events_expected_full.json',
            ],
            # expected_incomplete_event_groups
            None,
        ),
        pytest.param(
            # tags_in_mock
            ['fixer'],
            # activity_in_mock
            None,
            # udid_in_mock
            None,
            # init_incomplete_event_groups
            [
                'incomplete_events_no_activity_no_tags_respectively.json',
                'incomplete_events_no_activity_no_tags_respectively.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_second.json',
                'activity_events_expected_second.json',
            ],
            # expected_incomplete_event_groups
            [
                'incomplete_events_expected_first.json',
                'incomplete_events_expected_first.json',
            ],
        ),
        pytest.param(
            # tags_in_mock
            None,
            # activity_in_mock
            99,
            # udid_in_mock
            None,
            # init_incomplete_event_groups
            [
                'incomplete_events_no_activity_no_tags_respectively.json',
                'incomplete_events_no_activity_no_tags_respectively.json',
            ],
            # expected_activity_events_docs
            [
                'activity_events_expected_first.json',
                'activity_events_expected_first.json',
            ],
            # expected_incomplete_event_groups
            [
                'incomplete_events_expected_second.json',
                'incomplete_events_expected_second.json',
            ],
        ),
    ],
)
@pytest.mark.parametrize('tags_topics', [None, ['subventions']])
@common.suspend_all_periodic_tasks
async def test_events_fixer(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        pgsql,
        taxi_config,
        dms,
        driver_tags,
        unique_drivers,
        tags_in_mock,
        activity_in_mock,
        udid_in_mock,
        init_incomplete_event_groups,
        expected_activity_events_docs,
        expected_incomplete_event_groups,
        tags_topics,
):
    driver_tags.set_tags(tags_in_mock)
    dms.set_activity_value(activity_in_mock)
    unique_drivers.set_unique_driver_id(udid_in_mock)

    pg_helpers.init_incomplete_event_groups(
        load_json, pgsql, init_incomplete_event_groups,
    )

    await common.run_events_fixer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        tags_topics=tags_topics,
    )

    if expected_activity_events_docs is not None:
        _check_activity_events_unsent(
            load_json, pgsql, expected_activity_events_docs,
        )

    if expected_incomplete_event_groups is not None:
        expected, actual = pg_helpers.extract_incomplete_event_groups(
            load_json, pgsql, expected_incomplete_event_groups,
        )
        assert expected == actual

    if tags_topics is not None:
        for topics_requested in driver_tags.get_topics_requested():
            assert topics_requested == tags_topics
