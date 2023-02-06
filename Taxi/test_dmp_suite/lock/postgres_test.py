import pytest
import mock
import multiprocessing
import sys

from dmp_suite.lock.base import NotAcquiredLockError
from dmp_suite.lock.postgres import prolongable_lock


def get_foo_lock():
    with prolongable_lock('foo', wait_limit_sec=3):
        pass


@pytest.mark.slow
def test_prolongable_lock_is_reentrant():
    # Убедимся, что попытка захватить лок из того же потока
    # проходит не приводит к ошибке. Это потому что наш лок reentrant.

    with prolongable_lock('foo', wait_limit_sec=3):
        with prolongable_lock('foo', wait_limit_sec=3):
            pass

    # В подпроцессе тоже должно быть можно захватить тот же лок,
    # когда его уже держит родительский процесс:
    with prolongable_lock('foo', wait_limit_sec=3):
        process = multiprocessing.Process(target=get_foo_lock)
        process.start()
        process.join()
        assert process.exitcode == 0, 'Subprocess wasn\'t able to take the same lock'


@pytest.mark.slow
def test_prolongable_lock_on_multiple_hosts():
    # Попробуем смоделировать ситуацию, будто мы берём лок
    # с разных машинок, и на второй машинке взятие лока фейлится
    # из-за того, что он уже занят.

    lock_name = 'foo'

    with mock.patch('socket.gethostname') as gethostname:
        gethostname.return_value = 'first-host'
        with prolongable_lock(lock_name) as lock:
            # До того, как этот тест был написан, патч gethostname
            # не работал, потому что имя текущего хоста помещалось
            # в атрибут класс лишь единожды - в момент загрузки
            # модуля dmp_suite.lock.base.
            # Поэтому нужна дополнительная проверка того, что патчинг
            # работает как надо:
            assert lock.host == 'first-host'

            gethostname.return_value = 'second-host'
            with pytest.raises(NotAcquiredLockError):
                # По-умолчанию, prolongable_lock будет пытаться
                # захватить лок в течении часа.
                # В тестах мы так долго ждать не можем, поэтому
                # установим этот лимит в 3 секунды:
                with prolongable_lock(lock_name,
                                      wait_limit_sec=3):
                    assert True
