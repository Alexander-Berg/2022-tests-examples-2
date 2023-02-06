import datetime
import enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_TEST_PROVIDERS = [
    tags_tools.Provider.from_id(1000, True),
    tags_tools.Provider.from_id(1001, False),
    tags_tools.Provider.from_id(1002, False),
    tags_tools.Provider.from_id(1003, True),
    tags_tools.Provider.from_id(1004, True),
    tags_tools.Provider.from_id(1005, True),
    tags_tools.Provider.from_id(1006, True),
    tags_tools.Provider.from_id(1007, True),
    tags_tools.Provider.from_id(1008, False),
    tags_tools.Provider.from_id(1009, False),
    tags_tools.Provider.from_id(1010, False),
    tags_tools.Provider.from_id(1011, False),
    tags_tools.Provider.from_id(1012, True),
    tags_tools.Provider.from_id(1013, True),
    tags_tools.Provider.from_id(1014, False),
    tags_tools.Provider.from_id(1015, False),
]

_TEST_ENTITIES = [
    tags_tools.Entity(1000, 'license_0'),
    tags_tools.Entity(1001, 'license_1'),
]

_TEST_TAG_NAMES = [
    tags_tools.TagName(1000, 'tag_0'),
    tags_tools.TagName(1001, 'tag_1'),
    tags_tools.TagName(1002, 'tag_2'),
    tags_tools.TagName(1003, 'tag_3'),
]

_TEST_SERVICE_NAMES = ['service_test_0', 'service_test_1']

_BASE = 'base'
_AUDITED = 'audited'
_UNIQUE_DRIVER_ID = 'udid'
_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
_NOW = datetime.datetime(2019, 10, 25, 12, 45, 32, 0)
_EXPIRATION = _NOW + datetime.timedelta(hours=24)


def _tag(
        name_index: int,
        provider_index: int,
        entity_index: int,
        updated: Optional[str] = None,
        ttl: datetime.datetime = _INFINITY,
):
    return tags_tools.Tag(
        _TEST_TAG_NAMES[name_index].tag_name_id,
        _TEST_PROVIDERS[provider_index].provider_id,
        _TEST_ENTITIES[entity_index].entity_id,
        updated=updated,
        ttl=ttl,
    )


def _search_result(providers: List[tags_tools.Provider]):
    not_sorted = [provider.search_result() for provider in providers]
    return sorted(not_sorted, key=lambda provider: provider.get('id'))


def _insert_service_providers(data: List[Tuple[int, List[str], str]]):
    query = (
        'INSERT INTO service.providers'
        ' (provider_id, service_names, authority) '
        'VALUES '
    )

    first_value = True
    for row in data:
        if not first_value:
            query += ', '
        services = '{' + ','.join('\"' + name + '\"' for name in row[1]) + '}'
        query += (
            '({provider_id}, \'{service_names}\', \'{authority}\')'.format(
                provider_id=row[0], service_names=services, authority=row[2],
            )
        )
        first_value = False

    return query


