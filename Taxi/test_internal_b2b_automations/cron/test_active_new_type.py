# pylint: disable=redefined-outer-name
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
    {
        'spent': 5999,
        '_id': '5',
        'fullname': 'Fox Fox Fox',
        'is_active': True,
        'email': 'fox-mail@mail.ru',
        'nickname': '4',
        'phone': '+77777777779',
    },
]


@pytest.fixture
def mocks(mockserver):
    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/0')
    async def get_handler0(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[0], status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/1')
    async def get_handler1(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[1], status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/2')
    async def get_handler2(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[2], status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/3')
    async def get_handler3(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[3], status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/4')
    async def get_handler4(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[4], status=200)

    @mockserver.json_handler('taxi-compensation/api/1.0/client/token/user/5')
    async def get_handler5(request):  # pylint: disable=W0612
        return mockserver.make_response(json=USERS[5], status=200)


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_update_active_new_type(mocks, pgsql):
    await run_cron.main(
        [
            'internal_b2b_automations.crontasks.update_active_new_type',
            '-t',
            '0',
        ],
    )
    cursor = pgsql['internal_b2b'].cursor()
    cursor.execute('SELECT * FROM internal_b2b.staff_compensation;')
    record = cursor.fetchall()

    assert record[0][4]
    assert record[1][4]
    assert not record[2][4]
    assert not record[3][4]
    assert not record[4][4]
    assert not record[5][4]
