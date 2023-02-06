# root conftest for service eats-data-mappings
# pylint: disable=redefined-outer-name
import pytest


pytest_plugins = ['eats_data_mappings_plugins.pytest_plugins']

TICKET_HEADER = 'X-Ya-Service-Ticket'

# ya tool tvmknife unittest service --src 2345 --dst 2345
TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQqRI:Gpyba9yQgYaXqY_tnEcW3wWzbRb7kd-DI3JpK'
    'Q8qJRJ6M3f9vHGMEfLEZzejlZ1_1cqDfcR-ZDMwyTn7bhyXg46WIv_cHDu7vv5_SyAESMftf'
    'MxvT2tY7HTUwHkZy-hWVi2XnQoEBTxelkzZNirfXgFQXjsG3uHpfF3ET0JNhBk'
)


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_data_mappings'].dict_cursor()

    return create_cursor


@pytest.fixture()
def get_all_pairs(get_cursor):
    def do_get_all_pairs():
        cursor = get_cursor()
        cursor.execute(
            'SELECT primary_entity_type, primary_entity_value, '
            'secondary_entity_type, secondary_entity_value, '
            'updated_at FROM eats_data_mappings.entity_pairs',
        )
        pairs = [
            {
                'primary_entity_type': pair[0],
                'primary_entity_value': pair[1],
                'secondary_entity_type': pair[2],
                'secondary_entity_value': pair[3],
                'updated_at': pair[4],
            }
            for pair in list(cursor)
        ]
        return pairs

    return do_get_all_pairs


@pytest.fixture()
def get_all_pairs_noupdate(get_cursor):
    def do_get_all_pairs():
        cursor = get_cursor()
        cursor.execute(
            'SELECT primary_entity_type, primary_entity_value, '
            'secondary_entity_type, secondary_entity_value '
            'FROM eats_data_mappings.entity_pairs',
        )
        pairs = [
            {
                'primary_entity_type': pair[0],
                'primary_entity_value': pair[1],
                'secondary_entity_type': pair[2],
                'secondary_entity_value': pair[3],
            }
            for pair in list(cursor)
        ]
        return pairs

    return do_get_all_pairs


@pytest.fixture()
def get_all_pairs_with_created_at(get_cursor):
    def do_get_all_pairs():
        cursor = get_cursor()
        cursor.execute(
            'SELECT primary_entity_type, primary_entity_value, '
            'secondary_entity_type, secondary_entity_value, '
            'created_at FROM eats_data_mappings.entity_pairs',
        )
        pairs = [
            {
                'primary_entity_type': pair[0],
                'primary_entity_value': pair[1],
                'secondary_entity_type': pair[2],
                'secondary_entity_value': pair[3],
                'created_at': pair[4],
            }
            for pair in list(cursor)
        ]
        return pairs

    return do_get_all_pairs


@pytest.fixture()
def get_all_takeout_tasks(get_cursor):
    def do_get_all_takeout_tasks():
        request = (
            'SELECT id, task_type, done, takeout_id, '
            'mapping_id FROM eats_data_mappings.takeout_tasks;'
        )
        cursor = get_cursor()
        cursor.execute(request)

        tasks = list(cursor)
        found_tasks = [
            {
                'id': task[0],
                'task_type': task[1],
                'done': task[2],
                'takeout_id': task[3],
                'mapping_id': task[4],
            }
            for task in tasks
        ]
        return found_tasks

    return do_get_all_takeout_tasks


@pytest.fixture()
def get_all_takeouts(get_cursor):
    def do_get_all_takeouts():
        request = (
            'SELECT takeout_id, request_id, takeout_policy, '
            'yandex_uid, status FROM eats_data_mappings.takeout'
        )
        cursor = get_cursor()
        cursor.execute(request)

        takeouts = list(cursor)
        found_takeouts = [
            {
                'takeout_id': takeout[0],
                'request_id': takeout[1],
                'takeout_policy': takeout[2],
                'yandex_uid': takeout[3],
                'status': takeout[4],
            }
            for takeout in takeouts
        ]
        return found_takeouts

    return do_get_all_takeouts


