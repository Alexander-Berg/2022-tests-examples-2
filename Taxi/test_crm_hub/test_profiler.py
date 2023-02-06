# pylint: disable=import-only-modules
from crm_common.profiler import Profiler


async def test_profiler_example():
    # Two calls are suitable if you don't wish to change main code indentation.
    # 'With' shortens code but requires changing indentation level.
    # You are free to mix them
    Profiler.enter('level1')
    data = []
    Profiler.enter('level2_A')
    for _ in range(10):
        data.extend(range(10000))
    for _ in range(10000000):
        pass
    Profiler.exit('level2_A')

    for _ in range(20):
        with Profiler('level2_B'):
            data.extend(range(10000))
            for _ in range(2000000):
                pass

    for _ in range(40):
        data.extend(range(10000))

    for _ in range(30):
        Profiler.enter('level2_C')
        data.extend(range(10000))
        Profiler.exit('level2_C')

    Profiler.exit()
    Profiler.time_usage_log()
    Profiler.memory_usage_log()
