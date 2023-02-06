import dataclasses
import json
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_tags import common


_TOPICS = {'tag1': ['topic1'], 'tag2': ['topic2', 'topic3'], 'tag3': []}

_PROVIDERS = [
    {'name': 'provider0', 'type': 'service'},
    {'name': 'provider1', 'type': 'yql'},
    {'name': 'provider2', 'type': 'manual'},
]

_ENTITIES = [
    # profile dbid1_uuid1
    {'type': 'park', 'value': 'dbid1'},
    {'type': 'park_car_id', 'value': 'dbid1_car1'},
    {'type': 'udid', 'value': 'udid1'},
    {'type': 'dbid_uuid', 'value': 'dbid1_uuid1'},
    # profile dbid2_uuid1
    {'type': 'park', 'value': 'dbid2'},
    {'type': 'park_car_id', 'value': 'dbid2_car3'},
    {'type': 'dbid_uuid', 'value': 'dbid2_uuid1'},
    # profile dbid1_uuid3
    {'type': 'park', 'value': 'dbid1'},
    {'type': 'dbid_uuid', 'value': 'dbid1_uuid3'},
]
_DBID1_UUID1_ENTITIES = _ENTITIES[0:4]
_DBID2_UUID1_ENTITIES = _ENTITIES[4:7]
_DBID1_UUID3_ENTITIES = _ENTITIES[7:9]


@dataclasses.dataclass
class Entry:
    provider: Dict[str, Any]
    ttl: Optional[str] = None
    entity: Optional[Dict[str, Any]] = None


def _remove_nullable_keys(some_dict: Dict[str, Any]):
    return {k: v for k, v in some_dict.items() if v is not None}


@pytest.mark.unique_drivers(stream=common.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.parametrize(
    'park_id, profile_id, tags_request, tags_response',
    [
        pytest.param(
            'dbid1',
            'uuid1',
            _DBID1_UUID1_ENTITIES,
            [
                {'tag2': [Entry(_PROVIDERS[1])]},
                {'tag1': [Entry(_PROVIDERS[2], '2019-11-08T14:45:32+0000')]},
                {'tag2': [Entry(_PROVIDERS[2])]},
                {'tag3': [Entry(_PROVIDERS[0], '2019-11-09T12:45:32+0000')]},
            ],
            id='all entities',
        ),
        pytest.param(
            'dbid2',
            'uuid1',
            _DBID2_UUID1_ENTITIES,
            [{}, {}, {}],
            id='no unique driver id',
        ),
        pytest.param(
            'dbid1',
            'uuid3',
            _DBID1_UUID3_ENTITIES,
            [
                {
                    'tag3': [
                        Entry(_PROVIDERS[0], '2019-11-08T15:45:32+0000'),
                        Entry(_PROVIDERS[1], '2019-11-08T13:45:32+0000'),
                        Entry(_PROVIDERS[2], '2019-12-08T13:45:32+0000'),
                    ],
                },
                {},
            ],
            id='park & profile only',
        ),
    ],
)
async def test_tags_diagnostics(
        taxi_driver_tags,
        mockserver,
        park_id: str,
        profile_id: str,
        tags_request,
        tags_response,
):
    @mockserver.json_handler('tags/v1/admin/tags/match_diagnostics')
    def _match_diagnostics_handler(request):
        request_json = json.loads(request.get_data())
        assert request_json['entities'] == tags_request
        # generate response
        entities = []
        for entity in tags_response:
            tags = {}
            for tag, entries in entity.items():
                tags[tag] = {
                    'topics': _TOPICS[tag],
                    'entries': [
                        _remove_nullable_keys(dataclasses.asdict(entry))
                        for entry in entries
                    ],
                }
            entities.append({'tags': tags})
        return {'entities': entities}

    response = await taxi_driver_tags.get(
        f'admin/v1/tags-diagnostics?park_id={park_id}&profile_id={profile_id}',
    )
    assert response.status_code == 200
    data = response.json()

    # sort topics list
    for diagnostic in data['tags'].values():
        diagnostic['topics'].sort()

    # generate expected response
    expected_tags: Dict[str, Any] = {}
    for entity, tags in zip(tags_request, tags_response):
        for tag, entries in tags.items():
            init_value = {'topics': _TOPICS[tag], 'entries': []}
            expected_tags.setdefault(tag, init_value)
            for entry in entries:
                entry.entity = entity
                expected_tags[tag]['entries'].append(
                    _remove_nullable_keys(dataclasses.asdict(entry)),
                )
    for diagnostic in expected_tags.values():
        ttl_entries = [
            entry for entry in diagnostic['entries'] if 'ttl' in entry
        ]
        if ttl_entries == diagnostic['entries']:
            diagnostic['ttl'] = max(
                ttl_entries, key=lambda entry: entry['ttl'],
            )['ttl']

    assert data['tags'] == expected_tags
