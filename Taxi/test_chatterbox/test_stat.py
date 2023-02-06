# pylint: disable=too-many-lines
import datetime
import http
import operator

import pytest

from taxi import discovery
from taxi.util import dates

from test_chatterbox import plugins as conftest

OFFLINE_ACTIONS_STAT_TRANSLATIONS = {
    'stats.offline_actions.take_count': {'ru': 'Предлагалось'},
    'stats.offline_actions.close_count': {'ru': 'Выполнен'},
    'stats.offline_actions.comment_count': {'ru': 'Ожидание'},
    'stats.offline_actions.communicate_count': {'ru': 'Только отправлено'},
    'stats.offline_actions.forward_count': {'ru': 'На ручном'},
    'stats.offline_actions.dismiss_count': {'ru': 'НТО'},
    'stats.offline_actions.defer_count': {'ru': 'Отложено'},
    'stats.offline_actions.assign_count': {'ru': 'Назначено вручную'},
    'stats.offline_actions.export_count': {'ru': 'Экспорт'},
    'stats.offline_actions.reopen_count': {'ru': 'Реопены'},
    'stats.offline_actions.create_extra_ticket_count': {
        'ru': 'Дополнительных тикетов',
    },
    'stats.offline_actions.close_avg_latency': {'ru': 'Время ответа'},
    'stats.offline_actions.close_max_latency': {'ru': 'Анти-рекорд'},
    'stats.by_day': {'ru': 'ТЕКУЩИЕ СУТКИ'},
}

OFFLINE_ACTIONS_STAT_DESCRIPTIONS = [
    {
        'id': 'take',
        'label': 'Предлагалось',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'close',
        'label': 'Выполнен',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'comment',
        'label': 'Ожидание',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'communicate',
        'label': 'Только отправлено',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'forward',
        'label': 'На ручном',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'dismiss',
        'label': 'НТО',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'close_avg_latency',
        'label': 'Время ответа',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'duration',
    },
    {
        'id': 'close_max_latency',
        'label': 'Анти-рекорд',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'duration',
    },
    {
        'id': 'defer',
        'label': 'Отложено',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'assign',
        'label': 'Назначено вручную',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'create_extra_ticket',
        'label': 'Дополнительных тикетов',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'export',
        'label': 'Экспорт',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
    {
        'id': 'reopen',
        'label': 'Реопены',
        'group': 'ТЕКУЩИЕ СУТКИ',
        'format': 'number',
    },
]


@pytest.mark.parametrize(
    'user_id,data,expected_result',
    [
        (
            'user1_id',
            {},
            [
                {'status': 'archived', 'chats': 1},
                {'status': 'in_progress', 'chats': 1},
            ],
        ),
        ('user2_id', {}, [{'status': 'archived', 'chats': 1}]),
        (
            'user1_id',
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 1, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
            },
            [
                {'status': 'archived', 'chats': 1},
                {'status': 'in_progress', 'chats': 1},
            ],
        ),
        (
            'user2_id',
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 1, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
            },
            [{'status': 'archived', 'chats': 1}],
        ),
        (
            'user1_id',
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 15, 0, 0),
                ),
            },
            [],
        ),
        (
            'user2_id',
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 15, 0, 0),
                ),
            },
            [],
        ),
    ],
)
async def test_chats_by_user(cbox, user_id, data, expected_result):
    await cbox.post('/v1/stat/chats_by_user/{}'.format(user_id), data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert (
        sorted(
            cbox.body_data['chats_by_user'], key=operator.itemgetter('status'),
        )
        == expected_result
    )


@pytest.mark.parametrize(
    'data,expected_result',
    [
        ({}, 2),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 1, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
            },
            2,
        ),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 15, 0, 0),
                ),
            },
            0,
        ),
    ],
)
async def test_supporters_count(cbox, data, expected_result):
    await cbox.post('/v1/stat/supporters_count/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'supporters_count': expected_result}


async def test_supporters_online(cbox):
    await cbox.post('/v1/stat/supporters_online/', data={})
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'supporters_online': 2}


