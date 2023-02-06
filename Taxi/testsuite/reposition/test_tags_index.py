import copy
import datetime
import os
import shutil
import time

import flatbuffers
import pytest

from fbs.Yandex.Taxi.Tags.Index import Dump
from fbs.Yandex.Taxi.Tags.Index import EntitiesIndex
from fbs.Yandex.Taxi.Tags.Index import EntityTags
from fbs.Yandex.Taxi.Tags.Index import Response

from . import tags_cache_utils as tags_cache


BIG_OFFSET = 1000000000000
REPOSITION_ENTITY_TYPES = set({'udid', 'park', 'dbid_uuid'})

TAGS_CACHE_DUMP_FILENAME = 'cache_tags_dump.bin'

TAGS_CACHE_RESPONSE_EMPTY = {'entities': {}, 'revision': BIG_OFFSET}

TAGS_CACHE_RESPONSE_V4 = {
    'entities': {
        'udid': {'000000000000000000000005': {'tag_udid_05'}},
        'park': {
            '1947c2996ec645b9a1a6f5856f78b738': {'tag_park_01', 'tag_park_02'},
            'ac01ab487826408a8bff1bbab1808490': {'tag_park_03'},
        },
    },
    'revision': BIG_OFFSET + 4,
}

TAGS_CACHE_RESPONSE_V8 = {
    'entities': {
        'udid': {
            '000000000000000000000003': {'tag_udid_03'},
            '000000000000000000000004': {'tag_udid_04'},
        },
        'park': {
            '1947c2996ec645b9a1a6f5856f78b738': {'tag_park_01', 'tag_park_02'},
            'ac01ab487826408a8bff1bbab1808490': {'tag_park_03'},
            '1947c2996ec645b9a1a6f5856f78b732': {'tag_park_04'},
        },
        'dbid_uuid': {
            'parkid_driverid1': {'tag_dbid_uuid_01'},
            'parkid_driverid2': {'tag_dbid_uuid_02'},
        },
    },
    'revision': BIG_OFFSET + 8,
}

TAGS_CACHE_RESPONSE_V8_HALF = {
    'entities': {
        'udid': {
            '000000000000000000000003': {'tag_udid_03'},
            '000000000000000000000004': {'tag_udid_04'},
        },
        'dbid_uuid': {
            'parkid_driverid1': {'tag_dbid_uuid_01'},
            'parkid_driverid2': {'tag_dbid_uuid_02'},
        },
    },
    'revision': BIG_OFFSET + 4,
}

TAGS_CACHE_DUMP_EMPTY = {
    'topics': {'reposition'},
    'entity_types': REPOSITION_ENTITY_TYPES,
    'dump': TAGS_CACHE_RESPONSE_EMPTY,
}

TAGS_CACHE_DUMP_V4 = {
    'topics': {'reposition'},
    'entity_types': REPOSITION_ENTITY_TYPES,
    'dump': TAGS_CACHE_RESPONSE_V4,
}

TAGS_CACHE_DUMP_V8 = {
    'topics': {'reposition'},
    'entity_types': REPOSITION_ENTITY_TYPES,
    'dump': TAGS_CACHE_RESPONSE_V8,
}

TAGS_CACHE_DUMP_V8_HALF = {
    'topics': {'reposition'},
    'entity_types': REPOSITION_ENTITY_TYPES,
    'dump': TAGS_CACHE_RESPONSE_V8_HALF,
}


def clear_tags_cache(tags_cache_dump_dir):
    shutil.rmtree(tags_cache_dump_dir, True)


def read_tags_cache(tags_cache_dump_file):
    with open(tags_cache_dump_file, 'rb') as fl:
        data_fbs = fl.read()
        return data_fbs
    return None


def write_tags_cache(tags_cache_dump_file, data_fbs, date=None):
    os.makedirs(os.path.dirname(tags_cache_dump_file), exist_ok=True)
    with open(tags_cache_dump_file, 'wb') as fl:
        fl.write(data_fbs)
    if date:
        modified_time = time.mktime(date.timetuple())
        os.utime(tags_cache_dump_file, (modified_time, modified_time))


def exist_tags_cache(tags_cache_dump_file):
    return os.path.isfile(tags_cache_dump_file)


