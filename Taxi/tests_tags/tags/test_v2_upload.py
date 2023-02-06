# pylint: disable=C0302
import datetime

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_tools as tools

_CUSTOM_OFFICER = 'customs-officer'

_ENTITY_DRIVER_LICENSE = 'driver_license'
_ENTITY_CAR_NUMBER = 'car_number'
_ENTITY_PARK = 'park'
_ENTITY_UDID = 'udid'

_TEST_PROVIDERS = [
    tools.Provider.from_id(1000, True),
    tools.Provider.from_id(1001, False),
    tools.Provider.from_id(1, True),
    tools.Provider.from_id(2, True),
]

_TEST_ENTITIES = [
    tools.Entity(1000, 'udid_0', entity_type=_ENTITY_UDID),
    tools.Entity(1001, 'udid_1', entity_type=_ENTITY_UDID),
    tools.Entity(1002, 'udid_2', entity_type=_ENTITY_UDID),
    tools.Entity(1006, 'udid_3', entity_type=_ENTITY_UDID),
    tools.Entity(1003, 'udid_0', entity_type=_ENTITY_PARK),
    tools.Entity(1004, 'park_0', entity_type=_ENTITY_PARK),
    tools.Entity(1005, 'car_number_0', entity_type=_ENTITY_CAR_NUMBER),
]

_TEST_TAG_NAMES = [
    tools.TagName(1000, 'tag_0'),
    tools.TagName(1001, 'tag_1'),
    tools.TagName(1, 'tag_2'),
]

_TEST_TOPICS = [
    tools.Topic(2000, 'topic_0', False),
    tools.Topic(2001, 'topic_1', True),
    tools.Topic(2002, 'topic_2', False),
]

_INFINITY = 'infinity'
_NOW = datetime.datetime(2019, 8, 29, 10, 54, 9)
_TAG_LIFETIME = datetime.timedelta(days=1)
_TAG_OUTDATED = _NOW - _TAG_LIFETIME
#  Test tag livetime in seconds
_TEST_DURATION = 3600
#  Expected tag ttl
_TEST_TTL = _NOW + datetime.timedelta(seconds=_TEST_DURATION)


def _tag(
        name_index,
        provider_index,
        entity_index,
        updated=None,
        ttl=None,
        entity_type=None,
):
    return tools.Tag(
        name_id=_TEST_TAG_NAMES[name_index].tag_name_id,
        provider_id=_TEST_PROVIDERS[provider_index].provider_id,
        entity_id=_TEST_ENTITIES[entity_index].entity_id,
        updated=updated,
        ttl=ttl or _INFINITY,
        entity_type=entity_type,
    )


