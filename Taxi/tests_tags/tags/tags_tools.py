import datetime
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

from tests_tags.tags import tags_select


_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
_INFINITY_STR = 'infinity'
_TIMEDELTA_30_MINUTES = datetime.timedelta(minutes=30)


class Provider:
    def __init__(
            self, provider_id: int, name: str, desc: str, is_active: bool,
    ):
        self.provider_id = provider_id
        self.name = name
        self.desc = desc
        self.is_active = is_active
        self.tags_list: List[str] = []

    @classmethod
    def from_id(cls, provider_id, is_active=True):
        return Provider(
            provider_id=provider_id,
            name='name_%s' % provider_id,
            desc='desc_%s' % provider_id,
            is_active=is_active,
        )

    def values(self):
        return '({id}, \'{name}\', \'{desc}\', {is_active})'.format(
            id=self.provider_id,
            name=self.name,
            desc=self.desc,
            is_active=self.is_active,
        )

    def search_result(self):
        return {
            'id': self.name,
            'description': self.desc,
            'is_active': self.is_active,
            'tags_list': self.tags_list,
        }


def insert_providers(providers):
    return (
        'INSERT INTO state.providers (id, name, description, active) VALUES '
        + ', '.join(provider.values() for provider in providers)
        + ';'
    )


def insert_service_providers(data):
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


class Entity:
    def __init__(
            self, entity_id: int, value: str, entity_type='driver_license',
    ):
        self.entity_id = entity_id
        self.value = value
        self.type = entity_type

    def values(self):
        return '({id}, \'{value}\', \'{type}\')'.format(
            id=self.entity_id, value=self.value, type=self.type,
        )


def insert_entities(entities: Union[List[Entity], Iterator[Entity]]):
    return (
        'INSERT INTO state.entities (id, value, type) VALUES {values};'.format(
            values=', '.join(entity.values() for entity in entities),
        )
    )


class TagName:
    def __init__(self, tag_name_id: int, name: str):
        self.tag_name_id = tag_name_id
        self.name = name

    def values(self):
        return '({id}, \'{name}\')'.format(id=self.tag_name_id, name=self.name)


def insert_tag_names(tag_names: List[TagName]):
    return (
        'INSERT INTO meta.tag_names (id, name) VALUES '
        + ', '.join(tag_name.values() for tag_name in tag_names)
        + ';'
    )


class Topic:
    def __init__(self, topic_id: int, name: str, is_financial: bool):
        self.topic_id = topic_id
        self.name = name
        self.is_financial = is_financial

    def values(self):
        return (
            '({id}, \'{name}\', \'{description}\', \'{is_financial}\')'.format(
                id=self.topic_id,
                name=self.name,
                description='description of ' + self.name,
                is_financial=self.is_financial,
            )
        )


def insert_topics(topics):
    return (
        'INSERT INTO meta.topics (id, name, description, is_financial) VALUES '
        + ', '.join(topic.values() for topic in topics)
        + ';'
    )


class Relation:
    def __init__(self, tag_name_id, topic_id):
        self.tag_name_id = tag_name_id
        self.topic_id = topic_id

    def values(self):
        return '({topic_id}, {tag_name_id})'.format(
            topic_id=self.topic_id, tag_name_id=self.tag_name_id,
        )


def insert_relations(relations: List[Relation]):
    return (
        'INSERT INTO meta.relations (topic_id, tag_name_id) VALUES '
        + ', '.join(relation.values() for relation in relations)
        + ';'
    )