def modified_tags_cache(tags_cache_dump_file):
    modified_time = os.path.getmtime(tags_cache_dump_file)
    return datetime.datetime.fromtimestamp(modified_time)


def wait_for_dump(tags_cache_dump_file, date_after=None, timeout=20, sleep=1):
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < end:
        if exist_tags_cache(tags_cache_dump_file) and (
                date_after is None
                or modified_tags_cache(tags_cache_dump_file) > date_after
        ):
            return
        time.sleep(sleep)
    raise TimeoutError()


def build_tags_cache_fbs(builder, data):
    entities_fbs = {}
    for entity, values in data['entities'].items():
        if len(values) == 0:
            continue
        entities_fbs[entity] = {}
        for value, tags in values.items():
            if len(tags) == 0:
                continue

            tags_fbs = [builder.CreateString(tag) for tag in tags]
            EntityTags.EntityTagsStartTagsVector(builder, len(tags_fbs))
            for tag_fbs in tags_fbs:
                builder.PrependUOffsetTRelative(tag_fbs)
            tags_fbs = builder.EndVector(len(tags_fbs))

            name_fbs = builder.CreateString(value)
            EntityTags.EntityTagsStart(builder)
            EntityTags.EntityTagsAddName(builder, name_fbs)
            EntityTags.EntityTagsAddTags(builder, tags_fbs)
            value_fbs = EntityTags.EntityTagsEnd(builder)
            entities_fbs[entity][value] = value_fbs

    for entity, values in entities_fbs.items():
        EntitiesIndex.EntitiesIndexStartItemsVector(builder, len(values))
        for value_fbs in values.values():
            builder.PrependUOffsetTRelative(value_fbs)
        entity_fbs = builder.EndVector(len(values))

        entity_type_fbd = builder.CreateString(entity)
        EntitiesIndex.EntitiesIndexStart(builder)
        EntitiesIndex.EntitiesIndexAddEntityType(builder, entity_type_fbd)
        EntitiesIndex.EntitiesIndexAddItems(builder, entity_fbs)
        entities_fbs[entity] = EntitiesIndex.EntitiesIndexEnd(builder)

    Response.ResponseStartEntitiesVector(builder, len(entities_fbs))
    for entity_fbs in entities_fbs.values():
        builder.PrependUOffsetTRelative(entity_fbs)
    entities_fbs = builder.EndVector(len(entities_fbs))

    Response.ResponseStart(builder)
    Response.ResponseAddRevision(builder, data['revision'])
    Response.ResponseAddEntities(builder, entities_fbs)
    data_fbs = Response.ResponseEnd(builder)

    return data_fbs


def fbs_dump_tags_cache_with_metadata(data):
    builder = flatbuffers.Builder(0)

    entity_types = data['entity_types']
    entity_types_fbs = [builder.CreateString(type) for type in entity_types]
    Dump.DumpStartEntityTypesVector(builder, len(entity_types_fbs))
    for entity_type_fbs in entity_types_fbs:
        builder.PrependUOffsetTRelative(entity_type_fbs)
    entity_types_fbs = builder.EndVector(len(entity_types_fbs))

    topics = data['topics'] if 'topics' in data else set()
    topics_fbs = [builder.CreateString(topic) for topic in topics]
    Dump.DumpStartTopicsVector(builder, len(topics_fbs))
    for topic_fbs in topics_fbs:
        builder.PrependUOffsetTRelative(topic_fbs)
    topics_fbs = builder.EndVector(len(topics_fbs))

    data_fbs = build_tags_cache_fbs(builder, data['dump'])

    Dump.DumpStart(builder)
    Dump.DumpAddEntityTypes(builder, entity_types_fbs)
    Dump.DumpAddTopics(builder, topics_fbs)
    Dump.DumpAddResponse(builder, data_fbs)
    dump_fbs = Dump.DumpEnd(builder)

    builder.Finish(dump_fbs)
    return builder.Output()


def parse_tags_cache_fbs(response):
    data = {'entities': {}, 'revision': response.Revision()}
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
    return data


