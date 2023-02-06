# -*- coding: utf-8 -*-

from passport.backend.core.geobase import get_as_lookup


# Помечаем фикстуру как общую при запуске тестов в несколько потоков
# nose выполнит код в мастер-процессе один раз для всех тестов пакета
# http://nose.readthedocs.org/en/latest/doc_tests/test_multiprocess/multiprocess.html#controlling-distribution
_multiprocess_shared_ = True


def setup_package():
    get_as_lookup()
