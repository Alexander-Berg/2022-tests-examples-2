import asyncio
import json

from taxi import default_executor
from taxi.logs import auto_log_extra


async def test_log_extra_copying():
    dumped_extras = []

    def dump_log_extra():
        """Writing logs equivalent."""
        dumped_extras.append(json.dumps(auto_log_extra.get_log_extra()))

    def test():
        auto_log_extra.update_log_extra(foo='foo')
        dump_log_extra()

    auto_log_extra.update_log_extra(foo='bar')
    dump_log_extra()
    asyncio.get_event_loop().run_in_executor(
        default_executor.ThreadPoolExecutor(), test,
    )
    dump_log_extra()

    assert len(dumped_extras) == 3
    dumped_extras = [json.loads(extra) for extra in dumped_extras]

    links = [extra.pop('_link') for extra in dumped_extras]
    assert len(set(links)) == 1

    foos = [extra['extdict']['foo'] for extra in dumped_extras]
    assert foos == ['bar', 'foo', 'bar']
