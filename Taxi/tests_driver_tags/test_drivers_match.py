import copy
import typing

import pytest

from tests_driver_tags import common
from tests_driver_tags import match_utils


_FBS_HEADER = {'Content-Type': 'application/x-flatbuffers'}


def _extract_tags(info):
    return info['tags'].keys() if 'tags' in info else []


def _exclude_udid(info):
    return {k: v for k, v in info.items() if k != 'udid'}


def _exclude_udids(drivers):
    result = []
    for driver in drivers:
        result.append({k: v for k, v in driver.items() if k != 'udid'})
    return result


def _exclude_tags_info(info):
    result = copy.deepcopy(info)
    if 'tags' in info:
        result['tags'] = {tag: {} for tag in info['tags'].keys()}
    return result


def _body_for_retrieve(dbid, uuid, topics):
    body = {'park_id': dbid, 'driver_profile_id': uuid}
    if topics is not None:
        body['topics'] = topics
    return body


@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.match_tags(
    entity_type='park',
    entity_value='dbid1',
    entity_tags_info={
        'tag0': {'topics': ['topic0'], 'ttl': '2020-01-15T15:34:07+0000'},
        'tag1': {'topics': ['topic0', 'topic1']},
    },
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid', entity_value='dbid1_uuid1', entity_tags=['tag2'],
)
@pytest.mark.match_tags(
    entity_type='udid',
    entity_value='udid1',
    entity_tags_info={'tag4': {'topics': ['topic1']}},
)
@pytest.mark.match_tags(
    entity_type='park_car_id', entity_value='dbid1_car1', entity_tags={'tag6'},
)
@pytest.mark.parametrize(
    'topics, extended_info',
    [
        (
            None,
            {
                'tags': {
                    'tag0': {
                        'ttl': '2020-01-15T15:34:07+0000',
                        'topics': ['topic0'],
                    },
                    'tag1': {'topics': ['topic0', 'topic1']},
                    'tag2': {},
                    'tag4': {'topics': ['topic1']},
                    'tag6': {},
                },
                'udid': 'udid1',
            },
        ),
        (
            ['topic0', 'topic1'],
            {
                'tags': {
                    'tag0': {
                        'ttl': '2020-01-15T15:34:07+0000',
                        'topics': ['topic0'],
                    },
                    'tag1': {'topics': ['topic0', 'topic1']},
                    'tag4': {'topics': ['topic1']},
                },
                'udid': 'udid1',
            },
        ),
        (
            ['topic0'],
            {
                'tags': {
                    'tag0': {
                        'ttl': '2020-01-15T15:34:07+0000',
                        'topics': ['topic0'],
                    },
                    'tag1': {'topics': ['topic0', 'topic1']},
                },
                'udid': 'udid1',
            },
        ),
        (
            ['topic1'],
            {
                'tags': {
                    'tag1': {'topics': ['topic0', 'topic1']},
                    'tag4': {'topics': ['topic1']},
                },
                'udid': 'udid1',
            },
        ),
        (['unknown'], {'tags': {}, 'udid': 'udid1'}),
    ],
)
async def test_driver_profile(
        taxi_driver_tags,
        mockserver,
        taxi_driver_tags_monitor,
        topics,
        extended_info,
):
    body = {'dbid': 'dbid1', 'uuid': 'uuid1'}
    if topics is not None:
        body['topics'] = topics

    # clear statistics
    await taxi_driver_tags_monitor.get_metrics('match-statistic')

    response = await taxi_driver_tags.post('v1/drivers/match/profile', body)
    assert response.status_code == 200
    data = response.json()
    assert set(data['tags']) == set(_extract_tags(extended_info))

    response = await taxi_driver_tags.post('v2/drivers/match/profile', body)
    assert response.status_code == 200
    data = response.json()
    assert data == _exclude_udid(extended_info)

    body['reveal_ttl'] = False
    body['reveal_topics'] = False
    body['reveal_udid'] = True
    response = await taxi_driver_tags.post('v2/drivers/match/profile', body)
    assert response.status_code == 200
    data = response.json()
    assert data == _exclude_tags_info(extended_info)

    # This will make /v1/drivers/retrieve/profile
    # fallback into usual /v2/match_single
    @mockserver.json_handler('tags/v2/match_urgent')
    def _urgent_handler(request):
        return mockserver.make_response('you can\'t use database', status=500)

    response = await taxi_driver_tags.post(
        'v1/drivers/retrieve/profile',
        _body_for_retrieve('dbid1', 'uuid1', topics),
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data['tags']) == set(_extract_tags(extended_info))

    metrics = await taxi_driver_tags_monitor.get_metrics('match-statistic')
    assert metrics['match-statistic'] == {
        'found': {
            'udid': 4,
            'dbid_uuid': 4,
            'park': 4,
            'park_car_id': 4,
            '$meta': {'solomon_children_labels': 'entity_type'},
        },
        'not_found_percent': {
            'udid': 0.0,
            'dbid_uuid': 0.0,
            'park': 0.0,
            'park_car_id': 0.0,
            '$meta': {'solomon_children_labels': 'entity_type'},
        },
        'total': 4,
        '$meta': {'solomon_children_labels': 'versus'},
    }