@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.translations(
    chatterbox={'lines.corp': {'ru': '✍️ Корпоративный тарифчик'}},
)
@pytest.mark.parametrize(
    ['lines', 'expected_code', 'expected_result'],
    [
        (
            [],
            200,
            {
                'items': [
                    {
                        'id': 'corp',
                        'name': '✍️ Корпоративный тарифчик',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': 0.55,
                            'daily_lost_by_line': 0,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': 0,
                            'oldest_ticket_time': 0,
                            'supports_count': 5,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 612999,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'driver_first',
                        'name': 'Первая водительская линия',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': None,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': None,
                            'oldest_ticket_time': 0,
                            'supports_count': 0,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'first',
                        'name': 'Первая линия',
                        'stats': {
                            'daily_create_by_line': 12,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': None,
                            'hourly_create_by_line': 12,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': None,
                            'oldest_ticket_time': 59,
                            'supports_count': 4,
                            'tasks_in_queue_count': 1,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'urgent',
                        'name': 'Ургент',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': None,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': None,
                            'oldest_ticket_time': 0,
                            'supports_count': 0,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'vip',
                        'name': 'ВИП',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': 0,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': 0,
                            'oldest_ticket_time': 0,
                            'supports_count': 1,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'tasks_in_queue_count',
                        'label': 'tasks_in_queue_count',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.realtime',
                        'id': 'oldest_ticket_time',
                        'label': 'oldest_ticket_time',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'supports_count',
                        'label': 'supports_count',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_line_sla',
                        'label': 'daily_line_sla',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_hour',
                        'id': 'hourly_line_sla',
                        'label': 'hourly_line_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_line',
                        'label': 'daily_first_accept_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_first_accept_by_line',
                        'label': 'hourly_first_accept_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_create_by_line',
                        'label': 'daily_create_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_create_by_line',
                        'label': 'hourly_create_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_lost_by_line',
                        'label': 'daily_lost_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_lost_by_line',
                        'label': 'hourly_lost_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_max_answer_by_line',
                        'label': 'daily_max_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_hour',
                        'id': 'hourly_max_answer_by_line',
                        'label': 'hourly_max_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_line',
                        'label': 'daily_first_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_hour',
                        'id': 'hourly_first_answer_by_line',
                        'label': 'hourly_first_answer_by_line',
                    },
                ],
                'total': {
                    'daily_create_by_line': 12,
                    'daily_first_accept_by_line': 0,
                    'daily_lost_by_line': 0,
                    'hourly_create_by_line': 12,
                    'hourly_first_accept_by_line': 0,
                    'hourly_lost_by_line': 0,
                    'oldest_ticket_time': 59,
                    'supports_count': 10,
                    'tasks_in_queue_count': 1,
                    'daily_max_answer_by_line': 612999,
                    'hourly_max_answer_by_line': 0,
                    'daily_first_answer_by_line': 0,
                    'hourly_first_answer_by_line': 0,
                },
            },
        ),
        (
            ['corp', 'vip', 'driver_first'],
            200,
            {
                'items': [
                    {
                        'id': 'corp',
                        'name': '✍️ Корпоративный тарифчик',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': 0.55,
                            'daily_lost_by_line': 0,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': 0,
                            'oldest_ticket_time': 0,
                            'supports_count': 5,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 612999,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'vip',
                        'name': 'ВИП',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': 0,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': 0,
                            'oldest_ticket_time': 0,
                            'supports_count': 1,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                    {
                        'id': 'driver_first',
                        'name': 'Первая водительская линия',
                        'stats': {
                            'daily_create_by_line': 0,
                            'daily_first_accept_by_line': 0,
                            'daily_line_sla': None,
                            'daily_lost_by_line': None,
                            'hourly_create_by_line': 0,
                            'hourly_first_accept_by_line': 0,
                            'hourly_line_sla': None,
                            'hourly_lost_by_line': None,
                            'oldest_ticket_time': 0,
                            'supports_count': 0,
                            'tasks_in_queue_count': 0,
                            'daily_max_answer_by_line': 0,
                            'hourly_max_answer_by_line': 0,
                            'daily_first_answer_by_line': 0,
                            'hourly_first_answer_by_line': 0,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'tasks_in_queue_count',
                        'label': 'tasks_in_queue_count',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.realtime',
                        'id': 'oldest_ticket_time',
                        'label': 'oldest_ticket_time',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'supports_count',
                        'label': 'supports_count',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_line_sla',
                        'label': 'daily_line_sla',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_hour',
                        'id': 'hourly_line_sla',
                        'label': 'hourly_line_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_line',
                        'label': 'daily_first_accept_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_first_accept_by_line',
                        'label': 'hourly_first_accept_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_create_by_line',
                        'label': 'daily_create_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_create_by_line',
                        'label': 'hourly_create_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_lost_by_line',
                        'label': 'daily_lost_by_line',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_hour',
                        'id': 'hourly_lost_by_line',
                        'label': 'hourly_lost_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_max_answer_by_line',
                        'label': 'daily_max_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_hour',
                        'id': 'hourly_max_answer_by_line',
                        'label': 'hourly_max_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_line',
                        'label': 'daily_first_answer_by_line',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_hour',
                        'id': 'hourly_first_answer_by_line',
                        'label': 'hourly_first_answer_by_line',
                    },
                ],
                'total': {
                    'daily_create_by_line': 0,
                    'daily_first_accept_by_line': 0,
                    'daily_lost_by_line': 0,
                    'hourly_create_by_line': 0,
                    'hourly_first_accept_by_line': 0,
                    'hourly_lost_by_line': 0,
                    'oldest_ticket_time': 0,
                    'supports_count': 6,
                    'tasks_in_queue_count': 0,
                    'daily_max_answer_by_line': 612999,
                    'hourly_max_answer_by_line': 0,
                    'daily_first_answer_by_line': 0,
                    'hourly_first_answer_by_line': 0,
                },
            },
        ),
    ],
)
async def test_line_stats(
        cbox: conftest.CboxWrap,
        patch_support_metrics_get_stat,
        lines,
        expected_code,
        expected_result,
):
    await cbox.post('/v1/stat/realtime/lines/', data={'lines': lines})
    assert cbox.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        assert cbox.body_data == expected_result


@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.translations(
    chatterbox={
        'lines.telephony_line': {'ru': 'Линия телефонии'},
        'success_call_gt5_lt10_name': {'ru': '>5, <10'},
    },
)
@pytest.mark.config(
    CHATTERBOX_STAT_IVR_CALLS_SETTINGS={
        'success_call': {
            'enabled': True,
            'conditions': [
                {
                    'title_tankers': {'count': 'success_call_gt5_lt10_name'},
                    'name': 'success_call_gt5_lt10',
                    'lower_limit': 5,
                    'upper_limit': 10,
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    [
        'lines',
        'expected_request_data',
        'expected_response',
        'expected_code',
        'expected_result',
    ],
    [
        ([], None, None, 400, None),
        (
            ['telephony_line', 'telephony_line_second'],
            {
                'action_name': 'success_call',
                'filter_by': 'waiting_time',
                'finish': '2019-06-07T00:00:59+0300',
                'lines': 'telephony_line|telephony_line_second',
                'lower_limit': 5,
                'start': '2019-06-06T23:00:59+0300',
                'upper_limit': 10,
            },
            {
                'filter': '5.0 <= waiting_time <= 10.0',
                'interval_finish': '2021-07-20 00:19:00+00:00',
                'interval_start': '2021-07-18 00:19:00+00:00',
                'values_by_line': [
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 1, 'total': 4},
                            },
                        ],
                        'line': 'telephony_line',
                    },
                    {
                        'counters': [
                            {
                                'name': 'missed_calls_count',
                                'result': {'count': 2, 'total': 2},
                            },
                        ],
                        'line': 'telephony_line_second',
                    },
                ],
            },
            200,
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'active_tasks_count',
                        'label': 'active_tasks_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'tasks_in_progress_count',
                        'label': 'tasks_in_progress_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'tasks_in_queue_count',
                        'label': 'tasks_in_queue_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'supports_count',
                        'label': 'supports_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.realtime',
                        'id': 'free_supports_count',
                        'label': 'free_supports_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.ivr_success_calls_count',
                        'id': 'ivr_success_calls_count_success_call_gt5_lt10',
                        'label': '>5, <10',
                    },
                    {
                        'format': 'string',
                        'group': 'stats.ivr_success_calls_count',
                        'id': (
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10'
                        ),
                        'label': (
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10'
                        ),
                    },
                ],
                'items': [
                    {
                        'id': 'telephony_line',
                        'name': 'telephony_line',
                        'stats': {
                            'active_tasks_count': 2,
                            'free_supports_count': 2,
                            'supports_count': 3,
                            'tasks_in_progress_count': 1,
                            'tasks_in_queue_count': 1,
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10': '25.0%',
                            'ivr_success_calls_count_success_call_gt5_lt10': 1,
                        },
                    },
                    {
                        'id': 'telephony_line_second',
                        'name': 'telephony_line_second',
                        'stats': {
                            'active_tasks_count': 0,
                            'free_supports_count': 1,
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10': '100.0%',
                            'supports_count': 2,
                            'tasks_in_progress_count': 0,
                            'tasks_in_queue_count': 0,
                            'ivr_success_calls_count_success_call_gt5_lt10': 2,
                        },
                    },
                ],
                'total': {
                    'active_tasks_count': 2,
                    'free_supports_count': 3,
                    'supports_count': 5,
                    'tasks_in_progress_count': 1,
                    'tasks_in_queue_count': 1,
                    'ivr_success_calls_count_success_call_gt5_lt10': 3,
                },
            },
        ),
    ],
)
async def test_ivr_calls_stats(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        lines,
        expected_request_data,
        expected_response,
        expected_code,
        expected_result,
):
    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'GET')
    def _patch_request(method, url, **kwargs):
        assert method == 'get'
        assert kwargs['params'] == expected_request_data
        assert (
            url
            == '%s/v1/chatterbox/non-aggregated-stat/actions/count-by-line'
            % support_metrics_service.url
        )
        return response_mock(json=expected_response)

    await cbox.post('/v1/stat/ivr_calls/by_line/', data={'lines': lines})
    assert cbox.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        assert cbox.body_data == expected_result


