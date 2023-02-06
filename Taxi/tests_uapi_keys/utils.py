import datetime

import dateutil.parser


USER_ENDPOINT_URL = '/v2/keys/by-user'

V2KEY_1 = {
    'id': '1',
    'consumer_id': 'fleet-api-internal',
    'client_id': 'antontodua',
    'is_enabled': True,
    'entity_id': 'Ferrari-Land',
    'permission_ids': [],
    'comment': 'ключ без прав',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex'},
    'created_at': '2018-02-26T16:11:13+00:00',
    'updated_at': '2020-05-04T09:48:13+00:00',
}

V2KEY_2 = {
    'id': '2',
    'consumer_id': 'fleet-api-internal',
    'client_id': 'antontodua',
    'is_enabled': True,
    'entity_id': 'Disneyland',
    'permission_ids': ['fleet-api:v1-users-list:POST'],
    'comment': 'ключ с некорректным правом',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex_team'},
    'created_at': '2018-02-27T12:43:13+00:00',
    'updated_at': '2020-05-04T09:48:33+00:00',
}

V2KEY_3 = {
    'id': '3',
    'consumer_id': 'fleet-api-internal',
    'client_id': 'antontodua',
    'is_enabled': False,
    'entity_id': 'Ferrari-Land',
    'permission_ids': ['fleet-api:v1-users-list:POST'],
    'comment': 'обычный отключенный ключ',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex_team'},
    'created_at': '2018-02-27T12:49:13+00:00',
    'updated_at': '2020-05-04T09:48:53+00:00',
}


def check_updated_at_datatime(updated_at):
    delta = datetime.datetime.now(datetime.timezone.utc) - updated_at
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1), delta


def check_updated_at(updated_at):
    updated_at = dateutil.parser.parse(updated_at)
    check_updated_at_datatime(updated_at)


# checks and pops updated_at, created_at
def check_timestamps_after_creation(response_object):
    created_at = response_object.pop('created_at')
    updated_at = response_object.pop('updated_at')
    assert created_at == updated_at
    check_updated_at(updated_at)
    return response_object


# checks and pops id, updated_at, created_at
def check_key_after_creation(response_object):
    key_id = response_object.pop('id')
    assert isinstance(key_id, str) and key_id, key_id
    return check_timestamps_after_creation(response_object)


# checks and pops updated_at, created_at from pgsql object
def check_created_at_after_creation(pgsql_object):
    created_at = pgsql_object.pop('created_at')
    updated_at = pgsql_object.pop('updated_at')
    assert created_at == updated_at
    check_updated_at_datatime(updated_at)
    return pgsql_object


# check and pop updated_at from pgsql object
def check_updated_at_after_update(pgsql_object):
    updated_at = pgsql_object.pop('updated_at')
    check_updated_at_datatime(updated_at)
    return pgsql_object


def select_keys(pgsql, key_fields, key_id=None):
    assert len(key_fields) >= 1

    cursor = pgsql['api-keys'].conn.cursor()
    keys = ','.join(key_fields)
    query = f'SELECT {keys} FROM db.keys'
    if key_id is not None:
        query += f' WHERE id = \'{key_id}\''
    cursor.execute(query)
    row = cursor.fetchone()
    return {col.name: value for col, value in zip(cursor.description, row)}
