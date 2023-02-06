import asyncio
import typing
from collections import defaultdict
from concurrent.futures import Future
import kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api as pqlib
from tests.conftest import AutoCloseGenerator
from stall.logbroker import (
    CreateConsumerError,
    LogbrokerBaseCreator,
    LogbrokerCommitMessage,
    LogbrokerError,
    LogbrokerReaderCreator,
    LogbrokerWriter,
    LogbrokerReader,
)


async def test_create_api(tap, setup_topic):
    with tap.plan(1, 'Проверим установку GRPC соединения'):
        target = await setup_topic('t/lb_1')

        creator = LogbrokerBaseCreator(target)
        api = await creator.create_api(creator.endpoint, creator.port)
        tap.ok(api, 'GRPC соединение установлено')


async def test_cache_api(tap, setup_topic):
    with tap.plan(3, 'Проверим переиспользование подключения'):
        target = await setup_topic('t/lb_2')

        writer = LogbrokerWriter()
        api = await writer.api(target)
        tap.ok(api, 'Подключение к логброкеру установлено')

        api2 = await writer.api(target)
        tap.is_ok(api, api2, 'Переиспользуем подключение')

        writer3 = LogbrokerWriter()
        api3 = await writer3.api(target)
        tap.ne_ok(api, api3, 'Новый writer - новое подключение')


async def test_cache_producer(tap, setup_topic):
    with tap.plan(4, 'Проверим переиспользование продьюсера'):
        target = await setup_topic('t/lb_3')

        writer = LogbrokerWriter()
        producer = await writer.producer(target)
        tap.ok(producer, 'Продьюсер запущен')
        tap.eq(producer.seq_no, 1, 'Нумеруем сообщения с 1')

        producer2 = await writer.producer(target)
        tap.is_ok(producer, producer2, 'Переиспользуем продьюсера')

        writer3 = LogbrokerWriter()
        producer3 = await writer3.producer(target)
        tap.ne_ok(producer, producer3, 'Новый writer - новое продьюсер')


async def test_close_producer(tap, setup_topic):
    # pylint: disable=protected-access
    with tap.plan(4, 'Проверим закрытие продьюсера'):
        target = await setup_topic('t/lb_4')

        writer = LogbrokerWriter()
        producer = await writer.producer(target)
        tap.ok(producer._started, 'Продьюсер запущен')
        tap.eq(len(writer._producers), 1, 'В кеше 1 продьюсер')

        await writer.stop_producer(target)
        tap.ok(producer._stopped, 'Продьюсер остановлен')
        tap.eq(len(writer._producers), 0, 'Кеш продьюсеров пуст')


async def test_write_bad_message(tap, now, logbroker_read, setup_topic):
    # pylint: disable=protected-access
    with tap.plan(4, 'Попытка записать несериализуемое сообщение'):
        target = await setup_topic('t/lb_5')

        writer = LogbrokerWriter()
        original_message = {
            'data': now()
        }
        tap.ok(
            await writer.write_messages(target, [original_message]),
            'Попытка отправить сообщение'
        )

        producer =  await writer.producer(target)
        tap.eq(producer.seq_no, 1, 'Ошибка не увеличивает счетчик')
        tap.ok(not producer._stopped,
            'Ошибка в сообщении не влияет на продьюсера')

        read = await logbroker_read(target)
        tap.eq(read, [], 'Нет новых сообщений')


