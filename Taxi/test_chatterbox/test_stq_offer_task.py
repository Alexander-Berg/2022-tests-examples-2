# pylint: disable=no-member, invalid-name, no-self-use, protected-access
# pylint: disable=redefined-outer-name
import concurrent.futures
import datetime
import json

import bson
import pytest

from chatterbox import constants
from chatterbox import stq_task
from chatterbox.internal import logbroker

NOW = datetime.datetime(2019, 7, 25, 10)

sent: list = []


@pytest.fixture
def mock_passport(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/', 'GET')
    def _dummy_passport(method, url, *args, **kwargs):
        assert 'yandex-team.ru' in url
        return response_mock(
            text=json.dumps(
                {
                    'users': [
                        {
                            'uid': {'value': '1120000000410312'},
                            'login': 'user_17',
                        },
                    ],
                },
            ),
        )


@pytest.fixture
def mock_logbroker_telephony(mock_passport, monkeypatch):
    monkeypatch.setattr(
        logbroker.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )


@pytest.fixture
def mock_lb_first_write_fail(mock_passport, monkeypatch):
    monkeypatch.setattr(
        logbroker.LogbrokerAsyncWrapper,
        '_create_api',
        _create_first_write_fail_api,
    )


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'third': {'mode': 'offline'},
        'logbroker2': {'mode': 'online'},
    },
)
@pytest.mark.parametrize(
    ('task_id', 'tasks_count'),
    [
        (bson.ObjectId('5b2cae5db2682a976914c2a2'), 0),
        (bson.ObjectId('5b2cae5cb2682a976914c2bb'), 0),
        (bson.ObjectId('5d398480779fb31808752015'), 0),
        (bson.ObjectId('5d398480779fb31808752025'), 1),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_wrong_status_or_line_to_offer(cbox, stq, task_id, tasks_count):
    await stq_task.online_chat_processing(cbox.app, task_id, [])
    assert not stq.chatterbox_online_chat_processing.has_calls
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*) '
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            str(task_id),
        )
        assert result[0]['count'] == tasks_count


@pytest.mark.config(CHATTERBOX_LINES={'first': {'mode': 'online'}})
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('task_id', 'timedelta'),
    [
        (bson.ObjectId('5b2cae5db2682a976914c2a3'), 10),
        (bson.ObjectId('5d398480779fb3180875201c'), 10),
    ],
)
async def test_reoffer(cbox, stq, task_id, timedelta):
    await stq_task.online_chat_processing(cbox.app, task_id, [])
    assert stq.chatterbox_online_chat_processing.times_called == 1
    stq_call = stq.chatterbox_online_chat_processing.next_call()
    assert (
        stq_call['id'] == 'offer_{}_4f53cda18c2baa0c0354bb5f9a3ecbe5ed'
        '12ab4d8e11ba873c2f11161202b945'.format(task_id)
    )
    assert stq_call['eta'] == NOW + datetime.timedelta(seconds=timedelta)
    assert stq_call['args'] == [{'$oid': str(task_id)}, []]
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*) '
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            str(task_id),
        )
        assert result[0]['count'] == 0


