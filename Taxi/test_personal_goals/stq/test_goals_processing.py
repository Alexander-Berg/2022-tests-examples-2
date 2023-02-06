# pylint: disable=redefined-outer-name
import copy
import datetime

import aiohttp
import bson
from dateutil import tz
import pytest

from personal_goals import const
from personal_goals.stq import goals_processing


DEFAULT_PROC = {
    '_id': 'random_order_id',
    'status': 'finished',
    'order': {
        'user_uid': 'yandex_uid',
        'taxi_status': 'complete',
        'performer': {'tariff': {'class': 'econom'}},
        'nz': 'moscow',
        'cost': '300',
    },
    'extra_data': {'cashback': {'is_cashback': True}},
    'payment_tech': {'type': 'card'},
    'created': datetime.datetime(
        2020, 9, 10, 12, 52, 5, 701000, tzinfo=tz.UTC,
    ),
}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=False,
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=True,
                ),
            ],
        ),
    ],
)
async def test_goals_processing_no_uid(
        stq3_context, mockserver, order_archive_mock,
):
    order = {'taxi_status': 'complete'}

    @mockserver.json_handler('/archive-api/archive/order')
    async def _mock_archive(request, **kwargs):
        doc = {'doc': order}

        return aiohttp.web.Response(
            body=bson.BSON.encode(doc),
            headers={'Content-Type': 'application/bson'},
        )

    proc = copy.copy(DEFAULT_PROC)
    proc['order'] = order
    order_archive_mock.set_order_proc(proc)

    await goals_processing.task(stq3_context, 'random_order_id')


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=False,
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=True,
                ),
            ],
        ),
    ],
)
async def test_goals_processing_no_user_agent(
        stq3_context, mockserver, stq, order_archive_mock,
):
    order = {'taxi_status': 'complete', 'user_uid': '666666'}

    @mockserver.json_handler('/archive-api/archive/order')
    async def _mock_archive(request, **kwargs):
        doc = {'doc': order}

        return aiohttp.web.Response(
            body=bson.BSON.encode(doc),
            headers={'Content-Type': 'application/bson'},
        )

    proc = copy.copy(DEFAULT_PROC)
    proc['order'] = order
    order_archive_mock.set_order_proc(proc)

    await goals_processing.task(stq3_context, 'random_order_id')
    assert stq.is_empty


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=False,
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    PERSONAL_GOALS_REGISTER_MIN_VERSIONS={
        'iphone': {'version': [4, 98]},
        'android': {'version': [4, 15]},
    },
)
@pytest.mark.parametrize(
    'useragent, application',
    [
        (
            'ru.yandex.ytaxi/4.95.34240 '
            '(iPhone; iPhone11,8; iOS 12.2; Darwin)',
            'iphone',
        ),
        ('yandex-taxi/3.115.0.90269 Android/9 (samsung; SM-G960F)', 'android'),
        (
            'ru.yandex.taxi.inhouse/4.97.3459 (iPhone; iPhone10,6; iOS 12.4; '
            'Darwin)',
            'iphone',
        ),
    ],
)
async def test_goals_processing_user_agent(
        stq3_context,
        mockserver,
        stq,
        useragent,
        application,
        order_archive_mock,
):
    order = {
        'taxi_status': 'complete',
        'user_uid': '666666',
        'created': datetime.datetime(2018, 1, 28, 12, 8, 48),
        'user_agent': useragent,
        'statistics': {'application': application},
    }

    @mockserver.json_handler('/archive-api/archive/order')
    async def _mock_archive(request, **kwargs):
        doc = {'doc': order}

        return aiohttp.web.Response(
            body=bson.BSON.encode(doc),
            headers={'Content-Type': 'application/bson'},
        )

    proc = copy.copy(DEFAULT_PROC)
    proc['order'] = order
    order_archive_mock.set_order_proc(proc)

    await goals_processing.task(stq3_context, 'random_order_id')
    assert stq.is_empty


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=False,
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    PERSONAL_GOALS_REGISTER_MIN_VERSIONS={
        'iphone': {'version': [4, 98]},
        'android': {'version': [3, 115]},
    },
)
async def test_goals_processing(
        stq3_context,
        mock_personal_goals,
        mockserver,
        stq,
        response_mock,
        order_archive_mock,
):
    order = {
        'taxi_status': 'complete',
        'user_uid': '666666',
        'created': datetime.datetime(2018, 1, 28, 12, 8, 48),
        'user_agent': (
            'yandex-taxi/3.115.0.90269 Android/9' ' (samsung; SM-G960F)'
        ),
        'statistics': {'application': 'android'},
        'request': {'excluded_parks': ['1234231']},
    }

    @mockserver.json_handler('/archive-api/archive/order')
    async def _mock_archive(request, **kwargs):
        doc = {'doc': order}

        return aiohttp.web.Response(
            body=bson.BSON.encode(doc),
            headers={'Content-Type': 'application/bson'},
        )

    @mock_personal_goals('/internal/register/order')
    async def _mock_register_order(request, **kwargs):
        return {
            'goals': [
                {'goal_id': goal_id, 'status': const.GOAL_STATUS_REGISTERED},
                {
                    'goal_id': 'buy_plus',
                    'status': const.GOAL_STATUS_NOT_REGISTERED,
                },
            ],
        }

    @mock_personal_goals('/internal/v2/goal/complete')
    def _mock_complete_order(request):
        return {
            'goals': [
                {'goal_id': goal_id, 'status': const.GOAL_STATUS_FINISHED},
            ],
        }

    proc = copy.copy(DEFAULT_PROC)
    proc['order'] = order
    order_archive_mock.set_order_proc(proc)

    goal_id = '5_comfort_rides'
    await goals_processing.task(stq3_context, 'random_order_id')

    assert stq.goals_finish_processing.times_called == 1
    task = stq.goals_finish_processing.next_call()
    assert task['args'] == [goal_id]


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=False,
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    PERSONAL_GOALS_USING_ORDER_PROC_ENABLED=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    PERSONAL_GOALS_REGISTER_MIN_VERSIONS={
        'iphone': {'version': [55, 4, 98]},
        'android': {'version': [2, 3, 115]},
    },
    PERSONAL_GOALS_RETRIEVE_APP_VERSION_FROM_USER_API=True,
    TVM_RULES=[{'src': 'personal-goals', 'dst': 'archive-api'}],
)
@pytest.mark.parametrize(
    'application, version, expected_calls',
    [
        ('iphone', '70.2.3', 1),
        ('iphone', '1.2.3', 0),
        ('alice', None, 1),
        (None, None, 0),
    ],
)
async def test_app_version_retrieve(
        stq_runner,
        mock_personal_goals,
        mockserver,
        application,
        version,
        expected_calls,
        order_archive_mock,
):
    order = {
        'taxi_status': 'complete',
        'user_uid': '666666',
        'user_id': 'user_id_1',
        'created': datetime.datetime(2018, 1, 28, 12, 8, 48),
        'statistics': {'application': 'android'},
        'request': {'excluded_parks': ['1234231']},
    }

    @mockserver.json_handler('/archive-api/archive/order')
    async def _mock_archive(request, **kwargs):
        doc = {'doc': order}

        return aiohttp.web.Response(
            body=bson.BSON.encode(doc),
            headers={'Content-Type': 'application/bson'},
        )

    @mockserver.json_handler('/user-api/users/get')
    async def _mock_user_api(request, **kwargs):
        return {
            'id': 'user_id',
            'application': application,
            'application_version': version,
        }

    @mock_personal_goals('/internal/register/order')
    async def _mock_register_order(request, **kwargs):
        return {'goals': []}

    @mock_personal_goals('/internal/v2/goal/complete')
    def _mock_complete_order(request):
        return {'goals': []}

    proc = copy.copy(DEFAULT_PROC)
    proc['order'] = order
    order_archive_mock.set_order_proc(proc)

    await stq_runner.goals_processing.call(args=('random_order_id',))

    assert _mock_register_order.times_called == expected_calls