def fbs_restore_tags_cache_with_metadata(data_fbs):
    dump = Dump.Dump.GetRootAsDump(data_fbs, 0)
    data = {'entity_types': set()}

    for i in range(dump.EntityTypesLength()):
        entity_type_fbs = dump.EntityTypes(i)
        entity_type = entity_type_fbs.decode('utf-8')
        data['entity_types'].add(entity_type)

    if dump.TopicsLength():
        data['topics'] = set()
        for i in range(dump.TopicsLength()):
            topic_fbs = dump.Topics(i)
            topic = topic_fbs.decode('utf-8')
            data['topics'].add(topic)

    data['dump'] = parse_tags_cache_fbs(dump.Response())
    return data


def parse_tags_cache_revision_fbs(data_fbs):
    dump = Dump.Dump.GetRootAsDump(data_fbs, 0)
    response = dump.Response()
    return response.Revision()


# apply TAGS_CACHE_DUMP_V8
@pytest.mark.tags_v2_index(
    tags_list=[
        ('udid', '000000000000000000000003', 'tag_udid_03'),
        ('udid', '000000000000000000000004', 'tag_udid_04'),
        ('dbid_uuid', 'parkid_driverid1', 'tag_dbid_uuid_01'),
        ('dbid_uuid', 'parkid_driverid2', 'tag_dbid_uuid_02'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_01'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_02'),
        ('park', 'ac01ab487826408a8bff1bbab1808490', 'tag_park_03'),
        ('park', '1947c2996ec645b9a1a6f5856f78b732', 'tag_park_04'),
    ],
    topic_relations=[
        ('reposition', 'tag_udid_03'),
        ('reposition', 'tag_udid_04'),
        ('reposition', 'tag_park_01'),
        ('reposition', 'tag_park_02'),
        ('reposition', 'tag_park_03'),
        ('reposition', 'tag_park_04'),
        ('reposition', 'tag_dbid_uuid_01'),
        ('reposition', 'tag_dbid_uuid_02'),
    ],
)
def test_tags_cache_dump(taxi_reposition, tags_cache_path, config):
    TAGS_CACHE_DUMP_FILE = tags_cache_path + '/' + TAGS_CACHE_DUMP_FILENAME

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    clear_tags_cache(tags_cache_path)
    tags_cache.change_tags_cache_config(
        config, True, dump_restore_enabled=True,
    )

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200
    tags_cache.change_tags_cache_config(
        config, False, dump_restore_enabled=True,
    )
    wait_for_dump(TAGS_CACHE_DUMP_FILE)

    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    assert data == TAGS_CACHE_DUMP_V8
    clear_tags_cache(tags_cache_path)


# pass 4 items & apply TAGS_CACHE_DUMP_V8
@pytest.mark.tags_v2_index(
    tags_list=[
        None,
        None,
        None,
        None,
        ('udid', '000000000000000000000003', 'tag_udid_03'),
        ('udid', '000000000000000000000004', 'tag_udid_04'),
        ('dbid_uuid', 'parkid_driverid1', 'tag_dbid_uuid_01'),
        ('dbid_uuid', 'parkid_driverid2', 'tag_dbid_uuid_02'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_01'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_02'),
        ('park', 'ac01ab487826408a8bff1bbab1808490', 'tag_park_03'),
        ('park', '1947c2996ec645b9a1a6f5856f78b732', 'tag_park_04'),
    ],
    topic_relations=[
        ('reposition', 'tag_udid_03'),
        ('reposition', 'tag_udid_04'),
        ('reposition', 'tag_park_01'),
        ('reposition', 'tag_park_02'),
        ('reposition', 'tag_park_03'),
        ('reposition', 'tag_park_04'),
        ('reposition', 'tag_dbid_uuid_01'),
        ('reposition', 'tag_dbid_uuid_02'),
    ],
)
def test_tags_cache_restore(taxi_reposition, tags_cache_path, config):
    TAGS_CACHE_DUMP_FILE = tags_cache_path + '/' + TAGS_CACHE_DUMP_FILENAME

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    clear_tags_cache(tags_cache_path)
    data_fbs = fbs_dump_tags_cache_with_metadata(TAGS_CACHE_DUMP_V4)
    write_tags_cache(TAGS_CACHE_DUMP_FILE, data_fbs)

    now = datetime.datetime.now()
    tags_cache.change_tags_cache_config(
        config, True, dump_restore_enabled=True,
    )

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200
    tags_cache.change_tags_cache_config(
        config, False, dump_restore_enabled=True,
    )

    wait_for_dump(TAGS_CACHE_DUMP_FILE, now)

    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    expected = copy.deepcopy(TAGS_CACHE_DUMP_V4)
    expected['dump']['entities']['udid'].update(
        {
            '000000000000000000000003': {'tag_udid_03'},
            '000000000000000000000004': {'tag_udid_04'},
        },
    )
    expected['dump']['entities']['park'].update(
        {'1947c2996ec645b9a1a6f5856f78b732': {'tag_park_04'}},
    )
    expected['dump']['entities']['dbid_uuid'] = {
        'parkid_driverid1': {'tag_dbid_uuid_01'},
        'parkid_driverid2': {'tag_dbid_uuid_02'},
    }
    expected['dump']['revision'] = BIG_OFFSET + 12

    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    assert data == expected
    clear_tags_cache(tags_cache_path)


