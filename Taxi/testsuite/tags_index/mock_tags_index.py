import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import flatbuffers
import pytest
# pylint: disable=import-error
from yandex.taxi.tags.index import EntitiesIndex
from yandex.taxi.tags.index import EntityTags
from yandex.taxi.tags.index import Response
from yandex.taxi.tags.snapshot import EntityTags as SnapshotEntityTags
from yandex.taxi.tags.snapshot import Response as SnapshotResponse

# Usage: @pytest.mark.tags_v2_index(
#            tags_list=[
#                ('driver_license', 'CE123123', 'tag'),
#                ('udid', 'c3sdf3dfzdf32', 'tag'),
#            ],
#            topic_relations=[
#                ('topic', 'tag1'),
#                ('topic', 'tag2'),
#            ]
#        )
#
#   If you don't specify topic_relations,
#   no topics filtering would be applied.
_V2_INDEX_MARKER = 'tags_v2_index'

# Usage: @pytest.mark.tags_index_error(
#            handler='/v2/index',
#            error_code=500,
#            error_message={'message': 'Server error', 'code': '500'}',
#        )
_ERROR_MARKER = 'tags_index_error'

_SERVICE = '/tags'
_V1_SNAPSHOT_URL = '/v1/snapshot'
_V2_INDEX_URL = '/v2/index'


class TagsIndexContext:
    def __init__(self):
        self.tags_list = []
        self.tags_relations = None
        self.entity_tags_list = []
        self.errors = {}

    def reset(self):
        self.tags_list = []
        self.tags_relations = None
        self.entity_tags_list = []
        self.errors = {}

    def set_tags_list(self, tags_list, topic_relations=None):
        self.tags_list = tags_list
        if topic_relations is not None:
            self.tags_relations = {}
            for topic, tag in topic_relations:
                self.tags_relations.setdefault(tag, set()).add(topic)

    def set_entity_tags_list(self, entity_tags_list):
        self.entity_tags_list = sorted(
            entity_tags_list, key=lambda item: item[2],
        )

    def set_error(self, handler, error_code, error_message=None):
        self.errors[handler] = {
            'code': error_code,
            'message': error_message or 'Server error',
        }

    @staticmethod
    def _build_tags_snapshot_response(builder, response_json):
        revision = response_json['revision']
        entities_tags = response_json['entities_tags']
        fbs_entities = []
        for entity_tags in entities_tags:
            entity_type = entity_tags['type']
            entity_name = entity_tags['name']
            tags = entity_tags['tags']

            fbs_entity_type = builder.CreateString(entity_type)
            fbs_entity_name = builder.CreateString(entity_name)
            fbs_tags = [builder.CreateString(tag) for tag in tags]

            SnapshotEntityTags.EntityTagsStartTagsVector(
                builder, len(fbs_tags),
            )
            for fbs_tag in fbs_tags:
                builder.PrependUOffsetTRelative(fbs_tag)
            fbs_tags = builder.EndVector(len(fbs_tags))

            SnapshotEntityTags.EntityTagsStart(builder)
            SnapshotEntityTags.EntityTagsAddType(builder, fbs_entity_type)
            SnapshotEntityTags.EntityTagsAddName(builder, fbs_entity_name)
            SnapshotEntityTags.EntityTagsAddTags(builder, fbs_tags)
            fbs_entities.append(SnapshotEntityTags.EntityTagsEnd(builder))

        SnapshotResponse.ResponseStartEntitiesTagsVector(
            builder, len(fbs_entities),
        )
        for fbs_entity in fbs_entities:
            builder.PrependUOffsetTRelative(fbs_entity)
        fbs_entities = builder.EndVector(len(fbs_entities))

        SnapshotResponse.ResponseStart(builder)
        SnapshotResponse.ResponseAddRevision(builder, revision)
        SnapshotResponse.ResponseAddEntitiesTags(builder, fbs_entities)
        response_fbs = SnapshotResponse.ResponseEnd(builder)

        return response_fbs

    def build_tags_snapshot_response(self, response_json):
        builder = flatbuffers.Builder(0)
        response_fbs = self._build_tags_snapshot_response(
            builder, response_json,
        )
        builder.Finish(response_fbs)
        return builder.Output()

    @staticmethod
    def _build_tags_index_response(builder, response_json):
        fbs_entities = []
        entities_json = response_json['entities']
        for entity_type, index in entities_json.items():
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
        entities_fbs = builder.EndVector(len(fbs_entities))

        revision = response_json['revision']
        has_more_tags = (
            response_json['has_more_tags']
            if 'has_more_tags' in response_json
            else False
        )

        Response.ResponseStart(builder)
        Response.ResponseAddRevision(builder, revision)
        Response.ResponseAddEntities(builder, entities_fbs)
        Response.ResponseAddHasMoreTags(builder, has_more_tags)
        response_fbs = Response.ResponseEnd(builder)

        return response_fbs

    def build_tags_index_response(self, response_json):
        builder = flatbuffers.Builder(0)
        response_fbs = self._build_tags_index_response(builder, response_json)
        builder.Finish(response_fbs)
        return builder.Output()

    @staticmethod
    def _parse_tags_index_response(response):
        data = {'entities': {}, 'revision': 0}

        for i in range(response.EntitiesLength()):
            entity_fbs = response.Entities(i)
            entity = entity_fbs.EntityType().decode('utf-8')
            data['entities'][entity] = {}

            for j in range(entity_fbs.ItemsLength()):
                value_fbs = entity_fbs.Items(j)
                value = value_fbs.Name().decode('utf-8')
                data['entities'][entity][value] = set()
                for k in range(value_fbs.TagsLength()):
                    tag = value_fbs.Tags(k)
                    data['entities'][entity][value].add(tag.decode('utf-8'))
        data['revision'] = response.Revision()

        return data

    def parse_tags_index_response(self, response_fbs):
        response = Response.Response.GetRootAsResponse(response_fbs, 0)
        return self._parse_tags_index_response(response)


