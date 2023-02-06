# -*- coding: utf-8 -*-
import requests
import types
import json
import os


class ABApi():
    url = "https://ab.yandex-team.ru/api/"

    def __init__(self, token):

        # Считываем конфиг по умолчанию для новых флагов
        location = os.path.join(os.getcwd(), os.path.dirname(__file__))
        flagFile = open(os.path.join(location, 'flag_config.json'), 'r')
        self.flag_config = flagFile.read()
        flagFile.close()

        # Общая сессия на запросы, для поддержки keep-alive соединения
        session = requests.Session()
        session.headers.update({'Authorization': 'OAuth ' + token})
        self.requestSession = session

    """
    Проставление специального тега заявке для тестирования асессорами
    Args:
        testid: str testid
    Returns:
        testid
    """

    def add_testid_tag(self, testid):
        params = {
            'name': 'zero_testing_application',
            'target_type': 2,
            'target_id': testid
        }

        self.requestSession.post(self.url + 'tag', data=params)
        return testid

    """
    Создание testid для флага и значения
    Args:
        flag: str имя флага
        value: str значение флага
    Returns:
        testid: testid созданного флага
    """

    def create_flag_testid(self, flag, value):
        params = json.loads(self.flag_config.replace('{flag}', flag).replace('{value}', value))

        # Флаги rearr сильно длинные, костыль чтобы не использовать их значение
        title = 'rearr (serp-js)' if flag == 'rearr' else flag + '=' + value

        params = {
            'title': title,
            'type': 'ABT',
            'queue_id': 1,
            'params': json.dumps(params),
            'replace_token': '<testid>'
        }

        resp = self.requestSession.post(self.url + 'testid', data=params)
        data = resp.json()
        self.add_testid_tag(data['testid'])

        return data['testid']

    """
    Получение tesid для флага и значения
    Args:
        flag: str имя флага
        value: str значение флага
    Returns:
        dict: информацию о флаге
        None: если флаг не найден
    """

    def get_flag_testid(self, flag, value):
        resp = self.request('testid', '?search__by_value1=REPORT:' + flag + '=' + json.dumps(value) + '&author=robot-serp-bot')

        if not isinstance(resp, types.ListType):
            raise Exception('AB API response not a list', resp)

        return resp[0] if len(resp) > 0 else None

    """
    Проверка наличия testid в продакшене
    Args:
        testid: str testid
    Returns:
        bool: True если testid в проде или False если нет
    """

    def check_testid_online(self, testid):
        resp = self.request('testid/activity/current', '?config_id=0&id=' + str(testid))

        if not isinstance(resp, types.ListType):
            raise Exception('AB API response not a list', resp)

        return len(resp) > 0

    """
    Заявка на выкладку testid в прод
    Args:
        testid: str testid
    Returns:
        dict: ответ сервера
    """

    def publish_testid(self, testid):
        params = {
            'title': 'zero_testing_application',
            'aspect': 'ipreg',
            'testids': testid,
            'regions': 10000,
            'staff_only': '0',
            'ttl': 31536000  # один год
        }

        publishUrl = 'zero_testing/application/'

        resp = self.requestSession.post(self.url + publishUrl, data=params)
        return resp

    """
    Получение информации о имени флага из flag_storage
    Args:
        flag: str имя флага
    Returns:
        dict: ответ сервера с информацией
        None: если флаг не заведен в flag_storage
    """

    def get_flag_info(self, flag):
        resp = self.request('flag_storage', flag)
        return resp if 'name' in resp else None

    """
    Основная обработка запроса
    Args:
        method: str Имя метода для запроса
        params: str Параметры запроса
    Returns:
        json: ответ ручки ab
    """

    def request(self, method, params):
        url = self.__get_request_url(method, params)
        r = self.requestSession.get(url)

        try:
            return r.json()
        except Exception as err:
            raise Exception('AB API Connection', 'method: {}, params: {}, err: {}'.format(method, params, err))

    """
    Получение урла для запроса.
    Строит урл для запроса на основе метода и параметров запроса
    Args:
        method: str имя метода для запроса
    Returns:
        str: url запроса к ab
    """

    def __get_request_url(self, method, params):
        return self.url + method + '/' + params
