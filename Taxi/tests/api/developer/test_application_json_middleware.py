from aiohttp.web import Response

import libstall.json_pp as json
from libstall.error_code import ER_ACCESS
from stall.middlewares.faa_application_json import middleware


async def test_success(tap):
    data = {
        'lyrics': 'We all came out to Montreux on the lake Geneva shoreline',
        'numbers': [1, 23]
    }

    # pylint: disable=unused-argument
    async def handler(request):
        return data

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            200,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps(data),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_vanilla_error_code(tap):
    # pylint: disable=unused-argument
    async def handler(request):
        return ER_ACCESS

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            403,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({
                'code': 'ER_ACCESS',
                'message': 'Access denied',
            }, indent=4),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_modified_error_code(tap):
    # pylint: disable=unused-argument
    async def handler(request):
        return ER_ACCESS(message='Number of the beast', status=666, details={
            'lyrics': 'Six, six, six the number of the beast',
            'number': 666
        })

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            666,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({
                'code': 'ER_ACCESS',
                'message': 'Number of the beast',
                'details': {'lyrics': 'Six, six, six the number of the beast',
                            'number': 666},
            }, indent=4),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_scalar(tap):
    data1 = 'Some string'
    data2 = 238

    # pylint: disable=unused-argument
    async def handler1(request):
        return data1

    # pylint: disable=unused-argument
    async def handler2(request):
        return data2

    with tap.plan(8):
        response = await middleware(None, handler1)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            200,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({'message': data1, 'code': 'OK'}),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )

        response = await middleware(None, handler2)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            200,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({'message': str(data2), 'code': 'OK'}),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_3_tuple(tap):
    # pylint: disable=unused-argument
    async def handler(request):
        return 666, 'ER_NUMBER_OF_THE_BEAST', 'Number of the beast'

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            666,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({
                'code': 'ER_NUMBER_OF_THE_BEAST',
                'message': 'Number of the beast'
            }, indent=4),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_2_tuple_status_scalar(tap):
    # pylint: disable=unused-argument
    async def handler(request):
        return 403, 'Some test message'

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            403,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({
                'message': 'Some test message',
                'code': 'ER_ACCESS'
            }, indent=4),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )


async def test_2_tuple_status_dict(tap):
    # pylint: disable=unused-argument
    async def handler(request):
        return 666, {'code': 'ER_SOME_CODE',
                     'message': 'Some message',
                     'details': {'key': 'value'}}

    with tap.plan(4):
        response = await middleware(None, handler)

        tap.ok(isinstance(response, Response),
               'aiohttp.web.Response is returned')
        tap.eq_ok(
            response.status,
            666,
            'Correct status code'
        )
        tap.eq_ok(
            response.text,
            json.dumps({
                'code': 'ER_SOME_CODE',
                'message': 'Some message',
                'details': {'key': 'value'}
            }, indent=4),
            'Correct text'
        )
        tap.eq_ok(
            response.headers['Content-Type'],
            'application/json; charset=UTF-8',
            'Correct Content-Type'
        )