def _get_tag_data(name_index, entity_index, ttl=None, until=None):
    return tools.Tag.get_tag_data(
        _TEST_TAG_NAMES[name_index].name,
        _TEST_ENTITIES[entity_index].value,
        ttl=ttl,
        until=until,
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDERS[0]]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_request_results(
            [
                tools.Token('already_processed_token', _NOW, 200),
                tools.Token('already_failed_token', _NOW, 401),
                tools.Token('still_in_process_token', _NOW, None),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'skip_token_threshold, token, expected_code',
    [
        pytest.param(
            None, 'already_processed_token', 200, id='restore_code_200',
        ),
        pytest.param(
            None, 'already_failed_token', 200, id='ignore_failed_token',
        ),
        pytest.param(
            None, 'still_in_process_token', 500, id='request_in_flight',
        ),
        pytest.param(
            1,
            'still_in_process_token',
            200,
            id='request_in_flight_ignore_token',
        ),
    ],
)
async def test_request_in_process(
        taxi_tags, taxi_config, skip_token_threshold, token, expected_code,
):
    taxi_config.set_values(
        dict(
            TAGS_CUSTOMS_SETTINGS=tools.make_customs_settings_config(
                skip_token_threshold,
            ),
        ),
    )
    await taxi_tags.invalidate_caches()

    data = {
        'provider_id': _TEST_PROVIDERS[0].name,
        'append': [
            {
                'entity_type': _ENTITY_UDID,
                'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
            },
        ],
    }
    response = await taxi_tags.post(
        'v2/upload', data, headers=dict([('X-Idempotency-Token', token)]),
    )
    assert response.status_code == expected_code


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDERS[0]]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
    ],
)
@pytest.mark.parametrize(
    'error_code, data, headers',
    [
        (400, None, constants.TEST_TOKEN_HEADER),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                    },
                ],
            },
            None,
        ),
        (
            400,
            {
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {'provider_id': _TEST_PROVIDERS[0].name},
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(0, 0)],
                    },
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(1, 1)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            tools.Tag.get_tag_data(
                                'a' * 256, _TEST_ENTITIES[0].value,
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            tools.Tag.get_tag_data(
                                '', _TEST_ENTITIES[0].value,
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {'provider_id': _TEST_PROVIDERS[0].name, 'append': []},
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            tools.Tag.get_tag_data(
                                'абвгде',
                                _TEST_ENTITIES[0].value,
                                ttl=_TEST_DURATION,
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            tools.Tag.get_tag_data(
                                '-!?', _TEST_ENTITIES[0].value,
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            404,
            {
                'provider_id': _TEST_PROVIDERS[1].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(0, 0)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            _get_tag_data(
                                0,
                                0,
                                ttl=_TEST_DURATION,
                                until=tools.time_to_str(_TEST_TTL),
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            _get_tag_data(
                                0, 0, until=tools.time_to_str(_TAG_OUTDATED),
                            ),
                        ],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [{'entity_type': _ENTITY_UDID, 'tags': []}],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(0, 0, ttl=0)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_DRIVER_LICENSE,
                        'tags': [_get_tag_data(0, 0)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_CAR_NUMBER,
                        'tags': [_get_tag_data(0, 0)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_PARK,
                        'tags': [_get_tag_data(0, 0)],
                    },
                ],
                'remove': [
                    {
                        'entity_type': _ENTITY_PARK,
                        'tags': [_get_tag_data(0, 0)],
                    },
                ],
            },
            constants.TEST_TOKEN_HEADER,
        ),
    ],
)
@pytest.mark.pgsql('tags')
async def test_fail_request(taxi_tags, error_code, data, headers):
    response = await taxi_tags.post('v2/upload', data, headers=headers)
    assert response.status_code == error_code


@pytest.mark.nofilldb()
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'reposition', 'dst': constants.TAGS_TVM_NAME},
        {'src': 'driver-protocol', 'dst': constants.TAGS_TVM_NAME},
    ],
)
@pytest.mark.parametrize(
    'expected_code, expected_revision_diff, provider_name, append_tags, '
    'remove_tags, tvm_enabled, source_service, expected_provider_tags',
    [
        # Effectively removing one tag from service
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(0, 0)]}],
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 0)]}],
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW, _NOW)],
        ),
        # Appending already existing tag
        (
            200,
            0,
            _TEST_PROVIDERS[0].name,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(0, 0)]}],
            None,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
        ),
        # One tag removal
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            None,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(0, 0)]}],
            True,
            'reposition',
            [_tag(1, 0, 0, _NOW)],
        ),
        # Removing all the tags
        (
            200,
            2,
            _TEST_PROVIDERS[0].name,
            None,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0), _get_tag_data(1, 0)],
                },
            ],
            True,
            'reposition',
            [],
        ),
        # Various entities for append & remove
        (
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [{'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(2, 4)]}],
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0), _get_tag_data(1, 0)],
                },
            ],
            True,
            'reposition',
            [_tag(2, 0, 4, _NOW, entity_type=_ENTITY_PARK)],
        ),
        # tools.Entity with unique id, but different from existing types type
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [{'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(0, 5)]}],
            None,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                _tag(0, 0, 5, _NOW, entity_type=_ENTITY_PARK),  # appended tag
            ],
        ),
        # tools.Entity with same id, but different from existing tags type
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [{'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(0, 4)]}],
            None,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                _tag(0, 0, 4, _NOW, entity_type=_ENTITY_PARK),  # appended tag
            ],
        ),
        # Update tag with limited ttl & remove another tag
        (
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                },
            ],
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 0)]}],
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW, _TEST_TTL), _tag(1, 0, 0, _NOW, _NOW)],
        ),
        # Append tag with limited ttl
        #   updates one tag, but upsert increments revision two times a row
        (
            200,
            2,
            _TEST_PROVIDERS[0].name,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                },
            ],
            None,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW, _TEST_TTL), _tag(1, 0, 0, _NOW)],
        ),
        # Append new tag with limited ttl
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                {
                    'entity_type': _ENTITY_PARK,
                    'tags': [_get_tag_data(0, 5, ttl=_TEST_DURATION)],
                },
            ],
            None,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                # appended tag
                _tag(0, 0, 5, _NOW, _TEST_TTL, entity_type=_ENTITY_PARK),
            ],
        ),
        # Removal of tag with ttl specified
        (
            200,
            1,
            _TEST_PROVIDERS[0].name,
            None,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                },
            ],
            True,
            'reposition',
            [_tag(1, 0, 0, _NOW)],
        ),
        # Removal of already removed tag
        (
            200,
            0,
            _TEST_PROVIDERS[1].name,
            None,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 1)]}],
            True,
            'driver-protocol',
            [
                _tag(1, 1, 0, _NOW),
                # this tag should not be changed
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
        ),
        # Turn off TVM, non-audited provider
        (
            200,
            0,
            _TEST_PROVIDERS[1].name,
            None,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 1)]}],
            False,
            None,
            [
                _tag(1, 1, 0, _NOW),
                # this tag should not be changed
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
        ),
        # Request from non-service provider
        (
            401,
            0,
            _TEST_PROVIDERS[2].name,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 0)]}],
            None,
            False,
            None,
            None,
        ),
        # Request from non-registered service provider
        (
            403,
            0,
            _TEST_PROVIDERS[1].name,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(1, 1, ttl=_TEST_DURATION)],
                },
            ],
            None,
            True,
            'reposition',
            None,
        ),
        # Request from admin-service, financial tag
        (
            401,
            0,
            _TEST_PROVIDERS[0].name,
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'tags': [_get_tag_data(0, 0, ttl=_TEST_DURATION)],
                },
            ],
            None,
            False,
            None,
            None,
        ),
        # Request from admin-service, non-financial tag
        (
            403,
            0,
            _TEST_PROVIDERS[1].name,
            [{'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(0, 1)]}],
            None,
            True,
            'driver-protocol',
            None,
        ),
        # Requests (remove) with deprecated entity_type
        (
            400,
            0,
            _TEST_PROVIDERS[0].name,
            None,
            [
                {
                    'entity_type': _ENTITY_DRIVER_LICENSE,
                    'tags': [_get_tag_data(1, 0)],
                },
            ],
            False,
            None,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
        ),
        # Multi action & entity-type requests
        (
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [
                {'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(2, 4)]},
                {'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 3)]},
            ],
            [
                {'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(1, 0)]},
                {'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(1, 5)]},
            ],
            False,
            None,
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 3, _NOW, entity_type=_ENTITY_UDID),
                _tag(2, 0, 4, _NOW, entity_type=_ENTITY_PARK),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:3]),
        tools.insert_service_providers(
            [
                (_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited'),
                (_TEST_PROVIDERS[1].provider_id, ['driver-protocol'], 'base'),
            ],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES[:2]),
        tools.insert_entities(_TEST_ENTITIES),
        tools.insert_tags(
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 0, _NOW),
                _tag(1, 1, 0, _NOW),
                # already outdated tag
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
        ),
        tools.insert_topics(_TEST_TOPICS),
        tools.insert_relations(
            [
                tools.Relation(
                    _TEST_TAG_NAMES[0].tag_name_id, _TEST_TOPICS[0].topic_id,
                ),
                tools.Relation(
                    _TEST_TAG_NAMES[0].tag_name_id, _TEST_TOPICS[1].topic_id,
                ),
                tools.Relation(
                    _TEST_TAG_NAMES[1].tag_name_id, _TEST_TOPICS[2].topic_id,
                ),
            ],
        ),
        tools.insert_request_results(
            [
                tools.Token('token0', _NOW - datetime.timedelta(days=5), 200),
                tools.Token(
                    'token1', _TAG_OUTDATED - datetime.timedelta(hours=1), 200,
                ),
                tools.Token('token2', _TAG_OUTDATED, 200),
                tools.Token(
                    'token4', _TAG_OUTDATED + datetime.timedelta(hours=4), 200,
                ),
                tools.Token('token5', _NOW, 200),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_upload(
        taxi_tags,
        taxi_config,
        load,
        expected_code,
        expected_revision_diff,
        provider_name,
        append_tags,
        remove_tags,
        tvm_enabled,
        source_service,
        expected_provider_tags,
        pgsql,
):
    taxi_config.set_values(dict(TVM_ENABLED=tvm_enabled))
    setup_revision = tools.get_latest_revision(pgsql['tags'])

    data = {'provider_id': provider_name}
    if append_tags:
        data['append'] = append_tags
    if remove_tags:
        data['remove'] = remove_tags

    headers = constants.TEST_TOKEN_HEADER
    if source_service:
        constants.add_tvm_header(load, headers, source_service)

    # make request and repeat it with the same confirmation token
    for _ in [0, 1]:
        response = await taxi_tags.post('v2/upload', data, headers=headers)
        assert response.status_code == expected_code

        await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

        if expected_provider_tags is not None:
            tools.verify_provider_tags(
                provider_name, expected_provider_tags, pgsql['tags'], _NOW,
            )

        updated_revision = tools.get_latest_revision(pgsql['tags'])
        assert updated_revision - setup_revision == expected_revision_diff


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['driver-protocol'], 'base')],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES[:1]),
        tools.insert_entities(_TEST_ENTITIES[:1]),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('action', ['append', 'remove'])
async def test_duplicate_upload(taxi_tags, action):
    tag_record = {'name': 'tag_0', 'entity': 'udid_0'}
    provider_name = _TEST_PROVIDERS[0].name

    data = {
        'provider_id': provider_name,
        action: [
            {'entity_type': _ENTITY_UDID, 'tags': [tag_record, tag_record]},
        ],
    }

    response = await taxi_tags.post(
        'v2/upload', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == 400


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
    ],
)
@pytest.mark.parametrize(
    'data, expected_tags',
    [
        pytest.param(
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            {'name': 'tag_0', 'entity': 'udid_0'},
                            {'name': 'tag_0', 'entity': 'udid_1'},
                        ],
                    },
                ],
            },
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'entity_value': 'udid_0',
                    'tag_name': 'tag_0',
                },
                {
                    'entity_type': _ENTITY_UDID,
                    'entity_value': 'udid_1',
                    'tag_name': 'tag_0',
                },
            ],
            id='append-udid',
        ),
        pytest.param(
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            {'name': 'tag_0', 'entity': 'udid_0'},
                            {'name': 'tag_0', 'entity': 'udid_1'},
                        ],
                    },
                ],
                'remove': [
                    {
                        'entity_type': _ENTITY_PARK,
                        'tags': [
                            {'name': 'tag_0', 'entity': 'udid_0'},
                            {'name': 'tag_0', 'entity': 'udid_1'},
                        ],
                    },
                ],
            },
            [
                {
                    'entity_type': _ENTITY_UDID,
                    'entity_value': 'udid_0',
                    'tag_name': 'tag_0',
                },
                {
                    'entity_type': _ENTITY_UDID,
                    'entity_value': 'udid_1',
                    'tag_name': 'tag_0',
                },
            ],
            id='append-and-remove',
        ),
    ],
)
async def test_clean_upload(taxi_tags, pgsql, data, expected_tags):
    response = await taxi_tags.post(
        'v2/upload', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tags = tools.get_provider_tags(data['provider_id'], pgsql['tags'])
    assert tags == expected_tags


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES[:2]),
        tools.insert_entities(_TEST_ENTITIES[:3]),
        tools.insert_tags(
            [
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                    ttl=_TAG_OUTDATED,
                ),
                _tag(
                    name_index=1,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                ),
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=1,
                    updated=_TAG_OUTDATED,
                    ttl=_TEST_TTL,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('ttl_until', [True, False])
@pytest.mark.parametrize(
    'expected_code, data, expected_tags',
    [
        (
            200,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            # This tag is now going to live forever
                            _get_tag_data(0, 0),
                            # Tag with TTL specified
                            # that matches it's current value
                            _get_tag_data(0, 1, ttl=_TEST_DURATION),
                        ],
                    },
                ],
            },
            [
                # tools.Tag updated to live forever
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=0,
                    updated=_NOW,
                ),
                # Not changed
                _tag(
                    name_index=1,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                ),
                # tools.Tag updated to live a shorter life
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=1,
                    updated=_NOW,
                    ttl=_TEST_TTL,
                ),
            ],
        ),
        (
            400,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            _get_tag_data(0, 0),
                            _get_tag_data(0, 1, ttl=0),
                        ],
                    },
                ],
            },
            [
                # No changes
                _tag(
                    name_index=1,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                ),
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=1,
                    updated=_TAG_OUTDATED,
                    ttl=_TEST_TTL,
                ),
            ],
        ),
        (
            200,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            # This tag is now going to live
                            # for a limited duration
                            _get_tag_data(0, 0, ttl=_TEST_DURATION),
                        ],
                    },
                ],
            },
            [
                # Tag updated to for a limited duration
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=0,
                    updated=_NOW,
                    ttl=_TEST_TTL,
                ),
                # Not changed
                _tag(
                    name_index=1,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                ),
                # tools.Tag should not be updated
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=1,
                    updated=_TAG_OUTDATED,
                    ttl=_TEST_TTL,
                ),
            ],
        ),
        (
            200,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'append': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            # This tag is now going to live
                            # for a limited duration
                            _get_tag_data(0, 0, ttl=_TEST_DURATION),
                        ],
                    },
                ],
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [_get_tag_data(1, 0), _get_tag_data(0, 1)],
                    },
                ],
            },
            [
                # tools.Tag updated to for a limited duration
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=0,
                    updated=_NOW,
                    ttl=_TEST_TTL,
                ),
            ],
        ),
        (
            200,
            {
                'provider_id': _TEST_PROVIDERS[0].name,
                'remove': [
                    {
                        'entity_type': _ENTITY_UDID,
                        'tags': [
                            # This tag is to be removed
                            _get_tag_data(0, 0, ttl=_TEST_DURATION),
                        ],
                    },
                ],
            },
            [
                _tag(
                    name_index=0,
                    provider_index=0,
                    entity_index=1,
                    updated=_TAG_OUTDATED,
                    ttl=_TEST_TTL,
                ),
                # Not changed
                _tag(
                    name_index=1,
                    provider_index=0,
                    entity_index=0,
                    updated=_TAG_OUTDATED,
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_ttl(
        taxi_tags, pgsql, expected_code, data, expected_tags, ttl_until,
):
    starting_tags = [
        _tag(
            name_index=1,
            provider_index=0,
            entity_index=0,
            updated=_TAG_OUTDATED,
        ),
        _tag(
            name_index=0,
            provider_index=0,
            entity_index=1,
            updated=_TAG_OUTDATED,
            ttl=_TEST_TTL,
        ),
    ]

    tools.verify_provider_tags(
        provider_name=_TEST_PROVIDERS[0].name,
        expected_tags=starting_tags,
        db=pgsql['tags'],
        now=_NOW,
    )

    if ttl_until:
        if 'append' in data:
            tags_records = data['append']
            for tag_records in tags_records:
                for tag in tag_records['tags']:
                    if 'ttl' in tag:
                        ttl = tag['ttl']
                        until = _NOW + datetime.timedelta(seconds=ttl)
                        tag['until'] = tools.time_to_str(until)
                        del tag['ttl']

    response = await taxi_tags.post(
        'v2/upload', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == expected_code

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tools.verify_provider_tags(
        provider_name=_TEST_PROVIDERS[0].name,
        expected_tags=expected_tags,
        db=pgsql['tags'],
        now=_NOW,
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_metric_calls(taxi_tags, statistics):
    async with statistics.capture(taxi_tags) as capture:
        data = {
            'provider_id': _TEST_PROVIDERS[0].name,
            'append': [
                {'entity_type': _ENTITY_UDID, 'tags': [_get_tag_data(0, 0)]},
            ],
            'remove': [
                {'entity_type': _ENTITY_PARK, 'tags': [_get_tag_data(0, 1)]},
            ],
        }
        await taxi_tags.post(
            'v2/upload', data, headers=constants.TEST_TOKEN_HEADER,
        )
    assert capture.statistics == {
        'tags.v2_upload.pg.find_or_create_tag_name_id.success': 2,
        'tags.v2_upload.pg.insert_entities.success': 2,
        'tags.v2_upload.pg.customs_insert.success': 1,
    }