@pytest.fixture()
def get_all_takeout_mapping_elements(get_cursor):
    def do_get_all_takeout_mapping_elements(all=False):
        request = (
            'SELECT id, takeout_id, mapping_id, ordinal_number, primary_type, '
            'secondary_type, yandex_uid, search_by, search_in, target_link, done '
            'FROM eats_data_mappings.takeout_mapping_elements;'
        )
        cursor = get_cursor()
        cursor.execute(request)

        takeout_mapping_elements = list(cursor)
        found_takeout_mapping_elements = [
            {
                **{
                    'ordinal_number': takeout_mapping_element[3],
                    'primary_type': takeout_mapping_element[4],
                    'secondary_type': takeout_mapping_element[5],
                    'search_by': takeout_mapping_element[7],
                    'search_in': takeout_mapping_element[8],
                    'target_link': takeout_mapping_element[9],
                },
                **(
                    {
                        'takeout_id': takeout_mapping_element[1],
                        'mapping_id': takeout_mapping_element[2],
                        'done': takeout_mapping_element[10],
                        'yandex_uid': takeout_mapping_element[6],
                    }
                    if all
                    else {}
                ),
            }
            for takeout_mapping_element in takeout_mapping_elements
        ]
        return found_takeout_mapping_elements

    return do_get_all_takeout_mapping_elements


@pytest.fixture()
def get_all_takeout_data(get_cursor):
    def do_get_all_takeout_data():
        request = (
            'SELECT id, takeout_id, mapping_id, target_link, '
            'primary_type, primary_value, secondary_type, '
            'secondary_value, real_id, created_at '
            'FROM eats_data_mappings.takeout_data;'
        )
        cursor = get_cursor()
        cursor.execute(request)

        takeout_data = list(cursor)
        found_takeout_data = [
            {
                'takeout_id': takeout_data[1],
                'mapping_id': takeout_data[2],
                'target_link': takeout_data[3],
                'primary_type': takeout_data[4],
                'primary_value': takeout_data[5],
                'secondary_type': takeout_data[6],
                'secondary_value': takeout_data[7],
                'real_id': takeout_data[8],
                'created_at': takeout_data[9],
            }
            for takeout_data in takeout_data
        ]
        return found_takeout_data

    return do_get_all_takeout_data


@pytest.fixture()
def get_status_takeout_task_by_id(get_cursor):
    def do_get_status_takeout_task_by_id(id):
        cursor = get_cursor()
        query = (
            'SELECT done FROM eats_data_mappings.takeout_tasks WHERE id = {0}'
        ).format(id)
        cursor.execute(query)
        return list(cursor)[0][0]

    return do_get_status_takeout_task_by_id


@pytest.fixture()
def get_status_takeout_mapping_element(get_cursor):
    def do_get_status_takeout_mapping_element(
            takeout_id, mapping_id, ordinal_number, search_in,
    ):
        cursor = get_cursor()
        query = (
            'SELECT done FROM eats_data_mappings.takeout_mapping_elements WHERE takeout_id = {0} AND mapping_id = {1} AND ordinal_number = {2} and search_in = \'{3}\''.format(
                takeout_id, mapping_id, ordinal_number, search_in,
            )
        )
        cursor.execute(query)
        return list(cursor)[0][0]

    return do_get_status_takeout_mapping_element


@pytest.fixture()
def get_takeout_tasks_retrieve_data_by_takeout_id(get_cursor):
    def do_get_takeout_tasks_retrieve_data_by_takeout_id(takeout_id):
        cursor = get_cursor()
        query = (
            'SELECT task_type, done, takeout_id, mapping_id FROM eats_data_mappings.takeout_tasks WHERE takeout_id = {0} AND task_type = \'retrieve_data\' AND done = False'.format(
                takeout_id,
            )
        )
        cursor.execute(query)

        takeout_tasks = list(cursor)
        found_takeout_tasks = [
            {
                'task_type': takeout_task[0],
                'done': takeout_task[1],
                'takeout_id': takeout_task[2],
                'mapping_id': takeout_task[3],
            }
            for takeout_task in takeout_tasks
        ]
        return found_takeout_tasks

    return do_get_takeout_tasks_retrieve_data_by_takeout_id