@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.match_tags(
    entity_type='park',
    entity_value='dbid1',
    entity_tags_info={
        'tag0': {'topics': ['topic0']},
        'tag1': {'topics': ['topic0', 'topic1']},
    },
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid', entity_value='dbid1_uuid1', entity_tags=['tag2'],
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid', entity_value='dbid2_uuid2', entity_tags=['tag2'],
)
@pytest.mark.match_tags(
    entity_type='udid',
    entity_value='udid1',
    entity_tags_info={'tag4': {'topics': ['topic1']}},
)
@pytest.mark.match_tags(
    entity_type='park_car_id', entity_value='dbid1_car1', entity_tags={'tag6'},
)
@pytest.mark.parametrize(
    'drivers, topics, drivers_info, metrics',
    [
        pytest.param(
            [{'dbid': '', 'uuid': ''}],
            None,
            [{'dbid': '', 'uuid': '', 'tags': []}],
            {
                'found': {
                    'udid': 0,
                    'dbid_uuid': 0,
                    'park': 0,
                    'park_car_id': 0,
                },
                'not_found_percent': {
                    'udid': 100.0,
                    'dbid_uuid': 100.0,
                    'park': 100.0,
                    'park_car_id': 100.0,
                },
                'total': 2,
            },
            id='invalid_driver',
        ),
        pytest.param(
            [{'dbid': 'dbid1', 'uuid': 'uuid1'}],
            None,
            [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'tags': ['tag0', 'tag1', 'tag2', 'tag4', 'tag6'],
                    'udid': 'udid1',
                },
            ],
            {
                'found': {
                    'udid': 2,
                    'dbid_uuid': 2,
                    'park': 2,
                    'park_car_id': 2,
                },
                'not_found_percent': {
                    'udid': 0.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 0.0,
                },
                'total': 2,
            },
            id='single_driver',
        ),
        pytest.param(
            [
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
            ],
            None,
            [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'tags': ['tag0', 'tag1', 'tag2', 'tag4', 'tag6'],
                    'udid': 'udid1',
                },
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'tags': ['tag0', 'tag1', 'tag2', 'tag4', 'tag6'],
                    'udid': 'udid1',
                },
            ],
            {
                'found': {
                    'udid': 4,
                    'dbid_uuid': 4,
                    'park': 4,
                    'park_car_id': 4,
                },
                'not_found_percent': {
                    'udid': 0.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 0.0,
                },
                'total': 4,
            },
            id='duplicate_driver',
        ),
        pytest.param(
            [
                {'dbid': 'dbid1', 'uuid': 'doesnotexist'},
                {'dbid': 'dbid2', 'uuid': 'uuid2'},
                {'dbid': 'dbid1', 'uuid': 'doesnotexist'},
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
            ],
            None,
            [
                {
                    'dbid': 'dbid1',
                    'uuid': 'doesnotexist',
                    'tags': ['tag0', 'tag1'],
                },
                {'dbid': 'dbid2', 'uuid': 'uuid2', 'tags': ['tag2']},
                {
                    'dbid': 'dbid1',
                    'uuid': 'doesnotexist',
                    'tags': ['tag0', 'tag1'],
                },
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'tags': ['tag0', 'tag1', 'tag2', 'tag4', 'tag6'],
                    'udid': 'udid1',
                },
            ],
            {
                'found': {
                    'udid': 2,
                    'dbid_uuid': 8,
                    'park': 8,
                    'park_car_id': 2,
                },
                'not_found_percent': {
                    'udid': 75.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 75.0,
                },
                'total': 8,
            },
            id='four_ordered_drivers',
        ),
        pytest.param(
            [{'dbid': 'dbid1', 'uuid': 'uuid1'}],
            ['topic1'],
            [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'tags': ['tag1', 'tag4'],
                    'udid': 'udid1',
                },
            ],
            {
                'found': {
                    'udid': 2,
                    'dbid_uuid': 2,
                    'park': 2,
                    'park_car_id': 2,
                },
                'not_found_percent': {
                    'udid': 0.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 0.0,
                },
                'total': 2,
            },
            id='topic_request',
        ),
        pytest.param(
            [],
            None,
            [],
            {
                'found': {
                    'udid': 0,
                    'dbid_uuid': 0,
                    'park': 0,
                    'park_car_id': 0,
                },
                'not_found_percent': {
                    'udid': 0.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 0.0,
                },
                'total': 0,
            },
            id='no drivers specified',
        ),
        pytest.param(
            [],
            ['topic1'],
            [],
            {
                'found': {
                    'udid': 0,
                    'dbid_uuid': 0,
                    'park': 0,
                    'park_car_id': 0,
                },
                'not_found_percent': {
                    'udid': 0.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 0.0,
                },
                'total': 0,
            },
            id='no drivers, but topic is defined',
        ),
        pytest.param(
            [
                {'dbid': 'unknown', 'uuid': 'unknown'},
                {'dbid': 'dbid2', 'uuid': 'uuid2'},
            ],
            None,
            [
                {'dbid': 'unknown', 'uuid': 'unknown', 'tags': []},
                {'dbid': 'dbid2', 'uuid': 'uuid2', 'tags': ['tag2']},
            ],
            {
                'found': {
                    'udid': 0,
                    'dbid_uuid': 4,
                    'park': 4,
                    'park_car_id': 0,
                },
                'not_found_percent': {
                    'udid': 100.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 100.0,
                },
                'total': 4,
            },
            id='non-skip unknown driver',
        ),
        pytest.param(
            [
                {'dbid': 'unknown', 'uuid': 'unknown'},
                {'dbid': 'dbid2', 'uuid': 'uuid2'},
            ],
            ['topic0', 'topic1', 'topic2'],
            [
                {'dbid': 'unknown', 'uuid': 'unknown', 'tags': []},
                {'dbid': 'dbid2', 'uuid': 'uuid2', 'tags': []},
            ],
            {
                'found': {
                    'udid': 0,
                    'dbid_uuid': 4,
                    'park': 4,
                    'park_car_id': 0,
                },
                'not_found_percent': {
                    'udid': 100.0,
                    'dbid_uuid': 0.0,
                    'park': 0.0,
                    'park_car_id': 100.0,
                },
                'total': 4,
            },
            id='non-skip unknown driver, topics are defined',
        ),
    ],
)
async def test_drivers_profiles(
        taxi_driver_tags,
        taxi_driver_tags_monitor,
        drivers,
        topics,
        drivers_info,
        metrics,
):
    body = {'drivers': drivers}
    if topics is not None:
        body['topics'] = topics

    # clear statistics
    await taxi_driver_tags_monitor.get_metrics('match-statistic')

    # json handler version
    response = await taxi_driver_tags.post('v1/drivers/match/profiles', body)
    assert response.status_code == 200

    drivers = response.json().get('drivers')
    assert drivers is not None
    for driver_data in drivers:
        driver_tags = driver_data.get('tags')
        assert driver_tags is not None
        driver_tags.sort()
    # json handler does not return 'udid' fields: exclude them
    assert drivers == _exclude_udids(drivers_info)

    # fbs handler version
    request = match_utils.pack_profiles_fbs_request(body)
    response = await taxi_driver_tags.post(
        'v1/drivers/match/profiles_fbs', headers=_FBS_HEADER, data=request,
    )
    assert response.status_code == 200
    response = match_utils.unpack_profiles_fbs_response(response.content)

    drivers = response.get('drivers')
    assert drivers is not None
    for driver_data in drivers:
        driver_tags = driver_data.get('tags')
        assert driver_tags is not None
        driver_tags.sort()
    assert drivers == drivers_info

    # check metrics
    metric = await taxi_driver_tags_monitor.get_metrics('match-statistic')
    metrics['$meta'] = {'solomon_children_labels': 'versus'}
    metrics['found']['$meta'] = {'solomon_children_labels': 'entity_type'}
    metrics['not_found_percent']['$meta'] = {
        'solomon_children_labels': 'entity_type',
    }
    assert metric['match-statistic'] == metrics


