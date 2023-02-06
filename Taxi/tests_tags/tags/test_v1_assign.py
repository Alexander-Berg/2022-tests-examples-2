# pylint: disable=C0302
import datetime

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools as tools


_CUSTOM_OFFICER = 'customs-officer'

_ENTITY_DRIVER_LICENSE = 'driver_license'
_ENTITY_PARK = 'park'
_ENTITY_UDID = 'udid'

_TEST_PROVIDER = tools.Provider.from_id(1000, True)

_TEST_ENTITIES = [
    tools.Entity(3000, 'udid_0', entity_type=_ENTITY_UDID),
    tools.Entity(3001, 'park', entity_type=_ENTITY_PARK),
    tools.Entity(3002, 'udid_2', entity_type=_ENTITY_UDID),
]

_TEST_TAG_NAMES = [
    tools.TagName(1000, 'tag_0'),
    tools.TagName(1001, 'tag_1'),
    tools.TagName(1002, 'tag_2'),
]

_TEST_TOPIC = tools.Topic(2001, 'topic_1', True)

_INFINITY = 'infinity'
_NOW = datetime.datetime(2019, 8, 29, 10, 54, 9)
_TAG_OUTDATED = _NOW - datetime.timedelta(seconds=45)
#  Test tag livetime in seconds
_TEST_DURATION = 3600
#  Expected tag ttl
_TEST_TTL = _NOW + datetime.timedelta(seconds=_TEST_DURATION)


def _tag(name_index, entity_index, updated=None, ttl=None, entity_type=None):
    return tools.Tag(
        name_id=_TEST_TAG_NAMES[name_index].tag_name_id,
        provider_id=_TEST_PROVIDER.provider_id,
        entity_id=_TEST_ENTITIES[entity_index].entity_id,
        updated=updated,
        ttl=ttl or _INFINITY,
        entity_type=entity_type,
    )


def _get_tags_data(name_index, ttl=None, until=None):
    data = {'name': _TEST_TAG_NAMES[name_index].name}
    if ttl is not None:
        data['ttl'] = ttl
    if until is not None:
        data['until'] = until
    return data


