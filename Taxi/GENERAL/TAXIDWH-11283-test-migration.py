from dmp_suite.task.execution import run_task, ExecutionMode
from dmp_suite.migration import migration
from dmp_suite.task import PyTask
# from dmp_suite.yt.migration import add_columns


def do_nothing():
    print('Doing nothing')


step = PyTask('do-nothing', do_nothing)
step.idempotent = True

migration_task = migration(
    'TAXIDWH-11283',
    # add_columns(SomeTable),
    step,
)

# Пример запуска в админке:
# https://tariff-editor.taxi.tst.yandex-team.ru/dev/scripts/493d8315ac1743a1965c232fd5be2402
if __name__ == '__main__':
    run_task(
        migration_task,
        execution_mode=ExecutionMode.GRAPH
    )
