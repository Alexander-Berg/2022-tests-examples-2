import re
from stall.model.event_cache import EventQueue

def method_in_module():
    pass

class SomeClass:
    def method_in_class(self):
        pass

async def test_caller(tap):
    tap.plan(2, 'Вызывающая функция')
    event = EventQueue.create(
        tube='job',
        caller=None,
        callback=SomeClass.method_in_class
    )

    tap.eq_ok(event.tube, 'job', 'tube')
    tap.ok(
        re.match(
            r'^File \".+\/test_event_queue.py\" at line .+ in test_caller$',
            event.data['caller']
        ),
        'caller'
    )

async def test_caller_from_save(tap):
    tap.plan(2, 'При добавлении event в save возмём родительскую функцию')

    def save():
        return EventQueue.create(
            tube='job',
            caller=None,
            callback=SomeClass.method_in_class
        )

    event = save()
    tap.eq_ok(event.tube, 'job', 'tube')
    tap.ok(
        re.match(
            r'^File \".+\/test_event_queue.py\" at line .+ '
            'in test_caller_from_save$',
            event.data['caller']
        ),
        'caller'
    )

async def test_callback_class_method(tap):
    tap.plan(2, 'Сериализация метода класса')
    event = EventQueue.create(
        tube='job',
        caller=None,
        callback=SomeClass.method_in_class
    )
    tap.eq_ok(event.tube, 'job', 'tube')
    tap.in_ok(
        'tests.model.event_cache.test_event_queue.SomeClass.method_in_class',
        event.data['callback'],
        'callback'
    )

async def test_callback_module_method(tap):
    tap.plan(2, 'Сериализация метода модуля')
    event = EventQueue.create(
        tube='job',
        caller=None,
        callback=method_in_module
    )
    tap.eq_ok(event.tube, 'job', 'tube')
    tap.in_ok(
        'tests.model.event_cache.test_event_queue.method_in_module',
        event.data['callback'],
        'callback'
    )

async def test_callback_str(tap):
    tap.plan(2, 'Callback строкой оставляем как есть')
    event = EventQueue.create(
        tube='job',
        caller=None,
        callback='some_callback'
    )
    tap.eq_ok(event.tube, 'job', 'tube')
    tap.eq_ok(
        event.data['callback'],
        'some_callback',
        'callback'
    )
