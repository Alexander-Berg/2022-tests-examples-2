import pytest


@pytest.fixture(name='run_cargo_distlock_worker')
def _run_cargo_distlock_worker(testpoint):
    def _parse_statistics(stats):
        stats_by_alias = {}
        if stats is None:
            return stats_by_alias
        for alias, alias_value in stats['distlock_worker'].items():
            if alias == '$meta':
                continue
            for level, level_value in alias_value.items():
                if level == '$meta':
                    continue
                for metric_type, value in level_value.items():
                    if metric_type == '$meta':
                        continue
                    stats_by_alias[alias] = value
        return stats_by_alias

    async def _wrapper(service_fixture, task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await service_fixture.run_distlock_task(task_name)
        args = await task_result.wait_call()

        return _parse_statistics(args['result'])

    return _wrapper
