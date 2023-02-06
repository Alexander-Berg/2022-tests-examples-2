# pylint: disable=redefined-outer-name
import datetime

import pytest

from internal_b2b_automations.generated.cron import run_cron

USERS = [
    {
        'spent': 353,
        '_id': '0',
        'fullname': 'Cat Cat Cat',
        'is_active': True,
        'email': 'cat-mail@mail.ru',
        'nickname': '1',
        'phone': '+77777777777',
    },
    {
        'spent': 0,
        '_id': '1',
        'fullname': 'Dog Dog Dog',
        'is_active': True,
        'email': 'dog-mail@mail.ru',
        'nickname': '2',
        'phone': '+77777777778',
    },
    {
        'spent': 6001,
        '_id': '2',
        'fullname': 'Fox Fox Fox',
        'is_active': True,
        'email': 'fox-mail@mail.ru',
        'nickname': '3',
        'phone': '+77777777779',
    },
    {
        'spent': 6000,
        '_id': '3',
        'fullname': 'Fox Fox Fox',
        'is_active': True,
        'email': 'fox-mail@mail.ru',
        'nickname': '4',
        'phone': '+77777777779',
    },
    {
        'spent': 5999,
        '_id': '4',
        'fullname': 'Fox Fox Fox',
        'is_active': True,
        'email': 'fox-mail@mail.ru',
        'nickname': '4',
        'phone': '+77777777779',
    },
]


@pytest.fixture
def mocks(mockserver):
    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user')
    async def get_handler(request):  # pylint: disable=W0612
        if request.headers['Authorization'] != 'token':
            return mockserver.make_response(status=401)
        return mockserver.make_response(
            json={
                'items': USERS,
                'amount': 1,
                'skip': False,
                'limit': 2000,
                'sorting_field': 'fullname',
                'sorting_direction': 1,
            },
            status=200,
        )

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/0')
    async def put_handler0(request):  # pylint: disable=W0612
        USERS[0]['role'] = request.json['role']
        return mockserver.make_response(status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/1')
    async def put_handler1(request):  # pylint: disable=W0612
        USERS[1]['role'] = request.json['role']
        return mockserver.make_response(status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/2')
    async def put_handler2(request):  # pylint: disable=W0612
        USERS[2]['role'] = request.json['role']
        return mockserver.make_response(status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/3')
    async def put_handler3(request):  # pylint: disable=W0612
        USERS[3]['role'] = request.json['role']
        return mockserver.make_response(status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/4')
    async def put_handler4(request):  # pylint: disable=W0612
        USERS[4]['role'] = request.json['role']
        return mockserver.make_response(status=200)


@pytest.mark.now((datetime.datetime(2022, 4, 30)).strftime('%Y-%m-%d'))
async def test_update_compensation(mocks):
    await run_cron.main(
        ['internal_b2b_automations.crontasks.update_compensation', '-t', '0'],
    )
    assert USERS[0]['role']['limit'] == 6000
    assert USERS[1]['role']['limit'] == 6000
    assert USERS[2]['role']['limit'] == 5999
    assert USERS[3]['role']['limit'] == 6000
    assert USERS[4]['role']['limit'] == 6000
