import asyncio
import json
import logging.config
import re
import sys

from aiohttp import web
from math import floor
from random import random, choice
from uuid import uuid4, UUID

from aiohttp.web_request import Request

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'file': {
            'format': '%(asctime)s: [ %(levelname)s ]: %(module)s : [%(process)d]: %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'file',
            'stream': sys.stdout
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout'],
    },
})
logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

CITY_ID_MOCK = 300

@routes.get('/{dep_id}')
async def place_calls(request):
    dep_id = request.match_info['dep_id']
    settings = {
        'iptel': {
            'beeline': {},
        },
        'taxi': {
            'mts': {},
            'beeline': {},
        },
        'davos': {
            'mts': {},
            'beeline': {},
        },
        'test': {
            'mts': {},
            'beeline': {},
        },
    }
    call_settings = settings.get(dep_id)
    try:
        resp_ok = {}
        resp_fail = {}
        for provider in call_settings:
            dest_numbers = (i for i in request.query.get(provider, "").split(',') if i != "")
            for dest_number in dest_numbers:
                uuid = str(uuid4())
                job_uuid = str(uuid4())
                if re.match(r'^(\d+)$', dest_number):
                    dest_number = f'+{dest_number.strip()}'
                    resp_ok[uuid] = {
                        'provider': provider,
                        'dest_number': dest_number,
                        'api_response': {
                            'Content-Type': 'command/reply',
                            'Reply-Text': f'+OK Job-UUID: {job_uuid}',
                            'Job-UUID': job_uuid
                        }
                    }
                    await asyncio.sleep(random() * 2)
                else:
                    resp_fail[uuid] = {'provider': provider, 'dest_number': dest_number, 'api_response': "Wrong Format"}
        final_resp = {'Correct-Requests': resp_ok, 'Incorrect-Requests': resp_fail}
        return web.Response(text=json.dumps(final_resp), status=202)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def get_call_stat(request):
    records = {}
    good_answers = ['NORMAL_CLEARING']
    bad_answers = [
        'NORMAL_TEMPORARY_FAILURE',
        'ORIGINATOR_CANCEL',
        'NO_USER_RESPONSE',
        'NORMAL_UNSPECIFIED',
        'NO_ANSWER',
        'USER_BUSY',
        'NUMBER_CHANGED',
        'CALL_REJECTED',
        'UNALLOCATED_NUMBER',
        'INVALID_NUMBER_FORMAT',
        'SUBSCRIBER_ABSENT',
        'INTERWORKING',
        'RECOVERY_ON_TIMER_EXPIRE',
    ]
    na_answers = ['NA']
    for uuid_obj in request.query.get('ids', "").split(','):
        try:
            uuid = str(UUID(uuid_obj, version=4))
            r = floor(random() * 5)
            cause = choice(good_answers)
            if r == 0:
                cause = choice(bad_answers)
            elif r == 1:
                cause = choice(na_answers)
            records[uuid] = {'provider': 'NA',
                             'caller_id_number': 'NA',
                             'dest_number': 'NA',
                             'cause': cause,
                             'timestamp': 'NA'}
        except ValueError:
            pass
    await asyncio.sleep(random() * 5)
    return web.Response(text=json.dumps(records), status=200)


async def solomon_push(request: Request):
    logger.debug(request.query)
    logger.debug(await request.read())
    return web.Response(text=json.dumps({'result': 'ok'}), status=200)


async def geolib(request: Request):
    logger.debug(request.query)
    data = []
    global CITY_ID_MOCK
    if request.query.get('equals_search', "") == f'id:{CITY_ID_MOCK}':
        data = [{"id": f'{CITY_ID_MOCK}', "name": f'City{CITY_ID_MOCK}'}]
        CITY_ID_MOCK += 1
    return web.Response(
        text=json.dumps(data),
        status=200,
        headers={'Content-Type': 'application/json; charset=UTF-8'}
    )