async def test_problem_on_write(tap, uuid, logbroker_read, setup_topic):
    # pylint: disable=protected-access
    with tap.plan(8, 'Закрываем продьюсера при проблемах с отправкой'):
        target = await setup_topic('t/lb_6')

        writer = LogbrokerWriter()
        original_message = {'data': uuid()}
        tap.ok(
            await writer.write_messages(target, [original_message]),
            'Отправим сообщение'
        )

        producer =  await writer.producer(target)
        tap.eq(producer.seq_no, 2, 'Счетчик увеличился')
        tap.ok(not producer._stopped, 'Продьюсера работает')

        read = await logbroker_read(target)
        tap.ok(read, 'Сообщения получены')

        with tap.raises(ValueError, 'Попробуем отправим сообщение'):
            write_future = Future()

            def write(*args, **kwargs):
                # pylint: disable=unused-argument
                return write_future

            async def response():
                await asyncio.sleep(0.1)
                write_future.set_exception(ValueError())

            asyncio.create_task(response())

            producer.write = write
            await writer.write_messages(target, [original_message])

        tap.ok(producer._stopped, 'Продьюсер закрыт')
        tap.eq(producer.seq_no, 3, 'Счетчик увеличился')

        read = await logbroker_read(target)
        tap.ok(not read, 'Нет новых сообщений')


async def test_write_read(tap, now, uuid, logbroker_read, setup_topic):
    with tap.plan(4, 'Запись-Чтение'):
        target = await setup_topic('t/lb_7')
        writer = LogbrokerWriter()
        original_message = {
            'id': uuid(),
            'data': now().isoformat()
        }

        tap.ok(
            await writer.write_messages(target, [original_message]),
            'Сообщение отправлено'
        )

        read = await logbroker_read(target)
        tap.ok(read, 'Сообщения есть')
        tap.eq(read[0].topic, 'lb_7', 'Топик верный')
        tap.eq(read[0].data, original_message, 'Получено')


async def test_reader_statuses(tap, uuid, setup_topic):
    # pylint: disable=redefined-outer-name
    with tap.plan(7, 'Проверим статусы ридера'):
        target = await setup_topic('t/lb_8')

        writer = LogbrokerWriter()
        tap.ok(
            await writer.write_messages(target, [dict(id=uuid())]),
            'Сообщение отправлено'
        )

        class LogbrokerReaderLogStatus(LogbrokerReader):
            def __init__(self, *args, **kwargs) -> None:
                self.status_log = []
                super().__init__(*args, **kwargs)

            def __setattr__(self, __name: str, __value: typing.Any) -> None:
                if __name == 'status':
                    self.status_log.append(__value)
                return super().__setattr__(__name, __value)

        reader = LogbrokerReaderLogStatus(target, read_commit_messages=True)
        reader_gen = AutoCloseGenerator(reader.reading_generator, timeout=10)
        total_messages = []
        async for messages in reader_gen:
            if isinstance(messages, LogbrokerCommitMessage):
                break
            total_messages += messages
        tap.eq_ok(len(total_messages), 1, '1 сообщение получено')

        tap.ok(await reader.close(), 'Закроем читателя')
        tap.eq(reader.status, 'close', 'В close() ждем финального статуса')

        tap.ok(await reader.close(), 'Повторное закрытие ничего не ломает')

        tap.eq_ok(len(reader.status_log), 5, 'Все статусы пройдены')
        tap.eq_ok(
            reader.status_log,
            ['init', 'connecting', 'connect', 'closing', 'close'],
            'Верные статусы в верном порядке'
        )