class Tag:
    def __init__(
            self,
            name_id: int,
            provider_id: int,
            entity_id: int,
            updated=None,
            ttl='infinity',
            entity_type: str = None,
    ):
        self.name_id = name_id
        self.provider_id = provider_id
        self.entity_id = entity_id
        self.updated = updated
        self.ttl = ttl
        self.entity_type = entity_type or 'udid'

    @classmethod
    def from_instances(
            cls,
            tag_name: TagName,
            provider: Provider,
            entity: Entity,
            updated=None,
            ttl='infinity',
            entity_type: str = None,
    ):
        return cls(
            name_id=tag_name.tag_name_id,
            provider_id=provider.provider_id,
            entity_id=entity.entity_id,
            updated=updated,
            ttl=ttl,
            entity_type=entity_type,
        )

    def __repr__(self):
        return (
            'name_id %d, provider_id %d, entity_id %d, updated %s, ttl %s, '
            'type %s'
            % (
                self.name_id,
                self.provider_id,
                self.entity_id,
                self.updated,
                self.ttl,
                self.entity_type,
            )
        )

    def __eq__(self, other):
        return (
            self.provider_id == other.provider_id
            and self.entity_id == other.entity_id
            and self.entity_type == other.entity_type
            and self.name_id == other.name_id
            and self.ttl == other.ttl
            and self.updated == other.updated
        )

    def values(self, updated):
        return (
            (
                '({name_id}, {provider_id}, {entity_id}, '
                '\'{updated}\', \'{ttl}\', '
                '\'{entity_type}\')'
            ).format(
                name_id=self.name_id,
                provider_id=self.provider_id,
                entity_id=self.entity_id,
                updated=self.updated or updated,
                ttl=self.ttl,
                entity_type=self.entity_type,
            )
        )

    def customs_values(self, request_type):
        return (
            (
                '({priority}, {name_id}, {provider_id}, {entity_id}, '
                '\'{ttl}\', \'{request_type}\', \'{entity_type}\')'
            ).format(
                priority=0,
                name_id=self.name_id,
                provider_id=self.provider_id,
                entity_id=self.entity_id,
                ttl=self.ttl,
                request_type=request_type,
                entity_type=self.entity_type,
            )
        )

    def is_same(self, other):
        return (
            self.name_id == other.name_id
            and self.provider_id == other.provider_id
            and self.entity_id == other.entity_id
        )

    def find_in(self, expected_tags):
        for tag in expected_tags:
            if self.is_same(tag):
                return tag
        return None

    @staticmethod
    def get_data(name, entity_name, ttl=None, until=None):
        data = {'name': name, 'match': {'id': entity_name}}
        if ttl is not None:
            data['match']['ttl'] = ttl
        if until is not None:
            data['match']['until'] = until
        return data

    @staticmethod
    def get_tag_data(name, entity_name, ttl=None, until=None):
        data = {'name': name, 'entity': entity_name}
        if ttl is not None:
            data['ttl'] = ttl
        if until is not None:
            data['until'] = until
        return data


def insert_tags(tags, date=None):
    """
    Creates insert query to append tags

    :type tags: list of Tag
    :type date: string or None
    :return: string
    """
    if date is None:
        date = '2018-02-16 20:20:40'

    return (
        'INSERT INTO state.tags '
        '(tag_name_id, provider_id, entity_id, updated, ttl, entity_type) '
        'VALUES ' + ', '.join(tag.values(updated=date) for tag in tags) + ';'
    )


def insert_tags_customs(tags, request_type):
    return (
        'INSERT INTO state.tags_customs '
        '(priority, tag_name_id, provider_id, entity_id, ttl,'
        'request_type, entity_type) '
        'VALUES '
        + ', '.join(
            tag.customs_values(request_type=request_type) for tag in tags
        )
        + ';'
    )


def update_tag(tag, updated, ttl):
    return (
        'UPDATE state.tags '
        'SET updated = \'{}\', ttl = \'{}\' '
        'WHERE tag_name_id = {} AND provider_id = {} '
        'AND entity_id = {}'.format(
            updated, ttl, tag.name_id, tag.provider_id, tag.entity_id,
        )
    )


def find_provider_id(provider_name, db, expected_count=1):
    cursor = db.cursor()
    cursor.execute(
        'SELECT id FROM state.providers WHERE name=\'{name}\';'.format(
            name=provider_name,
        ),
    )
    rows = list(row for row in cursor)
    assert len(rows) == expected_count
    return rows[0][0]


