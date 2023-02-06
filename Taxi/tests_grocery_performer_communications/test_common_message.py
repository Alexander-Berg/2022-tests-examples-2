import pytest

import tests_grocery_performer_communications.constants as consts

TASK_ID = '08febfa0422ddd16a25fb785137b868f20d53380c357ee4c8f3fa0fc3f7fea25'

TITLE = {'key': 'common_message_title'}

TEXT = {
    'key': 'common_message_template',
    'args': [
        {'name': 'int_var', 'value': {'value': 123456, 'type': 'int'}},
        {
            'name': 'str_var',
            'value': {'value': 'qwertyuiop', 'type': 'string'},
        },
        {'name': 'double_var', 'value': {'value': 123.45, 'type': 'double'}},
        {'name': 'date_var', 'value': {'value': '2017-04-04', 'type': 'date'}},
        {
            'name': 'datetime_var',
            'value': {
                'value': '2017-04-04T15:32:22+10:00',
                'type': 'datetime',
            },
        },
        {
            'name': 'datetimef_var',
            'value': {
                'value': '2017-04-04T15:32:22+10:00',
                'type': 'datetime',
                'format': '%Y-%m-%d %H:%M:%S',
            },
        },
        {
            'name': 'price_var',
            'value': {'value': '123.45', 'type': 'price', 'currency': 'RUB'},
        },
        {
            'name': 'neg_price_var',
            'value': {'value': '-123.45', 'type': 'price', 'currency': 'RUB'},
        },
    ],
}

FEEDS_SERVICE = 'test_service'


@pytest.mark.experiments3(filename='experiments3.json')
async def test_grocery_performer_communications_common_message(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        assert request.json == {
            'id': TASK_ID,
            'service': FEEDS_SERVICE,
            'template': {
                'title': {
                    'keyset': consts.KEYSET,
                    'key': 'common_message_title',
                    'params': {},
                },
                'text': {
                    'keyset': consts.KEYSET,
                    'key': 'common_message_template',
                    'params': {
                        'int_var': '123456',
                        'str_var': 'qwertyuiop',
                        'double_var': '123.45',
                        'date_var': '2017-04-04',
                        'datetime_var': '04-04-2017 08:32:22',
                        'datetimef_var': '2017-04-04 08:32:22',
                        'price_var': '123,45 руб.',
                        'neg_price_var': '-123,45 руб.',
                    },
                },
                'type': 'newsletter',
                'format': 'markdown',
            },
            'drivers': [{'driver': consts.PERFORMER_ID}],
        }
        assert request.headers['X-Idempotency-Token'] == TASK_ID
        return mockserver.make_response(status=200, json={'id': '1'})

    @testpoint('common_message_task_finished_success')
    def task_finished(param):
        pass

    await stq_runner.grocery_performer_communications_common_message.call(
        task_id=TASK_ID,
        args=[
            consts.PERFORMER_ID,
            TITLE,
            TEXT,
            consts.DEPOT_ID_LEGACY,
            FEEDS_SERVICE,
        ],
    )

    assert driver_wall_add.times_called == 1
    assert task_finished.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_common_message': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_common_message_reschedule_if_error_driver_wall_return(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_common_message_' 'task_rescheduled',
    )
    def task_rescheduled(param):
        assert param['task_id'] == TASK_ID
        assert param['delay'] == 2000

    await stq_runner.grocery_performer_communications_common_message.call(
        task_id=TASK_ID,
        args=[
            consts.PERFORMER_ID,
            TITLE,
            TEXT,
            consts.DEPOT_ID_LEGACY,
            FEEDS_SERVICE,
        ],
    )

    assert driver_wall_add.times_called == 1
    assert task_rescheduled.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_common_message': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_common_message_stop_reschedule_when_exceed_counter(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_common_message_'
        'task_finished_count_reached',
    )
    def task_reschedule_finished(param):
        pass

    await stq_runner.grocery_performer_communications_common_message.call(
        task_id=TASK_ID,
        args=[
            consts.PERFORMER_ID,
            TITLE,
            TEXT,
            consts.DEPOT_ID_LEGACY,
            FEEDS_SERVICE,
        ],
        reschedule_counter=11,
    )

    assert driver_wall_add.times_called == 1
    assert task_reschedule_finished.times_called == 1
