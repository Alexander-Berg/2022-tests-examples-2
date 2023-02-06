import asyncio
import datetime
import http

import bson
import pymongo
import pytest

from quality_control import consts
from quality_control.repository import storage
from test_quality_control import utils as test_utils

DATA_URL = '/api/v1/data'
DATA_MANY_URL = '/api/v1/data/list'
DATA_BULK_RETRIEVE_URL = '/api/v1/data/bulk_retrieve'
STATE_URL = '/api/v1/state'
STATE_MANY_URL = '/api/v1/state/list'
STATE_BULK_RETRIEVE_URL = '/api/v1/state/bulk_retrieve'
BULK_COUNT = 10
LIMIT = 2

# поскольку мы не можем зафризить время в монге, не нужно фризить время:
# балковые ручки не вернут данные после апдейта, т.к. now стоит на месте
# pylint: disable=invalid-name
pytestmark = pytest.mark.dontfreeze


async def prepare_entities(qc_client, db, now, count=BULK_COUNT):
    # заливаем водителей и устанавливаем им экзамены
    data = []
    states = []
    disabled_states = []
    for i in range(count):
        data.append(
            {
                'id': str(i),
                'data': {'park': 'bulk', 'city': 'city', 'name': str(i)},
            },
        )
        states.append(dict(id=str(i), enabled=True))
        disabled_states.append(dict(id=str(i), enabled=False))
    response = await qc_client.post(
        DATA_MANY_URL, params=dict(type='driver'), json=data,
    )
    assert response.status == http.HTTPStatus.OK
    response = await qc_client.post(
        STATE_MANY_URL, params=dict(type='driver', exam='dkk'), json=states,
    )
    assert response.status == http.HTTPStatus.OK

    response = await qc_client.post(
        STATE_MANY_URL,
        params=dict(type='driver', exam='dkvu'),
        json=disabled_states,
    )
    assert response.status == http.HTTPStatus.OK

    # устанавливаем modified: одной половине - now, другой - на секунду раньше
    updates = []
    async for entity in db.qc_entities.find({}):
        new_datetime = (
            now
            if entity['entity_id'] >= str(count // 2)
            else now - datetime.timedelta(seconds=1)
        )
        saved_timestamp = entity['data']['modified_timestamp']
        updates.append(
            pymongo.operations.UpdateOne(
                filter={'_id': entity['_id']},
                update={
                    '$set': {
                        'data.modified_timestamp': bson.timestamp.Timestamp(
                            new_datetime, saved_timestamp.inc,
                        ),
                        'state.modified_timestamp': bson.timestamp.Timestamp(
                            new_datetime, saved_timestamp.inc,
                        ),
                    },
                },
            ),
        )
    await db.qc_entities.bulk_write(updates)


async def get_data_list(
        qc_client, limit=None, cursor=None, modified_from=None,
):
    params = {'type': 'driver'}
    if limit:
        params['limit'] = limit
    if cursor:
        params['cursor'] = cursor
    if modified_from:
        params['modified_from'] = str(modified_from)

    response = await qc_client.get(DATA_MANY_URL, params=params)
    assert response.status == http.HTTPStatus.OK
    return await response.json()


async def get_state_list(
        qc_client,
        limit=None,
        cursor=None,
        modified_from=None,
        show_disabled=None,
):
    params = {'type': 'driver'}
    if limit:
        params['limit'] = limit
    if cursor:
        params['cursor'] = cursor
    if modified_from:
        params['modified_from'] = str(modified_from)
    if show_disabled is not None:
        params['disabled'] = str(show_disabled).lower()

    response = await qc_client.get(STATE_MANY_URL, params=params)
    assert response.status == http.HTTPStatus.OK
    return await response.json()


async def test_read_data_bulk_by_limit(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    cursor = None
    for _ in range(int(BULK_COUNT / LIMIT)):
        data = await get_data_list(qc_client, LIMIT, cursor)
        assert len(data['items']) == LIMIT
        assert data['cursor'] != cursor

        cursor = data['cursor']


async def test_read_data_bulk_all(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    data = await get_data_list(qc_client)
    assert len(data['items']) == BULK_COUNT
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_data_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor


async def test_read_data_bulk_modified(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    # зачитываем все данные
    data = await get_data_list(
        qc_client, modified_from=now - datetime.timedelta(seconds=1),
    )
    assert len(data['items']) == BULK_COUNT
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_data_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor

    # зачитываем половину данных
    data = await get_data_list(qc_client, modified_from=now)
    assert len(data['items']) == int(BULK_COUNT / 2)
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_data_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor

    # ничего не зачитываем
    data = await get_data_list(
        qc_client, modified_from=now + datetime.timedelta(seconds=1),
    )
    assert not any(data['items'])
    assert data['modified']
    assert data['cursor']


async def test_data_bulk_retrieve(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    entities = [f'{x}' for x in range(1, BULK_COUNT, 2)]

    # Check filter
    response = await qc_client.post(
        DATA_BULK_RETRIEVE_URL,
        params=dict(type='driver'),
        json=dict(items=entities, filter=['name']),
    )

    assert response.status == http.HTTPStatus.OK
    data = await response.json()
    items = data.pop('items')
    assert data == dict()
    for item in items:
        item.pop('modified')

    assert sorted(items, key=lambda x: x['id']) == [
        dict(id=x, type='driver', data=dict(name=x)) for x in entities
    ]

    # Check full data
    response = await qc_client.post(
        DATA_BULK_RETRIEVE_URL,
        params=dict(type='driver'),
        json=dict(items=entities),
    )

    assert response.status == http.HTTPStatus.OK
    data = await response.json()
    items = data.pop('items')
    assert data == dict()
    for item in items:
        item.pop('modified')
    assert sorted(items, key=lambda x: x['id']) == [
        dict(id=x, type='driver', data=dict(park='bulk', city='city', name=x))
        for x in entities
    ]


async def test_state_bulk_retrieve(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    entities = [f'{x}' for x in range(1, BULK_COUNT, 2)]

    # Check full data
    response = await qc_client.post(
        STATE_BULK_RETRIEVE_URL,
        params=dict(type='driver'),
        json=dict(items=entities),
    )

    assert response.status == http.HTTPStatus.OK
    data = await response.json()
    items = data.pop('items')
    assert data == dict()
    items = [x['id'] for x in items]
    assert sorted(items) == entities


async def test_read_state_bulk_by_limit(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    cursor = None
    for _ in range(int(BULK_COUNT / LIMIT)):
        data = await get_state_list(qc_client, LIMIT, cursor)
        assert len(data['items']) == LIMIT
        assert data['modified']
        assert data['cursor'] != cursor

        cursor = data['cursor']


async def test_read_state_bulk_all(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    data = await get_state_list(qc_client)
    assert len(data['items']) == BULK_COUNT
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_state_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor


async def test_read_state_bulk_modified(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    # зачитываем все данные
    data = await get_state_list(
        qc_client, modified_from=now - datetime.timedelta(seconds=1),
    )
    assert len(data['items']) == BULK_COUNT
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_state_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor

    # зачитываем половину данных
    data = await get_state_list(qc_client, modified_from=now)
    assert len(data['items']) == int(BULK_COUNT / 2)
    assert data['modified']
    assert data['cursor']

    cursor = data['cursor']
    modified = data['modified']
    data = await get_state_list(qc_client, cursor=cursor)
    assert not any(data['items'])
    assert data['modified'] == modified
    assert data['cursor'] == cursor

    # ничего не зачитываем
    data = await get_state_list(
        qc_client, modified_from=now + datetime.timedelta(seconds=1),
    )
    assert not any(data['items'])
    assert data['modified']
    assert data['cursor']


async def test_read_bulk_with_disabled(qc_client, db):
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now)

    data = await get_state_list(qc_client, show_disabled=False)
    assert len(data['items']) == BULK_COUNT
    for item in data['items']:
        assert len(item['exams']) == 1
    assert data['modified']
    assert data['cursor']

    disabled_data = await get_state_list(qc_client, show_disabled=True)
    assert len(disabled_data['items']) == BULK_COUNT
    for disabled_i, i in zip(disabled_data.pop('items'), data.pop('items')):
        exams = i.pop('exams')
        assert len(exams) == 1
        assert len(disabled_i['exams']) == 2
        for exam in disabled_i.pop('exams'):
            enabled = exam.pop('enabled')
            if enabled:
                assert exam == exams[0]
            else:
                assert exam.pop('modified')
                assert exam == dict(code='dkvu')
        assert disabled_i == i
    assert disabled_data == data


async def test_read_data_after_insert(qc_client):
    entity_type = 'driver'
    entity_jack = {
        'id': '1',
        'type': entity_type,
        'data': {'name': 'jack', 'park_id': 'park_1', 'city': 'Москва'},
    }

    # проверяем, что данных нет
    response = await qc_client.get(
        DATA_MANY_URL, params={'type': entity_type, 'limit': 10},
    )

    assert response.status == http.HTTPStatus.OK
    assert (await response.json()) == {
        'items': [],
        'modified': '1970-01-01T00:00:00Z',
        'cursor': '0_0',
    }

    # заливаем сущность jack
    response = await qc_client.post(
        DATA_URL,
        params={'type': entity_type, 'id': entity_jack['id']},
        json=entity_jack['data'],
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данные появились
    response = await qc_client.get(
        DATA_MANY_URL, params={'type': entity_type, 'limit': 10},
    )
    assert response.status == http.HTTPStatus.OK

    read_data = await response.json()
    assert len(read_data.get('items', [])) == 1
    assert read_data['modified']
    assert read_data['cursor']

    read_entity = read_data['items'][0]
    assert read_entity['id'] == entity_jack['id']
    assert read_entity['data'] == entity_jack['data']
    assert read_entity['type'] == entity_jack['type']

    # проверяем, что после cursor данных нет
    response = await qc_client.get(
        DATA_MANY_URL,
        params={
            'type': entity_type,
            'limit': 10,
            'cursor': read_data['cursor'],
        },
    )
    assert response.status == http.HTTPStatus.OK
    assert (await response.json()) == {
        'items': [],
        'modified': read_data['modified'],
        'cursor': read_data['cursor'],
    }


async def test_read_data_after_update(qc_client, db):
    # заливаем 1 водителя
    now = datetime.datetime.utcnow()
    await prepare_entities(qc_client, db, now, 1)

    entity_type = 'driver'

    # проверяем, что данные появились, и забираем cursor
    # после cursor данных нет, проверено в пред. тесте
    response = await qc_client.get(
        DATA_MANY_URL, params={'type': entity_type, 'limit': 10},
    )
    assert response.status == http.HTTPStatus.OK

    read_data = await response.json()
    cursor = read_data['cursor']
    modified = read_data['modified']

    # изменяем данные
    new_data = {'name': 'jack', 'park_id': 'park_2', 'city': 'Новая Москва'}

    # точность modified - секунды
    await asyncio.sleep(1)
    response = await qc_client.post(
        DATA_URL, params={'type': entity_type, 'id': '1'}, json=new_data,
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данные появились после cursor
    response = await qc_client.get(
        DATA_MANY_URL,
        params={'type': entity_type, 'limit': 10, 'cursor': cursor},
    )
    assert response.status == http.HTTPStatus.OK

    read_data = await response.json()
    assert len(read_data['items']) == 1

    assert read_data['cursor'] != cursor
    assert read_data['modified'] != modified


async def test_read_state_after_insert(qc_client):
    entity_type = 'driver'
    entity_jack = {'id': '1', 'type': entity_type}
    exam_code = 'dkk'

    # заливаем сущность jack
    response = await qc_client.post(
        DATA_URL,
        params={'type': entity_type, 'id': entity_jack['id']},
        json={},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данных нет
    response = await qc_client.get(
        STATE_MANY_URL, params={'type': entity_type, 'limit': 10},
    )
    assert response.status == http.HTTPStatus.OK
    assert (await response.json()) == {
        'items': [],
        'modified': '1970-01-01T00:00:00Z',
        'cursor': '0_0',
    }

    # заливаем состояние jack
    response = await qc_client.post(
        STATE_URL,
        params={
            'type': entity_jack['type'],
            'id': entity_jack['id'],
            'exam': exam_code,
        },
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данные появились
    response = await qc_client.get(
        STATE_MANY_URL, params={'type': entity_type, 'limit': 10},
    )
    assert response.status == http.HTTPStatus.OK

    read_states = await response.json()
    assert len(read_states.get('items', [])) == 1
    assert read_states['modified']
    assert read_states['cursor']

    read_entity = read_states['items'][0]
    assert read_entity['id'] == entity_jack['id']

    # проверяем, что после cursor данных нет
    response = await qc_client.get(
        STATE_MANY_URL,
        params={
            'type': entity_type,
            'limit': 10,
            'cursor': read_states['cursor'],
        },
    )
    assert response.status == http.HTTPStatus.OK
    assert (await response.json()) == {
        'items': [],
        'modified': read_states['modified'],
        'cursor': read_states['cursor'],
    }


async def test_read_state_after_update(qc_client, db):
    # заливаем одного водителя
    entity_type = 'driver'
    exam_code = 'dkk'
    entity_jack = {'id': '1', 'type': entity_type}
    exam_code = 'dkk'

    response = await qc_client.post(
        DATA_URL,
        params={'type': entity_type, 'id': entity_jack['id']},
        json={},
    )
    assert response.status == http.HTTPStatus.OK

    # заливаем состояние
    response = await qc_client.post(
        STATE_URL,
        params={
            'type': entity_jack['type'],
            'id': entity_jack['id'],
            'exam': exam_code,
        },
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данные появились и забираем cursor
    # после cursor данных нет, проверено в пред. тесте
    response = await qc_client.get(
        STATE_MANY_URL, params={'type': entity_type, 'limit': 10},
    )
    assert response.status == http.HTTPStatus.OK

    read_states = await response.json()
    cursor = read_states['cursor']
    modified = read_states['modified']
    assert read_states['items'][0].get('exams')

    # изменяем состояние
    new_state = {'enabled': False}

    # точность modified - секунды
    await asyncio.sleep(1)
    response = await qc_client.post(
        STATE_URL,
        params={
            'type': entity_type,
            'id': entity_jack['id'],
            'exam': exam_code,
        },
        json=new_state,
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что данные появились после cursor
    response = await qc_client.get(
        STATE_MANY_URL,
        params={'type': entity_type, 'limit': 10, 'cursor': cursor},
    )
    assert response.status == http.HTTPStatus.OK

    read_states = await response.json()
    assert len(read_states['items']) == 1
    assert read_states['modified'] != modified
    assert read_states['cursor'] != cursor
    assert read_states['items'][0].get('exams') == []


async def test_no_pass(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])
    exam_code = 'dkk'
    # назначаем стандартное прохождение
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass'].get('id')
    assert pass_id

    delete_result = await storage.delete_pass(
        qc_context, {'_id': bson.ObjectId(pass_id)},
    )
    assert delete_result.deleted_count == 1

    # проверяем, что битый state не возвращается
    response = await qc_client.get(
        STATE_MANY_URL, params={'type': entity['type']},
    )
    assert response.status == http.HTTPStatus.OK

    read_states = await response.json()
    assert not read_states['items']
    assert read_states['modified']

    response = await qc_client.post(
        STATE_BULK_RETRIEVE_URL,
        params={'type': entity['type']},
        json={'items': [entity['id']]},
    )
    assert response.status == http.HTTPStatus.OK
    read_states = await response.json()
    assert not read_states['items']

    # перевызываем
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что теперь все ок
    response = await qc_client.get(
        STATE_MANY_URL, params={'type': entity['type']},
    )
    assert response.status == http.HTTPStatus.OK

    read_states = await response.json()
    assert read_states['items']
    assert read_states['modified']
    assert read_states['cursor']

    response = await qc_client.post(
        STATE_BULK_RETRIEVE_URL,
        params={'type': entity['type']},
        json={'items': [entity['id']]},
    )
    assert response.status == http.HTTPStatus.OK
    read_states = await response.json()
    assert read_states['items']


async def _create_entity_with_exam(qc_client, entity_type, entity_id, exam):
    await test_utils.prepare_entity(qc_client, entity_type, entity_id)
    await test_utils.prepare_exam(
        qc_client, entity_type, entity_id, exam, test_utils.STATES.CALL,
    )


@pytest.mark.config(QC_LAG_DELTA={consts.LAG_STATE_LIST: 1})
async def test_state_delta(db, qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    entities_count = 3
    # создаём entities_count сущностей и выставляем у них экзамен
    for i in range(entities_count):
        entity['id'] = str(i)
        await _create_entity_with_exam(
            qc_client, entity['type'], entity['id'], exam_code,
        )

    # устанавливаем у всех, кроме одного, modified_timestamp в прошлом
    updates = []
    now = datetime.datetime.now().timestamp()
    for i in range(entities_count - 1):
        updates.append(
            pymongo.operations.UpdateOne(
                filter={'entity_id': f'{i}', 'entity_type': entity['type']},
                update={
                    '$set': {
                        'state.modified_timestamp': bson.timestamp.Timestamp(
                            int(now - 100000), 0,
                        ),
                    },
                },
            ),
        )
    # а последнему ставим modified_timestamp в будущее, чтобы
    # state/list его не вернул
    updates.append(
        pymongo.operations.UpdateOne(
            filter={
                'entity_id': f'{entities_count - 1}',
                'entity_type': entity['type'],
            },
            update={
                '$set': {
                    'state.modified_timestamp': bson.timestamp.Timestamp(
                        int(now + 100000), 0,
                    ),
                },
            },
        ),
    )
    await db.qc_entities.bulk_write(updates)

    states = await test_utils.check_states(qc_client, 'driver', exam_code)
    # проверяем, что state/list не вернул одного
    assert len(states.get('items', [])) == entities_count - 1