# apply TAGS_CACHE_DUMP_V4
@pytest.mark.tags_v2_index(
    tags_list=[
        ('udid', '000000000000000000000005', 'tag_udid_05'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_01'),
        ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_02'),
        ('park', 'ac01ab487826408a8bff1bbab1808490', 'tag_park_03'),
    ],
    topic_relations=[
        ('reposition', 'tag_udid_05'),
        ('reposition', 'tag_park_01'),
        ('reposition', 'tag_park_02'),
        ('reposition', 'tag_park_03'),
    ],
)
@pytest.mark.parametrize('invalid', ['date', 'data', 'entity_types', 'topics'])
def test_tags_cache_invalid_restore(
        taxi_reposition, tags_cache_path, config, invalid,
):
    TAGS_CACHE_DUMP_FILE = tags_cache_path + '/' + TAGS_CACHE_DUMP_FILENAME

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    clear_tags_cache(tags_cache_path)

    if invalid == 'date':
        data_fbs = fbs_dump_tags_cache_with_metadata(TAGS_CACHE_DUMP_V4)
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=31)
        write_tags_cache(TAGS_CACHE_DUMP_FILE, data_fbs, timestamp)
    elif invalid == 'data':
        invalid_data_fbs = b'INVALID TAGS CACHE_DUMP'
        write_tags_cache(TAGS_CACHE_DUMP_FILE, invalid_data_fbs)
    elif invalid == 'entity_types':
        dump_v4 = copy.deepcopy(TAGS_CACHE_DUMP_V4)
        dump_v4['entity_types'] = {'udid', 'dbid_uuid', 'park'}
        data_fbs = fbs_dump_tags_cache_with_metadata(dump_v4)
        write_tags_cache(TAGS_CACHE_DUMP_FILE, data_fbs)
    else:  # invalid == 'topics'
        dump_v4 = copy.deepcopy(TAGS_CACHE_DUMP_V4)
        dump_v4['topics'] = {'new_topic'}
        data_fbs = fbs_dump_tags_cache_with_metadata(dump_v4)
        write_tags_cache(TAGS_CACHE_DUMP_FILE, data_fbs)

    tags_cache.change_tags_cache_config(
        config, True, dump_restore_enabled=True,
    )

    now = datetime.datetime.now()
    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200
    tags_cache.change_tags_cache_config(
        config, False, dump_restore_enabled=True,
    )

    wait_for_dump(TAGS_CACHE_DUMP_FILE, now)

    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    assert data == TAGS_CACHE_DUMP_V4
    clear_tags_cache(tags_cache_path)