@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.parametrize(
    ['payload', 'expected_result'],
    [
        (
            {
                'statuses': ['offline'],
                'date': '2019-09-04',
                'logins': ['user_{}'.format(num) for num in range(1, 11)],
            },
            {
                'items': [
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': 0.99,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 1200,
                            'daily_avg_sesions_by_support': 2.4,
                        },
                    },
                    {
                        'id': 'user_8',
                        'name': 'user_8',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'string',
                        'group': 'stats.realtime',
                        'id': 'status',
                        'label': 'status',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_support_sla',
                        'label': 'daily_support_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_support',
                        'label': 'daily_first_accept_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_support',
                        'label': 'daily_first_answer_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_aht_by_support',
                        'label': 'daily_aht_by_support',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_avg_sesions_by_support',
                        'label': 'daily_avg_sesions_by_support',
                    },
                ],
                'total': {
                    'daily_first_accept_by_support': 0,
                    'daily_first_answer_by_support': 0,
                    'daily_aht_by_support': 1200,
                    'daily_avg_sesions_by_support': 1.2,
                },
            },
        ),
        (
            {
                'statuses': [],
                'logins': ['user_{}'.format(num) for num in range(1, 11)],
            },
            {
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': 0.99,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 1200,
                            'daily_avg_sesions_by_support': 2.4,
                        },
                    },
                    {
                        'id': 'user_3',
                        'name': 'user_3',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_4',
                        'name': 'user_4',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_5',
                        'name': 'user_5',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_6',
                        'name': 'user_6',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_7',
                        'name': 'user_7',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_8',
                        'name': 'user_8',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_9',
                        'name': 'user_9',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                    {
                        'id': 'user_10',
                        'name': 'user_10',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': None,
                            'status': 'online',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 0,
                            'daily_avg_sesions_by_support': 0,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'string',
                        'group': 'stats.realtime',
                        'id': 'status',
                        'label': 'status',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_support_sla',
                        'label': 'daily_support_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_support',
                        'label': 'daily_first_accept_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_support',
                        'label': 'daily_first_answer_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_aht_by_support',
                        'label': 'daily_aht_by_support',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_avg_sesions_by_support',
                        'label': 'daily_avg_sesions_by_support',
                    },
                ],
                'total': {
                    'daily_first_accept_by_support': 0,
                    'daily_first_answer_by_support': 0,
                    'daily_aht_by_support': 1200,
                    'daily_avg_sesions_by_support': 0.24,
                },
            },
        ),
        (
            {'statuses': ['offline'], 'logins': ['user_2']},
            {
                'items': [
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': 0.99,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 1200,
                            'daily_avg_sesions_by_support': 2.4,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'string',
                        'group': 'stats.realtime',
                        'id': 'status',
                        'label': 'status',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_support_sla',
                        'label': 'daily_support_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_support',
                        'label': 'daily_first_accept_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_support',
                        'label': 'daily_first_answer_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_aht_by_support',
                        'label': 'daily_aht_by_support',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_avg_sesions_by_support',
                        'label': 'daily_avg_sesions_by_support',
                    },
                ],
                'total': {
                    'daily_first_accept_by_support': 0,
                    'daily_first_answer_by_support': 0,
                    'daily_aht_by_support': 1200,
                    'daily_avg_sesions_by_support': 2.4,
                },
            },
        ),
    ],
)
async def test_supporters_stats(
        cbox, patch_support_metrics_get_stat, payload, expected_result,
):
    await cbox.post('/v1/stat/realtime/supporters/', data=payload)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.parametrize(
    ['payload', 'expected_code', 'expected_result'],
    [
        ({'date': '2019-09-04', 'lines': ['driver_first']}, 400, {}),
        ({'date': '2019-09-04', 'lines': ['driver_first', 'vip']}, 400, {}),
        ({'date': '2019-09-04', 'lines': ['corp', 'vip']}, 400, {}),
        (
            {'date': '2019-09-04', 'lines': ['vip']},
            200,
            {
                'items': [
                    {
                        'id': '09:00-10:00',
                        'name': '09:00-10:00',
                        'stats': {
                            'hourly_create': 0,
                            'hourly_first_accept': 100,
                            'hourly_line_sla': 0.44,
                            'hourly_lost': 0,
                            'hourly_max_answer': 0,
                            'hourly_aht': 900,
                            'hourly_average_sessions': 1.5,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_create',
                        'label': 'hourly_create',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_first_accept',
                        'label': 'hourly_first_accept',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_lost',
                        'label': 'hourly_lost',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.load',
                        'id': 'hourly_line_sla',
                        'label': 'hourly_line_sla',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_max_answer',
                        'label': 'hourly_max_answer',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_aht',
                        'label': 'hourly_aht',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_average_sessions',
                        'label': 'hourly_average_sessions',
                    },
                ],
                'total': {
                    'hourly_create': 0,
                    'hourly_first_accept': 100,
                    'hourly_lost': 0,
                    'hourly_max_answer': 0,
                    'hourly_aht': 900,
                    'hourly_average_sessions': 1.5,
                },
            },
        ),
        (
            {'date': '2019-09-04', 'lines': ['corp']},
            200,
            {
                'items': [
                    {
                        'id': '09:00-10:00',
                        'name': '09:00-10:00',
                        'stats': {
                            'hourly_create': 15,
                            'hourly_first_accept': 10,
                            'hourly_line_sla': 1.0,
                            'hourly_lost': 0,
                            'hourly_max_answer': 0,
                            'hourly_aht': 900,
                            'hourly_average_sessions': 3,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_create',
                        'label': 'hourly_create',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_first_accept',
                        'label': 'hourly_first_accept',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_lost',
                        'label': 'hourly_lost',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.load',
                        'id': 'hourly_line_sla',
                        'label': 'hourly_line_sla',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_max_answer',
                        'label': 'hourly_max_answer',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_aht',
                        'label': 'hourly_aht',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_average_sessions',
                        'label': 'hourly_average_sessions',
                    },
                ],
                'total': {
                    'hourly_create': 15,
                    'hourly_first_accept': 10,
                    'hourly_lost': 0,
                    'hourly_max_answer': 0,
                    'hourly_aht': 900,
                    'hourly_average_sessions': 3,
                },
            },
        ),
        (
            {},
            200,
            {
                'items': [
                    {
                        'id': '09:00-10:00',
                        'name': '09:00-10:00',
                        'stats': {
                            'hourly_create': 15,
                            'hourly_first_accept': 110,
                            'hourly_line_sla': 0.491,
                            'hourly_lost': 0,
                            'hourly_max_answer': 0,
                            'hourly_aht': 1800,
                            'hourly_average_sessions': 4,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_create',
                        'label': 'hourly_create',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_first_accept',
                        'label': 'hourly_first_accept',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_lost',
                        'label': 'hourly_lost',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.load',
                        'id': 'hourly_line_sla',
                        'label': 'hourly_line_sla',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_max_answer',
                        'label': 'hourly_max_answer',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.load',
                        'id': 'hourly_aht',
                        'label': 'hourly_aht',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.load',
                        'id': 'hourly_average_sessions',
                        'label': 'hourly_average_sessions',
                    },
                ],
                'total': {
                    'hourly_create': 15,
                    'hourly_first_accept': 110,
                    'hourly_max_answer': 0,
                    'hourly_lost': 0,
                    'hourly_aht': 1800,
                    'hourly_average_sessions': 4,
                },
            },
        ),
    ],
)
async def test_stats_by_hour(
        cbox,
        patch_support_metrics_get_stat,
        payload,
        expected_code,
        expected_result,
):
    await cbox.post('/v1/stat/online/by_hour/', data=payload)
    assert cbox.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        data = cbox.body_data
        assert len(data['items']) == 24
        intervals_with_data = []
        for value in data['items']:
            if not any(value['stats'].values()):
                continue
            intervals_with_data.append(value)
        data['items'] = intervals_with_data
        assert data == expected_result


@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.translations(
    chatterbox={
        'lines.telephony_line': {'ru': 'Линия телефонии'},
        'success_call_gt5_lt10_name': {'ru': '>5, <10'},
    },
)
@pytest.mark.config(
    CHATTERBOX_STAT_IVR_CALLS_SETTINGS={
        'success_call': {
            'enabled': True,
            'conditions': [
                {
                    'title_tankers': {'count': 'success_call_gt5_lt10_name'},
                    'name': 'success_call_gt5_lt10',
                    'lower_limit': 5,
                    'upper_limit': 10,
                },
                {
                    'title_tankers': {'count': 'success_call_gt10_name'},
                    'name': 'success_call_gt10',
                    'lower_limit': 10,
                },
            ],
        },
        'missed_call': {
            'enabled': True,
            'conditions': [
                {
                    'name': 'missed_call_gt5_lt10',
                    'lower_limit': 5,
                    'upper_limit': 10,
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    ['payload', 'expected_code', 'expected_result'],
    [
        (
            {'date': '2019-09-04', 'lines': ['telephony_line']},
            200,
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.ivr_success_calls_count',
                        'id': 'ivr_success_calls_count_success_call_gt5_lt10',
                        'label': '>5, <10',
                    },
                    {
                        'format': 'string',
                        'group': 'stats.ivr_success_calls_count',
                        'id': (
                            'ivr_success_calls_count_percent'
                            '_success_call_gt5_lt10'
                        ),
                        'label': (
                            'ivr_success_calls_count_percent'
                            '_success_call_gt5_lt10'
                        ),
                    },
                    {
                        'format': 'number',
                        'group': 'stats.ivr_success_calls_count',
                        'id': 'ivr_success_calls_count_success_call_gt10',
                        'label': 'ivr_success_calls_count_success_call_gt10',
                    },
                    {
                        'format': 'string',
                        'group': 'stats.ivr_success_calls_count',
                        'id': (
                            'ivr_success_calls_count_'
                            'percent_success_call_gt10'
                        ),
                        'label': (
                            'ivr_success_calls_count_'
                            'percent_success_call_gt10'
                        ),
                    },
                    {
                        'format': 'number',
                        'group': 'stats.ivr_missed_calls_count',
                        'id': 'ivr_missed_calls_count_missed_call_gt5_lt10',
                        'label': 'ivr_missed_calls_count_missed_call_gt5_lt10',
                    },
                    {
                        'format': 'string',
                        'group': 'stats.ivr_missed_calls_count',
                        'id': (
                            'ivr_missed_calls_count_percent_'
                            'missed_call_gt5_lt10'
                        ),
                        'label': (
                            'ivr_missed_calls_count_percent_'
                            'missed_call_gt5_lt10'
                        ),
                    },
                ],
                'items': [
                    {
                        'id': '00:00-01:00',
                        'name': '00:00-01:00',
                        'stats': {
                            'ivr_missed_calls_count_missed_call_gt5_lt10': 12,
                            'ivr_success_calls_count_success_call_gt10': 0,
                            'ivr_success_calls_count_success_call_gt5_lt10': (
                                12
                            ),
                            'ivr_missed_calls_count_percent_'
                            'missed_call_gt5_lt10': '35.3%',
                            'ivr_success_calls_count_percent_'
                            'success_call_gt10': None,
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10': '30.0%',
                        },
                    },
                    {
                        'id': '01:00-02:00',
                        'name': '01:00-02:00',
                        'stats': {
                            'ivr_missed_calls_count_missed_call_gt5_lt10': 23,
                            'ivr_success_calls_count_success_call_gt10': 5,
                            'ivr_success_calls_count_success_call_gt5_lt10': (
                                23
                            ),
                            'ivr_missed_calls_count_percent_'
                            'missed_call_gt5_lt10': None,
                            'ivr_success_calls_count_percent_'
                            'success_call_gt10': '12.5%',
                            'ivr_success_calls_count_percent_'
                            'success_call_gt5_lt10': None,
                        },
                    },
                ],
                'total': {
                    'ivr_missed_calls_count_missed_call_gt5_lt10': 35,
                    'ivr_success_calls_count_success_call_gt10': 5,
                    'ivr_success_calls_count_success_call_gt5_lt10': 35,
                },
            },
        ),
    ],
)
async def test_ivr_calls_stats_by_hour(
        cbox,
        patch_support_metrics_get_stat,
        payload,
        expected_code,
        expected_result,
):
    await cbox.post('/v1/stat/ivr_calls/by_hour/', data=payload)
    assert cbox.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        data = cbox.body_data
        intervals_with_data = []
        for value in data['items']:
            if not any(value['stats'].values()):
                continue
            intervals_with_data.append(value)
        data['items'] = intervals_with_data
        assert data == expected_result


@pytest.mark.filldb(support_chatterbox='empty')
async def test_no_supporters_online(cbox):
    await cbox.post('/v1/stat/supporters_online/', data={})
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'supporters_online': 0}


@pytest.mark.parametrize(
    'data,expected_result',
    [
        (
            {},
            [{'login': 'admin1', 'chats': 2}, {'login': 'admin2', 'chats': 2}],
        ),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 1, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
            },
            [{'login': 'admin1', 'chats': 2}, {'login': 'admin2', 'chats': 2}],
        ),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 15, 0, 0),
                ),
            },
            [],
        ),
        ({'limit': 1}, [{'login': 'admin1', 'chats': 2}]),
        ({'limit': 1, 'offset': 1}, [{'login': 'admin2', 'chats': 2}]),
        (
            {'sort_by': 'login', 'sort_order': 'desc'},
            [{'login': 'admin2', 'chats': 2}, {'login': 'admin1', 'chats': 2}],
        ),
    ],
)
async def test_chats_by_supporter(cbox, data, expected_result):
    await cbox.post('/v1/stat/chats_by_supporter/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'chats_by_supporter': expected_result}


@pytest.mark.parametrize(
    'excluded,result',
    [
        (
            [],
            {
                'chats_by_status': [
                    {'status': 'archived', 'chats': 2},
                    {'chats': 1, 'status': 'closed'},
                    {'chats': 2, 'status': 'in_progress'},
                    {'chats': 2, 'status': 'offered'},
                ],
            },
        ),
        (
            ['archived', 'exported'],
            {
                'chats_by_status': [
                    {'chats': 1, 'status': 'closed'},
                    {'chats': 2, 'status': 'in_progress'},
                    {'chats': 2, 'status': 'offered'},
                ],
            },
        ),
    ],
)
async def test_chats_by_status(cbox, excluded, result):
    cbox.app.config.STATUSES_EXCLUDED_FROM_STAT = excluded

    await cbox.post('/v1/stat/chats_by_status/', data={})
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == result


@pytest.mark.parametrize(
    'data, expected_result',
    [
        ({'day': '2018-10-30', 'line': 'second'}, []),
        (
            {'day': '2018-10-30', 'in_addition': False},
            [
                {
                    'action_id': 'close',
                    'count': 1,
                    'average_latency': 60,
                    'min_latency': 60,
                    'max_latency': 60,
                },
            ],
        ),
        ({'day': '2018-05-06'}, []),
        ({'day': '2018-10-30', 'in_addition': True}, []),
    ],
)
@pytest.mark.now('2018-05-06')
async def test_actions(cbox, data, expected_result):
    await cbox.post('/v1/stat/actions/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'actions': expected_result}


@pytest.mark.parametrize(
    'data, expected_result',
    [
        ({}, {'actions_detailed': []}),
        (
            {
                'day_from': '2018-10-29',
                'day_to': '2018-10-31',
                'in_addition': False,
            },
            {
                'actions_detailed': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'count': 1,
                                'average_latency': 60,
                                'min_latency': 60,
                                'max_latency': 60,
                            },
                        ],
                        'date': '2018-10-30',
                    },
                ],
            },
        ),
    ],
)
async def test_actions_detailed(cbox, data, expected_result):
    await cbox.post('/v1/stat/actions_detailed/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {'day': '2018-10-30', 'sort_by': 'chats_taken'},
            {'actions_by_supporter': []},
        ),
        (
            {'day': '2018-10-30', 'login': 'admin1'},
            {'actions_by_supporter': []},
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'login': 'admin1',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                ],
            },
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'sort_by': 'chats_taken',
                'sort_order': 'desc',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 40.0,
                                'count': 2,
                                'max_latency': 70,
                                'min_latency': 10,
                            },
                        ],
                        'login': 'admin3',
                    },
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                    {
                        'actions': [
                            {
                                'action_id': 'dismiss',
                                'average_latency': 240.0,
                                'count': 1,
                                'max_latency': 240,
                                'min_latency': 240,
                            },
                        ],
                        'login': 'admin2',
                    },
                ],
            },
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1', 'admin2'],
                'sort_by': 'chats_taken',
                'sort_order': 'desc',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                    {
                        'actions': [
                            {
                                'action_id': 'dismiss',
                                'average_latency': 240.0,
                                'count': 1,
                                'max_latency': 240,
                                'min_latency': 240,
                            },
                        ],
                        'login': 'admin2',
                    },
                ],
            },
        ),
    ],
)
async def test_actions_by_supporter(cbox, data, expected_result):
    await cbox.post('/v1/stat/actions_by_supporter/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {'date': '2018-10-30'},
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [],
                'total': {},
            },
        ),
        (
            {'date': '2018-10-30', 'logins': ['admin1']},
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [],
                'total': {},
            },
        ),
        (
            {
                'date': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1'],
            },
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [
                    {'id': 'admin1', 'name': 'admin1', 'stats': {'take': 1}},
                ],
                'total': {'take': 1},
            },
        ),
        (
            {
                'date': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1', 'admin2'],
            },
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [
                    {'id': 'admin1', 'name': 'admin1', 'stats': {'take': 1}},
                    {
                        'id': 'admin2',
                        'name': 'admin2',
                        'stats': {'dismiss': 1},
                    },
                ],
                'total': {'take': 1, 'dismiss': 1},
            },
        ),
    ],
)
@pytest.mark.translations(chatterbox=OFFLINE_ACTIONS_STAT_TRANSLATIONS)
async def test_offline_actions(cbox, data, expected_result):
    await cbox.post('/v1/stat/offline/actions/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    'day, expected_status, expected_result',
    [
        (
            '2018-10-30',
            200,
            {
                'lines_statistics': [
                    {
                        'line': 'first',
                        'count': 3,
                        'first_answer_median': 100,
                        'full_resolve_median': 200,
                    },
                    {'line': 'urgent', 'count': 1},
                ],
                'total_statistics': {
                    'count': 4,
                    'first_answer_median': 100,
                    'full_resolve_median': 200,
                },
            },
        ),
        ('2018-10-29', 404, {'status': 'not_found'}),
    ],
)
async def test_common_stat(cbox, day, expected_status, expected_result):
    await cbox.post('v1/stat/common', data={'day': day, 'in_addition': False})
    assert cbox.status == expected_status
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    ['payload', 'expected_result', 'expected_raw_stat_params'],
    [
        (
            {'stat_day': '2019-10-11'},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 15,
                            'daily_success_calls_count': 13,
                            'daily_incoming_calls_count': 13,
                            'daily_success_calls_avg_duration': 108,
                            'daily_incoming_calls_avg_duration': 108,
                        },
                    },
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_total_calls_count': 13,
                            'daily_success_calls_count': 11,
                            'daily_incoming_calls_count': 11,
                            'daily_success_calls_avg_duration': 60,
                            'daily_incoming_calls_avg_duration': 60,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 28,
                    'daily_success_calls_count': 24,
                    'daily_success_calls_avg_duration': 86,
                    'daily_incoming_calls_count': 24,
                    'daily_incoming_calls_avg_duration': 86,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
            },
        ),
        (
            {'stat_day': '2019-10-11', 'logins': ['user_1']},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 15,
                            'daily_success_calls_count': 13,
                            'daily_incoming_calls_count': 13,
                            'daily_success_calls_avg_duration': 108,
                            'daily_incoming_calls_avg_duration': 108,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 15,
                    'daily_success_calls_count': 13,
                    'daily_incoming_calls_count': 13,
                    'daily_success_calls_avg_duration': 108,
                    'daily_incoming_calls_avg_duration': 108,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
                'logins': 'user_1',
            },
        ),
        (
            {
                'stat_day': '2019-10-11',
                'line': 'first',
                'logins': ['user_1', 'user_2'],
            },
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 10,
                            'daily_success_calls_count': 8,
                            'daily_incoming_calls_count': 8,
                            'daily_success_calls_avg_duration': 120,
                            'daily_incoming_calls_avg_duration': 120,
                        },
                    },
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_total_calls_count': 13,
                            'daily_success_calls_count': 11,
                            'daily_incoming_calls_count': 11,
                            'daily_success_calls_avg_duration': 66.7,
                            'daily_incoming_calls_avg_duration': 66.7,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 23,
                    'daily_success_calls_count': 19,
                    'daily_incoming_calls_count': 19,
                    'daily_success_calls_avg_duration': 89.1,
                    'daily_incoming_calls_avg_duration': 89.1,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_calculator|sip_success_calls_calculator|'
                    'sip_incoming_calls_calculator'
                ),
                'stat_interval': '1day',
                'line': 'first',
                'logins': 'user_1|user_2',
            },
        ),
        (
            {'stat_day': '2019-10-11', 'logins': ['user_3']},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [],
                'total': {},
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
                'logins': 'user_3',
            },
        ),
    ],
)
async def test_sip_calls_by_login(
        cbox,
        patch_support_metrics_stat_sip,
        payload,
        expected_result,
        expected_raw_stat_params,
):
    await cbox.post('/v1/stat/sip_calls/by_login', data=payload)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result
    raw_stat_call = patch_support_metrics_stat_sip.calls[0]
    assert raw_stat_call['kwargs']['params'] == expected_raw_stat_params