async def test_reader_read_twice(tap, uuid, logbroker_read,
                                 setup_topic):
    # pylint: disable=redefined-outer-name, too-many-locals, too-many-statements
    with tap.plan(
            5,
            'Нельзя запустить 2 чтения у одного ридера, но у разных можно'
    ):
        target = await setup_topic('t/lb_9')
        tap.note('Вычитаем сообщения', len(await logbroker_read(target)))
        writer = LogbrokerWriter()

        reader = LogbrokerReader(target, read_commit_messages=True)
        reader_gen = AutoCloseGenerator(reader.reading_generator, timeout=10)
        tap.eq(reader.status, 'init', 'Начальный статус')

        with tap.subtest(3, 'Выйдем из генератора по break') as taps:
            message_1 = uuid()
            taps.ok(
                await writer.write_messages(target, [message_1]),
                'Отправим сообщение'
            )
            read_message_1 = None
            async for messages in reader_gen:
                if isinstance(messages, LogbrokerCommitMessage):
                    break
                if len(messages):
                    read_message_1 = messages[0].data

            taps.eq(read_message_1, message_1, 'Сообщение прочитано')
            taps.ne(reader.status, 'init', 'Статус изменился')

        tap.note('Выход по break не закрывает генератор')
        with tap.subtest(3, 'Закроем читателя через close') as taps:
            message_2 = uuid()
            taps.ok(
                await writer.write_messages(target, [message_2]),
                'Отправим сообщение'
            )
            read_message_2 = None
            async for messages in reader_gen:
                if isinstance(messages, LogbrokerCommitMessage):
                    break
                if len(messages):
                    read_message_2 = messages[0].data
            taps.eq(read_message_2, message_2, 'Сообщение прочитано')

            taps.ok(await reader.close(), 'Закроем читателя')

        with tap.subtest(2, 'Закрытый генератор не читает') as taps:
            message_3 = uuid()
            taps.ok(
                await writer.write_messages(target, [message_3]),
                'Отправим сообщение'
            )
            read_message_3 = None
            async for messages in reader_gen:
                if isinstance(messages, LogbrokerCommitMessage):
                    break
                if len(messages):
                    read_message_3 = messages[0].data
            taps.eq(read_message_3, None,
                    'Генератор закрыт, сообщения не читаются')

        with tap.subtest(4, 'Новый генератор дочитает') as taps:
            other_reader = LogbrokerReader(target, read_commit_messages=True)
            other_reader_gen = AutoCloseGenerator(
                other_reader.reading_generator,
                timeout=10
            )
            taps.eq(other_reader.status, 'init',
                    'Начальный статус нового ридера')

            other_read_message = None
            async for messages in other_reader_gen:
                if isinstance(messages, LogbrokerCommitMessage):
                    break
                if len(messages):
                    other_read_message = messages[0].data
            taps.eq(other_read_message, message_3, 'Сообщение прочитано')
            taps.ne(other_reader.status, 'init', 'Статус изменился')

            taps.ok(await other_reader.close(), 'Закроем читателя')


async def test_write_several_messages(tap, uuid, logbroker_read, setup_topic):
    with tap.plan(2, 'Запись нескольких сообщений за раз'):
        target = await setup_topic('t/lb_10')

        writer = LogbrokerWriter()
        original_messages = [dict(id=uuid()) for _ in range(5)]

        tap.ok(
            await writer.write_messages(target, original_messages),
            'Сообщения отправлены'
        )

        read = await logbroker_read(target)
        tap.eq(len(read), 5, 'Сколько записали, столько получили')


async def test_error_while_processing(tap, now, uuid, setup_topic):
    with tap.plan(8, 'При ошибке повторное чтение читает тоже самое'):
        target = await setup_topic('t/lb_11')

        writer = LogbrokerWriter()
        original_message = {'id': uuid(), 'data': now().isoformat()}
        tap.ok(
            await writer.write_messages(target, [original_message]),
            'Сообщение отправлено'
        )

        reader = LogbrokerReader(target)
        reader_gen = AutoCloseGenerator(reader.reading_generator, timeout=10)
        read = []
        with tap.raises(LogbrokerError, 'Поймали прокинутую в читателя ошибку'):
            async for messages in reader_gen:
                read = messages
                try:
                    raise ValueError('asd')
                except ValueError as e:
                    tap.note('Прокинем ошибку в читателя')
                    await reader.throw(e)

        tap.eq(reader.status, 'close', 'От ошибки читатель закрывается')
        tap.ok(read, 'Сообщения прочитаны')
        tap.eq(read[0].data.get('id'), original_message['id'],
            'Исходное сообщение получено')

        reader = LogbrokerReader(target)
        reader_gen = AutoCloseGenerator(reader.reading_generator)
        read = []
        async for messages in reader_gen:
            read = messages
        tap.ok(read, 'Те же сообщения прочитаны ещё раз')
        tap.eq(read[0].data.get('id'), original_message['id'],
            'Исходное сообщение получено')

        reader = LogbrokerReader(target)
        reader_gen = AutoCloseGenerator(reader.reading_generator)
        read = []
        async for messages in reader_gen:
            read = messages
        tap.ok(not read, 'Все сообщения прочитаны. Новых нет')


