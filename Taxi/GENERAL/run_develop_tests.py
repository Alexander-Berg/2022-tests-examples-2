# coding: utf-8

import sys
import os
import argparse

ROOT_DIR = os.path.abspath(os.path.join('../../', os.path.dirname(__file__)))
# Чтобы находить не установленную библиотеку, а лежащее в папке develop
sys.path.insert(0, ROOT_DIR)
from business_models.util import Handler, retry
from business_models.botolib import bot
import pytest


def extract_failed_tests(filepath):
    failed_tests = []
    for line in open(filepath):
        if '\tfailed\t' in line:
            failed_tests.append(line.split('\t')[0])
    return failed_tests


@Handler(job_name='test develop', bot_report=bot, raise_exceptions=True)
@retry(RuntimeError)
def run_tests(output_file, job_cnt=4, select_test='', greenplum=True):
    """Запуск тестов business_models, исключая тесты помеченные как greenplum
    :param output_file: str - файл, в который летят логи
    :param job_cnt: int - количество процессов для режима параллельного запуска
    :param select_test: str - список тестов, которые нужно запустить
    :param greenplum: bool - если True, то запустит тесты помеченные как greenplum,
        но без распараллеливания
    """
    os.chdir(os.path.join(ROOT_DIR))
    if os.path.exists(output_file):
        os.remove(output_file)

    if not greenplum:
        parallel_mode = ['-n', str(job_cnt)]
        greenplum_mode = ['-m', 'not greenplum']
    else:
        parallel_mode = []
        greenplum_mode = ['-m', 'greenplum']

    tests_status = pytest.main(['-v', os.path.join(ROOT_DIR, 'tests/') + select_test,
                                '--output_file', output_file,
                                ] \
                               + parallel_mode \
                               + greenplum_mode)

    if tests_status == pytest.ExitCode.OK:
        return

    if tests_status == pytest.ExitCode.TESTS_FAILED:
        failed_tests = sorted(extract_failed_tests(output_file))
        if not os.path.exists(output_file):
            raise RuntimeError('Tests FAILED, but output file was not created')
        elif len(failed_tests) == 0:
            bot.send_file(file=output_file)
            raise RuntimeError('Tests FAILED, but "extract_failed_tests" could not find any error')

        # сообщение отдельно от файла, потому что иначе портится форматирование имен тестов и кровь из глаз
        bot.send_message('Develop tests failed: \n {}'.format('\n'.join(failed_tests)))
        resp = bot.send_file(file=output_file)
        if not resp['ok']:
            raise RuntimeError('Failed to send failed test results: {}'.format(resp))

    elif tests_status == pytest.ExitCode.INTERRUPTED:
        bot.send_message('Develop tests was INTERRUPTED by someone\nЭэээ, слыш! Кто это такой дерзкий?')

    elif tests_status == pytest.ExitCode.INTERNAL_ERROR:
        bot.send_message('Develop tests... Да хз, что с ними=(\nSome INTERNAL_ERROR appears in pytest XX')

    elif tests_status == pytest.ExitCode.USAGE_ERROR:
        bot.send_message('Develop tests USAGE_ERROR! Уберите свои кривые ручки!')

    elif tests_status == pytest.ExitCode.NO_TESTS_COLLECTED:
        bot.send_message('Develop tests couldn’t be found!\n\nКуды спрятались-то?...')

    else:
        bot.send_message('Develop tests, блджад! pytest тут что-то странное придумал')


def get_args():
    parser = argparse.ArgumentParser(description='test develop arguments')
    parser.add_argument('--test_job_count', default=4, type=int,
                        help='Parallel test jobs count')
    parser.add_argument('--tests_output_file', type=str, default='test_report.txt',
                        help='filename to store tests output')
    parser.add_argument('--select_test', type=str, default='',
                        help='select single test.')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    for greenplum in [True, False]:
        run_tests(output_file=args.tests_output_file, job_cnt=args.test_job_count,
                  select_test=args.select_test, greenplum=greenplum)


if __name__ == '__main__':
    main()
