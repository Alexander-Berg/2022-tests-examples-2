from collections.abc import (
    Mapping,
    Sequence,
)
from unittest import (
    skip,
    TestCase,
)

import flaky
from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_key,
)
from passport.backend.qa.autotests.base.settings.common import DEFAULT_FLAKY_TEST_RETRIES
from passport.backend.qa.autotests.base.settings.env import ENV
from passport.backend.qa.autotests.base.test_env import test_env


def limit_envs(development=True, testing=True, production=True, intranet_testing=True, intranet_production=True, description=None):
    def decorator(cls):
        if (
            (ENV in ('development', ) and not development) or
            (ENV in ('testing', ) and not testing) or
            (ENV in ('rc', 'production') and not production) or
            (ENV in ('intranet_testing', ) and not intranet_testing) or
            (ENV in ('intranet_rc', 'intranet_production') and not intranet_production)
        ):
            msg = f'Тест выключен в окружении {ENV}'
            if description:
                msg += f': {description}'
            return skip(msg)(cls)
        else:
            return cls
    return decorator


def flaky_test(retries=DEFAULT_FLAKY_TEST_RETRIES):
    """
    Декоратор предписывает запускать тест повторно, если он не прошёл с первого
    раза.

    Тест будет запускаться до первого успешного прохода или пока не кончатся
    попытки.

    Можно использовать как с целым классом TestCase, так и отдельными тестам
    в нём.

    Например,

    @flaky_test(retries=3)
    class MyTest(TestCase):
        def test1(self):
            assert False

        @flaky_test(retries=2)
        def test2(self):
            assert False

    test1 будет запущен 3 раза
    test2 будет запущен 2 раза

    Одна попытка запуска теста включает в себя:
        - setUp
        - вызов теста
        - tearDown
    """

    return flaky.flaky(max_runs=retries)


@flaky_test()
class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        test_env.reset()
        self.test_env = test_env

    @staticmethod
    def assert_has_entries(rv, key_value_pairs: Mapping):
        assert_that(
            rv,
            has_entries(key_value_pairs),
        )

    @staticmethod
    def assert_has_keys(rv, keys: Sequence):
        assert_that(
            rv,
            all_of(
                *(has_key(key) for key in keys),
            ),
        )