class Token:
    def __init__(
            self,
            token: str,
            valid_until: datetime.datetime,
            response_code=None,
    ):
        self.token = token
        self.valid_until = valid_until
        self.response_code = response_code

    def values(self):
        return '(\'{token}\', \'{valid_until}\', {response_code})'.format(
            token=self.token,
            valid_until=self.valid_until.isoformat(),
            response_code=self.response_code or 'NULL',
        )


def insert_request_results(tokens: List[Token]):
    return (
        'INSERT INTO service.request_results '
        '(confirmation_token, valid_until, response_code) '
        'VALUES ' + ', '.join(token.values() for token in tokens)
    )


def validate_request_results(expected_result, db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT confirmation_token, valid_until, response_code '
        'FROM service.request_results ORDER BY confirmation_token;',
    )

    tokens = list(row for row in cursor)
    assert tokens == expected_result


def get_latest_revision(db):
    cursor = db.cursor()
    cursor.execute('SELECT MAX(revision) FROM state.tags;')

    rows = list(row for row in cursor)
    return rows[0][0]


def get_first_revision(db):
    cursor = db.cursor()
    cursor.execute('SELECT MIN(revision) FROM state.tags;')

    rows = list(row for row in cursor)
    return rows[0][0]


def get_latest_revision_on_tag(db, tag_name):
    cursor = db.cursor()
    cursor.execute(
        'SELECT MAX(revision) FROM state.tags '
        'INNER JOIN meta.tag_names '
        'ON state.tags.tag_name_id=meta.tag_names.id '
        'WHERE meta.tag_names.name=\'{}\';'.format(tag_name),
    )

    rows = list(row for row in cursor)
    return rows[0][0]


def get_count_tag_record(db, tag_name):
    cursor = db.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM state.tags '
        'INNER JOIN meta.tag_names '
        'ON state.tags.tag_name_id=meta.tag_names.id '
        'WHERE meta.tag_names.name=\'{}\';'.format(tag_name),
    )

    rows = list(row for row in cursor)
    return rows[0][0]


def validate_provider_tags(provider_name, entity_tags, db):
    query = (
        'SELECT state.entities.value, meta.tag_names.name FROM state.tags '
        'INNER JOIN meta.tag_names ON state.tags.tag_name_id=meta.tag_names.id'
        ' INNER JOIN state.entities ON state.tags.entity_id=state.entities.id '
        'INNER JOIN state.providers '
        'ON state.tags.provider_id=state.providers.id '
        'WHERE state.providers.name=\'{provider_name}\';'.format(
            provider_name=provider_name,
        )
    )

    cursor = db.cursor()
    cursor.execute(query, provider_name)

    rows = list(row for row in cursor)
    result = dict()
    for row in rows:
        entity = row[0]
        tag = row[1]
        if entity not in result:
            result[entity] = set()
        result[entity].add(tag)
    assert entity_tags == result


def get_provider_tags(provider_name: str, db):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT entities.value, entities.type, tag_names.name '
        f'FROM state.entities '
        f'INNER JOIN state.tags on tags.entity_id = entities.id '
        f'INNER JOIN meta.tag_names on tags.tag_name_id = tag_names.id '
        f'INNER JOIN state.providers on tags.provider_id = providers.id '
        f'WHERE providers.name = \'{provider_name}\' AND ttl > updated '
        f'ORDER BY value, name',
    )
    rows = list(row for row in cursor)
    return [
        {'entity_value': row[0], 'entity_type': row[1], 'tag_name': row[2]}
        for row in rows
    ]