@pytest.mark.config(
    CHATTERBOX_LINES_OFFER_TIMEOUT={'__default__': 120, 'first': 60},
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'online'},
        'corp': {'mode': 'online'},
        'vip': {'mode': 'online'},
        'fifth': {'mode': 'online'},
        'eda_first': {'mode': 'online'},
        'telephony': {'mode': 'online'},
        'test_max_tasks': {'mode': 'online'},
        'test_no_pw_priority': {'mode': 'online'},
    },
    CHATTERBOX_MAX_ONLINE_TASKS={'__default__': 5, 'fifth': 1},
    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={'__default__': 500},
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=True,
    CHATTERBOX_LINES_WITH_PRIORITY_OF_PIECEWORKERS=['eda_first'],
)
@pytest.mark.parametrize(
    'task_id, correct_supporter_logins,'
    'excluded_supports, stq_eta, stq_task_id',
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a0'),
            ['user_1'],
            [],
            datetime.datetime(2019, 7, 25, 10, 1),
            {
                'user_1': (
                    'offer_5b2cae5cb2682a976914c2a0_'
                    'de01a91b3d59a9b402aedd4cc398822d'
                    'ffa6c0989f523df0f83e5d2e4fd25e6e'
                ),
                'user_4': (
                    'offer_5b2cae5cb2682a976914c2a0_'
                    'be692ad5f416d0009ceb00dd70cb3c09'
                    '6144a0563ab9014df44d4e2076606089'
                ),
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            ['user_1'],
            ['user_5'],
            datetime.datetime(2019, 7, 25, 10, 1),
            {
                'user_1': (
                    'offer_5b2cae5cb2682a976914c2a1_'
                    'acae26d2acf30ae58c8502a0d6cf7716'
                    '79d280cd4d1e980afd0750cadda3b9e8'
                ),
                'user_4': (
                    'offer_5b2cae5cb2682a976914c2a1_'
                    'e5484c68cc11acd7a1cc12dfacbcaedb'
                    '87b84b57b20eab1dd70093c83bca93a4'
                ),
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            ['user_5'],
            ['user_1'],
            datetime.datetime(2019, 7, 25, 10, 1),
            {
                'user_5': (
                    'offer_5b2cae5cb2682a976914c2a1_'
                    '709abcefa523119937248ae7ec6cf6db'
                    '8e576e8cb1adf712357e488316b2f7f1'
                ),
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            ['user_4'],
            ['user_1', 'user_5'],
            datetime.datetime(2019, 7, 25, 10, 1),
            {
                'user_4': (
                    'offer_5b2cae5cb2682a976914c2a1_'
                    '4e45901e6ef2261ec1326ca8a8ecf8df'
                    '329fd75c72b37b0d733c40abbaf82b21'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb318087520d7'),
            ['user_1', 'user_3'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_1': (
                    'offer_5d398480779fb318087520d7_'
                    'de01a91b3d59a9b402aedd4cc398822d'
                    'ffa6c0989f523df0f83e5d2e4fd25e6e'
                ),
                'user_3': (
                    'offer_5d398480779fb318087520d7_'
                    '5eb17f2b081463ad5d96ff1ebf339797'
                    'e59260ce9fbb95bb0b484639a0667151'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb318087520d8'),
            ['user_7'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_7': (
                    'offer_5d398480779fb318087520d8_'
                    '43f7f875a1b1e5334c1d64107da8aad1'
                    '9ff159cc49a1e267a1af5ebcaedf1fa1'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb318087520d8'),
            ['user_6'],
            ['user_5', 'user_7'],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_6': (
                    'offer_5d398480779fb318087520d8_'
                    'ca137931503ba2d03c67484d33524070'
                    '849b561fb5f0b952a84200863d19c55b'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb318087520d8'),
            ['user_9'],
            ['user_5', 'user_6', 'user_7'],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_9': (
                    'offer_5d398480779fb318087520d8_'
                    '0b4afb9bb2a3bde28135cf1ab1c42588'
                    '6a467db9f54c1b2ef6b0576743b0e94c'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb318087520d9'),
            ['user_9'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_9': (
                    'offer_5d398480779fb318087520d9_'
                    '479cb4e72747288745b6c2c0889d30c3'
                    'ca49e03f81c0081a646fca3ba52d7408'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb31808752019'),
            ['user_13'],
            ['user_14'],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_13': (
                    'offer_5d398480779fb31808752019_'
                    '2ce2a4f6d25c36b4f54b422633156d45'
                    '2d6cb0b4acbf8d321d48121242e892b1'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb3180875201a'),
            ['user_14'],
            ['user_13'],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_14': (
                    'offer_5d398480779fb3180875201a_'
                    '80fe09b43fb1fbbdd33731a428a85dee'
                    'c6a3fde4f3f6008956e2e21f11732a04'
                ),
            },
        ),
        (
            bson.ObjectId('5d398480779fb31808752021'),
            ['user_15'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_15': (
                    'offer_5d398480779fb31808752021_'
                    '23545818df4d7f4d2674550e519bd43b'
                    'a6569647a501d4dd835f6c4a7fcc87f6'
                ),
            },
        ),
        pytest.param(
            bson.ObjectId('5d398480779fb31808752021'),
            ['user_15'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_15': (
                    'offer_5d398480779fb31808752021_'
                    '23545818df4d7f4d2674550e519bd43b'
                    'a6569647a501d4dd835f6c4a7fcc87f6'
                ),
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={
                        'eda_first': 5,
                        '__default__': 500,
                    },
                ),
            ],
        ),
        pytest.param(
            bson.ObjectId('5d398480779fb31808752027'),
            ['user_22'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_22': (
                    'offer_5d398480779fb31808752027_'
                    '3050de0025d88fe6e2e010af4262ab43'
                    '351a9c5def91cbebc8f5a36f877b783a'
                ),
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_LINES_WITH_MAX_TASKS_PRIORITY={
                        'test_max_tasks': 2,
                    },
                ),
            ],
        ),
        pytest.param(
            bson.ObjectId('5d398480779fb31808752028'),
            ['user_24', 'user_25'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_24': (
                    'offer_5d398480779fb31808752028_'
                    '815a45c3189a36fe7c266b766fdeeaa2'
                    'f7c856e300ceda5accb1f6f0ed70c9f0'
                ),
                'user_25': (
                    'offer_5d398480779fb31808752028_'
                    'd30e4c4236b1818a623f2e8be1f1cae8'
                    '3b481567a216f44ef5ab2eb94984d7e0'
                ),
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_LINES_WITH_NO_PRIORITY_OF_PIECEWORKERS=[
                        'test_no_pw_priority',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_successfull_offer(
        cbox,
        stq,
        task_id,
        correct_supporter_logins,
        stq_eta,
        excluded_supports,
        stq_task_id,
):
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count',
        )
        supports_offer_skip_count = {
            el['supporter_login']: el['offer_skip_count'] for el in result
        }
    await stq_task.online_chat_processing(
        cbox.app, task_id, excluded_supports.copy(),
    )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert len(result) == 1
        assert result[0]['task_id'] == str(task_id)
        assert result[0]['supporter_login'] in correct_supporter_logins
        fetched_supporter_login = result[0]['supporter_login']
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == 'offered'
    assert task['history'] == [
        {
            'action': 'offer',
            'login': fetched_supporter_login,
            'created': NOW,
            'line': task['line'],
        },
    ]
    assert 'manual_solve' in task['tags']
    assert stq.chatterbox_online_chat_processing.times_called == 1
    stq_call = stq.chatterbox_online_chat_processing.next_call()
    assert stq_call['id'] == stq_task_id[fetched_supporter_login]
    assert stq_call['eta'] == stq_eta
    assert stq_call['args'] == [
        {'$oid': str(task_id)},
        excluded_supports + [fetched_supporter_login],
    ]
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = $1',
            fetched_supporter_login,
        )
    assert (
        result[0]['offer_skip_count']
        == supports_offer_skip_count.get(fetched_supporter_login, 0) + 1
    )


@pytest.mark.config(
    CHATTERBOX_LINES_OFFER_TIMEOUT={'__default__': 120, 'first': 60},
    CHATTERBOX_LINES={'telephony3': {'mode': 'online'}},
    CHATTERBOX_MAX_ONLINE_TASKS={'__default__': 5},
    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={'__default__': 500},
    CHATTERBOX_ONLINE_NO_FREE_SUPPORTER_ETA_BY_LINE={'__default__': 1200},
)
@pytest.mark.parametrize(
    'task_id, correct_supporter_logins,'
    'excluded_supports, stq_eta, stq_task_id',
    [
        pytest.param(
            bson.ObjectId('5d398480779fb31808752228'),
            ['user_21'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_21': (
                    'offer_5d398480779fb31808752228_'
                    '23545818df4d7f4d2674550e519bd43b'
                    'a6569647a501d4dd835f6c4a7fcc87f6'
                ),
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={
                        'telephony3': 3,
                        '__default__': 500,
                    },
                ),
            ],
        ),
        pytest.param(
            bson.ObjectId('5d398480779fb31808752228'),
            ['user_21'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_21': (
                    'offer_5d398480779fb31808752228_'
                    '23545818df4d7f4d2674550e519bd43b'
                    'a6569647a501d4dd835f6c4a7fcc87f6'
                ),
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_MAX_SKIPPED_OFFER_TASKS_BY_LINE={
                        '__default__': 3,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_over_limit_offer(
        cbox,
        stq,
        task_id,
        correct_supporter_logins,
        stq_eta,
        excluded_supports,
        stq_task_id,
        mock_logbroker_telephony,
):
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    previous_status = task['status']

    await stq_task.online_chat_processing(
        cbox.app, task_id, excluded_supports.copy(),
    )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert result is not None
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == previous_status
    assert 'history' not in task or task['history'] == []
    assert 'tags' not in task or task['tags'] == []
    assert stq.chatterbox_online_chat_processing.times_called == 1

    supporter_login = correct_supporter_logins[0]

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = $1',
            supporter_login,
        )
    assert result[0]['offer_skip_count'] == 0
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.online_supporters '
            'WHERE supporter_login = $1',
            supporter_login,
        )
    assert result[0]['status'] == 'offline'


@pytest.mark.config(
    CHATTERBOX_LINES_OFFER_TIMEOUT={'__default__': 120, 'first': 60},
    CHATTERBOX_MAX_ONLINE_TASKS={'__default__': 5, 'hard_line': 1},
    CHATTERBOX_ONLINE_NO_FREE_SUPPORTER_ETA_BY_LINE={'__default__': 1200},
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'hard_line': {'mode': 'online'},
        'new_line': {'mode': 'online'},
        'test_line': {'mode': 'online'},
        'corp': {'mode': 'online'},
        'fourth': {'mode': 'online'},
    },
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=True,
)
@pytest.mark.parametrize(
    'task_id, excluded_supports, stq_id',
    [
        (
            bson.ObjectId('5d398480779fb31808752010'),
            [],
            'offer_5d398480779fb31808752010_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb318087520d8'),
            ['user_5', 'user_6', 'user_7', 'user_9'],
            'offer_5d398480779fb318087520d8_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb31808752011'),
            ['user_5', 'user_6', 'user_7', 'user_8', 'user_9'],
            'offer_5d398480779fb31808752011_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb31808752011'),
            [],
            'offer_5d398480779fb31808752011_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb31808752012'),
            [],
            'offer_5d398480779fb31808752012_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb31808752014'),
            ['user_11'],
            'offer_5d398480779fb31808752014_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb31808752018'),
            [],
            'offer_5d398480779fb31808752018_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
        (
            bson.ObjectId('5d398480779fb3180875201b'),
            [],
            'offer_5d398480779fb3180875201b_'
            '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_no_free_supporter(
        cbox, stq, task_id, excluded_supports, stq_id,
):
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    previous_status = task['status']
    await stq_task.online_chat_processing(
        cbox.app, task_id, excluded_supports.copy(),
    )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT *' 'FROM chatterbox.supporter_tasks ' 'WHERE task_id = $1',
            str(task_id),
        )
        assert not result
    assert stq.chatterbox_online_chat_processing.times_called == 1
    stq_call = stq.chatterbox_online_chat_processing.next_call()
    assert stq_call['id'] == stq_id
    assert stq_call['eta'] == datetime.datetime(2019, 7, 25, 10, 20)
    assert stq_call['args'] == [{'$oid': str(task_id)}, []]
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] != 'offered'
    assert task['support_admin'] == 'superuser'
    if previous_status == 'reopened':
        assert not task.get('history')
    else:
        assert task['history'][-1]['action'] == 'reopen'


