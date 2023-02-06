# pylint: disable=unused-argument,protected-access

import asyncio

from stall.daemon.replication import ReplicationDaemonBase


async def test_block(tap, uuid):
    with tap.plan(3, 'запуск и остановка демона'):

        class MyTestDaemon(ReplicationDaemonBase):
            result = None

            async def _process(self, cursor: str = None):
                self.result = True
                return cursor

        daemon = MyTestDaemon(
            timeout_error = 1,
            timeout_empty = 1,
            stash=f'test-replication-daemon-{uuid()}',
            lock=f'test-replication-daemon-{uuid()}',
        )
        tap.ok(daemon, 'Демон создан')

        async def _shutdown():
            await asyncio.sleep(0.5)
            daemon.shutdown()

        try:
            await asyncio.wait(
                {asyncio.create_task(daemon.process()), _shutdown()},
                timeout=60.0,  # общий таймаут на тест
            )
        except asyncio.TimeoutError:
            tap.failed('timeout')
        else:
            tap.passed('timeout')

        tap.ok(daemon.result, 'Обработчик запускался')


async def test_cursor_error(tap, uuid):
    with tap.plan(
            10,
            'В какой-то момент не смогли получить данные '
            'и не вернули новый курсор'
    ):
        class MyTestDaemon(ReplicationDaemonBase):
            count = 0

            async def _process(self, cursor: str = None):
                if self.count == 0:
                    tap.eq(cursor, None, 'первый курсор с None')
                else:
                    tap.ne(
                        cursor,
                        None,
                        f'итерация {self.count} с курсором'
                    )

                cursor = self.count = self.count + 1

                if self.count == 5:
                    tap.passed('последняя итерация')
                    self.shutdown()

                if self.count == 3:
                    tap.passed('данные не были получены и вернули None')
                    return None

                return cursor

        daemon = MyTestDaemon(
            timeout_error = 1,
            timeout_empty = 1,
            stash=f'test-replication-daemon-{uuid()}',
            lock=f'test-replication-daemon-{uuid()}',
        )
        tap.ok(daemon, 'Демон создан')

        try:
            await asyncio.wait(
                {asyncio.create_task(daemon.process())},
                timeout=60.0,  # общий таймаут на тест
            )
        except asyncio.TimeoutError:
            tap.failed('timeout')
        else:
            tap.passed('timeout ')

        tap.eq(daemon.count, 5, 'все тестовые итерации прошли')


async def test_cursor_none(tap, uuid):
    with tap.plan(4, 'Запустили демон, но данных нет'):

        class MyTestDaemon(ReplicationDaemonBase):
            count = 0

            async def _process(self, cursor: str = None):
                self.count = self.count + 1

                if self.count == 5:
                    tap.passed('последняя итерация')
                    self.shutdown()

                return None

        daemon = MyTestDaemon(
            timeout_error = 1,
            timeout_empty = 1,
            stash=f'test-replication-daemon-{uuid()}',
            lock=f'test-replication-daemon-{uuid()}',
        )
        tap.ok(daemon, 'Демон создан')

        try:
            await asyncio.wait(
                {asyncio.create_task(daemon.process())},
                timeout=60.0,  # общий таймаут на тест
            )
        except asyncio.TimeoutError:
            tap.failed('timeout')
        else:
            tap.passed('timeout')

        tap.eq(daemon.count, 5, 'все тестовые итерации прошли')


async def test_instances(tap, uuid):
    with tap.plan(10, 'Запускаем несколько демонов параллельно'):

        def _gen_cursor():
            for i in range(1, 100):
                yield i
        _cursor = _gen_cursor()

        class MyTestDaemon(ReplicationDaemonBase):
            count: int = 0
            number: int = None

            def __init__(self, **kwargs):
                self.number = kwargs.get('number')
                super().__init__(**kwargs)

            async def _process(self, cursor: str = None):
                tap.note(
                    f'демон {self.number} '
                    f'итерация {self.count} '
                    f'курсор {cursor}'
                )

                if cursor is not None and cursor >= 5:
                    tap.passed('изменений больше нет')
                    self.shutdown()
                    return cursor

                cursor = next(_cursor)
                self.count += 1

                if not cursor % 3:
                    tap.passed(f'демон {self.number} отвалился')
                    self.shutdown()
                    await asyncio.sleep(self.timeout_process + 1)
                    return None

                return cursor

        stash=f'test-replication-daemon-{uuid()}'
        lock=f'test-replication-daemon-{uuid()}'

        daemons = []
        for i in range(4):
            daemon = MyTestDaemon(
                number = i+1,
                # таймаут между запусками демона, меньше 1.5 задавать нельзя
                timeout_process = 2,
                timeout_error = 2,
                timeout_empty = 2,
                stash=stash,
                lock=lock,
            )
            tap.ok(daemon, f'Демон {i+1} создан')
            daemons.append(daemon)

        try:
            tasks = []
            for daemon in daemons:
                tasks.append(asyncio.create_task(daemon.process()))

            await asyncio.wait(
                {*tasks},
                timeout=60.0,  # общий таймаут на тест
            )
        except asyncio.TimeoutError:
            tap.failed('timeout')
        else:
            tap.passed('timeout ')

        tap.eq(next(_cursor), 6, 'все тестовые итерации прошли')