def _make_tags_map(tags):
    data = {}
    for tag in tags:
        ttl = {}
        if 'ttl' in tag:
            ttl['ttl'] = tag['ttl']
        if 'until' in tag:
            ttl['until'] = tag['until']
        data[tag['name']] = ttl
    return data


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_request_results(
            [
                tools.Token('already_processed_token', _NOW, 200),
                tools.Token('still_in_process_token', _NOW, None),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'token, expected_code',
    [
        pytest.param(
            'already_processed_token', 200, id='previous request is done',
        ),
        pytest.param(
            'still_in_process_token', 500, id='previous request is not done',
        ),
    ],
)
async def test_request_in_process(taxi_tags, token, expected_code):
    data = {
        'provider': _TEST_PROVIDER.name,
        'entities': [
            {
                'type': _TEST_ENTITIES[0].type,
                'name': _TEST_ENTITIES[0].value,
                'tags': _make_tags_map([_get_tags_data(0)]),
            },
        ],
    }

    response = await taxi_tags.post(
        'v1/assign', data, headers=dict([('X-Idempotency-Token', token)]),
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'status': 'ok'}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'base')],
        ),
        tools.insert_tag_names([_TEST_TAG_NAMES[0]]),
        tools.insert_entities([_TEST_ENTITIES[0]]),
        tools.insert_topics([_TEST_TOPIC]),
        tools.insert_relations(
            [
                tools.Relation(
                    _TEST_TAG_NAMES[0].tag_name_id, _TEST_TOPIC.topic_id,
                ),
            ],
        ),
        tools.insert_tags([_tag(0, 0, _NOW)]),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'error_code, reassign_tags',
    [
        pytest.param(
            400,
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
            ],
            id='entity duplicate',
        ),
        pytest.param(
            400,
            [
                {
                    'type': _ENTITY_DRIVER_LICENSE,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
            ],
            id='deprecated entity type',
        ),
        pytest.param(
            400,
            [
                {
                    'type': _ENTITY_DRIVER_LICENSE,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [
                            _get_tags_data(
                                0,
                                ttl=_TEST_DURATION,
                                until=tools.time_to_str(_TEST_TTL),
                            ),
                        ],
                    ),
                },
            ],
            id='ttl and until are defined',
        ),
        pytest.param(
            400,
            [
                {
                    'type': _ENTITY_DRIVER_LICENSE,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [
                            _get_tags_data(
                                0, until=tools.time_to_str(_TAG_OUTDATED),
                            ),
                        ],
                    ),
                },
            ],
            id='ttl is expired',
        ),
        pytest.param(
            403,
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [_get_tags_data(0, ttl=_TEST_DURATION)],
                    ),
                },
            ],
            id='financial tags for append',
        ),
        pytest.param(
            403,
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
            ],
            id='financial tags for remove',
        ),
    ],
)
@pytest.mark.pgsql('tags')
async def test_fail_request(taxi_tags, load, error_code, reassign_tags):
    data = {'provider': _TEST_PROVIDER.name, 'entities': reassign_tags}

    headers = {
        'X-Idempotency-Token': 'testtoken',
        'X-Ya-Service-Ticket': load(f'tvm2_ticket_18_{constants.TAGS_TVM_ID}'),
    }
    response = await taxi_tags.post('v1/assign', data, headers=headers)
    assert response.status_code == error_code


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES),
        tools.insert_entities(_TEST_ENTITIES),
        tools.insert_tags([_tag(0, 0, _NOW), _tag(1, 1, _NOW, ttl=_TEST_TTL)]),
    ],
)
@pytest.mark.parametrize(
    'reassign_tags, expected_provider_tags, expected_revision_diff',
    [
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [_get_tags_data(1, ttl=_TEST_DURATION)],
                    ),
                },
            ],
            [_tag(1, 0, _NOW, ttl=_TEST_TTL), _tag(1, 1, _NOW, ttl=_TEST_TTL)],
            2,
            id='tags is not assigned',
        ),
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [
                            _get_tags_data(
                                0, until=tools.time_to_str(_TEST_TTL),
                            ),
                        ],
                    ),
                },
            ],
            [_tag(0, 0, _NOW, ttl=_TEST_TTL), _tag(1, 1, _NOW, ttl=_TEST_TTL)],
            2,
            id='tags is already assigned',
        ),
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[1].type,
                    'name': _TEST_ENTITIES[1].value,
                    'tags': _make_tags_map(
                        [_get_tags_data(1, ttl=_TEST_DURATION)],
                    ),
                },
            ],
            [_tag(0, 0, _NOW), _tag(1, 1, _NOW, ttl=_TEST_TTL)],
            0,
            id='tags is already assigned and ttl is the same',
        ),
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
                {
                    'type': _TEST_ENTITIES[1].type,
                    'name': _TEST_ENTITIES[1].value,
                    'tags': {},
                },
            ],
            [],
            2,
            id='clear tags',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_assign(
        taxi_tags,
        reassign_tags,
        expected_provider_tags,
        expected_revision_diff,
        pgsql,
):
    setup_revision = tools.get_latest_revision(pgsql['tags'])

    data = {'provider': _TEST_PROVIDER.name, 'entities': reassign_tags}
    response = await taxi_tags.post(
        'v1/assign', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tools.verify_provider_tags(
        _TEST_PROVIDER.name, expected_provider_tags, pgsql['tags'], _NOW,
    )

    updated_revision = tools.get_latest_revision(pgsql['tags'])
    assert updated_revision - setup_revision == expected_revision_diff


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tag_names(_TEST_TAG_NAMES),
        tools.insert_entities(_TEST_ENTITIES[:3]),
        tools.insert_tags(
            [
                _tag(0, 0, _NOW),
                _tag(1, 2, _NOW, ttl=_TEST_TTL),
                _tag(2, 2, _TAG_OUTDATED),
            ],
        ),
        tools.insert_tags_customs(
            [_tag(0, 0, _NOW, ttl=_TEST_TTL), _tag(1, 1, _NOW)], 'append',
        ),
        tools.insert_tags_customs([_tag(1, 2)], 'remove'),
    ],
)
@pytest.mark.parametrize(
    'reassign_tags, expected_provider_tags, expected_revision_diff',
    [
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [
                            _get_tags_data(0),
                            _get_tags_data(1, ttl=_TEST_DURATION),
                            _get_tags_data(2),
                        ],
                    ),
                },
            ],
            [
                _tag(0, 0, _NOW),
                _tag(1, 0, _NOW, ttl=_TEST_TTL),
                _tag(2, 0, _NOW),
                _tag(1, 1, _NOW),
                _tag(2, 2, _TAG_OUTDATED),
            ],
            4,
            id='assign some tags',
        ),
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': _make_tags_map(
                        [_get_tags_data(0, ttl=_TEST_DURATION + 100)],
                    ),
                },
                {
                    'type': _TEST_ENTITIES[1].type,
                    'name': _TEST_ENTITIES[1].value,
                    'tags': _make_tags_map([_get_tags_data(1)]),
                },
                {
                    'type': _TEST_ENTITIES[2].type,
                    'name': _TEST_ENTITIES[2].value,
                    'tags': _make_tags_map(
                        [_get_tags_data(1, ttl=_TEST_DURATION + 100)],
                    ),
                },
            ],
            [
                _tag(
                    0,
                    0,
                    _NOW,
                    ttl=_TEST_TTL + datetime.timedelta(seconds=100),
                ),
                _tag(1, 1, _NOW),
                _tag(
                    1,
                    2,
                    _NOW,
                    ttl=_TEST_TTL + datetime.timedelta(seconds=100),
                ),
            ],
            6,
            id='the required tags are in customs',
        ),
        pytest.param(
            [
                {
                    'type': _TEST_ENTITIES[0].type,
                    'name': _TEST_ENTITIES[0].value,
                    'tags': {},
                },
                {
                    'type': _TEST_ENTITIES[1].type,
                    'name': _TEST_ENTITIES[1].value,
                    'tags': {},
                },
                {
                    'type': _TEST_ENTITIES[2].type,
                    'name': _TEST_ENTITIES[2].value,
                    'tags': {},
                },
            ],
            [],
            3,
            id='clear all entities',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_assign_custom(
        taxi_tags,
        reassign_tags,
        expected_provider_tags,
        expected_revision_diff,
        pgsql,
):
    setup_revision = tools.get_latest_revision(pgsql['tags'])

    data = {'provider': _TEST_PROVIDER.name, 'entities': reassign_tags}
    response = await taxi_tags.post(
        'v1/assign', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == 200

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    tools.verify_provider_tags(
        _TEST_PROVIDER.name, expected_provider_tags, pgsql['tags'], _NOW,
    )

    updated_revision = tools.get_latest_revision(pgsql['tags'])
    assert updated_revision - setup_revision == expected_revision_diff


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tag_names([_TEST_TAG_NAMES[0]]),
        tools.insert_entities([_TEST_ENTITIES[0]]),
        tools.insert_tags([_tag(0, 0, _NOW)]),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_assign_new_tags_and_entity_name(taxi_tags, pgsql):
    setup_revision = tools.get_latest_revision(pgsql['tags'])

    data = {
        'provider': _TEST_PROVIDER.name,
        'entities': [
            {
                'type': _ENTITY_UDID,
                'name': 'new_udid',
                'tags': {'new_tag_name': {}},
            },
        ],
    }
    response = await taxi_tags.post(
        'v1/assign', data, headers=constants.TEST_TOKEN_HEADER,
    )
    assert response.status_code == 200

    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)

    rows = tags_select.select_named(
        f'SELECT id FROM state.entities WHERE value = \'new_udid\' '
        f'AND type = \'{_ENTITY_UDID}\'',
        pgsql['tags'],
    )

    assert len(rows) == 1
    entity_id = rows[0]['id']

    rows = tags_select.select_named(
        f'SELECT id FROM meta.tag_names WHERE name = \'new_tag_name\'',
        pgsql['tags'],
    )

    assert len(rows) == 1
    tag_name_id = rows[0]['id']

    expected_provider_tags = [
        _tag(0, 0, _NOW),
        tools.Tag(
            name_id=tag_name_id,
            provider_id=_TEST_PROVIDER.provider_id,
            entity_id=entity_id,
            updated=_NOW,
            ttl=_INFINITY,
            entity_type=_ENTITY_UDID,
        ),
    ]
    tools.verify_provider_tags(
        _TEST_PROVIDER.name, expected_provider_tags, pgsql['tags'], _NOW,
    )

    updated_revision = tools.get_latest_revision(pgsql['tags'])
    assert updated_revision - setup_revision == 1


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers([_TEST_PROVIDER]),
        tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'audited')],
        ),
        tools.insert_tag_names([_TEST_TAG_NAMES[0]]),
        tools.insert_entities([_TEST_ENTITIES[0]]),
        tools.insert_tags([_tag(0, 0, _NOW)]),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_metric_calls(taxi_tags, statistics):
    async with statistics.capture(taxi_tags) as capture:
        data = {
            'provider': _TEST_PROVIDER.name,
            'entities': [
                {
                    'type': _ENTITY_UDID,
                    'name': 'new_udid',
                    'tags': {'new_tag_name': {}},
                },
            ],
        }
        await taxi_tags.post(
            'v1/assign', data, headers=constants.TEST_TOKEN_HEADER,
        )
    prefix = 'tags.v1_assign.pg'
    assert capture.statistics == {
        f'{prefix}.find_or_create_tag_name_id.success': 1,
        f'{prefix}.get_entities_by_names.success': 1,
        f'{prefix}.insert_entities.success': 1,
        f'{prefix}.customs_insert.success': 1,
        f'{prefix}.find_tag_customs_records.success': 1,
        f'{prefix}.find_tag_records_by_provider_and_entities.success': 1,
    }
