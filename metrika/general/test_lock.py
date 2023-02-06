import os

from hamcrest import assert_that, has_property, equal_to

import metrika.admin.python.cms.lib.pg.lock as lock
import metrika.admin.python.cms.lib.pg.connection_manager as connection_manager


def get_connection_manager():
    pg_kwargs = {
        "host": os.getenv("POSTGRES_RECIPE_HOST"),
        "port": os.getenv("POSTGRES_RECIPE_PORT"),
        "dbname": os.getenv("POSTGRES_RECIPE_DBNAME"),
        "user": os.getenv("POSTGRES_RECIPE_USER"),
    }

    return connection_manager.ConnectionManager(**pg_kwargs)


def test_lock():
    """
    Берём лок, под этим локом берём его же ещё раз - должны не взять.
    :return:
    """
    l = lock.Lock(identity="id-unit-test", name="unit_test", connection_manager=get_connection_manager())

    with l.try_get_lock("lock-name1") as holder:
        assert_that(holder, has_property("is_aquired", equal_to(True)))

        with l.try_get_lock("lock-name1") as holder2:
            assert_that(holder2, has_property("is_aquired", equal_to(False)))


def test_lock_after():
    """
    Берём лок, выходим, берём лок ещё раз
    :return:
    """
    l = lock.Lock(identity="id-unit-test", name="unit_test", connection_manager=get_connection_manager())

    with l.try_get_lock("lock-name2") as holder:
        assert_that(holder, has_property("is_aquired", equal_to(True)))

    with l.try_get_lock("lock-name2") as holder2:
        assert_that(holder2, has_property("is_aquired", equal_to(True)))
