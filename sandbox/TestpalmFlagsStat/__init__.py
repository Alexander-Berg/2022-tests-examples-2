#! -*- coding: utf-8 -*-

import logging
import json

from sandbox import sdk2

from testpalm import TestpalmApi
from ab import ABApi
from report import FlagsReport


class TestpalmFlagsReport(sdk2.Resource):
    releasable = True
    any_arch = False
    executable = False
    auto_backup = False
    releasers = ['binarycat']


class TestpalmFlagsJson(sdk2.Resource):
    releasable = True
    any_arch = False
    executable = False
    auto_backup = False
    releasers = ['binarycat']


class TestpalmFlagsStat(sdk2.Task):
    """Получение статистики по флагам из testpalm для тестирования асессорами"""

    class Parameters(sdk2.Task.Parameters):
        project_name = sdk2.parameters.String(
            'TestPalm project',
            description=u'Имя проекта в TestPalm',
            required=True,
        )

    def on_execute(self):
        self.flags = {}

        logging.info('Starting testpalm project {}'.format(self.Parameters.project_name))
        testpalm = TestpalmApi(self.Parameters.project_name, sdk2.Vault.data('env.TESTPALM_TOKEN'))
        self.AB = ABApi(sdk2.Vault.data('robot-serp-bot_ab_experiments_oauth_token'))

        # Получаем полный список тесткейсов, включая их атрибуты
        testcases = testpalm.get_full_testcases()

        logging.info('Total testcases {}'.format(len(testcases)))

        for testcase in testcases:
            testcase['parsed_flags'] = []

            # Парсим каждый параметр тесткейса
            for key, params in testcase['attributes'].items():

                # Интересуют только параметры, заданные в формате params.*
                # остальные флагами не являются
                if 'params' not in key:
                    continue

                for param in params:
                    # Получение полной информации про флаг, включая его testid
                    flag = self.get_flag(key, param)

                    # Сохраняем инфу про то, в каких тесткейсах флаг используется
                    flag['testcases'].append(testcase['id'])

                    # Сохраняем информацию про флаг в тесткейсе
                    testcase['parsed_flags'].append(flag['hash'])

        # Ресурс с json данными флагов
        self.generate_json()

        # html отчет
        self.generate_report(testcases, self.flags)

    """
    Создание ресурса с json данными каждого флага
    """

    def generate_json(self):
        resource = sdk2.ResourceData(TestpalmFlagsJson(self, "Flags json", "flags.json"))
        resource.path.write_bytes(json.dumps(self.flags))

    """
    Создание ресурса с html отчетом
    """

    def generate_report(self, testcases, flags):
        resource = TestpalmFlagsReport(self, 'Flags report', 'report')
        data = sdk2.ResourceData(resource)
        data.path.mkdir(parents=True, exist_ok=True)

        report = FlagsReport(self.Parameters, testcases, flags)
        report.write(str(data.path.resolve()))

    """
    Получение имени и значения флага по параметрам из тесткейса
    Args:
        key: str Используемый ключ параметра
        val: str Значением параметра
    Returns:
        dict: Распарсенные имя и значение флага
            name: имя флага
            val: значение
            hash: хэш, описывающий имя и значение
    """

    def parse_flag(self, key, val):
        # Все нужные параметры всегда начинаются с params - это лишнее
        name = key.replace('params.', '')
        flagHash = '{}={}'.format(name, val)

        # Для полей flags и exp_flags имена и значения флагов находятся внутри val
        if name in ['flags', 'exp_flags']:
            flagSplit = val.split('=')
            name = flagSplit[0]
            # В случае если значение не указано, выставляем 1, по умолчанию значение репорта
            val = flagSplit[1] if len(flagSplit) > 1 else '1'

        return {'name': name, 'val': val, 'hash': flagHash}

    """
    Проверка, находится ли имя флага в flag_storage
    Args:
        flagName: str Имя флага
    Returns:
        bool: True если флаг есть в хранилище, False если нет
    """

    def check_flag_storage(self, flagName):
        try:
            flagInfo = self.AB.get_flag_info(flagName)
            return flagInfo is not None
        except Exception as err:
            logging.info(err)
            return False

    """
    Получение testid для указанного флага и значения
    Args:
        flag: dict Объект, описывающий флаг
            name: имя
            val: значение
    Returns:
        None: если testid не найден
        str: значение testid, если флаг найден
    """

    def get_flag_testid(self, flag):
        testid = self.AB.get_flag_testid(flag['name'], flag['val'])
        return None if testid is None else testid['testid']

    """
    Получение статуса testid в продакшене
    Args:
        testid: str Значение testid
    Returns:
        bool: True если testid в продакшене, False если нет
    """

    def get_testid_status(self, testid):
        if testid is None:
            return False
        return self.AB.check_testid_online(testid)

    """
    Получение полной информации про параметр тесткейса: его testid, статус в продакшене и тд
    Args:
        key: str Имя параметра
        val: str Значение параметра
    Returns:
        dict: Объект с флагом
            name: Имя флага
            val: Значение
            hash: hash имени и значения
            in_storage: находится ли имя флага в flag_storage
            testid: testid для флага, None если нет
            online: находится ли testid для флага в проде
            testcases: пустой массив для сохранения тесткейсов, наполняется выше
    """

    def get_flag(self, key, val):
        flag = self.parse_flag(key, val)

        if flag['hash'] in self.flags:
            return self.flags[flag['hash']]

        flag['in_storage'] = self.check_flag_storage(flag['name'])
        flag['testid'] = self.get_flag_testid(flag)
        flag['online'] = self.get_testid_status(flag['testid'])
        flag['testcases'] = []

        self.flags[flag['hash']] = flag

        return flag
