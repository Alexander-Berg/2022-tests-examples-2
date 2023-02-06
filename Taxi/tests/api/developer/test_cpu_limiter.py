import asyncio
import pytest


@pytest.mark.parametrize('interval', [1.0, 2.0])
async def test_cpu_limiter_pc(tap, cfg, http_api, interval):
    with tap.plan(4, 'Проверяем работу лимитера - очень низкий порог - %'):

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '3')


@pytest.mark.parametrize('interval', [1.0, 2.0])
async def test_cpu_limiter_rps(tap, cfg, http_api, interval):
    with tap.plan(4, 'Проверяем работу лимитера - очень низкий порог - rps'):

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_rps': 0, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '3')


async def test_rps_timings(tap, cfg, http_api):
    with tap.plan(20, 'Проверяем реальное ограничение по rps'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_rps': 1, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        tap.note('первый запрос уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.header_hasnt('Retry-After')

        tap.note('второй запрос не уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '3')

        tap.note('третий запрос не уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '3')

        tap.note('Подождем следующей секунды')
        await asyncio.sleep(1.0)

        tap.note('четвертый запрос уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.header_hasnt('Retry-After')

        tap.note('пятый запрос не уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '3')


async def test_rps_begin(tap, cfg, http_api):
    with tap.plan(6, 'Проверяем наполнение очереди подсчета rps'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_rps': 2}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        tap.note('первый запрос уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.note('второй запрос уложился в лимит')
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_cpu_limiter_normal(http_api, tap, cfg):
    with tap.plan(4, 'Проверяем работу лимитера - не сработал'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 100, 'retry': 4}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.header_hasnt('Retry-After')


async def test_cpu_limiter_rand(tap, cfg, http_api):
    with tap.plan(4, 'Повторы можно разбрасывать в диапазоне'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': {'min': 5, 'max': 10}}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_has('Retry-After')


@pytest.mark.skip(reason='fix after arcadia')
async def test_cpu_limiter_porto(tap, cfg, http_api):
    with tap.plan(4, 'Проверяем работу лимитера - очень низкий порог'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'porto']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 20, 'limit_pc': 0, 'retry': 5}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        # pylint: disable=unused-argument,import-outside-toplevel
        # pylint: disable=protected-access
        def _mock_cpu_percent(self, interval: float = 1.0):
            import time
            time.sleep(interval)
            return 50

        from stall.plugins.cpu_watcher import CpuWatcherSourcePorto
        CpuWatcherSourcePorto._cpu_percent = _mock_cpu_percent

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_TOO_MANY_REQUESTS')
        t.header_is('Retry-After', '5')


async def test_disabled(tap, cfg, http_api):
    with tap.plan(2, 'Лимитер не включен - лимитер не работает'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', False]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)


async def test_cpu_watcher_disabled(tap, cfg, http_api):
    with tap.plan(2, 'Плагин cpu_watcher не включен - лимитер не работает'):
        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', False]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(1.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)


async def test_no_data(tap, cfg, http_api):
    with tap.plan(2, 'Данных нет - лимитер не работает'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'porto']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': 6}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        # pylint: disable=unused-argument,import-outside-toplevel
        # pylint: disable=protected-access,useless-return
        def _mock_cpu_percent(self, interval: float = 1.0):
            import time
            time.sleep(interval)
            return None

        from stall.plugins.cpu_watcher import CpuWatcherSourcePorto
        CpuWatcherSourcePorto._cpu_percent = _mock_cpu_percent

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)


async def test_threshold(tap, cfg, http_api):
    with tap.plan(2, 'Список порогов не задан - лимитер не работает'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', False]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            []
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)


async def test_fake(tap, cfg, http_api):
    with tap.plan(2, 'Проверяем работу лимитера - фейковый режим'):
        interval = 1.0

        cfg(op=[['set', 'web.plugin.cpu_watcher.enable', True]])
        cfg(op=[['set', 'web.plugin.cpu_watcher.source', 'psutil']])
        cfg(op=[['set', 'web.plugin.cpu_watcher.interval', interval]])
        cfg(op=[['set', 'web.limiter.cpu.enable', True]])
        cfg(op=[['set', 'web.limiter.cpu.fake', True]])
        cfg(op=[[
            'set',
            'web.limiter.cpu.threshold',
            [{'load': 0, 'limit_pc': 0, 'retry': 3}]
        ]])
        cfg(op=[['set', 'web.limiter.cpu.log', 'debug']])

        t = await http_api()

        # UGLY: подождем данных
        await asyncio.sleep(interval + 0.5)

        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
