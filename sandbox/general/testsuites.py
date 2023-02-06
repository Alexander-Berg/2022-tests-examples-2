# -*- coding: utf-8 -*-
import json
import logging


class TestSuites(object):
    @staticmethod
    def get_release_exp_flags_testsuites(testsuites):
        """
        Фильтрует тест-сьюты, оставляет только сьюты для запуска на релиз флагов.

        :param testsuites: Список тест-сьютов
        :type testsuites: list of dict
        :rtype: list of dict
        """

        logging.debug('Filtering testsuites by property "release_exp_flags": {} '.format(TestSuites.dump(testsuites)))

        return filter(lambda testsuite: testsuite.get('release_exp_flags', False), testsuites)

    @staticmethod
    def add_testids_to_testsuites(testsuites, testids):
        """
        Добавляет тестиды в тест-сьюты. Дублирует тест-сьюты если тестидов большое 1.

        :param testsuites: Список тест-сьютов
        :type testsuites: list of dict
        :param testids: Тестид или список тестидов
        :type testids: str or list of str
        :rtype: list of dict
        """
        if not isinstance(testids, list):
            testids = [testids]

        result = []
        for testid in testids:
            if not testid:
                continue

            result.extend(TestSuites.add_testid_to_testsuites(testsuites, testid))

        return result

    @staticmethod
    def add_testid_to_testsuites(testsuites, testid):
        """
        Добавляет тестид в тест-сьюты.

        :param testsuites: Список тест-сьютов
        :type testsuites: list of dict
        :param testid: Тестид
        :type testid: int or str
        :rtype: list of dict
        """
        logging.debug('Adding testid "{testid}" to: {testsuites}'.format(
            testid=testid,
            testsuites=TestSuites.dump(testsuites),
        ))

        return map(lambda testsuite: dict(testsuite, release_exp_flags_testid=testid), testsuites)

    @staticmethod
    def add_ticket_id_to_testsuites(testsuites, ticket_id):
        """
        Добавляет ключ тикета в теги тест-сьютов.

        :param testsuites: Список тест-сьютов
        :type testsuites: list of dict
        :param ticket_id: Ключ тикета
        :type ticket_id: str
        :rtype: list of dict
        """
        logging.debug('Adding ticket_id "{ticket_id}" to tags: {testsuites}'.format(
            ticket_id=ticket_id,
            testsuites=TestSuites.dump(testsuites),
        ))

        return map(lambda testsuite: dict(testsuite, tags=testsuite.get('tags', []) + [ticket_id]), testsuites)

    @staticmethod
    def filter_testsuites_by_platforms(testsuites, platforms):
        """
         Фильтрует тест-сьюты по заданным платформам

         :param testsuites: Список тест-сьютов
         :type testsuites: list of dict
         :param platforms: Ключ тикета
         :type platforms: list of str
         :rtype: list of dict
         """
        logging.debug('Filtering by platforms "{platforms}": {testsuites}'.format(
            platforms=platforms,
            testsuites=TestSuites.dump(testsuites),
        ))

        return filter(lambda testsuite: testsuite.get('platform', None) in platforms, testsuites)

    @staticmethod
    def add_responsible_user_to_testsuites(testsuites, user):
        """
        Добавляет логин ответственного пользователя в свойства тест-сьютов.

        :param testsuites: Список тест-сьютов
        :type testsuites: list of dict
        :param user: Логин пользователя
        :type ticket_id: str
        :rtype: list of dict
        """
        return map(lambda testsuite: dict(testsuite, testsuite_properties=dict(testsuite.get('testsuite_properties', {}), responsible_user=user)), testsuites)

    @staticmethod
    def load(path):
        """
        :param path: Путь до файла с тест-сьютами
        :type path: str
        :rtype: dict
        """
        logging.debug('Loading testsuites from "{}"'.format(path))

        with open(path, 'r') as f:
            return json.load(f)

    @staticmethod
    def dump(testsuites, **kwargs):
        """
        Переводит тест-сьюты в строку в формате JSON.

        :param testsuites: Список тест-сьютов
        :type testsuites: dict or list
        :param kwargs: Дополнительно передаваемые в json.dumps параметры
        :type kwargs: dict
        :rtype: str
        """
        return json.dumps(testsuites, indent=2, sort_keys=True, **kwargs)