@pytest.mark.config(
    CHATTERBOX_LINES_OFFER_TIMEOUT={'__default__': 120, 'first': 60},
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'online'},
        'corp': {'mode': 'online'},
        'vip': {'mode': 'online'},
        'fifth': {'mode': 'online'},
        'eda_first': {'mode': 'online'},
        'telephony': {'mode': 'online'},
        'telephony2': {'mode': 'online'},
        'not_telephony': {'mode': 'online'},
    },
    CHATTERBOX_MAX_ONLINE_TASKS={'__default__': 5, 'fifth': 1},
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=True,
    CHATTERBOX_LINES_WITH_PRIORITY_OF_PIECEWORKERS=['eda_first'],
    CHATTERBOX_ONLINE_NO_FREE_SUPPORTER_ETA_BY_LINE={'__default__': 1200},
    CHATTERBOX_TELEPHONY_LINES=['telephony', 'telephony2', 'first', 'second'],
)
@pytest.mark.parametrize(
    (
        'task_id',
        'correct_supporter_logins',
        'excluded_supports',
        'stq_eta',
        'stq_task_id',
        'reoffer',
        'reshedule',
    ),
    [
        (
            bson.ObjectId('5d398480779fb31808752022'),
            ['user_1'],
            [],
            datetime.datetime(2019, 7, 25, 10, 1),
            {
                'user_1': (
                    'offer_5d398480779fb31808752022_'
                    'de01a91b3d59a9b402aedd4cc398822d'
                    'ffa6c0989f523df0f83e5d2e4fd25e6e'
                ),
            },
            False,
            False,
        ),
        (
            bson.ObjectId('5d398480779fb31808752023'),
            ['user_1', 'user_3'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_1': (
                    'offer_5d398480779fb31808752023_'
                    'de01a91b3d59a9b402aedd4cc398822d'
                    'ffa6c0989f523df0f83e5d2e4fd25e6e'
                ),
                'user_3': (
                    'offer_5d398480779fb31808752023_'
                    '5eb17f2b081463ad5d96ff1ebf339797'
                    'e59260ce9fbb95bb0b484639a0667151'
                ),
            },
            False,
            False,
        ),
        (
            bson.ObjectId('5d398480779fb31808752024'),
            ['user_18', 'user_19'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_18': (
                    'offer_5d398480779fb31808752024_'
                    '53e21917d35e94d641cdc8caf34b17bf'
                    '058dea83544a13ce7bb4b1adaa4bfd0e'
                ),
                'user_19': (
                    'offer_5d398480779fb31808752024_'
                    '4ca82d5c245084a402478ab8ded5ed42'
                    'da41f2edbd23f5e06afff2877b18c820'
                ),
            },
            True,
            False,
        ),
        (
            bson.ObjectId('5a59e916e62e4cb1ac384785'),
            ['user_17'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_17': (
                    'offer_5a59e916e62e4cb1ac384785_'
                    '53e21917d35e94d641cdc8caf34b17bf'
                    '058dea83544a13ce7bb4b1adaa4bfd0e'
                ),
            },
            False,
            False,
        ),
        (
            bson.ObjectId('5d398480779fb31808752026'),
            ['user_20'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_20': (
                    'offer_5a59e916e62e4cb1ac384785_'
                    '53e21917d35e94d641cdc8caf34b17bf'
                    '058dea83544a13ce7bb4b1adaa4bfd0e'
                ),
            },
            False,
            False,
        ),
        (
            bson.ObjectId('5d398480779fb31808752029'),
            ['user_18', 'user_19'],
            [],
            datetime.datetime(2019, 7, 25, 10, 2),
            {
                'user_18': (
                    'offer_5d398480779fb31808752024_'
                    '53e21917d35e94d641cdc8caf34b17bf'
                    '058dea83544a13ce7bb4b1adaa4bfd0e'
                ),
                'user_19': (
                    'offer_5d398480779fb31808752024_'
                    '4ca82d5c245084a402478ab8ded5ed42'
                    'da41f2edbd23f5e06afff2877b18c820'
                ),
            },
            True,
            True,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_force_tasks_reoffer_process(
        cbox,
        stq,
        task_id,
        correct_supporter_logins,
        stq_eta,
        excluded_supports,
        stq_task_id,
        mock_logbroker_telephony,
        reoffer,
        reshedule,
):
    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    previous_status = task['status']

    await stq_task.online_chat_processing(
        cbox.app, task_id, excluded_supports.copy(),
    )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert len(result) == 1
        assert result[0]['task_id'] == str(task_id)
        assert result[0]['supporter_login'] in correct_supporter_logins
        fetched_supporter_login = result[0]['supporter_login']

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    if reoffer:
        if previous_status == 'reopened':
            assert len(task['history']) == 1
        else:
            assert task['history'][-2]['action'] == 'reopen'
    else:
        assert len(task['history']) == 1
    assert task['status'] == 'offered'
    assert task['history'][-1] == {
        'action': 'offer',
        'login': fetched_supporter_login,
        'created': NOW,
        'line': task['line'],
    }
    if reshedule:
        assert stq.chatterbox_online_chat_processing.has_calls
    else:
        assert not stq.chatterbox_online_chat_processing.has_calls


@pytest.mark.config(
    CHATTERBOX_LINES={'first': {'mode': 'online'}},
    CHATTERBOX_TELEPHONY_LINES=['first'],
)
@pytest.mark.parametrize(
    (
        'task_id',
        'correct_supporter_logins',
        'excluded_supports',
        'stq_task_id',
    ),
    [
        (
            bson.ObjectId('5d398480779fb31808752022'),
            ['user_1'],
            [],
            {
                'user_1': (
                    'offer_5d398480779fb31808752022_'
                    'de01a91b3d59a9b402aedd4cc398822d'
                    'ffa6c0989f523df0f83e5d2e4fd25e6e'
                ),
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_logbroker_error(
        cbox,
        stq,
        task_id,
        correct_supporter_logins,
        excluded_supports,
        stq_task_id,
        mock_lb_first_write_fail,
):
    with pytest.raises(logbroker.logbroker.LBTimeoutError):
        await stq_task.online_chat_processing(
            cbox.app, task_id, excluded_supports.copy(),
        )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert len(result) == 1
        assert result[0]['supporter_login'] in correct_supporter_logins
        fetched_supporter_login = result[0]['supporter_login']

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert len(task['history']) == 1
    assert task['status'] == 'offered'
    assert task['history'][-1] == {
        'action': 'offer',
        'login': fetched_supporter_login,
        'created': NOW,
        'line': task['line'],
    }
    assert not stq.chatterbox_online_chat_processing.has_calls

    await stq_task.online_chat_processing(
        cbox.app, task_id, excluded_supports.copy(),
    )
    assert sent


class _DummyApi:
    def start(self):
        future = concurrent.futures.Future()
        future.set_result('start result')
        return future

    def create_retrying_producer(self, *args, **kwargs):
        return _DummyProducer()


class _FirstWriteFailApi(_DummyApi):
    def create_retrying_producer(self, *args, **kwargs):
        return _DummyProducer(first_write_fail=True)


async def _create_api(*args, **kwargs):
    return _DummyApi


async def _create_first_write_fail_api(*args, **kwargs):
    return _FirstWriteFailApi


class _DummyProducer:
    def start(self):
        future = concurrent.futures.Future()
        future.set_result(_DummyFutureResult)
        return future

    def __init__(self, first_write_fail=False):
        self._to_send = []
        self._first_write_fail = first_write_fail

    def stop(self):
        pass

    def write(self, seq_no, message):
        if self._first_write_fail:
            self._first_write_fail = False
            raise concurrent.futures.TimeoutError
        future = concurrent.futures.Future()
        self._to_send.append((future, message))
        _message = json.loads(message)
        _message.pop('id')
        assert _message == {
            'contactPoint': {
                'id': 'contact_point_id',
                'channel': constants.TELEPHONY_CHANNEL,
                'provider': constants.TELEPHONY_PROVIDER,
            },
            'service': {
                'timeout': 5,
                'type': constants.FORWARD_CALL_TYPE,
                'yuid': '1120000000410312',
            },
            'to': {'id': 'call_id'},
        }
        for fut, msg in self._to_send:
            fut.set_result(_DummyFutureResult)
            sent.append(msg)
        self._to_send = []

        return future


class _DummyFutureResult:
    @staticmethod
    def HasField(field):
        return True

    class init:
        max_seq_no = 0