async def test_several_writers(tap, logbroker_read, setup_topic):
    with tap.plan(3, 'Строгий порядок сообщений в рамках одного писателя'):
        target = await setup_topic('t/lb_12')

        writer1 = LogbrokerWriter()
        writer2 = LogbrokerWriter()

        for i in range(5):
            tasks = [
                writer1.write_messages(target, [{
                    'id': i * 2,
                    'type': 0,
                }]),
                writer2.write_messages(target, [{
                    'id': i * 2 + 1,
                    'type': 1,
                }]),
            ]

            await asyncio.gather(*tasks)

        read = await logbroker_read(target)
        tap.eq(len(read), 10, 'Сообщения есть')

        read_by_type = defaultdict(list)
        for it in read:
            read_by_type[it.data.get('type')].append(it.data.get('id'))

        for ids in read_by_type.values():
            tap.eq(ids, sorted(ids), 'Сообщения упорядочены в рамках писателя')
        tap.note('Сообщения от разных писателей могут быть неупорядочены')


async def test_read_small_package(tap, setup_topic):
    with tap.plan(2, 'Ограничение чтения количества сообщение за раз'):
        target = await setup_topic('t/lb_13')

        writer = LogbrokerWriter()
        messages = [dict(id=i) for i in range(5)]
        await writer.write_messages(target, messages)

        reader = LogbrokerReader(target, max_read_count=3)
        reader_gen = AutoCloseGenerator(reader.reading_generator)

        read_messages_count = 0
        max_batch_count = 0
        async for messages in reader_gen:
            read_messages_count += len(messages)
            max_batch_count = max(max_batch_count, len(messages))

        tap.eq(read_messages_count, 5, 'Все сообщения прочитаны')
        tap.ok(max_batch_count <= 3, 'Каждая из пачек не больше лимита')

async def test_close_producer_failed(tap, uuid, setup_topic, logbroker_read):
    # pylint: disable=protected-access
    with tap.plan(8, 'Не получилось закрыть продьюсера'):
        target = await setup_topic('t/lb_14')

        writer = LogbrokerWriter()
        original_message = {'data': uuid()}
        tap.ok(
            await writer.write_messages(target, [original_message]),
            'Отправим сообщение'
        )

        producer =  await writer.producer(target)
        tap.eq(producer.seq_no, 2, 'Счетчик увеличился')
        tap.ok(not producer._stopped, 'Продьюсер работает')

        read = await logbroker_read(target)
        tap.ok(read, 'Сообщения получены')

        class FailedToCloseProducerException(RuntimeError):
            pass

        with tap.raises(ValueError, 'Попробуем отправим сообщение'):
            write_future = Future()
            stop_future = Future()

            def write(*args, **kwargs):
                # pylint: disable=unused-argument
                return write_future

            def stop(*args, **kwargs):
                # pylint: disable=unused-argument
                return stop_future

            async def response():
                await asyncio.sleep(0.1)
                write_future.set_exception(ValueError())

                await asyncio.sleep(60)
                # Мы должны закрыть продьюсера раньше этой ошибки
                stop_future.set_exception(FailedToCloseProducerException())

            asyncio.create_task(response())

            producer.write = write
            producer.stop = stop
            await writer.write_messages(target, [original_message])

        tap.ok(target not in writer._producers, 'Продьюсер удален')
        tap.eq(producer.seq_no, 3, 'Счетчик увеличился')

        read = await logbroker_read(target)
        tap.ok(not read, 'Нет новых сообщений')

