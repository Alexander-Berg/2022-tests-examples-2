import copy
import json
from typing import Optional

# pylint: disable=import-error
from fbs.tags.handlers.v1_entity_index import EntityUpdateInfo
from fbs.tags.handlers.v1_entity_index import Response as EntityResponse
from fbs.tags.handlers.v2_internal_match_fbs import EntityTags
from fbs.tags.handlers.v2_internal_match_fbs import Response as V2FbsResponse
from fbs.tags.handlers.v2_match_fbs import Entity
from fbs.tags.handlers.v2_match_fbs import GroupTags
from fbs.tags.handlers.v2_match_fbs import Match
from fbs.tags.handlers.v2_match_fbs import Request
from fbs.tags.handlers.v2_match_fbs import Response
import flatbuffers
import pytest

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

# Usage: @pytest.mark.tags_v1_entity_index(
#            entity_tags_list=[
#                ('park', 'park0', 1),
#                ('udid', 'udid0', 32168),
#                ('dbid_uuid', 'dbid0_uuid0', 32169),
#                ('dbid_uuid', 'dbid0_uuid1', 32170),
#                ('park', 'park0', 100000),
#            ],
#            last_processed_revision=100000, # can be omitted
#        )
_V1_ENTITY_INDEX_MARKER = 'tags_v1_entity_index'

_V1_TOPICS_RELATIONS_MARKER = 'tags_topics_relations'
# Usage: @pytest.mark.tags_topics_relations(
#            topics_relations={
#                'topic0': ['tag1', 'tag2', 'tag3'],
#                'topic1': ['tag1', 'tag4'],
#            },
#        )

# Usage: @pytest.mark.tags_error(
#            handler='/v1/match',
#            error_code=500,
#            error_message={'message': 'Server error', 'code': '500'}',
#        )
_ERROR_MARKER = 'tags_error'

_SERVICE = '/tags'
_V1_MATCH_URL = '/v1/match'
_V1_BULK_MATCH_URL = '/v1/bulk_match'
_V2_MATCH_URL = '/v2/match'
_V2_MATCH_FBS_URL = '/v2/match_fbs'
_V2_INTERNAL_MATCH_FBS_URL = '/v2/internal/match_fbs'
_V1_ENTITY_INDEX_URL = '/v1/entity_index'
_V1_INTERNAL_MATCH_URL = '/v1/internal/match'
_V1_INTERNAL_MATCH_FBS_URL = '/v1/internal/match_fbs'
_V2_MATCH_SINGLE_URL = '/v2/match_single'
_V3_MATCH_SINGLE_URL = '/v3/match_single'
_V1_MATCH_PROFILE_URL = '/v1/drivers/match/profile'
_V1_MATCH_PROFILES_URL = '/v1/drivers/match/profiles'
_V2_MATCH_PROFILE_URL = '/v2/drivers/match/profile'
_V1_TOPICS_RELATIONS_URL = '/v1/topics_relations'


