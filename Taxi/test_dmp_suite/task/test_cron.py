import pytest

from dmp_suite.task.base import (
    TaskBound,
    BoundPath, filter_rtc_task_bounds, filter_lxc_task_bounds,
)
from dmp_suite.task.cron import (
    Cron,
    CRON_USER,
    generate_cron_records,
    schedule_interval,
)
from test_dmp_suite.task.utils import create_task, fake_module


def _strip(string):
    return ' '.join(i for i in string.split(' ') if i)


def assert_cron_line(result, expected):
    assert [_strip(r) for r in result] == [_strip(e) for e in expected]


@pytest.mark.parametrize('times, user, retry_times, retry_sleep, timeout, use_local_queue, expected', [
    ('* * * * *', CRON_USER, None, None, None, False, [
        '* * * * *     www-data    python3.7 -m dmp_suite.runner task fake_module.task'
    ]),
    ('* * * * *', CRON_USER, None, None, None, False, [
        '* * * * *     www-data    python3.7 -m dmp_suite.runner task fake_module.task'
    ]),
    ('* * * * *', CRON_USER, None, None, None, False, [
        '* * * * *     www-data    python3.7 -m dmp_suite.runner task fake_module.task'
    ]),
    ('* * * * *', CRON_USER, 10, 20, 60, False, [
        '* * * * *     www-data    python3.7 -m dmp_suite.runner task -r 10 -s 20 -t 60 fake_module.task'
    ]),
    # Здесь проверим вариант с local-queue
    (['20 * * * *', '*/15 * * * *'], CRON_USER, None, None, None, True, [
        '20 * * * *    www-data    python3.7 -m dmp_suite.local_queue.push --queue-timeout 3600 task fake_module.task',
        '*/15 * * * *    www-data    python3.7 -m dmp_suite.local_queue.push --queue-timeout 900 task fake_module.task',
    ]),
])
def test_cron_line(times, user, retry_times, retry_sleep, timeout, use_local_queue, expected):
    cron = Cron(times, user=user, retry_times=retry_times, retry_sleep=retry_sleep, timeout=timeout)
    assert_cron_line(
        list(cron.generate(
            create_task('foo', cron),
            BoundPath(fake_module, 'task'),
            add_check_enabled_option=False,
            use_local_queue=use_local_queue,
        )),
        expected
    )


def test_cron_line_testing():
    cron = Cron('* * * * *', user=CRON_USER, retry_times=10, retry_sleep=20, timeout=60)
    expected = ['* * * * *     www-data    python3.7 -m dmp_suite.runner task --check-enabled -r 10 -s 20 -t 60 fake_module.task']
    assert_cron_line(
        list(cron.generate(
            create_task('foo', cron),
            BoundPath(fake_module, 'task'),
            add_check_enabled_option=True,
        )),
        expected
    )


def test_cron_interval_calculator():
    assert schedule_interval('* * * * *') == 60
    assert schedule_interval('40 1 * * *') == 86400
    assert schedule_interval('0 0,12 * * *') == 43200
    assert schedule_interval('45 */4 * * *') == 14400
    assert schedule_interval('42 * * * *') == 3600
    assert schedule_interval('*/30 * * * *') == 1800


def test_cron_line_no_scheduler_lock_option():
    cron = Cron('* * * * *', user=CRON_USER, retry_times=10, retry_sleep=20, timeout=60, use_scheduler_lock=False)

    expected = ['* * * * *     www-data    python3.7 -m dmp_suite.runner task --no-scheduler-lock -r 10 -s 20 -t 60 fake_module.task']
    task = create_task('foo', cron)
    assert_cron_line(
        list(cron.generate(
            task,
            BoundPath(fake_module, 'task'),
            add_check_enabled_option=False,
        )),
        expected
    )


class FakeScheduler:
    pass


