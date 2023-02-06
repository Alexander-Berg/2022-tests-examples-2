import typing
import uuid

REPLACEMENT_MAP = {
    'A': 'А',
    'B': 'В',
    'C': 'С',
    'E': 'Е',
    'H': 'Н',
    'K': 'К',
    'M': 'М',
    'O': 'О',
    'P': 'Р',
    'T': 'Т',
    'X': 'Х',
    'Y': 'У',
}


class Predicates:
    CAR_NUMBER = '11111111-1111-1111-1111-111111111111'
    PARK_CAR_NUMBER = (
        '22222222-2222-2222-2222-222222222222'  # pylint: disable=C0103
    )
    LICENSE = '33333333-3333-3333-3333-333333333333'
    PARK_LICENSE = '44444444-4444-4444-4444-444444444444'


async def add_block(taxi_blocklist, add_request, headers):
    headers['X-Idempotency-Token'] = uuid.uuid4().hex
    response = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert response.status_code == 200
    return add_request['predicate_id'], response.json()['block_id']


async def delete_block(taxi_blocklist, delete_request, headers):
    response = await taxi_blocklist.post(
        '/admin/blocklist/v1/delete', json=delete_request, headers=headers,
    )
    assert response.status_code == 200


def normalize_car_in_kwargs(kwargs: dict):
    normalized = kwargs.get('car_number')
    if normalized:
        normalized = normalized.upper()
        for lat, kir in REPLACEMENT_MAP.items():
            normalized = normalized.replace(lat, kir)
        kwargs['car_number'] = normalized
    return kwargs


def load_kwargs(pgsql, block_id):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(
        'SELECT key, value FROM blocklist.kwargs '
        f'WHERE block_id = \'{block_id}\'',
    )
    return {key: value for key, value in cursor}


def load_kwargs_with_indexes(pgsql, block_id):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(
        'SELECT key, value, indexible FROM blocklist.kwargs '
        f'WHERE block_id = \'{block_id}\'',
    )
    return {key: {value, index} for key, value, index in cursor}


def load_meta(pgsql, block_id):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(
        'SELECT key, value FROM blocklist.meta '
        f'WHERE block_id = \'{block_id}\'',
    )
    return {key: value for key, value in cursor}


def load_block(pgsql, block_id):
    cursor = pgsql['blocklist'].cursor()
    fields = [
        'id',
        'mechanics',
        'predicate_id',
        'status',
        'expires',
        'reason',
        'revision',
    ]
    cursor.execute(
        'SELECT {} FROM blocklist.blocks WHERE id = \'{}\''.format(
            ', '.join(fields), block_id,
        ),
    )

    return {key: value for key, value in zip(fields, next(cursor))}


def flatten(
        dictionary: dict,
        delimiter: str = '.',
        prefix: typing.Optional[str] = None,
) -> dict:
    prefix = prefix + delimiter if prefix else ''
    result: dict = {}
    for key in dictionary:
        if isinstance(dictionary[key], dict):
            result.update(flatten(dictionary[key], delimiter, prefix + key))
            continue
        result[prefix + key] = dictionary[key]

    return result
