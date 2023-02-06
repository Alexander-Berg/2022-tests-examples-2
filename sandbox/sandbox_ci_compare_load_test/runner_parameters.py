# -*- coding: utf-8 -*-

from sandbox import sdk2


class QuotaParameters(sdk2.Parameters):
    with sdk2.parameters.Group('Environment') as quota_parameters:
        browser_id = sdk2.parameters.String('ID браузера', description='Будет взят из конфигурационного файла hermione')
        browser_version = sdk2.parameters.String('Версия браузера')
        with sdk2.parameters.String('Имя квоты, где доступен указанный браузер', required=True) as quota_name:
            quota_name.ui = quota_name.UI('select')
            quota_name.choices = [
                ('innokenty', 'innokenty'),
                ('web4-ssd-test-1', 'web4-ssd-test-1'),
                ('web4-ssd-test-2', 'web4-ssd-test-2'),
                ('cloud', 'cloud'),
                ('serp-test', 'serp-test')
            ]
        quota_name = quota_name()


class TestsParameters(sdk2.Parameters):
    with sdk2.parameters.Group('Параметры тестов') as tests_parameters:
        custom_opts = sdk2.parameters.String('Дополнительные опции для запуска тестирования')
        skip_list_id = sdk2.parameters.Integer('Skip list id')