class TagsContext:
    def __init__(self):
        self.tags_info = {}
        self.topics_relations = {}
        self.entity_tags_list = []
        self.last_processed_revision = None
        self.has_more = None
        self.errors = {}
        self.calls = {}

    def reset(self):
        self.tags_info = {}
        self.topics_relations = {}
        self.entity_tags_list = []
        self.last_processed_revision = None
        self.has_more = None
        self.errors = {}
        self.calls = {}

    def set_error(self, handler, error_code, error_message=None, call_count=0):
        self.errors[handler] = {
            'code': error_code,
            'message': error_message or 'Server error',
            'call_count': call_count,
        }

    def check_error(self, handler):
        if handler in self.errors:
            error = self.errors[handler]
            if error['call_count'] <= self.calls.get(handler, 0):
                return error
        return None

    def set_entity_tags_list(
            self,
            entity_tags_list,
            last_processed_revision: Optional[int] = None,
    ):
        self.entity_tags_list = sorted(
            entity_tags_list, key=lambda item: item[2],
        )
        self.last_processed_revision = last_processed_revision

    def set_topics_relations(self, topics_relations):
        self.topics_relations = topics_relations

    def get_topic_relations(self, topic):
        if topic in self.topics_relations:
            return self.topics_relations[topic]
        return None

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

    def add_calls(self, handler, calls=1):
        self.calls[handler] = self.calls.get(handler, 0) + calls

    def has_calls(self, handler=None):
        times_called = 0
        if handler is None:
            times_called = sum(self.calls.values())
        else:
            times_called = self.calls.get(handler, 0)
        return bool(times_called)

    def pack_v2_match_fbs_request(self, request_json):
        builder = flatbuffers.Builder(0)

        topics = request_json['topics'] if 'topics' in request_json else []
        fbs_topics = [builder.CreateString(topic) for topic in topics]
        Request.RequestStartTopicsVector(builder, len(fbs_topics))
        for fbs_topic in reversed(fbs_topics):
            builder.PrependUOffsetTRelative(fbs_topic)
        fbs_topics = builder.EndVector(len(fbs_topics))

        entities = (
            request_json['entities'] if 'entities' in request_json else []
        )
        fbs_entities = []
        for entity in entities:
            fbs_matches = []
            for match in entity['match']:
                fbs_type = builder.CreateString(match['type'])
                fbs_value = builder.CreateString(match['value'])
                Match.MatchStart(builder)
                Match.MatchAddType(builder, fbs_type)
                Match.MatchAddValue(builder, fbs_value)
                fbs_matches.append(Match.MatchEnd(builder))
            Entity.EntityStartMatchVector(builder, len(fbs_matches))
            for fbs_match in reversed(fbs_matches):
                builder.PrependUOffsetTRelative(fbs_match)
            fbs_matches = builder.EndVector(len(fbs_matches))

            fbs_id = builder.CreateString(entity['id'])
            Entity.EntityStart(builder)
            Entity.EntityAddId(builder, fbs_id)
            Entity.EntityAddMatch(builder, fbs_matches)
            fbs_entities.append(Entity.EntityEnd(builder))

        Request.RequestStartEntitiesVector(builder, len(fbs_entities))
        for fbs_entity in reversed(fbs_entities):
            builder.PrependUOffsetTRelative(fbs_entity)
        fbs_entities = builder.EndVector(len(fbs_entities))

        Request.RequestStart(builder)
        Request.RequestAddTopics(builder, fbs_topics)
        Request.RequestAddEntities(builder, fbs_entities)
        request_fbs = Request.RequestEnd(builder)
        builder.Finish(request_fbs)
        return builder.Output()

    def unpack_v2_match_fbs_request(self, data):
        root = Request.Request.GetRootAsRequest(data, 0)
        entities = []
        for i in range(root.EntitiesLength()):
            entity = root.Entities(i)
            entity_id = entity.Id().decode('utf-8') if entity.Id() else ''
            matches = []
            for j in range(entity.MatchLength()):
                match = entity.Match(j)
                matches.append(
                    {
                        'type': match.Type().decode('utf-8'),
                        'value': match.Value().decode('utf-8'),
                    },
                )
            entities.append({'id': entity_id, 'match': matches})

        request_json = {'entities': entities}
        if root.TopicsLength():
            topics = []
            for i in range(root.TopicsLength()):
                topics.append(root.Topics(i).decode('utf-8'))
            request_json['topics'] = topics
        return request_json

    def pack_v2_match_fbs_response(self, response_json):
        builder = flatbuffers.Builder(0)

        entities = (
            response_json['entities'] if 'entities' in response_json else []
        )
        fbs_entities = []
        for entity in entities:
            fbs_id = builder.CreateString(entity['id'])
            fbs_tags = []
            for tag in entity['tags']:
                # todo: it's CreateSharedString in C++ code
                fbs_tags.append(builder.CreateString(tag))

            GroupTags.GroupTagsStartTagsVector(builder, len(fbs_tags))
            for fbs_tag in reversed(fbs_tags):
                builder.PrependUOffsetTRelative(fbs_tag)
            fbs_tags = builder.EndVector(len(fbs_tags))

            GroupTags.GroupTagsStart(builder)
            GroupTags.GroupTagsAddId(builder, fbs_id)
            GroupTags.GroupTagsAddTags(builder, fbs_tags)
            fbs_entities.append(GroupTags.GroupTagsEnd(builder))

        Response.ResponseStartEntitiesVector(builder, len(fbs_entities))
        for fbs_entity in reversed(fbs_entities):
            builder.PrependUOffsetTRelative(fbs_entity)
        fbs_entities = builder.EndVector(len(fbs_entities))

        Response.ResponseStart(builder)
        Response.ResponseAddEntities(builder, fbs_entities)
        response_fbs = Response.ResponseEnd(builder)
        builder.Finish(response_fbs)

        return builder.Output()

    def unpack_v2_match_fbs_response(self, data):
        root = Response.Response.GetRootAsResponse(data, 0)
        entities = []
        for i in range(root.EntitiesLength()):
            entity = root.Entities(i)
            entity_id = entity.Id().decode('utf-8') if entity.Id() else ''
            tags = [
                entity.Tags(j).decode('utf-8')
                for j in range(entity.TagsLength())
            ]

            entities.append({'id': entity_id, 'tags': tags})
        return {'entities': entities}

    def create_v2_int_match_response(self, request_json):
        builder = flatbuffers.Builder(0)
        fbs_entities = []
        for topic in request_json['topics']:
            for entity_type, entity_ids in request_json['match'].items():
                for entity_id in entity_ids:
                    fbs_id = builder.CreateString(entity_id)
                    fbs_type = builder.CreateString(entity_type)
                    fbs_topic = builder.CreateString(topic)
                    fbs_tags = []
                    tags = self.get_tags(entity_type, entity_id, set([topic]))
                    for tag in tags:
                        fbs_tags.append(builder.CreateString(tag))

                    EntityTags.EntityTagsStartTagsVector(
                        builder, len(fbs_tags),
                    )
                    for fbs_tag in reversed(fbs_tags):
                        builder.PrependUOffsetTRelative(fbs_tag)
                    fbs_tags = builder.EndVector(len(fbs_tags))

                    EntityTags.EntityTagsStart(builder)
                    EntityTags.EntityTagsAddId(builder, fbs_id)
                    EntityTags.EntityTagsAddType(builder, fbs_type)
                    EntityTags.EntityTagsAddTopic(builder, fbs_topic)
                    EntityTags.EntityTagsAddTags(builder, fbs_tags)
                    fbs_entities.append(EntityTags.EntityTagsEnd(builder))

        V2FbsResponse.ResponseStartEntitiesVector(builder, len(fbs_entities))
        for fbs_entity in reversed(fbs_entities):
            builder.PrependUOffsetTRelative(fbs_entity)
        fbs_entities = builder.EndVector(len(fbs_entities))

        V2FbsResponse.ResponseStart(builder)
        V2FbsResponse.ResponseAddEntities(builder, fbs_entities)
        response_fbs = V2FbsResponse.ResponseEnd(builder)
        builder.Finish(response_fbs)

        return builder.Output()

    def pack_v1_entity_index_response(self, response_json):
        builder = flatbuffers.Builder(0)
        fbs_entities = []
        last_processed_revision = response_json['last_processed_revision']
        has_more = response_json['has_more']
        entities_json = response_json['entities']
        for entity in entities_json:
            fbs_entity_type = builder.CreateString(entity['type'])
            fbs_entity_name = builder.CreateString(entity['name'])

            EntityUpdateInfo.EntityUpdateInfoStart(builder)
            EntityUpdateInfo.EntityUpdateInfoAddType(builder, fbs_entity_type)
            EntityUpdateInfo.EntityUpdateInfoAddName(builder, fbs_entity_name)
            EntityUpdateInfo.EntityUpdateInfoAddRevision(
                builder, entity['revision'],
            )
            EntityUpdateInfo.EntityUpdateInfoAddUpdated(
                builder, entity['updated'],
            )
            fbs_entities.append(EntityUpdateInfo.EntityUpdateInfoEnd(builder))

        # store entities into fbs vector
        EntityResponse.ResponseStartEntitiesVector(builder, len(fbs_entities))
        for fbs_entity in reversed(fbs_entities):
            builder.PrependUOffsetTRelative(fbs_entity)
        entities_fbs = builder.EndVector(len(fbs_entities))

        EntityResponse.ResponseStart(builder)
        EntityResponse.ResponseAddEntities(builder, entities_fbs)
        if last_processed_revision is not None:
            EntityResponse.ResponseAddLastProcessedRevision(
                builder, last_processed_revision,
            )
        EntityResponse.ResponseAddHasMore(builder, has_more)
        response_fbs = EntityResponse.ResponseEnd(builder)

        builder.Finish(response_fbs)
        return builder.Output()

    def unpack_v1_entity_index_response(self, data):
        root = EntityResponse.Response.GetRootAsResponse(data, 0)
        entities = []
        for i in range(root.EntitiesLength()):
            entity_fbs = root.Entities(i)
            entities.append(
                {
                    'type': entity_fbs.Type().decode('utf-8'),
                    'name': entity_fbs.Name().decode('utf-8'),
                    'revision': entity_fbs.Revision(),
                },
            )
        data = {
            'entities': entities,
            'last_processed_revision': root.LastProcessedRevision(),
            'has_more': root.HasMore(),
        }
        return data


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_MATCH_MARKER}: match tags')
    config.addinivalue_line(
        'markers', f'{_V1_ENTITY_INDEX_MARKER}: entity index',
    )
    config.addinivalue_line(
        'markers', f'{_V1_TOPICS_RELATIONS_MARKER}: topics relarions',
    )
    config.addinivalue_line('markers', f'{_ERROR_MARKER}: tags error')


