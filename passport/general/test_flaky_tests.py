import logging

import allure
from nose_parameterized import parameterized
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.settings.common import DEFAULT_FLAKY_TEST_RETRIES
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    flaky_test,
)


logger = logging.getLogger(__name__)


@allure_setup(feature='Автотесты', story='Перезапуск мигающих тестов')
class FlakyTestsTestCase(BaseTestCase):
    custom_flaky_test_retries = DEFAULT_FLAKY_TEST_RETRIES + 5

    def test_default_retries(self):
        _retries.default += 1
        logger.info('default retries: %s' % _retries.default)
        self.flaky_step1()
        self.flaky_step2()

        assert _retries.default == DEFAULT_FLAKY_TEST_RETRIES

    @allure.step('Flaky step1')
    def flaky_step1(self):
        logger.info('Запуск Step1')

    @allure.step('Flaky step2')
    def flaky_step2(self):
        logger.info('Запуск Step2')

    @flaky_test(retries=custom_flaky_test_retries)
    def test_custom_retries(self):
        _retries.custom += 1
        assert _retries.custom == self.custom_flaky_test_retries

    @parameterized.expand('ab')
    def test_parameterized(self, param):
        _retries.parameterized.setdefault(param, 0)
        _retries.parameterized[param] += 1

        assert _retries.parameterized[param] == DEFAULT_FLAKY_TEST_RETRIES


class _retries:
    custom = 0
    default = 0
    parameterized = dict()
