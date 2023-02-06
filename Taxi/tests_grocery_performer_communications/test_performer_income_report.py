import pytest

import tests_grocery_performer_communications.constants as consts

# idempotency key for driver-wall service is sha256 hash of
# {performer_id}_{period_start}_{report_type}
PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256 = (
    '08febfa0422ddd16a25fb785137b868f20d53380c357ee4c8f3fa0fc3f7fea25'
)

TASK_ID = PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256


@pytest.mark.experiments3(filename='experiments3.json')
async def test_grocery_performer_communications_performer_income_report_weekly(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        assert request.json == {
            'id': PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256,
            'service': 'test_service',
            'template': {
                'title': {
                    'keyset': consts.KEYSET,
                    'key': 'performer_income_report_title',
                    'params': {},
                },
                'text': {
                    'keyset': consts.KEYSET,
                    'key': 'performer_income_report_template',
                    'params': {
                        'adjustment': '-30.22 ₪',
                        'employer': 'Self-employed',
                        'hours_total': '7.5',
                        'order_count': '24',
                        'period_end': '22.07',
                        'period_start': '15.07',
                        'slot_count': '10',
                        'tips': '25.11 ₪',
                        'total_income': '295.42 ₪',
                        'weekdays_duration_income': '100.31 ₪',
                        'weekdays_hours': '6',
                        'weekdays_orders': '17',
                        'weekdays_orders_income': '120.01 ₪',
                        'weekends_duration_income': '20 ₪',
                        'weekends_hours': '1.5',
                        'weekends_orders': '7',
                        'weekends_orders_income': '60.21 ₪',
                    },
                },
                'type': 'newsletter',
                'format': 'markdown',
            },
            'drivers': [{'driver': consts.PERFORMER_ID}],
        }
        assert (
            request.headers['X-Idempotency-Token']
            == PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256
        )
        return mockserver.make_response(status=200, json={'id': '1'})

    @testpoint('performer_income_report_task_finished_success')
    def task_finished(param):
        pass

    income_report = (
        stq_runner.grocery_performer_communications_performer_income_report
    )
    await income_report.call(
        task_id=TASK_ID,
        args=[consts.PERFORMER_ID, consts.REPORT_TYPE, consts.REPORT],
    )

    assert driver_wall_add.times_called == 1
    assert task_finished.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_performer_income_report': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_performer_income_report_reschedule_if_error_driver_wall_return(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_performer_income_report_'
        'task_rescheduled',
    )
    def task_rescheduled(param):
        assert param['task_id'] == TASK_ID
        assert param['delay'] == 2000

    income_report = (
        stq_runner.grocery_performer_communications_performer_income_report
    )
    await income_report.call(
        task_id=TASK_ID,
        args=[consts.PERFORMER_ID, consts.REPORT_TYPE, consts.REPORT],
    )

    assert driver_wall_add.times_called == 1
    assert task_rescheduled.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_performer_income_report': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_performer_income_report_stop_reschedule_when_exceed_counter(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_performer_income_report_'
        'task_finished_count_reached',
    )
    def task_reschedule_finished(param):
        pass

    income_report = (
        stq_runner.grocery_performer_communications_performer_income_report
    )
    await income_report.call(
        task_id=TASK_ID,
        args=[consts.PERFORMER_ID, consts.REPORT_TYPE, consts.REPORT],
        reschedule_counter=11,
    )

    assert driver_wall_add.times_called == 1
    assert task_reschedule_finished.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_performer_communications_performer_income_report',
    consumers=['grocery-performer-communications/performer-income-report'],
    clauses=[],
    default_value={
        'feeds_service': 'test_service',
        'is_enabled': True,
        'locale': 'en',
        'template_tanker_key': 'performer_income_report_template_extra',
        'title_tanker_key': 'performer_income_report_title',
    },
    is_config=True,
)
async def test_grocery_performer_communications_performer_income_report_extra(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        assert request.json == {
            'id': PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256,
            'service': 'test_service',
            'template': {
                'title': {
                    'keyset': consts.KEYSET,
                    'key': 'performer_income_report_title',
                    'params': {
                        'extra_argument': 'extra field value',
                        'unused_argument': 'unused argument value',
                    },
                },
                'text': {
                    'keyset': consts.KEYSET,
                    'key': 'performer_income_report_template_extra',
                    'params': {
                        'adjustment': '+30.22 ₪',
                        'employer': 'Self-employed',
                        'extra_argument': 'extra field value',
                        'hours_total': '7.5',
                        'order_count': '24',
                        'period_end': '22.07',
                        'period_start': '15.07',
                        'slot_count': '10',
                        'tips': '25.11 ₪',
                        'total_income': '295.42 ₪',
                        'unused_argument': 'unused argument value',
                    },
                },
                'type': 'newsletter',
                'format': 'markdown',
            },
            'drivers': [{'driver': consts.PERFORMER_ID}],
        }
        assert (
            request.headers['X-Idempotency-Token']
            == PERFORMER_ID_PERIOD_START_REPORT_TYPE_SHA256
        )
        return mockserver.make_response(status=200, json={'id': '1'})

    @testpoint('performer_income_report_task_finished_success')
    def task_finished(param):
        pass

    income_report = (
        stq_runner.grocery_performer_communications_performer_income_report
    )
    await income_report.call(
        task_id=TASK_ID,
        args=[consts.PERFORMER_ID, consts.REPORT_TYPE, consts.REPORT_EXTRA],
    )

    assert driver_wall_add.times_called == 1
    assert task_finished.times_called == 1
