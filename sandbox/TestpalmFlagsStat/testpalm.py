# -*- coding: utf-8 -*-
import requests
import types


class TestpalmApi():
    url = "https://testpalm.yandex-team.ru/api/"

    def __init__(self, project, token):
        self.project = project
        self.token = token

    """
    Получение списка тесткейсов в проекте
    Returns:
        list Набор тесткейсов в формате ответа из TestPalm
    """

    def get_testcases(self):
        res = self.request("testcases", True)

        if not isinstance(res, types.ListType):
            raise Exception('TestPalm API response not a list', res)

        return res

    """
    Получение списка тесткейсов вместе со значением их параметров
    Returns:
        list Набор тесткейсов, где id атрибутов заменены на их имена
    """

    def get_full_testcases(self):
        defs = self.get_definitions()
        testcases = self.get_testcases()

        result = []
        for testcase in testcases:
            resultDict = {'id': testcase['id'], 'attributes': {}, 'name': testcase['name']}

            # Заменяем id атрибутов на имена
            for key in testcase['attributes']:
                resultDict['attributes'][defs[key]] = testcase['attributes'][key]

            result.append(resultDict)

        return result

    """
    Получение имен атрибутов в проекте
    Returns:
        dict Словарь в формате id атрибута: имя
    """

    def get_definitions(self):
        resp = self.request("definition", True)

        if not isinstance(resp, types.ListType):
            raise Exception('TestPalm API response not a list', resp)

        resultDict = {}
        for item in resp:
            resultDict[item['id']] = item['title']

        return resultDict

    """
    Основная обработка запроса
    Args:
        method: str Имя метода для запроса
        isPreview: bool Использовать сокращенный или полный метод запроса к testpalm
    Returns:
        json: ответ ручки testpalm
    """

    def request(self, method, isPreview):
        url = self.__get_request_url(method) + '/preview' if isPreview else ''
        r = requests.get(url, headers={'Testpalm-Api-Token': self.token})

        try:
            return r.json()
        except Exception as err:
            raise Exception('TestPalm API Connection', err)

    """
    Получение урла для запроса.
    Строит урл для запроса на основе метода и имени проекта
    Args:
        method: str имя метода для запроса
    Returns:
        str: url запроса к testpalm
    """

    def __get_request_url(self, method):
        return self.url + method + "/" + self.project