def _insert_yql_provider(
        provider_id: int,
        entity: str,
        enabled: bool = True,
        name: Optional[str] = None,
        author: str = 'author_test',
        last_modifier: str = 'last_modifier_test',
        changed: str = '2018-08-30T12:34:56.0',
        created: str = '2018-08-30T12:34:56.0',
        period: int = 1800,
        query: str = 'USE hahn via SQL;',
        syntax: str = 'SQL',
):
    if name is None:
        name = 'name_test_' + str(provider_id)
    return yql_tools.insert_queries(
        [
            yql_tools.Query(
                name=name,
                provider_id=provider_id,
                entity_type=entity,
                tags=[],
                author=author,
                last_modifier=last_modifier,
                enabled=enabled,
                changed=changed,
                created=created,
                period=period,
                query=query,
                syntax=syntax,
            ),
        ],
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS),
        _insert_service_providers(
            [
                (_TEST_PROVIDERS[0].provider_id, _TEST_SERVICE_NAMES, _BASE),
                (
                    _TEST_PROVIDERS[1].provider_id,
                    [_TEST_SERVICE_NAMES[0]],
                    _AUDITED,
                ),
                (_TEST_PROVIDERS[2].provider_id, _TEST_SERVICE_NAMES, _BASE),
                (
                    _TEST_PROVIDERS[3].provider_id,
                    _TEST_SERVICE_NAMES,
                    _AUDITED,
                ),
                (
                    _TEST_PROVIDERS[5].provider_id,
                    [_TEST_SERVICE_NAMES[1]],
                    _BASE,
                ),
                (
                    _TEST_PROVIDERS[6].provider_id,
                    _TEST_SERVICE_NAMES,
                    _AUDITED,
                ),
                (
                    _TEST_PROVIDERS[8].provider_id,
                    [_TEST_SERVICE_NAMES[0]],
                    _BASE,
                ),
                (
                    _TEST_PROVIDERS[11].provider_id,
                    _TEST_SERVICE_NAMES,
                    _AUDITED,
                ),
            ],
        ),
        _insert_yql_provider(
            _TEST_PROVIDERS[12].provider_id, _UNIQUE_DRIVER_ID,
        ),
        _insert_yql_provider(
            _TEST_PROVIDERS[13].provider_id, _UNIQUE_DRIVER_ID,
        ),
        _insert_yql_provider(
            _TEST_PROVIDERS[14].provider_id, _UNIQUE_DRIVER_ID,
        ),
        _insert_yql_provider(
            _TEST_PROVIDERS[15].provider_id, _UNIQUE_DRIVER_ID,
        ),
    ],
)
@pytest.mark.parametrize(
    'types, only_active, only_verified',
    [
        pytest.param(None, False, None, id='no-types'),
        pytest.param(None, True, False, id='only-active'),
        pytest.param(None, False, True, id='only-verified'),
        pytest.param(['service'], None, False, id='only-service'),
        pytest.param(['service'], None, True, id='only-verified-service'),
        pytest.param(['yql'], None, None, id='only-yql'),
        pytest.param(['manual'], None, None, id='only-manual'),
        pytest.param(
            ['service', 'yql', 'manual'], None, True, id='all-types-verified',
        ),
        pytest.param(['service', 'yql', 'manual'], None, None, id='all-types'),
    ],
)
@pytest.mark.parametrize(
    'name_part, offset, limit',
    [
        pytest.param(None, None, None, id='no-limits'),
        pytest.param(None, 2, 2, id='limits-2'),
        pytest.param('abc', 0, 1, id='one-name'),
        pytest.param('01', 0, 2, id='two-names'),
    ],
)
async def test_search(
        taxi_tags,
        only_active: Optional[bool],
        only_verified: Optional[bool],
        types: List[str],
        name_part: str,
        limit: int,
        offset: int,
):
    service_providers = {
        _TEST_PROVIDERS[0].provider_id: (_TEST_SERVICE_NAMES, _BASE),
        _TEST_PROVIDERS[1].provider_id: ([_TEST_SERVICE_NAMES[0]], _AUDITED),
        _TEST_PROVIDERS[2].provider_id: (_TEST_SERVICE_NAMES, _BASE),
        _TEST_PROVIDERS[3].provider_id: (_TEST_SERVICE_NAMES, _AUDITED),
        _TEST_PROVIDERS[5].provider_id: ([_TEST_SERVICE_NAMES[1]], _BASE),
        _TEST_PROVIDERS[6].provider_id: (_TEST_SERVICE_NAMES, _AUDITED),
        _TEST_PROVIDERS[8].provider_id: ([_TEST_SERVICE_NAMES[0]], _BASE),
        _TEST_PROVIDERS[11].provider_id: (_TEST_SERVICE_NAMES, _AUDITED),
    }
    yql_providers = frozenset(
        [
            _TEST_PROVIDERS[12].provider_id,
            _TEST_PROVIDERS[13].provider_id,
            _TEST_PROVIDERS[14].provider_id,
            _TEST_PROVIDERS[15].provider_id,
        ],
    )

    data: Dict[str, Any] = dict()
    if types:
        data['types'] = types
    if only_active is not None:
        data['only_active'] = only_active
    if name_part is not None:
        data['name_part'] = name_part
    if types and 'service' in types and only_verified is not None:
        data['only_verified'] = only_verified
    if limit is not None:
        data['limit'] = limit
    if offset is not None:
        data['offset'] = offset

    response = await taxi_tags.post('v1/providers/search', data)
    assert response.status_code == 200

    service_type = 'service' in types if types else False
    yql_type = 'yql' in types if types else False
    manual_type = 'manual' in types if types else False
    result = []
    for provider in _TEST_PROVIDERS:
        provider_id = provider.provider_id
        if only_active and not provider.is_active:
            continue
        if name_part and provider.name.find(name_part) == -1:
            continue
        skip = service_type or yql_type or manual_type
        if (
                service_type
                and provider_id in service_providers
                and (
                    not only_verified
                    or service_providers[provider_id][1] == _AUDITED
                )
        ):
            skip = False
        if yql_type and provider_id in yql_providers:
            skip = False
        if (
                manual_type
                and provider_id not in service_providers
                and provider_id not in yql_providers
        ):
            skip = False
        if skip:
            continue
        provider_type = 'manual'
        names = None
        authority = None
        if provider_id in service_providers:
            provider_type = 'service'
            names, authority = service_providers[provider_id]
        elif provider_id in yql_providers:
            provider_type = 'yql'
            names = ['name_test_' + str(provider_id)]
        item = {
            'id': provider.name,
            'is_active': provider.is_active,
            'description': provider.desc,
            'source': {'type': provider_type},
        }
        if names is not None:
            item['source']['names'] = names
        if authority is not None:
            item['source']['authority'] = authority
        result.append(item)

    offset = offset or 0
    limit = limit or 200
    data_json = response.json().get('data')
    assert data_json == result[offset : offset + limit]


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'data, expected_code',
    [
        ({'limit': 0, 'offset': 0}, 400),
        ({'limit': -1, 'offset': 10}, 400),
        ({'offset': -1}, 400),
        ({'only_verified': True}, 400),
        ({'only_verified': True, 'types': ['yql', 'manual']}, 400),
        ({'types': []}, 400),
        ({'types': ['type_invalid', 'yql', 'manual']}, 400),
        ({'name_part': ''}, 400),
    ],
)
async def test_search_bad_input(taxi_tags, data, expected_code):
    response = await taxi_tags.post('v1/providers/search', data)
    assert response.status_code == expected_code


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS[:4]),
        _insert_service_providers(
            [
                (
                    _TEST_PROVIDERS[0].provider_id,
                    _TEST_SERVICE_NAMES[:1],
                    _BASE,
                ),
                (
                    _TEST_PROVIDERS[1].provider_id,
                    _TEST_SERVICE_NAMES,
                    _AUDITED,
                ),
            ],
        ),
        _insert_yql_provider(
            _TEST_PROVIDERS[2].provider_id, _UNIQUE_DRIVER_ID,
        ),
    ],
)
@pytest.mark.parametrize('verified', [False, True])
@pytest.mark.parametrize(
    'provider_id, data, expected_code, expected_search',
    [
        (None, {}, 400, None),
        ('new_provider', {}, 400, []),
        (
            _TEST_PROVIDERS[0].name,
            {},
            400,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': _TEST_PROVIDERS[0].is_active,
                    'description': _TEST_PROVIDERS[0].desc,
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES[:1],
                        'authority': _BASE,
                    },
                },
            ],
        ),
        (' invalid_provider_name ', {}, 400, None),
        (
            _TEST_PROVIDERS[0].name,
            {'description': 'overwrite_base_query'},
            200,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': _TEST_PROVIDERS[0].is_active,
                    'description': 'overwrite_base_query',
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES[:1],
                        'authority': _BASE,
                    },
                },
            ],
        ),
        (
            _TEST_PROVIDERS[0].name,
            {
                'description': 'overwrite_base_query',
                'services': _TEST_SERVICE_NAMES,
            },
            200,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': _TEST_PROVIDERS[0].is_active,
                    'description': 'overwrite_base_query',
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES,
                        'authority': _BASE,
                    },
                },
            ],
        ),
        (
            _TEST_PROVIDERS[2].name,
            {'description': 'overwrite_yql_query'},
            200,
            [
                {
                    'id': _TEST_PROVIDERS[2].name,
                    'is_active': True,
                    'description': 'overwrite_yql_query',
                    'source': {
                        'type': 'yql',
                        'names': [
                            'name_test_' + str(_TEST_PROVIDERS[2].provider_id),
                        ],
                    },
                },
            ],
        ),
        (
            _TEST_PROVIDERS[3].name,
            {'description': 'overwrite_manual_query'},
            200,
            [
                {
                    'id': _TEST_PROVIDERS[3].name,
                    'is_active': True,
                    'description': 'overwrite_manual_query',
                    'source': {'type': 'manual'},
                },
            ],
        ),
        (
            'new_provider',
            {'description': 'create_manual_query'},
            200,
            [
                {
                    'id': 'new_provider',
                    'is_active': True,
                    'description': 'create_manual_query',
                    'source': {'type': 'manual'},
                },
            ],
        ),
        (
            'new_provider',
            {
                'description': 'create_service_query',
                'services': _TEST_SERVICE_NAMES,
            },
            200,
            [
                {
                    'id': 'new_provider',
                    'is_active': True,
                    'description': 'create_service_query',
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES,
                        'authority': _BASE,
                    },
                },
            ],
        ),
        (
            _TEST_PROVIDERS[2].name,
            {
                'description': 'overwrite_yql_query',
                'services': _TEST_SERVICE_NAMES,
            },
            403,
            [
                {
                    'id': _TEST_PROVIDERS[2].name,
                    'is_active': _TEST_PROVIDERS[2].is_active,
                    'description': _TEST_PROVIDERS[2].desc,
                    'source': {
                        'type': 'yql',
                        'names': [
                            'name_test_' + str(_TEST_PROVIDERS[2].provider_id),
                        ],
                    },
                },
            ],
        ),
        (
            _TEST_PROVIDERS[3].name,
            {
                'description': 'overwrite_yql_query',
                'services': _TEST_SERVICE_NAMES,
            },
            403,
            [
                {
                    'id': _TEST_PROVIDERS[3].name,
                    'is_active': _TEST_PROVIDERS[3].is_active,
                    'description': _TEST_PROVIDERS[3].desc,
                    'source': {'type': 'manual'},
                },
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_providers(
        taxi_tags, verified, provider_id, data, expected_code, expected_search,
):
    query = 'v1/providers/verified/items' if verified else 'v1/providers/items'
    if provider_id:
        query += '?id=%s' % provider_id
    response = await taxi_tags.put(query, data)
    assert response.status_code == expected_code

    if expected_search is not None:
        search_result = await taxi_tags.post(
            'v1/providers/search', {'name_part': provider_id},
        )
        assert search_result.status_code == 200
        data_json = search_result.json().get('data')
        assert data_json == expected_search


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS[:1]),
        _insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, _TEST_SERVICE_NAMES, _AUDITED)],
        ),
    ],
)
@pytest.mark.parametrize(
    'verified, provider_id, data, expected_code, expected_search',
    [
        (
            False,
            _TEST_PROVIDERS[0].name,
            {'description': 'overwrite_audited_query'},
            403,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': _TEST_PROVIDERS[0].is_active,
                    'description': _TEST_PROVIDERS[0].desc,
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES,
                        'authority': _AUDITED,
                    },
                },
            ],
        ),
        (
            True,
            _TEST_PROVIDERS[0].name,
            {'description': 'overwrite_audited_query'},
            200,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': True,
                    'description': 'overwrite_audited_query',
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES,
                        'authority': _AUDITED,
                    },
                },
            ],
        ),
        (
            True,
            _TEST_PROVIDERS[0].name,
            {
                'description': 'overwrite_audited_query',
                'services': _TEST_SERVICE_NAMES[:1],
            },
            200,
            [
                {
                    'id': _TEST_PROVIDERS[0].name,
                    'is_active': True,
                    'description': 'overwrite_audited_query',
                    'source': {
                        'type': 'service',
                        'names': _TEST_SERVICE_NAMES[:1],
                        'authority': _AUDITED,
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_audited_providers(
        taxi_tags, verified, provider_id, data, expected_code, expected_search,
):
    query = 'v1/providers/verified/items' if verified else 'v1/providers/items'
    if provider_id:
        query += '?id=%s' % provider_id
    response = await taxi_tags.put(query, data)
    assert response.status_code == expected_code

    search_result = await taxi_tags.post(
        'v1/providers/search', {'name_part': provider_id},
    )
    assert search_result.status_code == 200
    data_json = search_result.json().get('data')
    assert data_json == expected_search


def _verify_updated_tags(provider_name: str, db, tags_before: Dict):
    provider_id = tags_tools.find_provider_id(provider_name, db)
    assert provider_id

    cursor = db.cursor()
    cursor.execute(
        f'SELECT tag_name_id, provider_id, entity_id, '
        'updated, ttl, revision, entity_type '
        f'FROM state.tags WHERE provider_id={provider_id};',
    )

    rows = list(row for row in cursor)
    for row in rows:
        tag_name_id, updated = row[0], row[3]
        if tag_name_id in tags_before:
            _, last_updated = tags_before[tag_name_id]
            assert updated > last_updated


async def _verify_tag_in_cache(
        taxi_tags,
        entity_type: str,
        entity_value: str,
        tag_name: str,
        should_exist: bool,
):
    data = {'entities': [{'type': entity_type, 'id': entity_value}]}
    response = await taxi_tags.post('v1/match', data)

    assert response.status_code == 200
    json = response.json()['entities']
    assert len(json) == 1
    tags = set(json[0]['tags'])
    assert (tag_name in tags) == should_exist


def collect_provider_info(provider_name: str, db):
    provider_id = tags_tools.find_provider_id(provider_name, db, 1)
    cursor = db.cursor()
    cursor.execute(
        'SELECT t.tag_name_id, p.active, t.updated FROM '
        'state.tags as t JOIN state.providers as p ON t.provider_id=p.id '
        'WHERE provider_id={};'.format(provider_id),
    )

    rows = list(row for row in cursor)
    data = {row[0]: row[1:] for row in rows}
    return data


class Action(enum.Enum):
    Activate = 1
    Deactivate = 2


async def _check_provider_active(taxi_tags, provider_id: int, activate: bool):
    search_result = await taxi_tags.post('v1/providers/search', {})
    assert search_result.status_code == 200

    data_json = search_result.json().get('data')
    for record in data_json:
        if record.get('id') == provider_id:
            assert record.get('is_active') == activate
            return
    assert False, f'expected to find record with id={provider_id}'


def _verify_status_queue_empty(db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM service.tags_update_queue;')
    rows = list(row for row in cursor)
    assert not rows


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS[:4]),
        tags_tools.insert_tag_names(_TEST_TAG_NAMES),
        tags_tools.insert_entities([_TEST_ENTITIES[0]]),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    _TEST_TAG_NAMES[0].tag_name_id,
                    _TEST_PROVIDERS[0].provider_id,
                    _TEST_ENTITIES[0].entity_id,
                    entity_type=_TEST_ENTITIES[0].type,
                ),
                tags_tools.Tag(
                    _TEST_TAG_NAMES[1].tag_name_id,
                    _TEST_PROVIDERS[1].provider_id,
                    _TEST_ENTITIES[0].entity_id,
                    entity_type=_TEST_ENTITIES[0].type,
                ),
                tags_tools.Tag(
                    _TEST_TAG_NAMES[2].tag_name_id,
                    _TEST_PROVIDERS[2].provider_id,
                    _TEST_ENTITIES[0].entity_id,
                    entity_type=_TEST_ENTITIES[0].type,
                ),
                tags_tools.Tag(
                    _TEST_TAG_NAMES[3].tag_name_id,
                    _TEST_PROVIDERS[3].provider_id,
                    _TEST_ENTITIES[0].entity_id,
                    entity_type=_TEST_ENTITIES[0].type,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'record_index, actions',
    [
        (0, [Action.Activate, Action.Deactivate]),
        (1, [Action.Deactivate, Action.Activate]),
        (2, [Action.Activate]),
        (3, [Action.Activate, Action.Deactivate]),
    ],
)
async def test_providers_activate(
        taxi_tags, taxi_config, record_index, actions, pgsql,
):
    final_action = actions[-1]
    provider_name = _TEST_PROVIDERS[record_index].name
    tag_name = _TEST_TAG_NAMES[record_index].name

    old_data = collect_provider_info(provider_name, pgsql['tags'])

    for action in actions:
        is_activate = action == Action.Activate
        query = 'v1/providers/activation_status?id=%s' % provider_name
        response = await taxi_tags.put(query, {'activate': is_activate})
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}
        await _check_provider_active(taxi_tags, provider_name, is_activate)

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    await taxi_tags.invalidate_caches()

    _verify_updated_tags(provider_name, pgsql['tags'], old_data)
    await _verify_tag_in_cache(
        taxi_tags,
        'driver_license',
        'license_0',
        tag_name,
        final_action == Action.Activate,
    )
    _verify_status_queue_empty(pgsql['tags'])


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS[:2]),
        _insert_service_providers(
            [
                (
                    _TEST_PROVIDERS[0].provider_id,
                    _TEST_SERVICE_NAMES[:1],
                    _BASE,
                ),
                (
                    _TEST_PROVIDERS[1].provider_id,
                    _TEST_SERVICE_NAMES,
                    _AUDITED,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'provider_name', [_TEST_PROVIDERS[0].name, _TEST_PROVIDERS[1].name],
)
async def test_providers_verify(taxi_tags, provider_name):
    query = '/v1/providers/verify?id=%s' % provider_name
    response = await taxi_tags.put(query)
    assert response.status_code == 200

    search_result = await taxi_tags.post(
        'v1/providers/search',
        {
            'name_part': provider_name,
            'types': ['service'],
            'only_verified': True,
        },
    )
    assert search_result.status_code == 200
    data = search_result.json().get('data')
    provider = next((x for x in data if x.get('id') == provider_name), None)
    assert provider is not None


@pytest.mark.parametrize(
    'provider_id, expected', [(None, 400), ('', 400), ('query_0', 404)],
)
async def test_activate_bad_input(
        taxi_tags, taxi_config, provider_id, expected,
):
    query = 'v1/providers/activation_status'
    if provider_id:
        query += '?id=%s' % provider_id
    response = await taxi_tags.put(query, {'activate': True})
    assert response.status_code == expected


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(_TEST_PROVIDERS[:2]),
        _insert_service_providers(
            [(_TEST_PROVIDERS[1].provider_id, _TEST_SERVICE_NAMES, _BASE)],
        ),
    ],
)
@pytest.mark.parametrize(
    'provider_id, expected_code, expected_text',
    [
        (None, 400, 'Missing id in query'),
        ('query_0', 404, 'provider with name "query_0" was not found'),
        (
            _TEST_PROVIDERS[0].name,
            404,
            'type of provider with name "name_1000" is not equal to service',
        ),
    ],
)
async def test_verified_bad_input(
        taxi_tags, provider_id, expected_code, expected_text,
):
    query = '/v1/providers/verify'
    if provider_id:
        query += '?id=%s' % provider_id
    response = await taxi_tags.put(query)
    assert response.status_code == expected_code
    json = response.json()
    assert json == {'code': f'{expected_code}', 'message': expected_text}