@pytest.fixture()
def get_takeout_tasks_mark_as_prepared_by_takeout_id(get_cursor):
    def do_get_takeout_tasks_mark_as_prepared_by_takeout_id(takeout_id):
        cursor = get_cursor()
        query = (
            'SELECT * FROM eats_data_mappings.takeout_tasks WHERE takeout_id = {0} AND task_type = \'mark_as_prepared\' AND done = False'.format(
                takeout_id,
            )
        )
        cursor.execute(query)

        return list(cursor)

    return do_get_takeout_tasks_mark_as_prepared_by_takeout_id


@pytest.fixture()
def compare_expected_with_found():
    def do_compare_expected_with_found(expected_items, found_items):
        assert len(expected_items) == len(found_items)

        for expected_item in expected_items:
            found = False
            for found_item in found_items:
                if expected_item == found_item:
                    found_item = []
                    found = True
                    break
            assert found, {str(expected_item) + ' not found'}
        return True

    return do_compare_expected_with_found


@pytest.fixture()
def ticket_header():
    return {TICKET_HEADER: TICKET}


@pytest.fixture()
def change_pair_order():
    def do_change_order(pair):
        if 'primary_entity_type' in pair.keys():
            return {
                'primary_entity_type': pair['secondary_entity_type'],
                'primary_entity_value': pair['secondary_entity_value'],
                'secondary_entity_type': pair['primary_entity_type'],
                'secondary_entity_value': pair['primary_entity_value'],
            }
        else:
            return {
                'first_entity_type': pair['second_entity_type'],
                'first_entity_value': pair['second_entity_value'],
                'second_entity_type': pair['first_entity_type'],
                'second_entity_value': pair['first_entity_value'],
            }

    return do_change_order


@pytest.fixture()
def get_all_chains(get_cursor):
    def do_get_all_chains():
        cursor = get_cursor()
        cursor.execute(
            'SELECT name, entities FROM eats_data_mappings.entity_chain',
        )
        pairs = [
            {'name': pair[0], 'entities': pair[1]} for pair in list(cursor)
        ]
        return pairs

    return do_get_all_chains


@pytest.fixture()
def ensure_inner():
    def do_ensure_inner(pair):
        new_pair = {}
        if 'first_entity_type' in pair:
            new_pair['primary_entity_type'] = pair['first_entity_type']
            new_pair['primary_entity_value'] = pair['first_entity_value']
            new_pair['secondary_entity_type'] = pair['second_entity_type']
            new_pair['secondary_entity_value'] = pair['second_entity_value']
        else:
            new_pair['primary_entity_type'] = pair['primary_entity_type']
            new_pair['primary_entity_value'] = pair['primary_entity_value']
            new_pair['secondary_entity_type'] = pair['secondary_entity_type']
            new_pair['secondary_entity_value'] = pair['secondary_entity_value']
        if 'created_at' in pair:
            new_pair['created_at'] = pair['created_at']
        if 'updated_at' in pair:
            new_pair['updated_at'] = pair['updated_at']
        if 'id' in pair:
            new_pair['id'] = pair['id']

        return new_pair

    return do_ensure_inner


@pytest.fixture()
def ensure_outer():
    def do_ensure_outer(pair):
        new_pair = {}
        if 'primary_entity_type' in pair:
            new_pair['first_entity_type'] = pair['primary_entity_type']
            new_pair['first_entity_value'] = pair['primary_entity_value']
            new_pair['second_entity_type'] = pair['secondary_entity_type']
            new_pair['second_entity_value'] = pair['secondary_entity_value']
        else:
            new_pair['first_entity_type'] = pair['first_entity_type']
            new_pair['first_entity_value'] = pair['first_entity_value']
            new_pair['second_entity_type'] = pair['second_entity_type']
            new_pair['second_entity_value'] = pair['second_entity_value']
        if 'created_at' in pair:
            new_pair['created_at'] = pair['created_at']
        if 'updated_at' in pair:
            new_pair['updated_at'] = pair['updated_at']
        if 'id' in pair:
            new_pair['id'] = pair['id']

        return new_pair

    return do_ensure_outer


