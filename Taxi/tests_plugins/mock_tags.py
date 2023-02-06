import copy
import json

import flatbuffers
import pytest

from fbs.Yandex.Taxi.Tags.Index import EntitiesIndex
from fbs.Yandex.Taxi.Tags.Index import EntityTags
from fbs.Yandex.Taxi.Tags.Index import Response

_SERVICE = '/tags'

_PASSENGER_SERVICE = '/passenger-tags'

# Usage: @pytest.mark.match_tags(
#            entity_type='car_number',
#            entity_value='CE123123',
#            entity_tags_info={
#                'tag': {
#                    'ttl': '2019-07-15T13:57:07.000+0000',
#                    'topics': ['topic'],
#                },
#                ...
#            },
#            entity_tags=['tag', ...]
#        )
_MATCH_MARKER = 'match_tags'

# Usage: @pytest.mark.tags_v2_index(
#            tags_list=[
#                ('driver_license', 'CE123123', 'tag1'),
#                ('udid', 'c3sdf3dfzdf32', 'tag2')
#            ],
#            topic_relations=[
#                ('topic', 'tag1'),
#                ('topic', 'tag2'),
#            ]
#        )
_V2_INDEX_MARKER = 'tags_v2_index'

# Usage: @pytest.mark.tags_errors(
#            handler='/v1/drivers/match/profile',
#            service=_SERVICE,
#            error_code=500,
#            error_message={'message': 'Server error', 'code': '500'}',
#        )
_ERROR_MARKER = 'tags_error'

_V1_MATCH_URL = '/v1/match'
_V1_BULK_MATCH_URL = '/v1/bulk_match'
_V2_MATCH_URL = '/v2/match'
_V2_MATCH_SINGLE_URL = '/v2/match_single'
_V3_MATCH_SINGLE_URL = '/v3/match_single'
_V1_MATCH_PROFILE_URL = '/v1/drivers/match/profile'
_V1_MATCH_PROFILES_URL = '/v1/drivers/match/profiles'
_V2_MATCH_PROFILE_URL = '/v2/drivers/match/profile'
_V2_INDEX_URL = '/v2/index'

_MAIN_ENTITIES = [
    'driver_license',
    'car_number',
    'park',
    'udid',
    'clid_uuid',
    'dbid_uuid',
    'park_car_id',
]

_PASSENGER_ENTITIES = [
    'phone',
    'phone_hash_id',
    'user_id',
    'user_phone_id',
    'personal_phone_id',
    'corp_client_id',
    'yandex_uid',
]

ENTITY_TYPES = {
    _SERVICE: _MAIN_ENTITIES,
    _PASSENGER_SERVICE: _PASSENGER_ENTITIES,
}


class TagsContext:
    def __init__(self):
        self.tags_info = {}
        self.tags_list = []
        self.tags_relations = {}
        self.errors = {}
        self.calls = {}

    def reset(self):
        self.tags_info = {}
        self.tags_list = []
        self.tags_relations = {}
        self.errors = {}
        self.calls = {}

    def set_error(
            self,
            handler,
            service=_SERVICE,
            error_code=500,
            error_message=None,
    ):
        self.errors.setdefault(service, dict())
        self.errors[service][handler] = {
            'code': error_code,
            'message': error_message or 'Server error',
        }

    def set_tags_info(
            self,
            entity_type,
            entity_value,
            entity_tags_info=None,
            entity_tags=None,
    ):
        tags_info = dict(entity_tags_info or {})
        if entity_tags:
            tags_info.update({tag: {} for tag in entity_tags})
        self.tags_info[(entity_type, entity_value)] = tags_info

    def get_tags_info(self, entity_type, entity_value, topics=None):
        tags_info = self.tags_info.get((entity_type, entity_value), {})
        if topics is not None:
            tags_info = {
                tag: info
                for tag, info in tags_info.items()
                if ('topics' in info) and (set(info['topics']) & topics)
            }
        return tags_info

    def get_tags(self, entity_type, entity_value, topics=None):
        tags_info = self.get_tags_info(entity_type, entity_value, topics)
        return set(tags_info.keys())

    def set_tags_list(self, tags_list, topic_relations=[]):
        self.tags_list = tags_list
        for topic, tag in topic_relations:
            self.tags_relations.setdefault(tag, set()).add(topic)

    def add_calls(self, handler, service=_SERVICE, calls=1):
        if service not in self.calls:
            self.calls[service] = {}
        self.calls[service][handler] = (
            self.calls[service].get(handler, 0) + calls
        )

    def times_called(self, handler=None, service=_SERVICE):
        if handler is None:
            return sum(self.calls[service].values())
        else:
            return self.calls[service].get(handler, 0)

    def has_calls(self, handler=None, service=_SERVICE):
        return bool(self.times_called(handler, service))