async def ebn_objects_list(request: Request):
    logger.debug(request.query)
    body = await request.read()
    js = json.loads(body)
    logger.debug('js %s', js)
    data = {'next_cursor': js['cursor'] + 1, 'limit': js['limit'], 'result': []}
    # tests
    if js['cursor'] == 0:
        # bad object type
        data['result'].append({'object_type': 'blabla', 'object': None, 'object_uuid': 'blabla'})
    elif js['cursor'] == 1:
        # untracked object type
        data['result'].append({'object_type': 'contract', 'object': None, 'object_uuid': 'contract01'})
    elif js['cursor'] == 2 and 'number' in js['filter']['object_types']:
        # numbers
        # skip: add number without tags
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': 'c4f6190e-5869-4f9a-9328-0d298169f5df',
                    'parent_object_uuid': 'contract01',
                    'number': 'bad01',
                    'priority': 1,
                    'city': 0,
                },
                'object_uuid': 'c4f6190e-5869-4f9a-9328-0d298169f5df',
            }
        )
        # error: add number with two group tags
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': '01ec0118-e0b6-47b9-88c9-c84a65408bc8',
                    'parent_object_uuid': 'contract01',
                    'number': 'bad02',
                    'priority': 1,
                    'city': 0,
                    'tags': [
                        {'tag': 't1_60sec'},
                        {'tag': 't2_60sec'},
                    ],
                },
                'object_uuid': '01ec0118-e0b6-47b9-88c9-c84a65408bc8',
            }
        )
        # error: add number without group tags
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': '8782cd0f-a1eb-43fa-9254-47b98df39abb',
                    'parent_object_uuid': 'contract01',
                    'number': 'bad03',
                    'priority': 1,
                    'city': 0,
                    'tags': [
                        {'tag': 'bla'},
                        {'tag': 'foo'},
                    ],
                },
                'object_uuid': '8782cd0f-a1eb-43fa-9254-47b98df39abb',
            }
        )
        # error: add number without city
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': '42c3b214-55b9-4fe8-b75b-c1e5604e3255',
                    'parent_object_uuid': 'contract01',
                    'number': 'bad04',
                    'priority': 1,
                    'city': 0,
                    'tags': [
                        {'tag': 't1_60sec'},
                    ],
                },
                'object_uuid': '42c3b214-55b9-4fe8-b75b-c1e5604e3255',
            }
        )
        # error: add number with bad city
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': 'c7456b74-96bc-4517-9f89-8481ebc12d19',
                    'parent_object_uuid': 'contract01',
                    'number': 'bad05',
                    'priority': 1,
                    'city': -2,
                    'tags': [
                        {'tag': 't1_60sec'},
                    ],
                },
                'object_uuid': 'c7456b74-96bc-4517-9f89-8481ebc12d19',
            }
        )
        # ok: city from cache
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': '5edbe7bb-50ac-4da8-9eb4-490cc3edbade',
                    'parent_object_uuid': 'contract01',
                    'number': 'city_ok_01',
                    'priority': 1,
                    'city': 213,
                    'tags': [
                        {'tag': 't1_60sec'},
                    ],
                },
                'object_uuid': '5edbe7bb-50ac-4da8-9eb4-490cc3edbade',
            }
        )
        # ok: city from geolib
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': '655e0089-f4d2-44ee-b4f7-d52bc9844ab3',
                    'parent_object_uuid': 'contract01',
                    'number': 'city_ok_02',
                    'priority': 1,
                    'city': CITY_ID_MOCK,
                    'tags': [
                        {'tag': 't1_60sec'},
                    ],
                },
                'object_uuid': '655e0089-f4d2-44ee-b4f7-d52bc9844ab3',
            }
        )
        # error: number without tags and auto sync flag
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': 'ea0315e5-25f9-465b-b47e-d229d0a1fefd',
                    'parent_object_uuid': 'contract01',
                    'number': '78880000004',
                    'priority': 1,
                    'city': 213,
                },
                'object_uuid': 'ea0315e5-25f9-465b-b47e-d229d0a1fefd',
            }
        )
        # ok: change phone_group, city, provider
        data['result'].append(
            {
                'object_type': 'number',
                'object': {
                    'object_uuid': 'f7bb9a72-a604-4023-8279-71ed4cc29e1c',
                    'parent_object_uuid': 'contract01',
                    'number': '78880000009',
                    'priority': 1,
                    'city': 213,
                    'tags': [
                        {'tag': 't3_parallel'},
                    ]
                },
                'object_uuid': 'f7bb9a72-a604-4023-8279-71ed4cc29e1c',
            }
        )
    elif js['cursor'] == 3 and 'number' in js['filter']['object_types']:
        # numbers delete
        # error: not number
        data['result'].append(
            {
                'object_type': 'contract',
                'object': None,
                'object_uuid': '9da891d7-78c5-48d1-83a4-6f70df6c5cae',
            }
        )
        # ok: city from cache
        data['result'].append(
            {
                'object_type': 'number',
                'object': None,
                'object_uuid': '5edbe7bb-50ac-4da8-9eb4-490cc3edbade',
            }
        )
        # ok: city from geolib
        data['result'].append(
            {
                'object_type': 'number',
                'object': None,
                'object_uuid': '655e0089-f4d2-44ee-b4f7-d52bc9844ab3',
            }
        )
        # error: number without auto sync flag
        data['result'].append(
            {
                'object_type': 'number',
                'object': None,
                'object_uuid': 'ea0315e5-25f9-465b-b47e-d229d0a1fefd',
            }
        )
        # error: number without auto sync flag
        data['result'].append(
            {
                'object_type': 'number',
                'object': None,
                'object_uuid': 'f7bb9a72-a604-4023-8279-71ed4cc29e1c',
            }
        )
    elif js['cursor'] == 2 and 'partner' in js['filter']['object_types']:
        # update
        data['result'].append(
            {
                'object_type': 'partner',
                'object': {
                    'object_uuid': '32df7fd1-8c9a-4e56-a897-e3befae6880c',
                    'name': 'Манго-Телеком',
                    'full_name': 'ООО "Манго-Телеком"',
                    'code': 'mango-telecom',
                },
                'object_uuid': '32df7fd1-8c9a-4e56-a897-e3befae6880c',
            }
        )
        # skip
        data['result'].append(
            {
                'object_type': 'partner',
                'object': {
                    'object_uuid': '677dcdad-1237-42a0-b8b4-5d5dc5749a25',
                    'name': 'Test Code',
                    'full_name': 'ООО "Test Code"',
                    'code': 'test_code',
                },
                'object_uuid': '677dcdad-1237-42a0-b8b4-5d5dc5749a25',
            }
        )
        # update
        data['result'].append(
            {
                'object_type': 'partner',
                'object': {
                    'object_uuid': '47db0d2b-7a98-45e6-add1-cebf1a65b995',
                    'name': 'BEELINE',
                    'full_name': 'ООО "BEELINE"',
                    'code': 'beeline',
                },
                'object_uuid': '47db0d2b-7a98-45e6-add1-cebf1a65b995',
            }
        )
        # update
        data['result'].append(
            {
                'object_type': 'partner',
                'object': {
                    'object_uuid': '2f8881e6-c334-4d26-a609-3a3a682d2793',
                    'name': 'СамТелеком',
                    'full_name': 'ООО "СамТелеком"',
                    'code': 'samtelecom',
                },
                'object_uuid': '2f8881e6-c334-4d26-a609-3a3a682d2793',
            }
        )
    elif js['cursor'] == 3 and 'partner' in js['filter']['object_types']:
        # skip
        data['result'].append(
            {
                'object_type': 'partner',
                'object': None,
                'object_uuid': '677dcdad-1237-42a0-b8b4-5d5dc5749a25',
            }
        )
        # error
        data['result'].append(
            {
                'object_type': 'partner',
                'object': None,
                'object_uuid': '47db0d2b-7a98-45e6-add1-cebf1a65b995',
            }
        )
        # delete
        data['result'].append(
            {
                'object_type': 'partner',
                'object': None,
                'object_uuid': '2f8881e6-c334-4d26-a609-3a3a682d2793',
            }
        )
    else:
        # loop tests
        data['next_cursor'] = 0
    return web.Response(
        text=json.dumps(data),
        status=200,
        headers={'Content-Type': 'application/json'},
    )