@pytest.fixture()
def strformat():
    def do_strformat(text, quote='\''):
        if text is None:
            return 'NULL'
        return quote + text + quote

    return do_strformat


@pytest.fixture()
def intformat():
    def do_intformat(num, quote='\''):
        if num is None:
            return 'NULL'
        return num

    return do_intformat


@pytest.fixture()
def insert_entities(get_cursor):
    def do_insert(entities):
        if entities:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.entity(name) VALUES {0}'
                ).format(
                    ', '.join(
                        ['(\'{0}\')'.format(entity) for entity in entities],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_entity_mappings(get_cursor, strformat):
    def do_insert(entity_mappings):
        if entity_mappings:
            cursor = get_cursor()
            query = (
                'INSERT INTO eats_data_mappings.entity_mapping '
                '(primary_entity_type, secondary_entity_type, '
                'tvm_write, tvm_read, takeout_policies) '
                'VALUES {0}'.format(
                    ', '.join(
                        [
                            (
                                '(\'{0}\', \'{1}\', \'{2}\', \'{3}\', {4}::'
                                'eats_data_mappings.mapping_takeout_policy[])'
                            ).format(
                                entity_mapping['first_entity_type'],
                                entity_mapping['second_entity_type'],
                                '{{{}}}'.format(
                                    ','.join(
                                        [
                                            '"{}"'.format(svc)
                                            for svc in entity_mapping[
                                                'tvm_write'
                                            ]
                                        ],
                                    ),
                                ),
                                '{{{}}}'.format(
                                    ','.join(
                                        [
                                            '"{}"'.format(svc)
                                            for svc in entity_mapping[
                                                'tvm_read'
                                            ]
                                        ],
                                    ),
                                ),
                                (
                                    'ARRAY[{}]::eats_data_mappings.'
                                    'mapping_takeout_policy[]'
                                ).format(
                                    ','.join(
                                        [
                                            '({0}, {1})'.format(
                                                strformat(
                                                    policy['takeout_policy'],
                                                ),
                                                strformat(
                                                    policy['takeout_chain'],
                                                ),
                                            )
                                            for policy in entity_mapping[
                                                'takeout_policies'
                                            ]
                                        ],
                                    ),
                                ),
                            )
                            for entity_mapping in entity_mappings
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_chains(get_cursor):
    def do_insert(chains):
        if chains:
            cursor = get_cursor()
            query = (
                'INSERT INTO eats_data_mappings.entity_chain '
                '(name, entities) VALUES {0}'.format(
                    ', '.join(
                        [
                            '(\'{0}\', \'{1}\')'.format(
                                chain['name'],
                                '{{{}}}'.format(
                                    ','.join(
                                        [
                                            '"{}"'.format(entity)
                                            for entity in chain['entities']
                                        ],
                                    ),
                                ),
                            )
                            for chain in chains
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_policies(get_cursor):
    def do_insert(policies):
        if policies:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.'
                    'takeout_policy(name) VALUES {0}'
                ).format(
                    ', '.join(
                        ['(\'{0}\')'.format(policy) for policy in policies],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


def booltosql(flag):
    if flag:
        return 'TRUE'
    else:
        return 'FALSE'


@pytest.fixture()
def alter_sequence(get_cursor):
    def do_alter(table, idx, data):
        cursor = get_cursor()
        max_id = max([entry[idx] for entry in data])
        query = (
            'ALTER SEQUENCE eats_data_mappings.{0}_{1}_seq RESTART WITH {2}'
        ).format(table, idx, max_id + 1)
        cursor.execute(query)

    return do_alter


@pytest.fixture()
def insert_tasks(get_cursor, alter_sequence, intformat):
    def do_insert(tasks):
        if tasks:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.takeout_tasks '
                    '(id, task_type, done, takeout_id, mapping_id) VALUES {0};'
                ).format(
                    ', '.join(
                        '({0}, \'{1}\', {2}, {3}, {4})'.format(
                            task['id'],
                            task['task_type'],
                            booltosql(task['done']),
                            task['takeout_id'],
                            intformat(task['mapping_id']),
                        )
                        for task in tasks
                    ),
                )
            )
            cursor.execute(query)

            alter_sequence('takeout_tasks', 'id', tasks)

    return do_insert


@pytest.fixture()
def insert_takeouts(get_cursor, alter_sequence):
    def do_insert(takeouts):
        if takeouts:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.takeout '
                    '(takeout_id, request_id, takeout_policy, yandex_uid, status) VALUES {0};'
                ).format(
                    ', '.join(
                        '({0}, \'{1}\', \'{2}\', \'{3}\', \'{4}\')'.format(
                            takeout['takeout_id'],
                            takeout['request_id'],
                            takeout['takeout_policy'],
                            takeout['yandex_uid'],
                            takeout['status'],
                        )
                        for takeout in takeouts
                    ),
                )
            )
            cursor.execute(query)

            alter_sequence('takeout', 'takeout_id', takeouts)

    return do_insert


def gettime(time):
    if time is not None and time != 'NOW()':
        return '\'{}\''.format(time)
    return 'NOW()'


@pytest.fixture()
def insert_pairs(get_cursor, ensure_outer):
    def do_insert(pairs):
        if pairs:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.entity_pairs ('
                    'primary_entity_type, '
                    'primary_entity_value, '
                    'secondary_entity_type, '
                    'secondary_entity_value, '
                    'created_at, '
                    'updated_at) '
                    'VALUES {0} '
                    'ON CONFLICT DO NOTHING;'
                ).format(
                    ', '.join(
                        [
                            '(\'{0}\', \'{1}\', \'{2}\', \'{3}\', {4}, NOW())'.format(
                                pair['first_entity_type'],
                                pair['first_entity_value'],
                                pair['second_entity_type'],
                                pair['second_entity_value'],
                                gettime(pair.get('created_at')),
                            )
                            for pair in [ensure_outer(pair) for pair in pairs]
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_pairs_with_id(get_cursor, ensure_outer, alter_sequence):
    def do_insert(pairs):
        if pairs:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.entity_pairs ('
                    'id,'
                    'primary_entity_type, '
                    'primary_entity_value, '
                    'secondary_entity_type, '
                    'secondary_entity_value, '
                    'created_at, '
                    'updated_at) '
                    'VALUES {0} '
                    'ON CONFLICT DO NOTHING;'
                ).format(
                    ', '.join(
                        [
                            '({0}, \'{1}\', \'{2}\', \'{3}\', \'{4}\', {5}, NOW())'.format(
                                pair['id'],
                                pair['first_entity_type'],
                                pair['first_entity_value'],
                                pair['second_entity_type'],
                                pair['second_entity_value'],
                                gettime(pair.get('created_at')),
                            )
                            for pair in [ensure_outer(pair) for pair in pairs]
                        ],
                    ),
                )
            )
            cursor.execute(query)

            alter_sequence('entity_pairs', 'id', pairs)

    return do_insert


@pytest.fixture()
def insert_takeout_mapping_elements(get_cursor):
    def do_insert(takeout_mapping_elements):
        if takeout_mapping_elements:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.takeout_mapping_elements ('
                    'takeout_id, '
                    'mapping_id, '
                    'ordinal_number, '
                    'done, '
                    'primary_type,'
                    'secondary_type, '
                    'yandex_uid, '
                    'search_by, '
                    'search_in, '
                    'target_link) '
                    'VALUES {0} '
                    'ON CONFLICT DO NOTHING;'
                ).format(
                    ', '.join(
                        [
                            (
                                '({0}, {1}, {2}, {3}, \'{4}\', \'{5}\', '
                                '\'{6}\', \'{7}\', \'{8}\', {9})'
                            ).format(
                                element['takeout_id'],
                                element['mapping_id'],
                                element['ordinal_number'],
                                booltosql(element['done']),
                                element['primary_type'],
                                element['secondary_type'],
                                element['yandex_uid'],
                                element['search_by'],
                                element['search_in'],
                                booltosql(element['target_link']),
                            )
                            for element in takeout_mapping_elements
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_takeout_data(get_cursor):
    def do_insert(takeout_data):
        if takeout_data:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.takeout_data ('
                    'takeout_id, '
                    'mapping_id, '
                    'target_link, '
                    'primary_type, '
                    'primary_value,'
                    'secondary_type, '
                    'secondary_value, '
                    'real_id, '
                    'created_at) '
                    'VALUES {0} '
                    'ON CONFLICT DO NOTHING;'
                ).format(
                    ', '.join(
                        [
                            (
                                '({0}, {1}, {2}, \'{3}\', \'{4}\', '
                                '\'{5}\', \'{6}\', {7}, {8})'
                            ).format(
                                entry['takeout_id'],
                                entry['mapping_id'],
                                booltosql(entry['target_link']),
                                entry['primary_type'],
                                entry['primary_value'],
                                entry['secondary_type'],
                                entry['secondary_value'],
                                entry['real_id'],
                                gettime(entry.get('created_at')),
                            )
                            for entry in takeout_data
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_takeout_mapping_elements(get_cursor):
    def do_insert(takeout_mapping_elements):
        if takeout_mapping_elements:
            cursor = get_cursor()
            query = (
                (
                    'INSERT INTO eats_data_mappings.takeout_mapping_elements ('
                    'takeout_id, '
                    'mapping_id, '
                    'ordinal_number, '
                    'done, '
                    'primary_type, '
                    'secondary_type, '
                    'yandex_uid, '
                    'search_by, '
                    'search_in, '
                    'target_link) '
                    'VALUES {0} '
                    'ON CONFLICT DO NOTHING;'
                ).format(
                    ', '.join(
                        [
                            (
                                '({0}, {1}, {2}, {3}, \'{4}\', '
                                '\'{5}\', \'{6}\', \'{7}\', \'{8}\', {9})'
                            ).format(
                                takeout_mapping_element['takeout_id'],
                                takeout_mapping_element['mapping_id'],
                                takeout_mapping_element['ordinal_number'],
                                booltosql(takeout_mapping_element['done']),
                                takeout_mapping_element['primary_type'],
                                takeout_mapping_element['secondary_type'],
                                takeout_mapping_element['yandex_uid'],
                                takeout_mapping_element['search_by'],
                                takeout_mapping_element['search_in'],
                                booltosql(
                                    takeout_mapping_element['target_link'],
                                ),
                            )
                            for takeout_mapping_element in takeout_mapping_elements
                        ],
                    ),
                )
            )
            cursor.execute(query)

    return do_insert


@pytest.fixture()
def insert_all(
        insert_entities,
        insert_entity_mappings,
        insert_chains,
        insert_policies,
):
    def do_insert(entities, entity_mappings, chains, policies):
        insert_entities(entities)
        insert_entity_mappings(entity_mappings)
        insert_chains(chains)
        insert_policies(policies)

    return do_insert


@pytest.fixture()
def update_status(get_cursor):
    def do_update(yandex_uids, request_ids, status):
        cursor = get_cursor()
        query = (
            (
                'UPDATE eats_data_mappings.takeout SET status = '
                '\'{0}\' WHERE request_id IN ({1}) AND yandex_uid IN ({2})'
            ).format(
                status,
                ', '.join(
                    [
                        '\'{}\''.format(request_id)
                        for request_id in request_ids
                    ],
                ),
                ', '.join(
                    [
                        '\'{}\''.format(yandex_uid)
                        for yandex_uid in yandex_uids
                    ],
                ),
            )
        )
        cursor.execute(query)

    return do_update
