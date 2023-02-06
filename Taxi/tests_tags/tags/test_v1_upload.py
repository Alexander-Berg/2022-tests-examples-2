# pylint: disable=C0302
import datetime
import re
from typing import Optional

import pytest

from tests_tags.tags import acl_tools
from tests_tags.tags import constants
from tests_tags.tags import tags_tools as tools


_CUSTOM_OFFICER = 'customs-officer'

_APPEND_POLICY = 'append'
_REPLACE_POLICY = 'replace'
_REMOVE_POLICY = 'remove'
_REPLACE_SAME_NAMED_TAGS_POLICY = 'replace_same_named_tags'

_ENTITY_DRIVER_LICENSE = 'driver_license'
_ENTITY_PHONE = 'phone'
_ENTITY_PARK = 'park'
_ENTITY_UDID = 'udid'
_ENTITY_CORP_CLIENT_ID = 'corp_client_id'

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
    tools.Entity(1, 'udid_3', entity_type=_ENTITY_UDID),
    tools.Entity(1003, 'udid_0', entity_type=_ENTITY_PARK),
    tools.Entity(1004, 'park_0', entity_type=_ENTITY_PARK),
    tools.Entity(1005, 'corp_0', entity_type=_ENTITY_CORP_CLIENT_ID),
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
_INFINITY_DATETIME = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
_NOW = datetime.datetime(2019, 8, 29, 10, 54, 9)
_TAG_LIFETIME = datetime.timedelta(days=1)
_TAG_OUTDATED = _NOW - _TAG_LIFETIME
#  Test tag livetime in seconds
_TEST_DURATION = 3600
#  Expected tag ttl
_TEST_TTL = _NOW + datetime.timedelta(seconds=_TEST_DURATION)
_MINUTE_TTL = _NOW + datetime.timedelta(minutes=1)
_DAY_TTL = _NOW + datetime.timedelta(days=1)


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
    'policy, skip_token_threshold, token, expected_code',
    [
        pytest.param(
            'append',
            None,
            'already_processed_token',
            200,
            id='restore_processed_code_200',
        ),
        pytest.param(
            'append',
            None,
            'still_in_process_token',
            500,
            id='request_in_flight_500_(append_policy)',
        ),
        pytest.param(
            'replace',
            1,
            'still_in_process_token',
            500,
            id='request_in_flight_500_(replace_policy)',
        ),
        pytest.param(
            'append',
            1,
            'still_in_process_token',
            200,
            id='ignore_request_in_flight_200_(append_policy)',
        ),
        pytest.param(
            'remove',
            1,
            'still_in_process_token',
            200,
            id='ignore_request_in_flight_200_(remove_policy)',
        ),
        pytest.param(
            'append', None, 'already_failed_token', 200, id='ignore_bad_code',
        ),
    ],
)
async def test_request_in_process(
        taxi_tags,
        taxi_config,
        policy,
        skip_token_threshold,
        token,
        expected_code,
):
    taxi_config.set_values(
        dict(
            TAGS_CUSTOMS_SETTINGS=tools.make_customs_settings_config(
                skip_token_threshold,
            ),
        ),
    )
    await taxi_tags.invalidate_caches()

    provider = _TEST_PROVIDERS[0].name
    query = f'v1/upload?provider_id={provider}&confirmation_token={token}'
    data = {
        'entity_type': 'udid',
        'merge_policy': policy,
        'tags': [
            tools.Tag.get_data(
                _TEST_TAG_NAMES[0].name,
                _TEST_ENTITIES[0].value,
                ttl=_TEST_DURATION,
            ),
        ],
    }
    response = await taxi_tags.post(query, data)
    assert response.status_code == expected_code


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'error_code, query, data',
    [
        (400, 'v1/upload', None),
        (400, 'v1/upload?provider_id=id', None),
        (400, 'v1/upload?confirmation_token=token', None),
        (400, 'v1/upload?provider_id=id&confirmation_token=token', None),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {'tags': [], 'merge_policy': 'UNKNOWN'},
        ),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': 'tag_name', 'match': {'id': 'ABC123'}}],
                'entity_type': 'unknown_entity_type',
            },
        ),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': 'a' * 256, 'match': {'id': 'ABC123'}}],
                'entity_type': _ENTITY_PARK,
            },
        ),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': '', 'match': {'id': 'ABC123'}}],
                'entity_type': _ENTITY_PARK,
            },
        ),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': 'абвгде', 'match': {'id': 'ABC123'}}],
                'entity_type': _ENTITY_PARK,
            },
        ),
        (
            400,
            'v1/upload?provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': '-!?', 'match': {'id': 'ABC123'}}],
                'entity_type': _ENTITY_PARK,
            },
        ),
        (
            404,
            'v1/upload&provider_id=id&confirmation_token=token',
            {
                'tags': [{'name': 'tag_name', 'match': {'id': 'ABC123'}}],
                'entity_type': _ENTITY_UDID,
            },
        ),
    ],
)
@pytest.mark.pgsql('tags')
async def test_fail_request(taxi_tags, error_code, query, data):
    response = await taxi_tags.post(query, data)
    assert response.status_code == error_code


