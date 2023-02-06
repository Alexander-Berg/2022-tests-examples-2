import pytest
from easytap.pytest_plugin import PytestTap


async def test_parallel(tap: PytestTap):
    with tap.plan(1):
        tap.ok(True, 'Тест запустился парллельно')


@pytest.mark.non_parallel
async def test_non_parallel(tap: PytestTap):
    with tap.plan(1):
        tap.ok(True, 'Тест запущен последовательно')