@pytest.fixture(name='tags_mocks')
def _tags_mocks(mockserver):
    tags_context = TagsContext()

    def _call_match(request_json, return_empty_entity):
        topics = None
        if 'topics' in request_json:
            topics = set(request_json['topics'])

        response_entities = []
        for entity in request_json.get('entities'):
            entity_id = entity.get('id')
            response_tags = set()
            for match_item in entity.get('match'):
                enitity_type = match_item['type']
                enitity_value = match_item['value']
                tags = tags_context.get_tags(
                    enitity_type, enitity_value, topics,
                )
                response_tags.update(tags)
            if response_tags or return_empty_entity:
                response_entities.append(
                    {'id': entity_id, 'tags': list(response_tags)},
                )
        return {'entities': response_entities}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_URL)
    def _mock_v1_match(request):
        tags_context.add_calls(_V1_MATCH_URL)
        request_json = json.loads(request.get_data())
        response = copy.deepcopy(request_json)
        for entity in response.get('entities'):
            enitity_type = entity['type']
            enitity_value = entity['id']
            tags = tags_context.get_tags(enitity_type, enitity_value)
            entity['tags'] = list(tags)

        return response

    @mockserver.json_handler(_SERVICE + _V1_BULK_MATCH_URL)
    def _mock_v1_bulk_match(request):
        tags_context.add_calls(_V1_BULK_MATCH_URL)
        request_json = json.loads(request.get_data())
        entity_type = request_json.get('entity_type')
        response_entities = []
        for entity in request_json.get('entities'):
            tags = tags_context.get_tags(entity_type, entity)
            if tags:
                response_entities.append({'id': entity, 'tags': tags})
        return {'entities': response_entities}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_URL)
    @mockserver.json_handler(_SERVICE + _V1_INTERNAL_MATCH_URL)
    def _mock_match(request):
        offset = request.url.find(_SERVICE)
        url = request.url[offset + len(_SERVICE) :]
        tags_context.add_calls(url)
        error = tags_context.check_error(url)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        return _call_match(
            json.loads(request.get_data()), return_empty_entity=False,
        )

    @mockserver.json_handler(_SERVICE + _V2_MATCH_FBS_URL)
    @mockserver.json_handler(_SERVICE + _V1_INTERNAL_MATCH_FBS_URL)
    def _mock_match_fbs(request):
        begin = request.url.find(_SERVICE) + len(_SERVICE)
        end = request.url.find('?', begin)
        url = request.url[begin:] if end == -1 else request.url[begin:end]
        tags_context.add_calls(url)
        error = tags_context.check_error(url)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = tags_context.unpack_v2_match_fbs_request(
            request.get_data(),
        )
        response_json = _call_match(request_json, return_empty_entity=True)

        return mockserver.make_response(
            tags_context.pack_v2_match_fbs_response(response_json),
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    @mockserver.json_handler(_SERVICE + _V2_INTERNAL_MATCH_FBS_URL)
    def _mock_v2_internal_match_fbs(request):
        begin = request.url.find(_SERVICE) + len(_SERVICE)
        end = request.url.find('?', begin)
        url = request.url[begin:] if end == -1 else request.url[begin:end]
        tags_context.add_calls(url)
        error = tags_context.check_error(url)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        return mockserver.make_response(
            tags_context.create_v2_int_match_response(
                json.loads(request.get_data()),
            ),
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    @mockserver.json_handler(_SERVICE + _V2_MATCH_SINGLE_URL)
    def _mock_v2_match_single(request):
        tags_context.add_calls(_V2_MATCH_SINGLE_URL)
        error = tags_context.check_error(_V2_MATCH_SINGLE_URL)
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
            enitity_type = match_item['type']
            enitity_value = match_item['value']
            tags = tags_context.get_tags(enitity_type, enitity_value, topics)
            response_tags.update(tags)
        return {'tags': list(response_tags)}

    @mockserver.json_handler(_SERVICE + _V3_MATCH_SINGLE_URL)
    def _mock_v3_match_single(request):
        tags_context.add_calls(_V3_MATCH_SINGLE_URL)
        error = tags_context.check_error(_V3_MATCH_SINGLE_URL)
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
            enitity_type = match_item['type']
            enitity_value = match_item['value']
            tags = tags_context.get_tags_info(
                enitity_type, enitity_value, topics,
            )
            response_tags.update(tags)
        return {'tags': response_tags}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILE_URL)
    def _mock_v1_match_profile(request):
        tags_context.add_calls(_V1_MATCH_PROFILE_URL)
        error = tags_context.check_error(_V1_MATCH_PROFILE_URL)
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
        error = tags_context.check_error(_V1_MATCH_PROFILES_URL)
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

    @mockserver.handler(_SERVICE + _V1_ENTITY_INDEX_URL)
    def _mock_v1_entity_index(request):
        tags_context.add_calls(_V1_ENTITY_INDEX_URL)
        error = tags_context.check_error(_V1_ENTITY_INDEX_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())

        entity_types = request_json['entity_types']
        request_range = request_json.get('range', {})
        newer_than = request_range.get('newer_than')
        limit = request_range.get('limit', 1)

        entities = []
        has_more = False
        last_processed_revision = None
        for entity_type, name, revision in tags_context.entity_tags_list:
            if revision > newer_than and entity_type in entity_types:
                entities.append(
                    {
                        'type': entity_type,
                        'name': name,
                        'revision': revision,
                        # revision used just to simplify integration
                        'updated': revision,
                    },
                )
                if (
                        last_processed_revision is None
                        or last_processed_revision < revision
                ):
                    last_processed_revision = revision
                if len(entities) >= limit:
                    has_more = True
                    break

        response_fbs = tags_context.pack_v1_entity_index_response(
            {
                'entities': entities,
                'last_processed_revision': (
                    tags_context.last_processed_revision
                    or last_processed_revision
                ),
                'has_more': has_more,
            },
        )

        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    @mockserver.json_handler(_SERVICE + _V1_TOPICS_RELATIONS_URL)
    def _mock_v1_topics_relations(request):
        tags_context.add_calls(_V1_TOPICS_RELATIONS_URL)
        error = tags_context.check_error(_V1_TOPICS_RELATIONS_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        response = {}
        for topic in request_json['topics']:
            tags = tags_context.get_topic_relations(topic)
            if tags is None:
                return mockserver.make_response(
                    json={'message': 'Bad request'}, status=400,
                )
            response[topic] = tags
        return response

    return tags_context


@pytest.fixture(name='tags_fixture', autouse=True)
def _tags_fixture(tags_mocks, request):
    tags_mocks.reset()

    # If not set, entities will have no tags specified
    for marker in request.node.iter_markers(_MATCH_MARKER):
        if marker.kwargs:
            tags_mocks.set_tags_info(**marker.kwargs)

    marker = request.node.get_closest_marker(_V1_ENTITY_INDEX_MARKER)
    if marker:
        tags_mocks.set_entity_tags_list(**marker.kwargs)

    marker = request.node.get_closest_marker(_V1_TOPICS_RELATIONS_MARKER)
    if marker:
        tags_mocks.set_topics_relations(**marker.kwargs)

    for marker in request.node.iter_markers(_ERROR_MARKER):
        if marker.kwargs:
            tags_mocks.set_error(**marker.kwargs)

    yield tags_mocks

    tags_mocks.reset()
