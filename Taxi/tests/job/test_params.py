class MyTestClass:
    @classmethod
    def mytest_cls(cls, **kwargs):
        return kwargs

    @staticmethod
    def mytest_static(**kwargs):
        return kwargs


def mytest(**kwargs):
    return kwargs


async def test_function(tap, job):
    with tap.plan(6, 'Функция'):
        task1 = await job.put(mytest, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(task2.callback, __name__ + '.mytest', 'Коллбек передан')
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'bar'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_cls_classmethod(tap, job):
    with tap.plan(6, 'Метод класса'):
        task1 = await job.put(MyTestClass.mytest_cls, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(
            task2.callback,
            __name__ + '.MyTestClass.mytest_cls',
            'Коллбек передан'
        )
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'bar'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_obj_classmethod(tap, job):
    with tap.plan(6, 'Метод объекта'):
        obj = MyTestClass()

        task1 = await job.put(obj.mytest_cls, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(
            task2.callback,
            __name__ + '.MyTestClass.mytest_cls',
            'Коллбек передан'
        )
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'bar'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_cls_staticmethod(tap, job):
    with tap.plan(6, 'Статический метод класса'):
        task1 = await job.put(MyTestClass.mytest_static, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(
            task2.callback,
            __name__ + '.MyTestClass.mytest_static',
            'Коллбек передан'
        )
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'bar'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_obj_staticmethod(tap, job):
    with tap.plan(6, 'Статический метод класса'):
        obj = MyTestClass()

        task1 = await job.put(obj.mytest_static, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(
            task2.callback,
            __name__ + '.MyTestClass.mytest_static',
            'Коллбек передан'
        )
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'bar'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')


async def test_str(tap, job):
    '''С уже сериализованным именем функции'''
    with tap.plan(6):
        task1 = await job.put(__name__ + '.mytest', foo='baz')
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.take()
        tap.ok(task2, 'Задание получено')
        tap.eq(task2.callback, __name__ + '.mytest', 'Коллбек передан')
        tap.eq(task2.data, {'foo': 'baz'}, 'Данные переданы')

        tap.eq(await job.call(task2), {'foo': 'baz'}, 'Функция выполнена')

        task3 = await job.ack(task2)
        tap.ok(task3, 'Задача подбверждена выполненной')