def _pass_topics_check(
        tag: str,
        requested_topics: Optional[List[str]],
        tags_relations: Optional[Dict[str, Set[str]]],
):
    if requested_topics is None or tags_relations is None:
        return True

    return tag in tags_relations and (
        set(requested_topics) & tags_relations[tag]
    )


@pytest.fixture(name='tags_index_mocks')
def _tags_index_mocks(mockserver):
    tags_index_context = TagsIndexContext()

    @mockserver.handler(_SERVICE + _V2_INDEX_URL)
    def _mock_v2_index(request):
        error = tags_index_context.errors.get(_V2_INDEX_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )
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

        max_revision = len(tags_index_context.tags_list)

        for pos in range(newer_than, min(newer_than + limit, max_revision)):
            entity_type, entity, tag = tags_index_context.tags_list[pos]
            if entity_type in entity_types and _pass_topics_check(
                    tag=tag,
                    requested_topics=topics,
                    tags_relations=tags_index_context.tags_relations,
            ):
                tags_by_entity_type.setdefault(entity_type, dict()).setdefault(
                    entity, [],
                ).append(tag)

        response_fbs = tags_index_context.build_tags_index_response(
            {
                'entities': tags_by_entity_type,
                'revision': min(newer_than + limit, max_revision) + big_offset,
                'has_more_tags': (newer_than + limit < max_revision),
            },
        )

        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    @mockserver.handler(_SERVICE + _V1_SNAPSHOT_URL)
    def _mock_v1_snapshot(request):
        # Mimic /v2/index handler for compatibility reasons
        error = tags_index_context.errors.get(_V2_INDEX_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())

        entity_types = request_json['entity_types']
        topics = request_json.get('topics', None)
        parts_count = request_json.get('parts')
        part_no = request_json.get('part')

        # fictional_key -> {'type': 'dbid_uuid', 'name': '..", 'tags': ['t1']}
        entities_tags = {}
        for entity_tags_tuple in tags_index_context.tags_list:
            entity_type, entity, tag = entity_tags_tuple
            if entity_type in entity_types and _pass_topics_check(
                    tag=tag,
                    requested_topics=topics,
                    tags_relations=tags_index_context.tags_relations,
            ):
                key = entity_type + '/' + entity
                entities_tags.setdefault(
                    key, {'type': entity_type, 'name': entity, 'tags': []},
                ).get('tags').append(tag)

        chunk_entities_tags = []
        for i, key in enumerate(entities_tags):
            if i % parts_count == part_no:
                chunk_entities_tags.append(entities_tags[key])

        response_fbs = tags_index_context.build_tags_snapshot_response(
            {
                'revision': len(tags_index_context.tags_list) + 1000000000000,
                'entities_tags': chunk_entities_tags,
            },
        )

        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    return tags_index_context


@pytest.fixture(name='tags_index_fixture', autouse=True)
def _tags_index_fixture(tags_index_mocks, request):
    tags_index_mocks.reset()

    # For now that marker will serve both /v2/index and /v1/snapshot data
    marker = request.node.get_closest_marker(_V2_INDEX_MARKER)
    if marker:
        tags_index_mocks.set_tags_list(**marker.kwargs)

    for marker in request.node.iter_markers(_ERROR_MARKER):
        if marker.kwargs:
            tags_index_mocks.set_error(**marker.kwargs)

    yield tags_index_mocks

    tags_index_mocks.reset()


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_V2_INDEX_MARKER}: tags v2 index')
    config.addinivalue_line('markers', f'{_ERROR_MARKER}: tags index error')