@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.tags_error(
    handler='/v2/match',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
@pytest.mark.tags_error(
    handler='/v2/match_fbs',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
@pytest.mark.tags_error(
    handler='/v2/match_single',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
@pytest.mark.tags_error(
    handler='/v3/match_single',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
async def test_tags_errors(taxi_driver_tags):
    driver = {'dbid': 'dbid1', 'uuid': 'uuid1'}

    response = await taxi_driver_tags.post('v1/drivers/match/profile', driver)
    assert response.status_code == 500

    response = await taxi_driver_tags.post('v2/drivers/match/profile', driver)
    assert response.status_code == 500

    response = await taxi_driver_tags.post(
        'v1/drivers/match/profiles', {'drivers': [driver]},
    )
    assert response.status_code == 500

    request = match_utils.pack_profiles_fbs_request({'drivers': [driver]})
    response = await taxi_driver_tags.post(
        'v1/drivers/match/profiles_fbs', headers=_FBS_HEADER, data=request,
    )
    assert response.status_code == 500


_URGENT_TAGS = ['this', 'really', 'works']
_CACHED_TAGS = ['these', 'are', 'cached', 'tags']


@pytest.mark.parametrize(
    'policy, expected_code',
    [('both_in_parallel', 200), ('urgent_only', 200), ('cached_only', 500)],
)
@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
async def test_retrieve_only_urgent(
        taxi_driver_tags,
        taxi_config,
        mockserver,
        policy: str,
        expected_code: int,
):
    taxi_config.set_values(
        dict(DRIVER_TAGS_RETRIEVE_SETTINGS={'policy': policy}),
    )

    # This should not break the handler
    @mockserver.json_handler('tags/v2/match_single')
    def _cache_handler(request):
        return mockserver.make_response(
            'you can\'t use cached data', status=500,
        )

    @mockserver.json_handler('tags/v2/match_urgent')
    def _db_handler(request):
        return {'tags': _URGENT_TAGS}

    response = await taxi_driver_tags.post(
        '/v1/drivers/retrieve/profile',
        {'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        assert set(data['tags']) == set(_URGENT_TAGS)


@pytest.mark.parametrize(
    'policy, expected_tags',
    [
        ('both_in_parallel', _URGENT_TAGS),
        ('urgent_only', _URGENT_TAGS),
        ('cached_only', _CACHED_TAGS),
    ],
)
@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
async def test_retrieve(
        taxi_driver_tags,
        taxi_config,
        mockserver,
        policy: str,
        expected_tags: typing.List[str],
):
    taxi_config.set_values(
        dict(DRIVER_TAGS_RETRIEVE_SETTINGS={'policy': policy}),
    )

    @mockserver.json_handler('tags/v2/match_single')
    def _cache_handler(request):
        return {'tags': _CACHED_TAGS}

    @mockserver.json_handler('tags/v2/match_urgent')
    def _db_handler(request):
        return {'tags': _URGENT_TAGS}

    response = await taxi_driver_tags.post(
        '/v1/drivers/retrieve/profile',
        {'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data['tags']) == set(expected_tags)