async def ebn_search_objects(request: Request):
    logger.debug(request.query)
    body = await request.read()
    js = json.loads(body)
    logger.debug('js %s', js)
    data = {'result': []}
    if js['object_type'] == 'partner':
        if (
            js['from_object']['uuid'] == '5edbe7bb-50ac-4da8-9eb4-490cc3edbade'
        ):
            data['result'].append({
                'object_type': 'partner',
                'object': {
                    'object_uuid': '32df7fd1-8c9a-4e56-a897-e3befae6880c',
                    'name': 'Манго-Телеком',
                    'full_name': 'ООО "Манго-Телеком"',
                    'code': 'mango-telecom',
                }})
        if (
            js['from_object']['uuid'] == '655e0089-f4d2-44ee-b4f7-d52bc9844ab3'
        ):
            data['result'].append({
                'object_type': 'partner',
                'object': {
                    'object_uuid': '2f8881e6-c334-4d26-a609-3a3a682d2793',
                    'name': 'СамТелеком',
                    'full_name': 'ООО "СамТелеком"',
                    'code': 'samtelecom',
                }})
        if (
            js['from_object']['uuid'] == 'ea0315e5-25f9-465b-b47e-d229d0a1fefd'
            or js['from_object']['uuid'] == 'f7bb9a72-a604-4023-8279-71ed4cc29e1c'
        ):
            data['result'].append({
                'object_type': 'partner',
                'object': {
                    'object_uuid': 'eaf84e06-73bc-4df2-bc03-207eb6ab57f0',
                    'name': 'MTS',
                    'full_name': 'ООО "МТС"',
                    'code': 'mts',
                }})
    return web.Response(
        text=json.dumps(data),
        status=200,
        headers={'Content-Type': 'application/json'},
    )


async def web_app():
    app = web.Application()
    app.add_routes([
        web.get(r'/{dep_id:\w+}/call', place_calls),
        web.get('/call_stat', get_call_stat),
        web.post('/push', solomon_push),
        web.post('/ebn/v1/objects/list', ebn_objects_list),
        web.post('/ebn/v1/search/objects', ebn_search_objects),
        web.get('/geo', geolib),
    ])
    return app

if __name__ == '__main__':
    web.run_app(web_app(), port=8081)
