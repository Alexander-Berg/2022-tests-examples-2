import asyncio

import pytest

from crawler_pool import components


@pytest.mark.config(CRAWLER_CONFIG={'max_rate': 5})
@pytest.mark.parametrize(
    'settings,expected_rate',
    [
        [{'config_name': 'CRAWLER_CONFIG', 'max_rate': 10}, 5],
        [{'max_rate': 10}, 10],
    ],
)
async def test_should_correct_set_max_rate(
        library_context, settings, expected_rate,
):
    pool = components.CrawlerPool(library_context, settings)
    await pool.on_startup()
    await asyncio.sleep(1)
    assert pool._max_rate == expected_rate  # pylint: disable=protected-access
    await pool.on_shutdown()


async def test_should_run_all_tasks(library_context):
    async def _test_coro1():
        await asyncio.sleep(0.1)
        return 1

    def _test_coro2():
        return _test_coro1()

    pool = components.CrawlerPool(library_context, {'max_rate': 5})
    await pool.on_startup()
    result1 = await pool.get_data([_test_coro1() for _ in range(0, 10)])
    result2 = await pool.get_data([_test_coro2() for _ in range(0, 10)])
    assert len(result1.items) == 10
    assert len(result2.items) == 10
    await pool.on_shutdown()
