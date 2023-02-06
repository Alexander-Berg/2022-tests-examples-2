import typing
from multiprocessing import Barrier

import pytest

import dmp_suite.cli.runners.migration as migration
import dmp_suite.migration.flow


class MockMigration(typing.NamedTuple):
    """Used to mock migrations without specifying their task."""
    path: str
    task: typing.Optional[
        typing.Type[
            dmp_suite.migration.flow.Migration
        ]
    ] = None
    manual: bool = False


@pytest.mark.parametrize(
    "path,expected", [
        ("etl", False),
        ("etl.package", False),
        ("etl.package.migrations", False),
        ("etl.migrations", True),
        ("etl.migrations.package", True),
    ]
)
def test_migration_filter(path, expected):
    actual = migration.migration_filter(path, False)
    assert actual == expected


def mock_is_migration_completed(path: str):
    return "completed" in path


@pytest.mark.parametrize(
    "migrations, expected_not_completed, expected_completed, expected_manual", [
        ([], [], [], []),
        ([MockMigration("task")], [MockMigration("task")], [], []),
        ([MockMigration("completed")], [], [MockMigration("completed")], []),
        (
        [MockMigration("completed"), MockMigration("task")], [MockMigration("task")], [MockMigration("completed")], []),
        ([MockMigration("completed"), MockMigration("task", manual=True)], [], [MockMigration("completed")],
         [MockMigration("task", manual=True)]),
        ([MockMigration("completed", manual=True)], [], [MockMigration("completed", manual=True)],[]),
    ]
)
def test_completed_migration_splitting(
        monkeypatch,
        migrations: typing.List[MockMigration],
        expected_not_completed: typing.List[MockMigration],
        expected_completed: typing.List[MockMigration],
        expected_manual: typing.List[MockMigration],
):
    monkeypatch.setattr(migration, "_is_migration_already_completed", mock_is_migration_completed)
    actual_not_completed, actual_completed, actual_manual = migration.split_migrations(migrations)  # type: ignore
    assert set(actual_not_completed) == set(expected_not_completed)
    assert set(actual_completed) == set(expected_completed)
    assert set(actual_manual) == set(expected_manual)


@pytest.mark.parametrize("parallel", [False, True])
@pytest.mark.parametrize(
    "migrations,expected", [
        ([MockMigration(' ')], 1),
        ([MockMigration(' '), MockMigration(' ')], 2),
        ([MockMigration(' '), MockMigration('')], 1),
    ]
)
def test_simple_migration_launch(monkeypatch, migrations, expected, parallel):
    """
    Тестируем, что возвращается суммарный результат применения всех миграций
    вне зависимости от способа запуска.
    """
    monkeypatch.setattr(migration, "_run_migration", len)
    actual = migration.run_migrations(migrations, run_sequentially=not parallel)  # type: ignore
    assert actual == expected


barrier = Barrier(4)


def dummy_migration(*args, **kwargs):
    """
    Локальная функция несереализуема, так что пришлось завести сюда.

    Нужно, чтобы проверить, что реально созданы отдельные треды.

    *args и **kwargs на случай, если интерфейс приватной функции
    изменится (что ожидаемо).
    """
    barrier.wait()
    return 0


def test_concurrent_migrations_launch(monkeypatch):
    """
    Тестируем, что реально создается 4 разных треда в случае 4 миграций.

    Если коротко, то тест может пройти только в случае, если были созданы
    4 конкурентных потока исполнения, которые ждут барьера.

    Потоки могут быть отдельными процессами или тредами или корутинами
    в рамках одного async loop'а, тестируется именно возможность запустить
    миграции конкурентно.
    """
    monkeypatch.setattr(migration, "_run_migration", dummy_migration)

    migrations = [MockMigration('task1'), MockMigration('task2'), MockMigration('task3'), MockMigration('task4')]
    actual = migration.run_migrations(migrations, run_sequentially=False)  # type: ignore
    assert actual == 0