def verify_provider_tags(
        provider_name: str,
        expected_tags: List[Tag],
        db,
        now: datetime.datetime,
):
    provider_id = find_provider_id(provider_name, db)
    assert provider_id

    cursor = db.cursor()
    cursor.execute(
        'SELECT tag_name_id, provider_id, entity_id, '
        'updated, ttl, revision, entity_type '
        'FROM state.tags WHERE provider_id={provider_id};'.format(
            provider_id=provider_id,
        ),
    )

    # Some time interval big enough to cover all the tests gone
    delta_time = _TIMEDELTA_30_MINUTES

    found_count = 0
    rows = list(row for row in cursor)
    for row in rows:
        parsed_tag = Tag(
            name_id=row[0],
            provider_id=row[1],
            entity_id=row[2],
            updated=row[3],
            ttl=row[4],
            # 5 is a revision as for v17 scheme
            entity_type=row[6],
        )

        expected_tag = parsed_tag.find_in(expected_tags)
        if expected_tag:
            #  tools.Tag is still active (it was expected)
            found_count += 1
            if expected_tag.ttl == _INFINITY_STR:
                assert parsed_tag.ttl == _INFINITY
            else:
                assert parsed_tag.ttl - expected_tag.ttl < delta_time
            assert parsed_tag.updated - expected_tag.updated < delta_time
            assert parsed_tag.entity_type == expected_tag.entity_type
        else:
            #  Tag was removed (ttl set to now())
            assert parsed_tag.ttl - now < delta_time
            assert parsed_tag.updated - now < delta_time
    assert len(expected_tags) == found_count


def insert_yql_tags_restrictions(operation_id, tag_names):
    """
    :type operation_id: string
    :type tag_names: list of TagName
    """
    return (
        'INSERT INTO service.yql_operation_relations '
        '(operation_id, tag_name_id) VALUES '
        + ', '.join(
            f'(\'{operation_id}\', {tag_name.id})' for tag_name in tag_names
        )
        + ';'
    )


async def activate_task(taxi_tags, task_name, response_code=200):
    response = await taxi_tags.post('service/cron', {'task_name': task_name})
    assert response.status_code == response_code


def time_to_str(time):
    datatime = time.strftime('%Y-%m-%dT%H:%M:%S')
    microseconds = time.strftime('%f').rstrip('0')
    if microseconds:
        return datatime + '.' + microseconds + '+0000'
    return datatime + '+0000'


def verify_active_tags(db, tags):
    rows = tags_select.select_table_named('state.tags', 'entity_id', db)
    not_deleted_tags = filter(lambda row: row['ttl'] > row['updated'], rows)
    existing_tags = list(
        map(
            lambda row: Tag(
                row['tag_name_id'],
                row['provider_id'],
                row['entity_id'],
                entity_type=row['entity_type'],
                ttl='infinity'
                if row['ttl'] == _INFINITY
                else time_to_str(row['ttl']),
            ),
            not_deleted_tags,
        ),
    )
    sorted_tags = sorted(tags, key=lambda x: x.entity_id)
    assert existing_tags == sorted_tags


def apply_queries(db, queries):
    cursor = db.cursor()
    for query_str in queries:
        cursor.execute(query_str)


class Endpoint:
    def __init__(self, topic: Topic, tvm_service_name: str, url: str):
        self.topic_id = topic.topic_id
        self.tvm_service_name = tvm_service_name
        self.url = url


def insert_endpoints(endpoints: List[Endpoint]):
    return (
        'INSERT INTO meta.endpoints (topic_id, tvm_service_name, url) '
        'VALUES '
        + ', '.join(
            f'({e.topic_id}, \'{e.tvm_service_name}\', \'{e.url}\')'
            for e in endpoints
        )
        + ' ON CONFLICT (topic_id) DO NOTHING;'
    )


def insert_history_operations(operations):
    return (
        'INSERT INTO service.history_operations (operation_id, path, created) '
        'VALUES'
        + ', '.join(
            f'(\'{operation_id}\', \'{path}\', \'{created}\')'
            for operation_id, path, created in operations
        )
    )


def verify_inserted_operations(operations, db):
    rows = tags_select.select_named(
        'SELECT operation_id, created FROM service.history_operations '
        'ORDER BY created',
        db,
    )
    assert rows == operations


def make_customs_settings_config(skip_token_threshold: Optional[int]):
    value = {
        'customs_processing_chunk_size': 512,
        'customs_uploading_chunk_size': 512,
        'updating_outdated_tags_chunk_size': 2048,
    }

    if skip_token_threshold is not None:
        value[
            'skip_confirmation_token_usage_for_requests_not_greater_than'
        ] = skip_token_threshold

    return {'__default__': value}