@pytest.fixture
def tags_mocks(mockserver):
    tags_context = TagsContext()

    def _extract_service(request):
        if request.path.startswith(_SERVICE):
            return _SERVICE
        if request.path.startswith(_PASSENGER_SERVICE):
            return _PASSENGER_SERVICE
        assert False

    def _check_entity_type(entity_type, service=_SERVICE):
        assert entity_type in ENTITY_TYPES[service]

    def _build_v2_index_response(tags_by_entity_type, revision, has_more_tags):
        builder = flatbuffers.Builder(0)

        fbs_entities = []
        for entity_type, index in tags_by_entity_type.items():
            fbs_entity_type = builder.CreateString(entity_type)

            fbs_items = []
            for entity, tags in index.items():
                fbs_entity_name = builder.CreateString(entity)

                # store tags into fbs vector
                fbs_tags = [builder.CreateString(tag) for tag in tags]
                EntityTags.EntityTagsStartTagsVector(builder, len(fbs_tags))
                for fbs_tag in fbs_tags:
                    builder.PrependUOffsetTRelative(fbs_tag)
                fbs_tags = builder.EndVector(len(fbs_tags))

                EntityTags.EntityTagsStart(builder)
                EntityTags.EntityTagsAddName(builder, fbs_entity_name)
                EntityTags.EntityTagsAddTags(builder, fbs_tags)
                fbs_items.append(EntityTags.EntityTagsEnd(builder))

            # store items into fbs vector
            EntitiesIndex.EntitiesIndexStartItemsVector(
                builder, len(fbs_items),
            )
            for fbs_item in fbs_items:
                builder.PrependUOffsetTRelative(fbs_item)
            fbs_items = builder.EndVector(len(fbs_items))

            EntitiesIndex.EntitiesIndexStart(builder)
            EntitiesIndex.EntitiesIndexAddEntityType(builder, fbs_entity_type)
            EntitiesIndex.EntitiesIndexAddItems(builder, fbs_items)
            fbs_entities.append(EntitiesIndex.EntitiesIndexEnd(builder))

        # store entities into fbs vector
        Response.ResponseStartEntitiesVector(builder, len(fbs_entities))
        for fbs_entity in fbs_entities:
            builder.PrependUOffsetTRelative(fbs_entity)
        fbs_entities = builder.EndVector(len(fbs_entities))

        Response.ResponseStart(builder)
        Response.ResponseAddRevision(builder, revision)
        Response.ResponseAddEntities(builder, fbs_entities)
        Response.ResponseAddHasMoreTags(builder, has_more_tags)
        response = Response.ResponseEnd(builder)

        builder.Finish(response)
        return builder.Output()

    @mockserver.json_handler(_SERVICE + _V1_MATCH_URL)
    def _mock_v1_match(request):
        tags_context.add_calls(_V1_MATCH_URL)
        request_json = json.loads(request.get_data())
        response = copy.deepcopy(request_json)
        for entity in response.get('entities'):
            entity_type = entity['type']
            _check_entity_type(entity_type)
            entity_value = entity['id']
            tags = tags_context.get_tags(entity_type, entity_value)
            entity['tags'] = list(tags)

        return response

    @mockserver.json_handler(_SERVICE + _V1_BULK_MATCH_URL)
    @mockserver.json_handler(_PASSENGER_SERVICE + _V1_BULK_MATCH_URL)
    def _mock_v1_bulk_match(request):
        service = _extract_service(request)

        tags_context.add_calls(_V1_BULK_MATCH_URL, service)
        request_json = json.loads(request.get_data())
        entity_type = request_json.get('entity_type')
        _check_entity_type(entity_type, service)

        response_entities = []
        for entity in request_json.get('entities'):
            tags = tags_context.get_tags(entity_type, entity)
            if tags:
                response_entities.append({'id': entity, 'tags': tags})
        return {'entities': response_entities}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_URL)
    @mockserver.json_handler(_PASSENGER_SERVICE + _V2_MATCH_URL)
    def _mock_v2_match(request):
        service = _extract_service(request)
        tags_context.add_calls(_V2_MATCH_URL, service)

        error = tags_context.errors.get(_V2_MATCH_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        topics = None
        if 'topics' in request_json:
            topics = set(request_json['topics'])

        response_entities = []
        for entity in request_json.get('entities'):
            entity_id = entity.get('id')
            response_tags = set()
            for match_item in entity.get('match'):
                entity_type = match_item['type']
                _check_entity_type(entity_type, service)
                entity_value = match_item['value']
                tags = tags_context.get_tags(entity_type, entity_value, topics)
                response_tags.update(tags)
            if response_tags:
                response_entities.append(
                    {'id': entity_id, 'tags': list(response_tags)},
                )
        return {'entities': response_entities}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_SINGLE_URL)
    @mockserver.json_handler(_PASSENGER_SERVICE + _V2_MATCH_SINGLE_URL)
    def _mock_v2_match_single(request):
        service = _extract_service(request)
        tags_context.add_calls(_V2_MATCH_SINGLE_URL, service)

        error = tags_context.errors.get(_V2_MATCH_SINGLE_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        match = request_json['match']

        topics = None
        if 'topics' in request_json:
            topics = set(request_json['topics'])

        response_tags = set()
        for match_item in match:
            entity_type = match_item['type']
            _check_entity_type(entity_type, service)
            entity_value = match_item['value']
            tags = tags_context.get_tags(entity_type, entity_value, topics)
            response_tags.update(tags)
        return {'tags': list(response_tags)}

    @mockserver.json_handler(_SERVICE + _V3_MATCH_SINGLE_URL)
    def _mock_v3_match_single(request):
        tags_context.add_calls(_V3_MATCH_SINGLE_URL)
        error = tags_context.errors.get(_V3_MATCH_SINGLE_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        match = request_json['match']
        topics = None
        if 'topics' in request_json:
            topics = set(request_json['topics'])

        response_tags = dict()
        for match_item in match:
            entity_type = match_item['type']
            _check_entity_type(entity_type)
            entity_value = match_item['value']
            tags = tags_context.get_tags_info(
                entity_type, entity_value, topics,
            )
            response_tags.update(tags)
        return {'tags': response_tags}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILE_URL)
    def _mock_v1_match_profile(request):
        tags_context.add_calls(_V1_MATCH_PROFILE_URL)
        error = tags_context.errors.get(_V1_MATCH_PROFILE_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        dbid_uuid = None
        topics = None
        if request.method == 'GET':
            dbid_uuid = request.args['dbid'] + '_' + request.args['uuid']
        elif request.method == 'POST':
            request_json = json.loads(request.get_data())
            dbid_uuid = request_json['dbid'] + '_' + request_json['uuid']
            topics = (
                request_json['topics'] if 'topics' in request_json else None
            )
        tags = tags_context.get_tags('dbid_uuid', dbid_uuid, topics)
        return {'tags': list(tags)}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILES_URL)
    def _mock_v1_match_profiles(request):
        tags_context.add_calls(_V1_MATCH_PROFILES_URL)
        error = tags_context.errors.get(_V1_MATCH_PROFILES_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        topics = request_json.get('topics')
        response_drivers = []
        for driver in request_json['drivers']:
            dbid = driver['dbid']
            uuid = driver['uuid']
            dbid_uuid = dbid + '_' + uuid
            tags = tags_context.get_tags('dbid_uuid', dbid_uuid, topics)
            response_drivers.append(
                {'dbid': dbid, 'uuid': uuid, 'tags': list(tags)},
            )

        return {'drivers': response_drivers}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_PROFILE_URL)
    def _mock_v2_match_profile(request):
        tags_context.add_calls(_V2_MATCH_PROFILE_URL)
        request_json = json.loads(request.get_data())
        dbid_uuid = request_json['dbid'] + '_' + request_json['uuid']
        topics = request_json['topics'] if 'topics' in request_json else None

        response_tags = tags_context.get_tags_info(
            'dbid_uuid', dbid_uuid, topics,
        )
        return {'tags': response_tags}

    @mockserver.handler(_SERVICE + _V2_INDEX_URL)
    def _mock_v2_index(request):
        tags_context.add_calls(_V2_INDEX_URL)
        request_json = json.loads(request.get_data())

        entity_types = request_json['entity_types']
        topics = request_json.get('topics', None)
        request_range = request_json.get('range', {})
        newer_than = request_range.get('newer_than')
        limit = request_range.get('limit', 1)

        tags_by_entity_type = {}
        big_offset = 1000000000000
        if newer_than >= big_offset:
            newer_than -= big_offset

        max_revision = len(tags_context.tags_list)
        for pos in range(newer_than, min(newer_than + limit, max_revision)):
            entity_type, entity, tag = tags_context.tags_list[pos]
            if (entity_type in entity_types) and (
                    (topics is None)
                    or (
                        (tag in tags_context.tags_relations)
                        and (set(topics) & tags_context.tags_relations[tag])
                    )
            ):
                tags_by_entity_type.setdefault(entity_type, dict()).setdefault(
                    entity, [],
                ).append(tag)

        data = _build_v2_index_response(
            tags_by_entity_type=tags_by_entity_type,
            revision=min(newer_than + limit, max_revision) + big_offset,
            has_more_tags=(newer_than + limit < max_revision),
        )

        return mockserver.make_response(
            data, content_type='application/x-flatbuffers; charset=utf-8',
        )

    return tags_context


@pytest.fixture(name='tags_fixture', autouse=True)
def tags_fixture(tags_mocks, request):
    tags_mocks.reset()

    if request.node.get_marker(_MATCH_MARKER):
        # If not set, entities will have no tags specified
        for req in request.node.get_marker(_MATCH_MARKER):
            if req.kwargs:
                tags_mocks.set_tags_info(**req.kwargs)

    if request.node.get_marker(_V2_INDEX_MARKER):
        req = request.node.get_marker(_V2_INDEX_MARKER)
        tags_mocks.set_tags_list(**req.kwargs)

    if request.node.get_marker(_ERROR_MARKER):
        for req in request.node.get_marker(_ERROR_MARKER):
            if req.kwargs:
                tags_mocks.set_error(**req.kwargs)

    yield tags_mocks

    tags_mocks.reset()
