# coding=utf-8
import collections
from json import loads
import os
import subprocess
import sys

from six import string_types
import yatest.common as yc


class XunistaterChecker(object):

    def __init__(self, cs_id2parser_id_map=None, config_path=None):
        self.xunistat_checker = yc.build_path() + '/passport/infra/daemons/xunistater/checker/xunistat_checker'
        self.config_path = config_path
        self.condition_set_id2tskv_parser_id = cs_id2parser_id_map

    def check_xunistater_signals(self, stdin, condition_set_ids, expected_signals=dict()):
        """
        Парсит набор строк и проверяет результат парсинга каждой xunistaterChecker'ом
        :param stdin: многострочный лог на вход парсера, или набор строк для проверки по которым можно итерироваться
        :param condition_set_ids: id проверок которые следует применить к логу
        :param expected_signals: набор сигналов и их количество {сигнал: кол-во, сигнал: кол-во, ...}, которые ожидаем на выходе
        """
        if isinstance(stdin, string_types):
            stdin_list = stdin.strip().splitlines()
        elif isinstance(stdin, (list, tuple)):
            stdin_list = stdin
        else:
            raise 'Unexpected \'stdin\' type: {}'.format(type(stdin))

        check_arguments = set()
        for cs in condition_set_ids:
            check_arguments.add((self.condition_set_id2tskv_parser_id[cs], cs))

        results_dict = collections.defaultdict(int)
        for stdin_line in stdin_list:
            for parser_id, condition_set_id in check_arguments:
                result = self.check_xunistater_signal(parser_id, condition_set_id, stdin_line.strip())
                for res in result:
                    results_dict[res[0]] += res[1]
        assert results_dict == expected_signals, '%s != %s' % (dict(results_dict), dict(expected_signals))

    def check_xunistater_signal(self, parser_id, condition_set_id, stdin):
        """
        :param parser_id: id парсера, по факту - имя лога (statbox.log , например)
        :param condition_set_id: id condition_set, необходим для обработки конкретного сигнала
        :param stdin: строка лога которая должна быть распаршена
        :return: list of lists результата обработки, к примеру: [["builder.rps.total.passport_dmmm",1]]
        """
        cmd = [
            self.xunistat_checker,
            'run_parser',
            'tskv_parser',
            '-c', self.config_path,
            '-p', "/config/component/tskv_parser[@id='{}']".format(parser_id),
            '--condition_set',
            "/config/component/tskv_parser[@id='{}']/condition_set[@id='{}']".format(parser_id, condition_set_id),
        ]
        checker = subprocess.Popen(
            cmd,
            env=os.environ.copy(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )

        stdout, stderr = checker.communicate(input=stdin.encode())
        assert checker.wait() == 0

        output = loads(stdout.strip().splitlines()[-1])
        return output