@pytest.mark.translations(
    chatterbox={
        'stats.config.chats_by_status': {
            'ru': 'Чаты по статусам',
            'en': 'Chats by status',
        },
        'stats.config.online_by_supporters': {
            'ru': 'Онлайн по саппортам',
            'en': 'Online by supporters',
        },
        'stats.config.logins': {'ru': 'Логины', 'en': 'Logins'},
        'stats.config.date': {'ru': 'Дата', 'en': 'Date'},
    },
)
@pytest.mark.config(
    CHATTERBOX_STATISTIC_HANDLERS=[
        {
            'id': 'chats-by-status',
            'name': 'stats.config.chats_by_status',
            'url': '/chats_by_status',
            'refreshPeriods': [900, 1200, 1800, 3600],
        },
        {
            'id': 'online-by-supporters',
            'name': 'stats.config.online_by_supporters',
            'filterFields': [
                {
                    'id': 'logins',
                    'type': 'logins',
                    'label': 'stats.config.logins',
                    'checks': ['not-empty'],
                },
                {
                    'id': 'date',
                    'type': 'date',
                    'label': 'stats.config.date',
                    'checks': ['not-empty'],
                },
            ],
            'url': '/realtime/supporters',
            'refreshPeriods': [900, 1200, 1800, 3600],
        },
    ],
)
@pytest.mark.parametrize(
    'locale, expected_body',
    [
        (
            'ru',
            {
                'types': [
                    {
                        'id': 'chats-by-status',
                        'name': 'Чаты по статусам',
                        'url': '/chats_by_status',
                        'refreshPeriods': [900000, 1200000, 1800000, 3600000],
                    },
                    {
                        'id': 'online-by-supporters',
                        'name': 'Онлайн по саппортам',
                        'filterFields': [
                            {
                                'id': 'logins',
                                'type': 'logins',
                                'label': 'Логины',
                                'checks': ['not-empty'],
                            },
                            {
                                'id': 'date',
                                'type': 'date',
                                'label': 'Дата',
                                'checks': ['not-empty'],
                            },
                        ],
                        'url': '/realtime/supporters',
                        'refreshPeriods': [900000, 1200000, 1800000, 3600000],
                    },
                ],
            },
        ),
    ],
)
async def test_get_stat_config(cbox, locale, expected_body):
    await cbox.query('/v1/stat/config', headers={'Accept-Language': locale})
    assert cbox.status == 200
    assert cbox.body_data == expected_body


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2019-06-07T00:00:59+0300')
@pytest.mark.parametrize(
    ['payload', 'expected_result'],
    [
        (
            {
                'statuses': ['offline'],
                'date': '2019-09-04',
                'logins': ['user_{}'.format(num) for num in range(1, 11)],
            },
            {
                'items': [
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': 0.99,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 1200,
                            'daily_avg_sesions_by_support': 2.4,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'string',
                        'group': 'stats.realtime',
                        'id': 'status',
                        'label': 'status',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_support_sla',
                        'label': 'daily_support_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_support',
                        'label': 'daily_first_accept_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_support',
                        'label': 'daily_first_answer_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_aht_by_support',
                        'label': 'daily_aht_by_support',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_avg_sesions_by_support',
                        'label': 'daily_avg_sesions_by_support',
                    },
                ],
                'total': {
                    'daily_first_accept_by_support': 0,
                    'daily_first_answer_by_support': 0,
                    'daily_aht_by_support': 1200,
                    'daily_avg_sesions_by_support': 2.4,
                },
            },
        ),
        (
            {
                'statuses': ['offline'],
                'date': '2019-09-04',
                'logins': ['user_5'],
            },
            {
                'items': [
                    {
                        'id': 'user_2',
                        'name': 'user_2',
                        'stats': {
                            'daily_first_accept_by_support': 0,
                            'daily_support_sla': 0.99,
                            'status': 'offline',
                            'daily_first_answer_by_support': 0,
                            'daily_aht_by_support': 1200,
                            'daily_avg_sesions_by_support': 2.4,
                        },
                    },
                ],
                'descriptions': [
                    {
                        'format': 'string',
                        'group': 'stats.realtime',
                        'id': 'status',
                        'label': 'status',
                    },
                    {
                        'format': 'percent',
                        'group': 'stats.by_day',
                        'id': 'daily_support_sla',
                        'label': 'daily_support_sla',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_first_accept_by_support',
                        'label': 'daily_first_accept_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_first_answer_by_support',
                        'label': 'daily_first_answer_by_support',
                    },
                    {
                        'format': 'duration',
                        'group': 'stats.by_day',
                        'id': 'daily_aht_by_support',
                        'label': 'daily_aht_by_support',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_avg_sesions_by_support',
                        'label': 'daily_avg_sesions_by_support',
                    },
                ],
                'total': {
                    'daily_first_accept_by_support': 0,
                    'daily_first_answer_by_support': 0,
                    'daily_aht_by_support': 1200,
                    'daily_avg_sesions_by_support': 2.4,
                },
            },
        ),
    ],
)
async def test_supporters_stats_limited(
        cbox,
        patch_support_metrics_get_stat,
        payload,
        expected_result,
        patch_auth,
        patch_tvm_auth,
):
    patch_auth(
        login='user_2', superuser=False, groups=['chatterbox_stat_limited'],
    )
    patch_tvm_auth('fake', 'fake')
    await cbox.post('/v1/stat/realtime/supporters/', data=payload)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'data,expected_result',
    [
        ({}, [{'login': 'admin1', 'chats': 2}]),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 1, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
            },
            [{'login': 'admin1', 'chats': 2}],
        ),
        (
            {
                'date_from': dates.timestring(
                    datetime.datetime(2018, 5, 10, 0, 0),
                ),
                'date_to': dates.timestring(
                    datetime.datetime(2018, 5, 15, 0, 0),
                ),
            },
            [],
        ),
        ({'limit': 1}, [{'login': 'admin1', 'chats': 2}]),
        ({'limit': 1, 'offset': 1}, []),
        (
            {'sort_by': 'login', 'sort_order': 'desc'},
            [{'login': 'admin1', 'chats': 2}],
        ),
    ],
)
async def test_chats_by_supporter_limited(
        cbox, data, expected_result, patch_auth, patch_tvm_auth,
):
    patch_auth(
        login='admin1', superuser=False, groups=['chatterbox_stat_limited'],
    )
    patch_tvm_auth('fake', 'fake')
    await cbox.post('/v1/stat/chats_by_supporter/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {'chats_by_supporter': expected_result}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {'day': '2018-10-30', 'sort_by': 'chats_taken'},
            {'actions_by_supporter': []},
        ),
        (
            {'day': '2018-10-30', 'login': 'admin1'},
            {'actions_by_supporter': []},
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'login': 'admin1',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                ],
            },
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'sort_by': 'chats_taken',
                'sort_order': 'desc',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                ],
            },
        ),
        (
            {
                'day': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1', 'admin2'],
                'sort_by': 'chats_taken',
                'sort_order': 'desc',
            },
            {
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'take',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'admin1',
                    },
                ],
            },
        ),
    ],
)
async def test_actions_by_supporter_limited(
        cbox, data, expected_result, patch_auth, patch_tvm_auth,
):
    patch_auth(
        login='admin1', superuser=False, groups=['chatterbox_stat_limited'],
    )
    patch_tvm_auth('fake', 'fake')
    await cbox.post('/v1/stat/actions_by_supporter/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {'date': '2018-10-30'},
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [],
                'total': {},
            },
        ),
        (
            {'date': '2018-10-30', 'logins': ['admin1']},
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [],
                'total': {},
            },
        ),
        (
            {
                'date': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1'],
            },
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [
                    {'id': 'admin1', 'name': 'admin1', 'stats': {'take': 1}},
                ],
                'total': {'take': 1},
            },
        ),
        (
            {
                'date': '2018-10-30',
                'in_addition': False,
                'line': 'first',
                'logins': ['admin1', 'admin2'],
            },
            {
                'descriptions': OFFLINE_ACTIONS_STAT_DESCRIPTIONS,
                'items': [
                    {'id': 'admin1', 'name': 'admin1', 'stats': {'take': 1}},
                ],
                'total': {'take': 1},
            },
        ),
    ],
)
@pytest.mark.translations(chatterbox=OFFLINE_ACTIONS_STAT_TRANSLATIONS)
async def test_offline_actions_limited(
        cbox, data, expected_result, patch_auth, patch_tvm_auth,
):
    patch_auth(
        login='admin1', superuser=False, groups=['chatterbox_stat_limited'],
    )
    patch_tvm_auth('fake', 'fake')
    await cbox.post('/v1/stat/offline/actions/', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ['payload', 'expected_result', 'expected_raw_stat_params'],
    [
        (
            {'stat_day': '2019-10-11'},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 15,
                            'daily_success_calls_count': 13,
                            'daily_incoming_calls_count': 13,
                            'daily_success_calls_avg_duration': 108,
                            'daily_incoming_calls_avg_duration': 108,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 15,
                    'daily_success_calls_count': 13,
                    'daily_success_calls_avg_duration': 108,
                    'daily_incoming_calls_count': 13,
                    'daily_incoming_calls_avg_duration': 108,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
                'logins': 'user_1',
            },
        ),
        (
            {'stat_day': '2019-10-11', 'logins': ['user_1']},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 15,
                            'daily_success_calls_count': 13,
                            'daily_incoming_calls_count': 13,
                            'daily_success_calls_avg_duration': 108,
                            'daily_incoming_calls_avg_duration': 108,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 15,
                    'daily_success_calls_count': 13,
                    'daily_incoming_calls_count': 13,
                    'daily_success_calls_avg_duration': 108,
                    'daily_incoming_calls_avg_duration': 108,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
                'logins': 'user_1',
            },
        ),
        (
            {'stat_day': '2019-10-11', 'logins': ['user_3']},
            {
                'descriptions': [
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_total_calls_count',
                        'label': 'daily_total_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_count',
                        'label': 'daily_success_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_success_calls_avg_duration',
                        'label': 'daily_success_calls_avg_duration',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_count',
                        'label': 'daily_incoming_calls_count',
                    },
                    {
                        'format': 'number',
                        'group': 'stats.by_day',
                        'id': 'daily_incoming_calls_avg_duration',
                        'label': 'daily_incoming_calls_avg_duration',
                    },
                ],
                'items': [
                    {
                        'id': 'user_1',
                        'name': 'user_1',
                        'stats': {
                            'daily_total_calls_count': 15,
                            'daily_success_calls_count': 13,
                            'daily_incoming_calls_count': 13,
                            'daily_success_calls_avg_duration': 108,
                            'daily_incoming_calls_avg_duration': 108,
                        },
                    },
                ],
                'total': {
                    'daily_total_calls_count': 15,
                    'daily_success_calls_count': 13,
                    'daily_incoming_calls_count': 13,
                    'daily_success_calls_avg_duration': 108,
                    'daily_incoming_calls_avg_duration': 108,
                },
            },
            {
                'created_ts': '2019-10-12T00:00:00+0300',
                'names': (
                    'sip_calls_by_login_calculator|'
                    'sip_success_calls_by_login_calculator|'
                    'sip_incoming_calls_by_login_calculator'
                ),
                'stat_interval': '1day',
                'logins': 'user_1',
            },
        ),
    ],
)
async def test_sip_calls_by_login_limited(
        cbox,
        patch_support_metrics_stat_sip,
        payload,
        expected_result,
        expected_raw_stat_params,
        patch_auth,
        patch_tvm_auth,
):
    patch_auth(
        login='user_1', superuser=False, groups=['chatterbox_stat_limited'],
    )
    patch_tvm_auth('fake', 'fake')
    await cbox.post('/v1/stat/sip_calls/by_login', data=payload)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_result
    raw_stat_call = patch_support_metrics_stat_sip.calls[0]
    assert raw_stat_call['kwargs']['params'] == expected_raw_stat_params
