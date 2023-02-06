import time
import pickle

from dmp_suite.local_queue.queue import UniqueQueue
from dmp_suite.local_queue.task import Task, DEFAULT_PRIORITY


def test_task_should_be_uniq():
    def make_task(max_rss):
        now = int(time.time())
        timeout = 60 # в этом тесте нам таймаут не важен
        until = now + timeout
        return Task('foo', max_rss, created_at=now, valid_until=until)

    # Очередь должна отбрасывать таски-дубликаты
    q = UniqueQueue()
    q.put(make_task(10))
    assert q.length() == 1

    # Добавление такого же таска не должно приводить к увеличению очереди
    q.put(make_task(10))
    assert q.length() == 1

    # И другой max_rss не должен на это влиять
    q.put(make_task(20))
    assert q.length() == 1

    # Если таск забрали на обработку, то очередь всё равно
    # должна про него помнить и не брать таких же:
    task = q.pop()
    assert q.length() == 0

    # Попробуем добавить таск-дубликат:
    q.put(make_task(30))
    # Он не должен добавиться, так как предыдущий foo ещё не обработан
    assert q.length() == 0

    # Но когда мы его пометим, как обработанный:
    q.mark_processed(task)
    assert q.length() == 0
    # то добавление нового такого же должно пройти успешно:
    q.put(make_task(30))
    assert q.length() == 1

def test_queue_is_picklable():
    def make_task(command):
        now = int(time.time())
        timeout = 60 # в этом тесте нам таймаут не важен
        until = now + timeout
        return Task(command, 100, created_at=now, valid_until=until)

    q = UniqueQueue()
    q.put(make_task('one'))
    q.put(make_task('two'))
    q.put(make_task('three'))

    one = q.pop()
    assert one.command == 'one'

    buffer = pickle.dumps(q)

    restored_q: UniqueQueue = pickle.loads(buffer)

    assert restored_q.length() == 2
    # Добавить 'one' снова не должно получиться, потому что
    # он в настоящий момент процессится
    restored_q.put(make_task('one'))
    assert restored_q.length() == 2

    # Cледующий таск в очереди должен быть 'two'
    two = restored_q.pop()
    assert two.command == 'two'


def test_priorities():
    def make_task(command, priority=DEFAULT_PRIORITY):
        now = int(time.time())
        timeout = 60 # в этом тесте нам таймаут не важен
        until = now + timeout
        return Task(command, 100, created_at=now, valid_until=until, priority=priority)

    q = UniqueQueue()
    # Эта команда с приоритетом по-умолчанию
    q.put(make_task('low'))
    # Этот таск должен быть поставлен в начало очереди
    q.put(make_task('medium-1', priority=50))
    # Эта с наивысшим, должна попасть тоже попасть в начало очереди
    # и отодвинуть medium-1
    q.put(make_task('high', priority=0))
    # А этот имеет такой же приоритет, как medium-1,
    # но он должен встать в очередь за medium-2.
    q.put(make_task('medium-2', priority=50))

    task_names = [
        q.pop().command
        for idx in range(q.length())
    ]
    assert task_names == ['high', 'medium-1', 'medium-2', 'low']


def test_return_back():
    def make_task(command, priority=DEFAULT_PRIORITY):
        now = int(time.time())
        timeout = 60 # в этом тесте нам таймаут не важен
        until = now + timeout
        return Task(command, 100, created_at=now, valid_until=until, priority=priority)

    q = UniqueQueue()
    q.put(make_task('low'))
    q.put(make_task('medium-1', priority=50))
    q.put(make_task('medium-2', priority=50))

    # Проверим, что вынув medium-1 и положив его обратно, мы
    # получим тот же medium-1 при следующем подходе

    t = q.pop()
    assert t.command == 'medium-1'
    q.return_back(t)

    t = q.pop()
    assert t.command == 'medium-1'
    q.return_back(t)

    t = q.pop()
    assert t.command == 'medium-1'
