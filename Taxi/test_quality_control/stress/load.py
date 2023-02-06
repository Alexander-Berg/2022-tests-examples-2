import json
import random

from taxi.util import itertools_ext

from test_quality_control.stress import init


class Mode:
    STATE_ID = 'state_id'
    STATE_LIMIT = 'state_limit'
    STATE_LOAD = 'state_load'
    STATE_ENABLE_PARKS = 'state_enable_parks'
    STATE_ENABLE_CITY = 'state_enable_city'
    DATA_LOAD = 'data_load'


ENTITY_IDS_LIMIT = 200000


async def generate_bullets(host, mode):
    entity_type = 'driver'
    if mode == Mode.STATE_ID:
        entity_ids = list(range(ENTITY_IDS_LIMIT))
        await state_id_bullets(entity_type, entity_ids)
        return

    if mode == Mode.STATE_LIMIT:
        await state_limit_bullets(host, entity_type)
        return

    if mode == Mode.STATE_LOAD:
        entity_ids = list(range(ENTITY_IDS_LIMIT))
        await state_load_bullets(entity_type, entity_ids)
        return

    if mode == Mode.DATA_LOAD:
        entity_ids = list(range(ENTITY_IDS_LIMIT))
        await data_load_bullets(entity_type, entity_ids, 'Moscow')
        return

    if mode == Mode.STATE_ENABLE_PARKS:
        park_ids = list(range(int(ENTITY_IDS_LIMIT / init.BATCH_COUNT)))
        await state_enabled_by_parks_bullets(entity_type, park_ids)
        return

    if mode == Mode.STATE_ENABLE_CITY:
        await state_enabled_by_city_bullets(entity_type, init.CITY)
        return


def write_headers(file):
    file.write('[Host: quality-control.taxi.tst.yandex.net]\n')
    file.write('[YaTaxi-Api-Key: qc-stress]\n')
    file.write('[User-Agent: Tank]\n')
    file.write('[Content-Type: application/json]\n')


async def state_id_bullets(entity_type, entity_ids):
    random.shuffle(entity_ids)
    with open('state_id.ammo.txt', 'w') as file:
        write_headers(file)
        for entity_id in entity_ids:
            file.write(
                '/api/v1/state?type={entity_type}&id={entity_id}'.format(
                    entity_type=entity_type, entity_id=entity_id,
                ),
            )
            file.write('\n')


async def state_limit_bullets(host, entity_type):
    cursor = None
    cursors = [cursor]
    limit = 100
    async with init.get_session() as session:
        for i in range(2000):
            for _ in range(5):
                response = await session.get(
                    '{host}/api/v1/state/list?type={entity_type}'
                    '&limit={limit}{cursor}'.format(
                        host=host,
                        entity_type=entity_type,
                        limit=limit,
                        cursor='&continuation={cursor}'.format(cursor=cursor)
                        if cursor
                        else '',
                    ),
                )
                status = response.status
                if status == 200:
                    json_data = await response.json()
                    if 'continuation' in json_data:
                        cursor = json_data['continuation']
                        cursors.append(cursor)
                    if (i + 1) % 10 == 0:
                        print(
                            '{iteration} iteration finished, modified '
                            '{modified}'.format(
                                iteration=i + 1,
                                modified=json_data['modified'],
                            ),
                        )
                    break

    random.shuffle(cursors)
    with open('state_list.ammo.txt', 'w') as file:
        write_headers(file)
        for cursor in cursors:
            file.write(
                '/api/v1/state/list?type={entity_type}'
                '&limit={limit}{cursor}'.format(
                    entity_type=entity_type,
                    limit=1000,
                    cursor='&continuation={cursor}'.format(cursor=cursor)
                    if cursor
                    else '',
                ),
            )
            file.write('\n')


async def state_enabled_by_parks_bullets(entity_type, parks):
    random.shuffle(parks)
    with open('state_enabled_parks.ammo.txt', 'w') as file:
        write_headers(file)
        for park_id in parks:
            body_1 = json.dumps({'enabled': False})
            body_2 = json.dumps({'enabled': True})

            for body in [body_1, body_2]:
                file.write(
                    '{body_length} {url}\n{body}\n'.format(
                        body_length=len(body),
                        url='/api/v1/state?type={entity_type}&exam={exam_code}'
                        '&group={group_code}&group_id={group_value}'.format(
                            entity_type=entity_type,
                            exam_code='dkvu',
                            group_code='park',
                            group_value=park_id,
                        ),
                        body=body,
                    ),
                )


async def state_enabled_by_city_bullets(entity_type, city):
    with open('state_enabled_city.ammo.txt', 'w') as file:
        write_headers(file)
        body_1 = json.dumps({'enabled': False})
        body_2 = json.dumps({'enabled': True})

        for body in [body_1, body_2]:
            file.write(
                '{body_length} {url}\n{body}\n'.format(
                    body_length=len(body),
                    url='/api/v1/state?type={entity_type}&exam={exam_code}'
                    '&group={group_code}&group_id={group_value}'.format(
                        entity_type=entity_type,
                        exam_code='dkvu',
                        group_code='city',
                        group_value=city,
                    ),
                    body=body,
                ),
            )


async def state_load_bullets(entity_type, entity_ids):
    random.shuffle(entity_ids)
    with open('state_load.ammo.txt', 'w') as file:
        write_headers(file)
        for entity_id in entity_ids:
            body_dkvu = json.dumps(
                {'present': {'can_pass': True, 'sanctions': ['orders_off']}},
            )

            file.write(
                '{body_length} {url}\n{body}\n'.format(
                    body_length=len(body_dkvu),
                    url='/api/v1/state?type={entity_type}&id={entity_id}'
                    '&exam={exam_code}'.format(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        exam_code='dkvu',
                    ),
                    body=body_dkvu,
                ),
            )

            file.write('\n')


async def data_load_bullets(entity_type, entity_ids, city):
    batch_count = 100
    random.shuffle(entity_ids)
    url = '/api/v1/data?type={type}'.format(type=entity_type)
    filename = 'data_load_{batch}.ammo.txt'.format(batch=batch_count)
    with open(filename, 'w') as file:
        write_headers(file)
        for batch, items in enumerate(
                itertools_ext.chunks(entity_ids, batch_count),
        ):
            body = json.dumps(
                [
                    {
                        'id': str(x),
                        'type': entity_type,
                        'data': {'city': city, 'park_id': str(batch + 1)},
                    }
                    for x in items
                ],
            )
            file.write(
                '{body_length} {url}\n{body}\n'.format(
                    body_length=len(body), url=url, body=body,
                ),
            )

            file.write('\n')
