import datetime
import json

import pytest

from tests_subventions_candidates_reader import common


def _isclose(_a, _b, rel_tol=1e-09, abs_tol=0.0):
    return abs(_a - _b) <= max(rel_tol * max(abs(_a), abs(_b)), abs_tol)


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
    class Context:
        def __init__(self):
            self.last_request = None
            self.handler_list_profiles = None
            self.no_unique_driver_id = False

    ctx = Context()

    @mockserver.json_handler('/candidates/list-profiles')
    def _list_profiles(request):
        data = request.json
        assert 'tl' in data
        assert 'br' in data
        assert 'search_area' in data
        assert 'data_keys' in data
        ctx.last_request = request.json

        response = {
            'drivers': [
                {
                    'uuid': '123456',
                    'dbid': '789',
                    'position': [37.642772999999998, 55.735455999999999],
                    'classes': ['econom'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid1',
                },
                {
                    'uuid': '888777',
                    'dbid': '789',
                    'position': [37.652772999999998, 55.725455999999999],
                    'classes': ['econom', 'comfort'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid2',
                },
                {
                    'uuid': '999777',
                    'dbid': '789',
                    'position': [37.652772999999998, 55.725455999999999],
                    'classes': ['econom', 'comfort'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid3',
                },
                {
                    'uuid': '321123',
                    'dbid': '789',
                    'position': [37.652772999999998, 55.725455999999999],
                    'classes': ['econom', 'comfort'],
                    'status': {'driver': 'free'},
                    'unique_driver_id': 'udid4',
                },
            ],
        }

        if ctx.no_unique_driver_id:
            for driver in response['drivers']:
                del driver['unique_driver_id']

        if 'payment_methods' in data['data_keys']:
            drivers = response['drivers']
            drivers[0]['payment_methods'] = ['card', 'coupon']
            drivers[1]['payment_methods'] = ['card']
            drivers[2]['payment_methods'] = ['corp', 'coupon']
            # The driver is expected to have no payment_type
            drivers[3]['payment_methods'] = ['google_pay']

        return response

    ctx.handler_list_profiles = _list_profiles
    return ctx


@pytest.fixture(name='driver_metrics_storage', autouse=True)
def mock_driver_metrics_storage(mockserver):
    class Context:
        def __init__(self):
            self.response = {
                'items': [
                    {'unique_driver_id': 'udid1', 'value': 77},
                    {'unique_driver_id': 'udid2'},
                    {'unique_driver_id': 'udid3', 'value': 80},
                ],
            }

        def set_response(self, response):
            self.response = response

    ctx = Context()

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _list(request):
        if ctx.response is None:
            return mockserver.make_response(status=500)

        return ctx.response

    return ctx


@pytest.fixture(name='driver_tags', autouse=False)
def mock_driver_tags(mockserver):
    class Context:
        def __init__(self):
            self.tags = {
                '123456': 'tag1',
                '888777': 'tag2',
                '999777': 'tag3',
                '321123': 'tag4',
            }
            self.topics_requested = []

        def set_tags(self, tags):
            self.tags = tags

        def get_topics_requested(self):
            return self.topics_requested

    ctx = Context()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _mock_v1_match_profiles(request):
        request_json = request.json
        response_drivers = []
        if ctx.tags is None:
            return mockserver.make_response(status=500)

        for driver in request_json['drivers']:
            dbid = driver['dbid']
            uuid = driver['uuid']
            response_drivers.append(
                {'dbid': dbid, 'uuid': uuid, 'tags': list(ctx.tags[uuid])},
            )

        if 'topics' in request_json:
            ctx.topics_requested.append(request_json['topics'])

        return {'drivers': response_drivers}

    return ctx


@pytest.fixture(name='unique_drivers')
def mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.unique_driver_id = 'udid1'

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


def _select_reader_tasks(pgsql):
    cursor = pgsql['subventions-candidates-reader'].cursor()
    query = """SELECT geoarea,processing_type,last_taken FROM
     subventions_candidates_reader.reader_tasks;"""
    cursor.execute(query)
    result = []
    for row in cursor:
        result.append(
            {
                'geoarea': row[0],
                'processing_type': row[1],
                'last_taken': row[2],
            },
        )
    return result


def _check_processed_reader_tasks(
        pgsql, expected_time_taken='2019-10-11T13:38:07+03:00',
):
    reader_tasks = _select_reader_tasks(pgsql)
    for item in reader_tasks:
        assert item['last_taken'].isoformat() == expected_time_taken


def _check_messsages(
        logbroker,
        tags_for_first_driver=('tag1',),
        tags_for_second_driver=('tag2',),
        timestamp='2019-10-11T10:38:07+00:00',
        billing_types=None,
):
    assert logbroker.publish['times_called'] == 4

    zone_msgs = common.get_published_messages_by_zones(logbroker)
    assert sorted(zone_msgs.keys()) == ['subv_zone1', 'subv_zone2']

    billing_types = ['geo_booking'] if billing_types is None else billing_types

    for zone in zone_msgs:
        message0 = zone_msgs[zone][0]
        assert message0 == {
            'classes': ['econom'],
            'billing_types': billing_types,
            'drivers': [
                {
                    'activity': 77,
                    'dbid': '789',
                    'unique_driver_id': 'udid1',
                    'uuid': '123456',
                },
            ],
            'geoarea': zone,
            'timestamp': timestamp,
            'tags': list(tags_for_first_driver),
            'payment_type_restrictions': 'online',
        }

        message1 = zone_msgs[zone][1]
        assert message1 == {
            'classes': ['econom', 'comfort'],
            'billing_types': billing_types,
            'drivers': [
                {
                    'activity': 90,
                    'dbid': '789',
                    'unique_driver_id': 'udid2',
                    'uuid': '888777',
                },
            ],
            'geoarea': zone,
            'timestamp': timestamp,
            'tags': list(tags_for_second_driver),
            'payment_type_restrictions': 'online',
        }


def _check_incomplete_messsages(
        logbroker,
        dms_failed,
        tags_failed,
        unique_drivers_fail,
        billing_types=None,
):
    assert logbroker.publish['times_called'] == 4

    zone_msgs = common.get_published_messages_by_zones(logbroker)
    assert sorted(zone_msgs.keys()) == ['subv_zone1', 'subv_zone2']

    billing_types = ['geo_booking'] if billing_types is None else billing_types

    for zone in zone_msgs:
        message0 = zone_msgs[zone][0]
        expected_message0 = {
            'classes': ['econom'],
            'billing_types': billing_types,
            'drivers': [
                {
                    'activity': 77,
                    'dbid': '789',
                    'unique_driver_id': 'udid1',
                    'uuid': '123456',
                },
            ],
            'geoarea': zone,
            'timestamp': '2019-10-11T10:38:07+00:00',
            'tags': list('tag1'),
            'payment_type_restrictions': 'online',
        }

        expected_message1 = {
            'classes': ['econom', 'comfort'],
            'billing_types': billing_types,
            'drivers': [
                {
                    'activity': 77,
                    'dbid': '789',
                    'unique_driver_id': 'udid1',
                    'uuid': '888777',
                },
            ],
            'geoarea': zone,
            'timestamp': '2019-10-11T10:38:07+00:00',
            'tags': list('tag2'),
            'payment_type_restrictions': 'online',
        }

        if dms_failed:
            del expected_message0['drivers'][0]['activity']
            del expected_message1['drivers'][0]['activity']

        if tags_failed:
            del expected_message0['tags']
            del expected_message1['tags']

        if unique_drivers_fail:
            del expected_message0['drivers'][0]['unique_driver_id']
            del expected_message1['drivers'][0]['unique_driver_id']
            if 'activity' in expected_message0['drivers'][0]:
                del expected_message0['drivers'][0][
                    'activity'
                ]  # we can't fetch activity without unique_driver_id
            if 'activity' in expected_message1['drivers'][0]:
                del expected_message1['drivers'][0][
                    'activity'
                ]  # we can't fetch activity without unique_driver_id

        assert message0 == expected_message0

        message1 = zone_msgs[zone][1]
        assert message1 == expected_message1


def _make_settings(
        candidates_filtration_type=None,
        candidates_filter_drivers_work_modes=None,
        enable_driver_tags_cache_fallback=None,
        send_incomplete_events=None,
        candidates_filter_work_modes_properties=None,
):
    settings = {
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
        'activity_fallback_value': 90,
    }
    if candidates_filtration_type is not None:
        settings['candidates_filtration_type'] = candidates_filtration_type
    if candidates_filter_drivers_work_modes is not None:
        settings[
            'candidates_filter_drivers_work_modes'
        ] = candidates_filter_drivers_work_modes
    if enable_driver_tags_cache_fallback is not None:
        settings[
            'enable_driver_tags_cache_fallback'
        ] = enable_driver_tags_cache_fallback
    if send_incomplete_events is not None:
        settings['send_incomplete_events'] = send_incomplete_events
    if candidates_filter_work_modes_properties is not None:
        settings[
            'candidates_filter_work_modes_properties'
        ] = candidates_filter_work_modes_properties
    return settings


def _make_joint_settings(tags_topics=None):
    settings = {}
    if tags_topics is not None:
        settings['tags_topics'] = tags_topics
    return settings


@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings())
@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.driver_tags_match(dbid='789', uuid='123456', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='789', uuid='888777', tags=['tag2'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_scheduler(
        taxi_subventions_candidates_reader, pgsql, testpoint, logbroker,
):
    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    _check_processed_reader_tasks(
        pgsql, expected_time_taken='2019-10-11T13:38:07+03:00',
    )
    _check_messsages(logbroker)


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings())
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_read_candidates_no_tags_for_drivers(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        logbroker,
        mockserver,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _profiles(request):
        data = json.loads(request.get_data())
        assert 'drivers' in data
        return {'drivers': []}

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    _check_messsages(
        logbroker,
        tags_for_first_driver=tuple(),
        tags_for_second_driver=tuple(),
    )


@pytest.mark.config(
    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
        enable_driver_tags_cache_fallback=True,
    ),
)
@pytest.mark.driver_tags_match(dbid='789', uuid='123456', tags=['tag1'])
@pytest.mark.driver_tags_match(dbid='789', uuid='888777', tags=['tag2'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_read_candidates_tags_fallback(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        logbroker,
        mockserver,
        mocked_time,
):
    mocked_time.set(datetime.datetime(2019, 10, 11, 10, 38, 7))

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    _check_messsages(logbroker)

    logbroker.clean()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _profiles(request):
        return mockserver.make_response(status=500)

    mocked_time.set(datetime.datetime(2019, 10, 11, 10, 38, 8))

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    _check_messsages(logbroker, timestamp='2019-10-11T10:38:08+00:00')


@pytest.mark.parametrize(
    'reader_tasks,expected_filters,expected_data_keys',
    [
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            dict(),
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='default',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            {'filtration': 'base'},
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='filtration=base',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filtration_type='base',
                    ),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            {'filtration': 'active'},
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='filtration=activt',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filtration_type='active',
                    ),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            {'filtration': 'searchable'},
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='filtration=searchable',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filtration_type='searchable',
                    ),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_WORKMODE_BASED_READER_TASKS,
            # expected_filters
            {'drivers_work_modes': ['driver_fix', 'super_driver_fix']},
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='driver_work_modes,workmode_based',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filter_drivers_work_modes=[
                            'driver_fix',
                            'super_driver_fix',
                        ],
                    ),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_WORKMODE_BASED_READER_TASKS,
            # expected_filters
            {'work_mode': {'properties': ['time_based_subvention']}},
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='driver_work_mode_properties,workmode_based',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filter_work_modes_properties=[
                            'time_based_subvention',
                        ],
                    ),
                    SUBVENTIONS_CANDIDATES_READER_USE_WORK_MODE_PROPERTIES_FILTER=True,  # noqa: E501
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            dict(),
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='driver_work_modes,tags_based',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
                        candidates_filter_drivers_work_modes=[
                            'driver_fix',
                            'super_driver_fix',
                        ],
                    ),
                ),
            ],
        ),
        pytest.param(
            # reader_tasks
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            # expected_filters
            dict(),
            # expected_data_keys
            ['classes', 'unique_driver_id', 'payment_methods'],
            id='payment_methods',
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(),
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_candidates_request(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        logbroker,
        candidates,
        reader_tasks,
        expected_filters,
        expected_data_keys,
):
    await common.run_scheduler(
        taxi_subventions_candidates_reader, pgsql, reader_tasks,
    )

    assert candidates.last_request['only_free'] is True

    for key in expected_filters:
        assert candidates.last_request[key] == expected_filters[key]

    assert candidates.last_request['data_keys'] == expected_data_keys


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.parametrize(
    'reader_tasks,expected_billing_types',
    [
        pytest.param(
            common.DEFAULT_TAGS_BASED_READER_TASKS,
            ['geo_booking'],
            id='tag-based',
        ),
        pytest.param(
            common.DEFAULT_WORKMODE_BASED_READER_TASKS,
            ['driver_fix'],
            id='workmode-based',
        ),
    ],
)
@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings())
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_passing_billing_types(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        logbroker,
        mockserver,
        reader_tasks,
        expected_billing_types,
):
    await common.run_scheduler(
        taxi_subventions_candidates_reader, pgsql, reader_tasks,
    )

    msgs_by_zone = common.get_published_messages_by_zones(logbroker)

    for zone in msgs_by_zone:
        msgs = msgs_by_zone[zone]
        for msg in msgs:
            assert msg['billing_types'] == expected_billing_types


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.config(
    SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings(
        send_incomplete_events=True,
    ),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize(
    'dms_fail',
    [pytest.param(False, id='+'), pytest.param(True, id='dms_fail')],
)
@pytest.mark.parametrize(
    'tags_fail',
    [pytest.param(False, id='+'), pytest.param(True, id='tags_fail')],
)
@pytest.mark.parametrize(
    'unique_drivers_fail',
    [
        pytest.param(False, id='+'),
        pytest.param(True, id='unique_drivers_fail'),
    ],
)
async def test_read_candidates_with_incomplete_events(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        logbroker,
        candidates,
        driver_metrics_storage,
        driver_tags,
        unique_drivers,
        dms_fail,
        tags_fail,
        unique_drivers_fail,
):
    candidates.no_unique_driver_id = (
        True  # trigger fetching of unique_dirver_id from unique-drivers
    )

    if dms_fail:
        driver_metrics_storage.set_response(None)
    if tags_fail:
        driver_tags.set_tags(None)
    if unique_drivers_fail:
        unique_drivers.set_unique_driver_id(None)

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    _check_incomplete_messsages(
        logbroker, dms_fail, tags_fail, unique_drivers_fail,
    )


@pytest.mark.now('2019-10-11T10:38:07+0000')
@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_settings())
@pytest.mark.parametrize('tags_topics', [None, ['subventions']])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_passing_tags_topics(
        taxi_subventions_candidates_reader,
        pgsql,
        taxi_config,
        testpoint,
        logbroker,
        mockserver,
        driver_tags,
        tags_topics,
):
    taxi_config.set_values(
        dict(
            SUBVENTIONS_SCR_AND_SAP_JOINT_SETTINGS=_make_joint_settings(
                tags_topics=['subventions'],
            ),
        ),
    )
    await taxi_subventions_candidates_reader.invalidate_caches()

    await common.run_scheduler(
        taxi_subventions_candidates_reader,
        pgsql,
        common.DEFAULT_TAGS_BASED_READER_TASKS,
    )

    if tags_topics is not None:
        for topics_requested in driver_tags.get_topics_requested():
            assert topics_requested == tags_topics