def test_generate_cron_records():
    tasks = [
        create_task('task', Cron('* * * * *')),
        # skip task
        create_task('task_no_scheduler', None),
        create_task('task_fake_scheduler', FakeScheduler()),
    ]
    task_bounds = [TaskBound(task, {BoundPath(fake_module, task.name)}) for task in tasks]

    result = list(generate_cron_records(task_bounds, False, False))
    expected = ['* * * * *     www-data    python3.7 -m dmp_suite.runner task fake_module.task']
    assert_cron_line(result, expected)

    result = list(generate_cron_records(task_bounds, False, True))
    expected = ['* * * * *     www-data    python3.7 -m dmp_suite.local_queue.push --queue-timeout 60 task fake_module.task']
    assert_cron_line(result, expected)


def test_filter_lxc_task_bounds_when_gradual():
    # В режиме плавной миграции, для LXC в списке должны остаться
    # только таски у которых в Cron нет признака disable_lxc.
    tasks = [
        create_task('task1', Cron('* * * * *')),
        # Этот таск должен быть отфильтрован из-за явного указания флага:
        create_task('task2', Cron('* * * * *', disable_lxc=True)),
        # Этот таск должен быть отфильтрован,
        # потому что для него не задан крон:
        create_task('task3', None),
    ]
    task_bounds = [TaskBound(task, {BoundPath(fake_module, task.name)}) for task in tasks]

    filtered = filter_lxc_task_bounds(task_bounds, gradual_rtc_migration=True)
    assert len(filtered) == 1
    assert filtered[0].task.name == 'task1'


def test_filter_lxc_task_bounds_when_not_gradual():
    # В сервисах, которые перезжают целиком, для LXC в списке должны остаться
    # все таски у которых задан Cron. У таких сервисов крон в LXC
    # будет отключаться вручную удалением пакета:
    tasks = [
        create_task('task1', Cron('* * * * *')),
        # Этот таск будет присутствовать в кроне,
        # так как при gradual_rtc_migration=False
        # флаг disable_lxc игнорируется:
        create_task('task2', Cron('* * * * *', disable_lxc=True)),
        # Этот таск должен быть отфильтрован,
        # потому что для него не задан крон:
        create_task('task3', None),
    ]
    task_bounds = [TaskBound(task, {BoundPath(fake_module, task.name)}) for task in tasks]

    filtered = filter_lxc_task_bounds(task_bounds, gradual_rtc_migration=False)
    assert len(filtered) == 2
    assert filtered[0].task.name == 'task1'
    assert filtered[1].task.name == 'task2'


def test_filter_rtc_task_bounds_when_gradual():
    # В режиме плавной миграции, для RTC в крно должны попасть
    # только таски у которых в Cron есть признака enable_rtc.
    tasks = [
        # Тут признака нет, поэтому он будет отфильтрован:
        create_task('task1', Cron('* * * * *')),
        # Этот таск должен попасть в крон:
        create_task('task2', Cron('* * * * *', enable_rtc=True)),
        # Этот таск должен быть отфильтрован,
        # потому что для него не задан крон:
        create_task('task3', None),
    ]
    task_bounds = [TaskBound(task, {BoundPath(fake_module, task.name)}) for task in tasks]

    filtered = filter_rtc_task_bounds(task_bounds, gradual_rtc_migration=True)
    assert len(filtered) == 1
    assert filtered[0].task.name == 'task2'


def test_filter_rtc_task_bounds_when_not_gradual():
    # В сервисах, которые переезжают целиком, для RTC в списке должны остаться
    # все таски у которых задан Cron. Дальше при сборке образа или sandbox
    # ресурса, этот файл либо попадёт в контейнер либо нет. Но это
    # уже будет зависеть от настройки deploy_crons_to_rtc в service.yaml:
    tasks = [
        create_task('task1', Cron('* * * * *')),
        # В таком режиме нам всё равно, есть признак или нет.
        create_task('task2', Cron('* * * * *', enable_rtc=True)),
        # Этот таск должен быть отфильтрован,
        # потому что для него не задан крон:
        create_task('task3', None),
    ]
    task_bounds = [TaskBound(task, {BoundPath(fake_module, task.name)}) for task in tasks]

    filtered = filter_rtc_task_bounds(task_bounds, gradual_rtc_migration=False)
    assert len(filtered) == 2
    assert filtered[0].task.name == 'task1'
    assert filtered[1].task.name == 'task2'
