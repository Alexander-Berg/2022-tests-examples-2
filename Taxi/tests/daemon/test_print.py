import asyncio

from stall.daemon.print import PrintDaemon


class Daemon(PrintDaemon):
    printed: list

    def __init__(self, *args, waiter=None, **kwargs):
        self.printed = []
        self.waiter = waiter

        super().__init__(*args, **kwargs)

    async def print(self, target, file_type, document):
        self.printed.append((target, file_type, document))
        if self.waiter:
            self.waiter.set_result(self.printed[-1])



async def test_ping(tap, dataset, server):
    with tap.plan(7):
        app = await server(spec=('doc/api/print-client.yaml',
                                 'doc/api/ev.yaml'))
        tap.ok(app, 'Сервер создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        atrun = asyncio.get_event_loop().create_future()
        atexit = asyncio.get_event_loop().create_future()

        daemon = Daemon(
            event_url = f'http://localhost:{app.port}/api/ev',
            print_client_url = f'http://localhost:{app.port}/api/print-client',
            print_client_token = store.printer_token,
            event_timeout=1,
            store_id=store.store_id,
        )

        tap.ok(daemon, 'Демон инстанцирован')
        asyncio.get_event_loop().create_task(
            daemon.run(atrun=atrun, atexit=atexit)
        )

        tap.ok(await asyncio.wait_for(atrun, timeout=5), 'Демон запущен')
        tap.ok(await daemon.ping(), 'ping')

        await daemon.stop()
        tap.ok(not daemon.is_run, 'Демон остановлен')
        tap.ok(await atexit, 'Демон остановлен')

        # pylint: disable=protected-access
        await dataset.Event._stop_daemon()


async def test_print_exists_task(tap, dataset, server):
    with tap.plan(10):
        app = await server(spec=('doc/api/print-client.yaml',
                                 'doc/api/ev.yaml'))
        tap.ok(app, 'Сервер событий создан')

        waiter = asyncio.get_event_loop().create_future()

        store = await dataset.store()
        task = await dataset.printer_task(store=store, payload='hello')
        tap.ok(task, 'задача создана')

        tap.ok(store, 'склад создан')

        atrun = asyncio.get_event_loop().create_future()
        atexit = asyncio.get_event_loop().create_future()

        daemon = Daemon(
            event_url = f'http://localhost:{app.port}/api/ev',
            print_client_url = f'http://localhost:{app.port}/api/print-client',
            print_client_token = store.printer_token,
            event_timeout=1,
            store_id=store.store_id,
            waiter=waiter,
        )

        tap.ok(daemon, 'Демон инстанцирован')
        asyncio.get_event_loop().create_task(
            daemon.run(atrun=atrun, atexit=atexit)
        )

        tap.ok(await atrun, 'Демон запущен')

        print_item = await waiter

        tap.eq(print_item[0], task.target, 'target')
        tap.eq(print_item[1], task.type, 'type')
        tap.eq(print_item[2], 'hello', 'payload')

        await daemon.stop()
        tap.ok(not daemon.is_run, 'Демон остановлен')
        tap.ok(await atexit, 'Демон остановлен')
        # pylint: disable=protected-access
        await dataset.Event._stop_daemon()



async def test_print(tap, dataset, server):
    with tap.plan(10):
        app = await server(spec=('doc/api/print-client.yaml',
                                 'doc/api/ev.yaml'))
        tap.ok(app, 'Сервер событий создан')

        waiter = asyncio.get_event_loop().create_future()

        store = await dataset.store()

        tap.ok(store, 'склад создан')

        atrun = asyncio.get_event_loop().create_future()
        atexit = asyncio.get_event_loop().create_future()

        daemon = Daemon(
            event_url = f'http://localhost:{app.port}/api/ev',
            print_client_url = f'http://localhost:{app.port}/api/print-client',
            print_client_token = store.printer_token,
            event_timeout=1,
            store_id=store.store_id,
            waiter=waiter,
        )

        tap.ok(daemon, 'Демон инстанцирован')
        asyncio.get_event_loop().create_task(
            daemon.run(atrun=atrun, atexit=atexit)
        )
        tap.ok(await atrun, 'Демон запущен')

        await asyncio.sleep(.5)

        task = await dataset.printer_task(store=store, payload='hello')
        tap.ok(task, 'задача создана')

        print_item = await waiter

        tap.eq(print_item[0], task.target, 'target')
        tap.eq(print_item[1], task.type, 'type')
        tap.eq(print_item[2], 'hello', 'payload')

        await daemon.stop()
        tap.ok(not daemon.is_run, 'Демон остановлен')
        tap.ok(await atexit, 'Демон остановлен')

        # pylint: disable=protected-access
        await dataset.Event._stop_daemon()