@pytest.mark.nofilldb()
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'reposition', 'dst': constants.TAGS_TVM_NAME},
        {'src': 'driver-protocol', 'dst': constants.TAGS_TVM_NAME},
    ],
)
@pytest.mark.parametrize(
    'expected_code, expected_revision_diff, provider_name, tags, merge_policy,'
    'entity_type, tvm_enabled, source_service, expected_provider_tags',
    [
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Replace the same name tags, no tags',
        ),
        pytest.param(
            200,
            2,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW, ttl=_TEST_TTL), _tag(1, 0, 0, _NOW)],
            id='Replace the same name tags, one exist finance tags',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[2].name, _TEST_ENTITIES[0].value,
                ),
            ],
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 0, _NOW),
                _tag(2, 0, 0, _NOW, entity_type=_ENTITY_UDID),
            ],
            id='Replace the same name tags, non-exist tags',
        ),
        pytest.param(
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value,
                ),
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[2].name, _TEST_ENTITIES[1].value,
                ),
            ],
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [
                _tag(0, 0, 1, _NOW, entity_type=_ENTITY_UDID),
                _tag(1, 0, 0, _NOW),
                _tag(2, 0, 1, _NOW, entity_type=_ENTITY_UDID),
            ],
            id='Replace the same name tags, some tags',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW, _NOW)],
            id='Effectively removing one tag from service',
        ),
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Appending already existing tag',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
            ],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(1, 0, 0, _NOW)],
            id='One tag removal',
        ),
        pytest.param(
            200,
            2,
            _TEST_PROVIDERS[0].name,
            [],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [],
            id='Removing all the tags',
        ),
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _APPEND_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Appending nothing',
        ),
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Removing nothing',
        ),
        pytest.param(
            200,
            2,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[0].value,
                ),
            ],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [],
            id='Removing all',
        ),
        pytest.param(
            404,
            0,
            'not_existing_provider',
            [],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            None,
            id='Provider does no exist',
        ),
        pytest.param(
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[2].name, _TEST_ENTITIES[3].value,
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(2, 0, 3, _NOW, entity_type=_ENTITY_UDID)],
            id='tools.Tags without entities present',
        ),
        pytest.param(
            404,
            0,
            _TEST_PROVIDERS[3].name,
            [],
            _APPEND_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            None,
            id='New provider, no tags',
        ),
        pytest.param(
            404,
            0,
            _TEST_PROVIDERS[3].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[2].name, _TEST_ENTITIES[3].value,
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            None,
            id='New provider, some tags',
        ),
        pytest.param(
            404,
            0,
            _TEST_PROVIDERS[3].name,
            [],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            None,
            id='New provider, no tags',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[5].value,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_PARK,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                _tag(0, 0, 5, _NOW, entity_type=_ENTITY_PARK),  # appended tag
            ],
            id='tools.Entity with unique id, but different tags type',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[4].value,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_PARK,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                _tag(0, 0, 4, _NOW, entity_type=_ENTITY_PARK),  # appended tag
            ],
            id='tools.Entity with same id, but different tags type',
        ),
        pytest.param(
            200,
            3,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW, _TEST_TTL), _tag(1, 0, 0, _NOW, _NOW)],
            id='Replace tag with limited ttl updates two tags, '
            'but upsert increments revision two times a row',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value, ttl=0,
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Zero ttl is not allowed',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    until=tools.time_to_str(_TAG_OUTDATED),
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Outdated ttl is not allowed',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                    until=tools.time_to_str(_TAG_OUTDATED),
                ),
            ],
            _REPLACE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Defined ttl and until fields, it is not allowed',
        ),
        pytest.param(
            200,
            2,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW, _TEST_TTL), _tag(1, 0, 0, _NOW)],
            id='Append tag with limited ttl updates one tag, '
            'but upsert increments revision two times a row',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[5].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_PARK,
            True,
            'reposition',
            [
                _tag(0, 0, 0, _NOW),  # old tag
                _tag(1, 0, 0, _NOW),  # old tag
                # appended tag
                _tag(0, 0, 5, _NOW, _TEST_TTL, entity_type=_ENTITY_PARK),
            ],
            id='Append new tag with limited ttl',
        ),
        pytest.param(
            200,
            1,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'reposition',
            [_tag(1, 0, 0, _NOW)],
            id='Removal of tag with ttl specified',
        ),
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[1].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[1].value,
                ),
            ],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            True,
            'driver-protocol',
            [
                _tag(1, 1, 0, _NOW),
                # this tag should not be changed
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
            id='Removal of already removed tag',
        ),
        pytest.param(
            200,
            0,
            _TEST_PROVIDERS[1].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[1].value,
                ),
            ],
            _REMOVE_POLICY,
            _ENTITY_UDID,
            False,
            None,
            [
                _tag(1, 1, 0, _NOW),
                # this tag should not be changed
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
            id='Turn off TVM, non-audited provider',
        ),
        pytest.param(
            401,
            0,
            _TEST_PROVIDERS[2].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[0].value,
                ),
            ],
            None,
            _ENTITY_UDID,
            False,
            None,
            None,
            id='Request from non-service provider',
        ),
        pytest.param(
            401,
            0,
            _TEST_PROVIDERS[2].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[0].value,
                ),
            ],
            None,
            _ENTITY_UDID,
            False,
            None,
            None,
            id='Request from non-service provider',
        ),
        pytest.param(
            403,
            0,
            _TEST_PROVIDERS[1].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[1].name,
                    _TEST_ENTITIES[1].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            None,
            _ENTITY_UDID,
            True,
            'reposition',
            None,
            id='Request from non-registered service provider',
        ),
        pytest.param(
            401,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            None,
            _ENTITY_UDID,
            False,
            None,
            None,
            id='Request from admin-service, financial tag',
        ),
        pytest.param(
            401,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            None,
            _ENTITY_UDID,
            False,
            None,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Request from admin-service, financial tag',
        ),
        pytest.param(
            403,
            0,
            _TEST_PROVIDERS[1].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value,
                ),
            ],
            None,
            _ENTITY_UDID,
            True,
            'driver-protocol',
            None,
            id='Request from admin-service, non-financial tag',
        ),
        pytest.param(
            403,
            0,
            _TEST_PROVIDERS[1].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value,
                ),
            ],
            None,
            _ENTITY_UDID,
            True,
            'driver-protocol',
            [
                _tag(1, 1, 0, _NOW),
                # this tag should not be changed
                _tag(1, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
            ],
            id='Request from driver-protocol, non-financial tag',
        ),
        pytest.param(
            400,
            0,
            'not_existing_provider',
            [],
            _REPLACE_POLICY,
            _ENTITY_DRIVER_LICENSE,
            True,
            'reposition',
            None,
            id='Requests with deprecated entity_type',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _APPEND_POLICY,
            _ENTITY_DRIVER_LICENSE,
            True,
            'reposition',
            None,
            id='Deprecated driver_license type',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _APPEND_POLICY,
            _ENTITY_PHONE,
            True,
            'reposition',
            None,
            id='Deprecated phone type',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [],
            _REMOVE_POLICY,
            _ENTITY_DRIVER_LICENSE,
            False,
            None,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Deprecated driver_license type #2',
        ),
        pytest.param(
            400,
            0,
            _TEST_PROVIDERS[0].name,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[6].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            _APPEND_POLICY,
            _ENTITY_CORP_CLIENT_ID,
            True,
            'reposition',
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],  # old tags
            id='Append passenger-tags\' entity-type (check DB)',
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
        tools.insert_entities(_TEST_ENTITIES[:3]),
        tools.insert_entities(_TEST_ENTITIES[4:]),
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
        tags,
        merge_policy,
        entity_type,
        tvm_enabled,
        source_service,
        expected_provider_tags,
        pgsql,
):
    taxi_config.set_values(dict(TVM_ENABLED=tvm_enabled))
    setup_revision = tools.get_latest_revision(pgsql['tags'])

    query = 'v1/upload?provider_id={0}&confirmation_token=token_{0}'.format(
        provider_name,
    )
    data = {'tags': tags, 'entity_type': entity_type}
    if merge_policy:
        data['merge_policy'] = merge_policy

    headers = {}
    if source_service:
        constants.add_tvm_header(load, headers, source_service)

    # make request and repeat it with the same confirmation token
    for _ in [0, 1]:
        response = await taxi_tags.post(query, data, headers=headers)
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
@pytest.mark.parametrize(
    'merge_policy, excepted_tags',
    [
        (_APPEND_POLICY, [_tag(0, 0, 0, _NOW, entity_type=_ENTITY_UDID)]),
        (_REPLACE_POLICY, [_tag(0, 0, 0, _NOW, entity_type=_ENTITY_UDID)]),
        (_REMOVE_POLICY, []),
        (
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            [_tag(0, 0, 0, _NOW, entity_type=_ENTITY_UDID)],
        ),
    ],
)
async def test_duplicate_upload(taxi_tags, merge_policy, excepted_tags, pgsql):
    tag_record = {'name': 'tag_0', 'match': {'id': 'udid_0'}}
    provider_name = _TEST_PROVIDERS[0].name
    query = 'v1/upload?provider_id={0}&confirmation_token=token_{0}'.format(
        provider_name,
    )

    data = {
        'merge_policy': merge_policy,
        'entity_type': _ENTITY_UDID,
        'tags': [tag_record, tag_record],
    }

    response = await taxi_tags.post(query, data)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tools.verify_provider_tags(
        provider_name, excepted_tags, pgsql['tags'], _NOW,
    )


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
@pytest.mark.parametrize(
    'ttl_range, expected_ttl',
    [
        ([_TEST_TTL, None], _INFINITY),
        ([None, _TEST_TTL], _INFINITY),
        ([None, _MINUTE_TTL, _TEST_TTL, _DAY_TTL], _INFINITY),
        ([_DAY_TTL, _TEST_TTL, _MINUTE_TTL], _DAY_TTL),
        ([_TEST_TTL, _MINUTE_TTL], _TEST_TTL),
        ([_MINUTE_TTL], _MINUTE_TTL),
        ([_MINUTE_TTL, _DAY_TTL, _TEST_TTL], _DAY_TTL),
    ],
)
async def test_remove_duplicate_tags_upload(
        taxi_tags, ttl_range, expected_ttl, pgsql,
):
    tag_records = [
        {
            'name': 'tag_0',
            'match': (
                {'id': 'udid_0', 'until': tools.time_to_str(ttl)}
                if ttl is not None
                else {'id': 'udid_0'}
            ),
        }
        for ttl in ttl_range
    ]
    provider_name = _TEST_PROVIDERS[0].name
    query = 'v1/upload?provider_id={0}&confirmation_token=token_{0}'.format(
        provider_name,
    )
    data = {
        'merge_policy': _APPEND_POLICY,
        'entity_type': _ENTITY_UDID,
        'tags': tag_records,
    }

    response = await taxi_tags.post(query, data)
    assert response.status_code == 200
    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    expected_tags = [
        _tag(
            0, 0, 0, updated=_NOW, ttl=expected_ttl, entity_type=_ENTITY_UDID,
        ),
    ]
    tools.verify_provider_tags(
        provider_name, expected_tags, pgsql['tags'], _NOW,
    )


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
    'merge_policy, entity_type, tags',
    [
        (
            _APPEND_POLICY,
            _ENTITY_UDID,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value,
                ),
            ],
        ),
        (
            _REPLACE_POLICY,
            _ENTITY_UDID,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value,
                ),
            ],
        ),
    ],
)
async def test_clean_upload(taxi_tags, merge_policy, entity_type, tags):
    query = 'v1/upload?provider_id={id}&confirmation_token=token_0'.format(
        id=_TEST_PROVIDERS[0].name,
    )
    data = {
        'tags': tags,
        'merge_policy': merge_policy,
        'entity_type': entity_type,
    }
    response = await taxi_tags.post(query, data)
    assert response.status_code == 200

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)


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
    'expected_code, merge_policy, entity_type, tags, expected_tags',
    [
        (
            200,
            _APPEND_POLICY,
            _ENTITY_UDID,
            [
                # This tag is now going to live forever
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
                # tools.Tag with TTL specified that matches it's current value
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[1].value,
                    ttl=_TEST_DURATION,
                ),
            ],
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
            _APPEND_POLICY,
            _ENTITY_UDID,
            [
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                ),
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[1].value, ttl=0,
                ),
            ],
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
            _APPEND_POLICY,
            _ENTITY_UDID,
            [
                # This tag is now going to live for a limited duration
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            [
                # tools.Tag updated to for a limited duration
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
            _REPLACE_POLICY,
            _ENTITY_UDID,
            [
                # This tag is now going to live for a limited duration
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
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
            _REMOVE_POLICY,
            _ENTITY_UDID,
            [
                # This tag is to be removed
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
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
        (
            200,
            _REPLACE_SAME_NAMED_TAGS_POLICY,
            _ENTITY_UDID,
            [
                # This tag is now going to live for a limited duration
                tools.Tag.get_data(
                    _TEST_TAG_NAMES[0].name,
                    _TEST_ENTITIES[0].value,
                    ttl=_TEST_DURATION,
                ),
            ],
            [
                # tools.Tag updated to for a limited duration
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
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_ttl(
        taxi_tags,
        pgsql,
        expected_code,
        merge_policy,
        entity_type,
        tags,
        expected_tags,
        ttl_until,
):
    provider_id = _TEST_PROVIDERS[0].name

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
        provider_name=provider_id,
        expected_tags=starting_tags,
        db=pgsql['tags'],
        now=_NOW,
    )

    if ttl_until:
        for tag in tags:
            if 'ttl' in tag['match']:
                until = _NOW + datetime.timedelta(seconds=tag['match']['ttl'])
                tag['match']['until'] = tools.time_to_str(until)
                del tag['match']['ttl']

    query = 'v1/upload?provider_id={id}&confirmation_token=token_0'.format(
        id=provider_id,
    )
    data = {
        'tags': tags,
        'merge_policy': merge_policy,
        'entity_type': entity_type,
    }
    response = await taxi_tags.post(query, data)
    assert response.status_code == expected_code

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tools.verify_provider_tags(
        provider_name=provider_id,
        expected_tags=expected_tags,
        db=pgsql['tags'],
        now=_NOW,
    )


@pytest.mark.nofilldb()
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': [_TEST_TOPICS[2].name],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.parametrize(
    'tag_name, provider_name, replace_all, assign,'
    'remove, ttl, is_financial, audit_group_name, expected_code,'
    'expected_revision_diff, expected_provider_tags',
    [
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            False,
            None,
            None,
            None,
            False,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='Incorrect action combination: replace=false, all empty',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            True,
            None,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[1].value],
            None,
            False,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='replace=true, assign=[], remove=[\'value\',...]',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            True,
            None,
            None,
            None,
            False,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='replace=true, all others empty',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            True,
            [_TEST_ENTITIES[0].value],
            [_TEST_ENTITIES[1].value],
            None,
            False,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='- replace=true, assign=[\'value1\'], remove=[\'value2\']',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            None,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[1].value],
            [_TEST_ENTITIES[1].value],
            None,
            False,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='- replace=false, assign=[\'value1\'], remove=[\'value1\']',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            _TAG_OUTDATED,
            True,
            None,
            400,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='invalid ttl',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            False,
            None,
            403,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='forbidden-since-not-a-financial-handler',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            None,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            True,
            None,
            200,
            1,
            [_tag(1, 0, 0, _NOW)],
            id='remove financial tag',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[1].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            False,
            None,
            403,
            0,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_PRODUCT_AUDIT_TMP={'is_required': True},
                ),
            ],
            id='append audit required (non-financial) tag, '
            'and audit is required',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[1].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            True,
            None,
            200,
            1,
            [
                _tag(0, 1, 0, _NOW),
                _tag(0, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
                _tag(1, 1, 0, _NOW, _INFINITY, _ENTITY_UDID),
            ],
            id='append audit required (non-financial) tag',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            None,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            True,
            None,
            200,
            1,
            [_tag(1, 0, 0, _NOW)],
            id='removing tags from service (financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[1].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            False,
            None,
            200,
            1,
            [
                _tag(0, 1, 0, _NOW),
                _tag(0, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
                _tag(1, 1, 0, _NOW, None, _ENTITY_UDID),
            ],
            id='appending tags to service (non-financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[1].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            _TEST_DURATION,
            False,
            None,
            200,
            1,
            [
                _tag(0, 1, 0, _NOW),
                _tag(0, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
                _tag(1, 1, 0, _NOW, _TEST_TTL, _ENTITY_UDID),
            ],
            id='appending with ttl (non-financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[1].name,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            _TEST_TTL,
            False,
            None,
            200,
            1,
            [
                _tag(0, 1, 0, _NOW),
                _tag(0, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
                _tag(1, 1, 0, _NOW, _TEST_TTL, _ENTITY_UDID),
            ],
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            False,
            [_TEST_ENTITIES[2].value],
            [_TEST_ENTITIES[0].value],
            None,
            True,
            None,
            200,
            2,
            [
                _tag(1, 0, 0, _NOW),
                _tag(0, 0, 2, _NOW, _INFINITY, _ENTITY_UDID),
            ],
            id='appending & removing (financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[0].name,
            False,
            [_TEST_ENTITIES[2].value],
            [_TEST_ENTITIES[0].value],
            None,
            True,
            'candidates-blocking',
            403,
            0,
            [_tag(0, 0, 0, _NOW), _tag(1, 0, 0, _NOW)],
            id='appending & removing (financial) with only product audit',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[0].name,
            True,
            [_TEST_ENTITIES[2].value],
            None,
            None,
            False,
            None,
            200,
            2,
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 2, _NOW, _INFINITY, _ENTITY_UDID),
            ],
            id='replace (non-financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[0].name,
            True,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[2].value],
            None,
            None,
            False,
            None,
            200,
            1,
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 0, _NOW),
                _tag(1, 0, 2, _NOW, _INFINITY, _ENTITY_UDID),
            ],
            id='replace exist (non-financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            _TEST_PROVIDERS[0].name,
            True,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[2].value],
            None,
            _TEST_DURATION,
            False,
            None,
            200,
            3,
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 0, _NOW, _TEST_TTL),
                _tag(1, 0, 2, _NOW, _TEST_TTL, _ENTITY_UDID),
            ],
            id='replace with ttl (non-financial)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[2].name,
            True,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[2].value],
            None,
            None,
            False,
            None,
            401,
            0,
            None,
            id='request from service provider (non-finance handler)',
        ),
        pytest.param(
            _TEST_TAG_NAMES[0].name,
            _TEST_PROVIDERS[2].name,
            True,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[2].value],
            None,
            None,
            True,
            None,
            401,
            0,
            None,
            id='request from service provider (finance handler)',
        ),
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:3]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[2].provider_id, ['driver-protocol'], 'base')],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES[:2]),
        tools.insert_entities(_TEST_ENTITIES[:3]),
        tools.insert_entities(_TEST_ENTITIES[4:]),
        tools.insert_tags(
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 0, _NOW),
                _tag(0, 1, 0, _NOW),
                _tag(0, 1, 1, _TAG_OUTDATED, _TAG_OUTDATED),
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
async def test_admin_upload(
        taxi_tags,
        taxi_config,
        tag_name,
        provider_name,
        replace_all,
        assign,
        remove,
        ttl,
        is_financial,
        audit_group_name: Optional[str],
        expected_code,
        expected_revision_diff,
        expected_provider_tags,
        acl_enabled,
        pgsql,
        mockserver,
):
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    setup_revision = tools.get_latest_revision(pgsql['tags'])

    query = 'v1/admin/finance/upload' if is_financial else 'v1/admin/upload'
    data = {
        'tag_name': tag_name,
        'entity_type': _ENTITY_UDID,
        'provider': provider_name,
        'confirmation_token': 'token_' + provider_name,
    }
    if replace_all is not None:
        data['replace_all'] = replace_all
    if assign is not None:
        data['assign'] = assign
    if remove is not None:
        data['remove'] = remove
    if ttl is not None:
        data['ttl'] = {}
        if isinstance(ttl, int):
            data['ttl']['duration'] = ttl
        else:
            data['ttl']['until'] = tools.time_to_str(ttl)
    if audit_group_name:
        data['audit_group_name'] = audit_group_name

    # Make request and repeat it with the same confirmation token
    for _ in [0, 1]:
        response = await taxi_tags.post(
            query, data, headers=constants.TEST_LOGIN_HEADER,
        )
        assert response.status_code == expected_code

        await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)
        if expected_provider_tags is not None:
            tools.verify_provider_tags(
                provider_name, expected_provider_tags, pgsql['tags'], _NOW,
            )

        updated_revision = tools.get_latest_revision(pgsql['tags'])
        assert updated_revision - setup_revision == expected_revision_diff


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'product',
                'title': 'Tests product team',
                'topics': ['product_topic'],
            },
        ],
    },
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_tag_names(
            [
                tools.TagName(0, 'product_tag'),
                tools.TagName(1, 'financial_tag'),
            ],
        ),
        tools.insert_topics(
            [
                tools.Topic(2000, 'product_topic', False),
                tools.Topic(2001, 'financial_topic', True),
            ],
        ),
        tools.insert_relations(
            [tools.Relation(0, 2000), tools.Relation(1, 2001)],
        ),
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_request_results(
            [
                tools.Token(
                    'token0', _NOW - datetime.timedelta(seconds=3), None,
                ),
                tools.Token('token5', _NOW, 200),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'tag_name, provider_name, confirmation_token, entity_type,'
    'replace_all, assign, remove, ttl,'
    'expected_code, expected_message, audit_group_name',
    [
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            None,
            [_TEST_ENTITIES[0].value, _TEST_ENTITIES[1].value],
            None,
            400,
            'properties replace_all and remove can\'t be used together',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            [_TEST_ENTITIES[0].value],
            [_TEST_ENTITIES[1].value],
            None,
            400,
            'properties replace_all and remove can\'t be used together',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            None,
            None,
            None,
            400,
            'assign should be specified with replace_all',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            None,
            None,
            None,
            None,
            400,
            'no action was specified',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            [_TEST_ENTITIES[0].value],
            None,
            400,
            'entity "udid_0" found in both "append" and "remove" lists',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            '',
            False,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            400,
            # do not check standart library error messages
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            'entity_type_invalid',
            False,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            400,
            # never check standard library error messages
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            None,
            _TAG_OUTDATED,
            400,
            'time is expired',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            None,
            str(_TEST_TTL),
            400,
            # never check standard library messages
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token0',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            400,
            'confirmation token already was used',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token5',
            _ENTITY_UDID,
            True,
            [_TEST_ENTITIES[1].value, _TEST_ENTITIES[0].value],
            None,
            None,
            400,
            'confirmation token already was used',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[1].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            None,
            None,
            404,
            'provider "' + _TEST_PROVIDERS[1].name + '" was not found',
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[0].value],
            None,
            _TEST_TTL,
            200,
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            None,
            [_TEST_ENTITIES[0].value],
            None,
            200,
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            False,
            [_TEST_ENTITIES[1].value],
            [_TEST_ENTITIES[0].value],
            None,
            200,
            None,
            None,
        ),
        (
            'tag_0',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            [_TEST_ENTITIES[1].value, _TEST_ENTITIES[0].value],
            None,
            _TEST_DURATION,
            200,
            None,
            None,
        ),
        (
            'financial_tag',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            [_TEST_ENTITIES[1].value, _TEST_ENTITIES[0].value],
            None,
            _TEST_DURATION,
            200,
            None,
            'financial',
        ),
        (
            'product_tag',
            _TEST_PROVIDERS[0].name,
            'token',
            _ENTITY_UDID,
            True,
            [_TEST_ENTITIES[1].value, _TEST_ENTITIES[0].value],
            None,
            _TEST_DURATION,
            200,
            None,
            'product',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_check_admin_upload(
        taxi_tags,
        tag_name,
        provider_name,
        confirmation_token,
        entity_type,
        replace_all,
        assign,
        remove,
        ttl,
        expected_code,
        expected_message,
        audit_group_name,
        mockserver,
        taxi_config,
        acl_enabled,
):
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    data = {
        'tag_name': tag_name,
        'entity_type': entity_type,
        'provider': provider_name,
        'confirmation_token': confirmation_token,
    }
    if replace_all is not None:
        data['replace_all'] = replace_all
    if assign is not None:
        data['assign'] = assign
    if remove is not None:
        data['remove'] = remove
    if ttl is not None:
        data['ttl'] = {}
        if isinstance(ttl, int):
            data['ttl']['duration'] = ttl
        elif isinstance(ttl, str):
            data['ttl']['until'] = ttl
        else:
            data['ttl']['until'] = tools.time_to_str(ttl)

    response = await taxi_tags.post(
        'v1/admin/finance/check_upload',
        data,
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code
    json = response.json()
    if expected_code == 200:
        change_doc_id = json.pop('change_doc_id', None)
        expected_data = data
        if audit_group_name:
            expected_data['audit_group_name'] = audit_group_name
        assert json == {'data': expected_data}
        # check change_doc_id like 'assign_{tag}_{uuid}'
        regexp = f'^assign_{data["tag_name"]}_[A-Za-z0-9]{{32}}$'
        assert re.match(regexp, change_doc_id) is not None
    if expected_message:
        assert json['code'] == f'{expected_code}'
        assert json['message'] == expected_message


@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.parametrize(
    'is_financial', [False, True], ids=['finance_off', 'finance_on'],
)
@pytest.mark.parametrize(
    'tag_name, expected_code, expected_topics, expected_message',
    [
        pytest.param(
            _TEST_TAG_NAMES[0].name, 200, [], None, id='tag without topic',
        ),
        pytest.param(
            _TEST_TAG_NAMES[1].name,
            403,
            [_TEST_TOPICS[0].name],
            f'tag {_TEST_TAG_NAMES[1].name} is '
            f'in acl prohibited topics: {_TEST_TOPICS[0].name}; '
            f'acl prohibited topics: {_TEST_TOPICS[0].name}',
            id='prohibited tag in one topic',
        ),
        pytest.param(
            _TEST_TAG_NAMES[2].name,
            403,
            [_TEST_TOPICS[0].name, _TEST_TOPICS[2].name],
            f'tag {_TEST_TAG_NAMES[2].name} is '
            f'in acl prohibited '
            f'topics: {_TEST_TOPICS[0].name}, {_TEST_TOPICS[2].name}; '
            f'acl prohibited '
            f'topics: {_TEST_TOPICS[0].name}, {_TEST_TOPICS[2].name}',
            id='prohibited tag in multiple topics',
        ),
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:1]),
        tools.insert_tag_names(_TEST_TAG_NAMES[:3]),
        tools.insert_topics(_TEST_TOPICS),
        tools.insert_relations(
            [
                tools.Relation(
                    _TEST_TAG_NAMES[1].tag_name_id, _TEST_TOPICS[0].topic_id,
                ),
                tools.Relation(
                    _TEST_TAG_NAMES[2].tag_name_id, _TEST_TOPICS[0].topic_id,
                ),
                tools.Relation(
                    _TEST_TAG_NAMES[2].tag_name_id, _TEST_TOPICS[2].topic_id,
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_admin_upload_acl_prohibited(
        taxi_tags,
        mockserver,
        tag_name,
        is_financial,
        expected_code,
        expected_topics,
        expected_message,
):
    mock_acl = acl_tools.make_mock_acl_prohibited(
        mockserver, constants.TEST_LOGIN, expected_topics, expected_topics,
    )

    data = {
        'tag_name': tag_name,
        'entity_type': _ENTITY_UDID,
        'provider': _TEST_PROVIDERS[0].name,
        'confirmation_token': 'token0',
        'assign': [_TEST_ENTITIES[0].value],
        'ttl': {'duration': _TEST_DURATION},
    }

    response = await taxi_tags.post(
        'v1/admin/finance/check_upload',
        data,
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code
    if expected_code == 403:
        assert response.json() == {'code': '403', 'message': expected_message}
        assert mock_acl.times_called == 1

    endpoint = 'v1/admin/finance/upload' if is_financial else 'v1/admin/upload'

    response = await taxi_tags.post(
        endpoint, data, headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == expected_code

    if response.status_code == 403:
        assert response.json() == {'code': '403', 'message': expected_message}
        assert mock_acl.times_called == 2


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'is_financial', [True, False], ids=['financial', 'non_financial'],
)
@pytest.mark.parametrize(
    'tag_name, assign, remove, expected_code, entity_type',
    [
        # append normal tag
        (
            _TEST_TAG_NAMES[1].name,
            [_TEST_ENTITIES[0].value],
            None,
            200,
            _ENTITY_UDID,
        ),
        # append a tag with driver_licence
        (
            _TEST_TAG_NAMES[1].name,
            [_TEST_ENTITIES[0].value],
            None,
            400,
            _ENTITY_DRIVER_LICENSE,
        ),
        # removing tags from service with driver_licence
        (
            _TEST_TAG_NAMES[0].name,
            None,
            [_TEST_ENTITIES[0].value],
            400,
            _ENTITY_DRIVER_LICENSE,
        ),
        # appending and removing tags from service with driver_licence
        (
            _TEST_TAG_NAMES[1].name,
            [_TEST_ENTITIES[1].value],
            [_TEST_ENTITIES[0].value],
            400,
            _ENTITY_DRIVER_LICENSE,
        ),
    ],
)
@pytest.mark.pgsql(
    'tags', queries=[tools.insert_providers(_TEST_PROVIDERS[1:2])],
)
@pytest.mark.now(_NOW.isoformat())
async def test_admin_upload_entity_deprecated(
        taxi_tags,
        tag_name,
        assign,
        remove,
        is_financial,
        expected_code,
        entity_type,
):

    query = 'v1/admin/finance/upload' if is_financial else 'v1/admin/upload'
    data = {
        'tag_name': tag_name,
        'entity_type': entity_type,
        'provider': _TEST_PROVIDERS[1].name,
        'confirmation_token': 'token',
    }
    if assign is not None:
        data['assign'] = assign
    if remove is not None:
        data['remove'] = remove

    response = await taxi_tags.post(
        query, data, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_tag_names(_TEST_TAG_NAMES[:1]),
        tools.insert_providers(_TEST_PROVIDERS[:2]),
        tools.insert_entities(_TEST_ENTITIES[:1]),
        tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tags([_tag(0, 0, 0, _NOW), _tag(0, 1, 0, _NOW)]),
    ],
)
@pytest.mark.parametrize(
    'url, data, component_name, labels',
    [
        pytest.param(
            'v1/upload?provider_id={id}&confirmation_token=token_0'.format(
                id=_TEST_PROVIDERS[0].name,
            ),
            {
                'tags': [
                    tools.Tag.get_data(
                        _TEST_TAG_NAMES[0].name, _TEST_ENTITIES[0].value,
                    ),
                    tools.Tag.get_data(
                        _TEST_TAG_NAMES[1].name, _TEST_ENTITIES[1].value,
                    ),
                ],
                'merge_policy': _REPLACE_POLICY,
                'entity_type': _ENTITY_UDID,
            },
            'v1_upload',
            [
                'customs_insert',
                'find_or_create_tag_name_id',
                'insert_entities',
            ],
            id='upload handler',
        ),
        pytest.param(
            'v1/admin/upload',
            {
                'tag_name': _TEST_TAG_NAMES[1].name,
                'entity_type': _ENTITY_UDID,
                'provider': _TEST_PROVIDERS[1].name,
                'assign': [_TEST_ENTITIES[1].value],
                'confirmation_token': 'token_0',
            },
            'admin_upload',
            [
                'customs_insert',
                'find_or_create_tag_name_id',
                'insert_entities',
            ],
            id='admin upload handler',
        ),
        pytest.param(
            'v1/admin/finance/upload',
            {
                'tag_name': _TEST_TAG_NAMES[0].name,
                'entity_type': _ENTITY_UDID,
                'provider': _TEST_PROVIDERS[1].name,
                'remove': [_TEST_ENTITIES[0].value],
                'confirmation_token': 'token_0',
            },
            'admin_upload',
            ['customs_insert'],
            id='admin finance upload handler',
        ),
    ],
)
async def test_metric_calls(
        taxi_tags, statistics, url, data, component_name, labels,
):
    async with statistics.capture(taxi_tags) as capture:
        response = await taxi_tags.post(
            url, data, headers=constants.TEST_LOGIN_HEADER,
        )
        assert response.status_code == 200

    assert capture.statistics == {
        f'tags.{component_name}.pg.{label}.success': 1 for label in labels
    }
