def mytest(**kwargs):  # pylint: disable=unused-argument
    return 'baz'


async def test_base(tap, job):
    '''Базовые функции'''
    with tap.plan(6):
        task_out = await job.put(mytest, foo='bar')
        tap.ok(task_out, 'Задание отправлено')

        task_in = await job.take()
        tap.ok(task_in, 'Задание получено')

        tap.eq(task_in.callback, __name__ + '.mytest',
               'Коллбек передан')
        tap.eq(task_in.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task_in), 'baz', 'Функция выполняется')

        task3 = await job.ack(task_in)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_parallel(tap, job):
    '''Параллельное взятие нескольких тасок'''
    with tap.plan(9):
        task_out1 = await job.put(mytest, foo=1)
        tap.ok(task_out1, 'Задание 1 отправлено')

        task_out2 = await job.put(mytest, foo=2)
        tap.ok(task_out2, 'Задание 2 отправлено')

        task_out3 = await job.put(mytest, foo=3)
        tap.ok(task_out3, 'Задание 3 отправлено')

        task_in1 = await job.take()
        tap.ok(task_in1, 'Задание 1 получено')
        tap.eq(task_in1.data['foo'], 1, 'Задание 1 с данными')

        task_in2 = await job.take()
        tap.ok(task_in2, 'Задание 2 получено')
        tap.eq(task_in2.data['foo'], 2, 'Задание 2 с данными')

        task_in3 = await job.take()
        tap.ok(task_in3, 'Задание 3 получено')
        tap.eq(task_in3.data['foo'], 3, 'Задание 3 с данными')

        await job.ack(task_in1)
        await job.ack(task_in2)
        await job.ack(task_in3)
