import collections

import pytest


@pytest.fixture(name='grocery_tags', autouse=True)
def mock_grocery_tags(mockserver):
    tags_by_phone_id = collections.defaultdict(list)
    tags_by_yandex_uid = collections.defaultdict(list)
    tags_by_store_item_id = collections.defaultdict(list)

    class Context:
        def __init__(self):
            self.response_with_error = False

        def add_tag(self, *, personal_phone_id, tag):
            if tag not in tags_by_phone_id[personal_phone_id]:
                tags_by_phone_id[personal_phone_id].append(tag)

        def add_tags(self, *, personal_phone_id, tags):
            for tag in tags:
                self.add_tag(personal_phone_id=personal_phone_id, tag=tag)

        def add_yandex_uid_tag(self, *, yandex_uid, tag):
            if tag not in tags_by_yandex_uid[yandex_uid]:
                tags_by_yandex_uid[yandex_uid].append(tag)

        def add_store_item_id_tag(self, *, store_item_id, tag):
            if tag not in tags_by_store_item_id:
                tags_by_store_item_id[store_item_id].append(tag)

        def add_store_item_id_tags(self, *, store_item_id, tags):
            for tag in tags:
                self.add_store_item_id_tag(
                    store_item_id=store_item_id, tag=tag,
                )

        def set_response_with_error(self, *, is_error):
            self.response_with_error = is_error

        def bulk_match_times_called(self):
            return mock_bulk_match.times_called

        def v2_match_times_called(self):
            return mock_v2_match.times_called

        def flush_all(self):
            mock_bulk_match.flush()
            mock_v1_match.flush()
            mock_v2_match.flush()
            mock_v2_match_single.flush()

    context = Context()

    @mockserver.json_handler('/grocery-tags/v1/bulk_match')
    def mock_bulk_match(request):
        if context.response_with_error:
            return mockserver.make_response('Error', 500)
        entities = []
        if request.json['entity_type'] == 'personal_phone_id':
            for request_phone_id in request.json['entities']:
                if request_phone_id in tags_by_phone_id:
                    entities.append(
                        {
                            'id': request_phone_id,
                            'tags': tags_by_phone_id[request_phone_id],
                        },
                    )
        elif request.json['entity_type'] == 'yandex_uid':
            for request_yandex_uid in request.json['entities']:
                if request_yandex_uid in tags_by_yandex_uid:
                    entities.append(
                        {
                            'id': request_yandex_uid,
                            'tags': tags_by_yandex_uid[request_yandex_uid],
                        },
                    )
        elif request.json['entity_type'] == 'store_item_id':
            for request_store_item_id in request.json['entities']:
                if request_store_item_id in tags_by_store_item_id:
                    entities.append(
                        {
                            'id': request_store_item_id,
                            'tags': tags_by_store_item_id[
                                request_store_item_id
                            ],
                        },
                    )

        return {'entities': entities}

    @mockserver.json_handler('/grocery-tags/v1/match')
    def mock_v1_match(request):
        if context.response_with_error:
            return mockserver.make_response('Error', 500)
        entities = []
        for entity in request.json['entities']:
            if entity['type'] == 'personal_phone_id':
                entity_phone_id = entity['id']
                if entity_phone_id in tags_by_phone_id:
                    entities.append(
                        {
                            'id': entity_phone_id,
                            'tags': tags_by_phone_id[entity_phone_id],
                            'type': 'personal_phone_id',
                        },
                    )
            elif entity['type'] == 'store_item_id':
                store_item_id = entity['id']
                if store_item_id in tags_by_store_item_id:
                    entities.append(
                        {
                            'id': store_item_id,
                            'tags': tags_by_store_item_id[store_item_id],
                            'type': 'store_item_id',
                        },
                    )
        return {'entities': entities}

    @mockserver.json_handler('/grocery-tags/v2/match')
    def mock_v2_match(request):
        if context.response_with_error:
            return mockserver.make_response('Error', 500)
        entities = []
        for entity in request.json['entities']:
            entity_type = entity['match'][0]['type']
            entity_value = entity['match'][0]['value']
            entity_id = entity['id']

            response_tags = None
            if (
                    entity_type == 'personal_phone_id'
                    and entity_value in tags_by_phone_id
            ):
                response_tags = tags_by_phone_id[entity_value]
            elif (
                entity_type == 'store_item_id'
                and entity_value in tags_by_store_item_id
            ):
                response_tags = tags_by_store_item_id[entity_value]

            if response_tags is not None:
                entities.append({'id': entity_id, 'tags': response_tags})
        return {'entities': entities}

    @mockserver.json_handler('/grocery-tags/v2/match_single')
    def mock_v2_match_single(request):
        if context.response_with_error:
            return mockserver.make_response('Error', 500)
        entity_type = request.json['match'][0]['type']
        entity_value = request.json['match'][0]['value']

        response_tags = None
        if (
                entity_type == 'personal_phone_id'
                and entity_value in tags_by_phone_id
        ):
            response_tags = tags_by_phone_id[entity_value]
        elif (
            entity_type == 'store_item_id'
            and entity_value in tags_by_store_item_id
        ):
            response_tags = tags_by_store_item_id[entity_value]

        return {'tags': response_tags}

    return context
