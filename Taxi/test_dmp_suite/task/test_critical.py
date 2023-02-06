from dmp_suite.critical import is_critical
from dmp_suite.task.base import PyTask
from dmp_suite.task.execution import run_task


def test_not_critical_task():
    # Проверим, что флаг не выставляется
    # при выполнении критичного таска.
    def func(args):
        assert is_critical() is False

    task = PyTask('task', func)

    run_task(task)


def test_critical_task():
    # Проверим, что флаг выставляется
    # при выполнении критичного таска.
    def func(args):
        assert is_critical() is True

    task = PyTask('task', func).critical()

    run_task(task)