@pytest.mark.parametrize(
    'request_max_count,excepted_data',
    [(1, TAGS_CACHE_DUMP_V8_HALF), (8, TAGS_CACHE_DUMP_V8)],
)
def test_tags_cache_multi_partial_update(
        taxi_reposition,
        tags_cache_path,
        tags_mocks,
        config,
        request_max_count,
        excepted_data,
):
    TAGS_CACHE_DUMP_FILE = tags_cache_path + '/' + TAGS_CACHE_DUMP_FILENAME

    config.set_values(
        dict(
            TAGS_CACHE_SETTINGS={
                '__default__': {
                    'enabled': True,
                    'dump_restore_enabled': True,
                    'dump_interval': 1,
                    'request_interval': 0,
                    'request_size': 4,
                    'request_max_count': request_max_count,
                },
            },
        ),
    )

    # clean update
    clear_tags_cache(tags_cache_path)
    start = now = datetime.datetime.now()
    taxi_reposition.invalidate_caches(start, clean_update=True)
    wait_for_dump(TAGS_CACHE_DUMP_FILE, now)
    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    assert data == TAGS_CACHE_DUMP_EMPTY

    # partial update
    tags_mocks.set_tags_list(
        tags_list=[
            # apply TAGS_CACHE_DUMP_V8
            ('udid', '000000000000000000000003', 'tag_udid_03'),
            ('udid', '000000000000000000000004', 'tag_udid_04'),
            ('dbid_uuid', 'parkid_driverid1', 'tag_dbid_uuid_01'),
            ('dbid_uuid', 'parkid_driverid2', 'tag_dbid_uuid_02'),
            ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_01'),
            ('park', '1947c2996ec645b9a1a6f5856f78b738', 'tag_park_02'),
            ('park', 'ac01ab487826408a8bff1bbab1808490', 'tag_park_03'),
            ('park', '1947c2996ec645b9a1a6f5856f78b732', 'tag_park_04'),
        ],
        topic_relations=[
            ('reposition', 'tag_udid_03'),
            ('reposition', 'tag_udid_04'),
            ('reposition', 'tag_park_01'),
            ('reposition', 'tag_park_02'),
            ('reposition', 'tag_park_03'),
            ('reposition', 'tag_park_04'),
            ('reposition', 'tag_dbid_uuid_01'),
            ('reposition', 'tag_dbid_uuid_02'),
        ],
    )

    clear_tags_cache(tags_cache_path)
    now = datetime.datetime.now()
    taxi_reposition.invalidate_caches(
        start + datetime.timedelta(minutes=10), clean_update=False,
    )
    wait_for_dump(TAGS_CACHE_DUMP_FILE, now)
    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    data = fbs_restore_tags_cache_with_metadata(data_fbs)
    assert data == excepted_data

    clear_tags_cache(tags_cache_path)


# skip 1 item
@pytest.mark.tags_v2_index(
    tags_list=[None, ('udid', '000000000000000000000005', 'tag_udid_00')],
    topic_relations=[('reposition', 'tag_udid_00')],
)
@pytest.mark.parametrize(
    'entity_types,entities_count,tags_count',
    [
        (['udid'], 1, 1),
        (['udid'], 2000000, 1),
        (['udid'], 1, 2000000),
        (['udid', 'park'], 1, 1),
        (['udid', 'park'], 200000, 1),
        (['udid', 'park'], 1, 200000),
    ],
)
def test_tags_cache_mega_restore(
        taxi_reposition,
        tags_cache_path,
        config,
        entity_types,
        entities_count,
        tags_count,
):
    TAGS_CACHE_DUMP_FILE = tags_cache_path + '/' + TAGS_CACHE_DUMP_FILENAME

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    tags_cache_response = {'entities': {}, 'revision': BIG_OFFSET + 2}
    for entity_type in entity_types:
        tags_cache_response['entities'][entity_type] = {}
        for entity_index in range(entities_count):
            entity_name = 'entity_' + str(entity_index)
            tags = set(
                ['tag_' + str(tag_index) for tag_index in range(tags_count)],
            )
            tags_cache_response['entities'][entity_type][entity_name] = tags
    tags_cache_dump = {
        'topics': {'reposition'},
        'entity_types': REPOSITION_ENTITY_TYPES,
        'dump': tags_cache_response,
    }
    clear_tags_cache(tags_cache_path)

    data_fbs = fbs_dump_tags_cache_with_metadata(tags_cache_dump)
    write_tags_cache(TAGS_CACHE_DUMP_FILE, data_fbs)

    config.set_values(
        dict(
            TAGS_CACHE_SETTINGS={
                '__default__': {
                    'enabled': True,
                    'dump_restore_enabled': True,
                    'request_interval': 10,
                    'request_size': 2,
                },
            },
        ),
    )

    now = datetime.datetime.now()
    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200
    tags_cache.change_tags_cache_config(
        config, False, dump_restore_enabled=True,
    )

    wait_for_dump(TAGS_CACHE_DUMP_FILE, now)

    data_fbs = read_tags_cache(TAGS_CACHE_DUMP_FILE)
    revision = parse_tags_cache_revision_fbs(data_fbs)
    assert revision == BIG_OFFSET + 2
    clear_tags_cache(tags_cache_path)