async def test_recreate_api_on_consumer(tap, uuid, setup_topic):
    # pylint: disable=redefined-outer-name, protected-access
    # pylint: disable=too-many-statements
    with tap.plan(
            14,
            'При рестарте кластера логброкера старый grpc коннект залипает '
            'и не может создать консюмера. Убьём его)'
    ):
        class LogbrokerReaderCreatorMock(LogbrokerReaderCreator):
            async def create_consumer(self, api: pqlib.PQStreamingAPI):
                if getattr(api, 'raise_create_consumer', False):
                    raise CreateConsumerError('Test error')
                return await super().create_consumer(api)

        class LogbrokerReaderLogStatus(LogbrokerReader):
            _creator = LogbrokerReaderCreatorMock

            def __init__(self, *args, **kwargs) -> None:
                self.status_log = []
                super().__init__(*args, **kwargs)

            def __setattr__(self, __name: str, __value: typing.Any) -> None:
                if __name == 'status':
                    self.status_log.append(__value)
                return super().__setattr__(__name, __value)

        target = await setup_topic('t/lb_15')
        writer = LogbrokerWriter()
        reader = LogbrokerReaderLogStatus(target, read_commit_messages=True)
        reader_gen = AutoCloseGenerator(reader.reading_generator, timeout=10)

        tap.ok(
            await writer.write_messages(target, [dict(id=uuid())]),
            'Сообщение отправлено'
        )

        total_messages = []
        async for messages in reader_gen:
            if isinstance(messages, LogbrokerCommitMessage):
                break
            total_messages += messages
        tap.eq(len(total_messages), 1, '1 сообщение получено')

        tap.eq_ok(len(LogbrokerReaderLogStatus._api), 1, '1 grpc коннект')
        api_backup = list(LogbrokerReaderLogStatus._api.values())[0]

        tap.ok(
            await writer.write_messages(target, [dict(id=uuid())]),
            'Сообщение отправлено'
        )

        with tap.raises(LogbrokerError, 'Поймали прокинутую в читателя ошибку'):
            async for messages in reader_gen:
                total_messages += messages
                try:
                    raise ValueError('asd')
                except ValueError as e:
                    tap.note('Прокинем ошибку в читателя')
                    await reader.throw(e)

        tap.eq(reader.status, 'close', 'От ошибки читатель закрывается')
        tap.eq(len(total_messages), 2, 'Сообщения прочитаны')

        tap.eq_ok(
            len(LogbrokerReaderLogStatus._api),
            1,
            'Всё ещё 1 grpc коннект'
        )
        tap.eq(
            list(LogbrokerReaderLogStatus._api.values())[0],
            api_backup,
            'Этот тот же Grpc коннект'
        )

        tap.note('Симулируем ошибку при создании консюмера')
        setattr(api_backup, 'raise_create_consumer', True)

        tap.note('Перезапускаем чтение топика')
        reader = LogbrokerReaderLogStatus(target)
        reader_gen = AutoCloseGenerator(reader.reading_generator)
        with tap.raises(CreateConsumerError, 'Не удалось создать консюмера'):
            async for messages in reader_gen:
                total_messages += messages
        tap.eq(len(total_messages), 2, 'Новых сообщений нет')

        tap.eq(len(LogbrokerReaderLogStatus._api), 0, 'Убили grpc коннект')

        tap.ok(
            await writer.write_messages(target, [dict(id=uuid())]),
            'Сообщение отправлено'
        )

        tap.note('При следующем запуске чтения создадим новый grpc')
        reader = LogbrokerReaderLogStatus(target)
        reader_gen = AutoCloseGenerator(reader.reading_generator)
        async for messages in reader_gen:
            total_messages += messages
        tap.ok(len(total_messages) >= 3, 'Новые сообщения есть')
