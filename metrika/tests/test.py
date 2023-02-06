# coding=utf-8
#
__author__ = 'alexsingle'

"""
Скрипт сравнивает две версии browser.xml. По умолчанию предполагается, что продова версия лежит в папке data, тестовая - tools
На выходе получается таблица формата: Key - Old Value - New Value - Number of conflicted useragents - Exmaple of user agent

Пример использования:
python test.py -rd /home/alexsingle/arcadia/metrika/uatraits/tests/ -rp /home/alexsingle/arcadia/metrika/uatraits/data/ -p //home/metrica-analytics/alexsingle/useragent_top_5M -l 1000000

Опции запуска:
-rd, --rules_dev - Путь до папки uatraits/tools. По умолчанию используется папка из home директории
-rd, --rules_prod - Путь до папки uatraits/data. По умолчанию используется папка из home директории
-p, --path - Путь до таблицы с useragent на кластере hahn. По умолчанию оставил свою папку, где всегда лежит более-менее свежая выгрузка 1M useragent
-l, --limit - Top-l юзерагентов, 1000000 по умолчанию
-f, --file - Путь до файла с useragent. Если указан этот параметр, то ему отдается предпочтение
-v, --verbose - Полный вывод всех конфликтующийх юзерагентов

Необходимы дополнительные библиотеки:
yt, pandas, uatraits
"""

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
import multiprocessing
import Queue
import argparse
import time
import sys
import os
import random
from StringIO import StringIO
import pandas as pd
import uatraits
import yt.wrapper as yt
reload(sys)
sys.setdefaultencoding('utf8')
yt.config.set_proxy('hahn.yt.yandex.net')


def get_ua_list(path, limit):
    """
    Функция читает список ua на hahn. path - путь на hahn. limit - сколько строк прочиатать
    """
    limit_path = ''
    if limit:
        limit_path = '[:#{limit}]'.format(limit=limit)
    full_list_df = pd.DataFrame(yt.read_table(path + limit_path, format=yt.SchemafulDsvFormat(columns=['useragent']), raw=False))
    full_list = full_list_df['useragent'].values
    return full_list


def get_ua_data(out_queue, ua_list, rules_dev, rules_prod):
    """
    Основная функция для проверки корректности новой версии uatraits-data.
    Вариант для использования совместно с multiprocessing
    """
    test_data = ''
    # Создаются два обеъкта детектора. При этом загружаются все наборы правил: browser.xml, profiles.xml, extra.xml
    dev_detector = uatraits.detector(rules_dev + 'browser.xml', rules_dev + 'profiles.xml', rules_dev + 'extra.xml')
    prod_detector = uatraits.detector(rules_prod + 'browser.xml', rules_prod + 'profiles.xml', rules_prod + 'extra.xml')

    for one in ua_list:
        try:
            result_dev = dev_detector.detect(one)
            result_prod = prod_detector.detect(one)
            # Далее проверка на то, что в каждом dict одинаковый набор ключей и все значения совпадают
            for one_key in result_dev:
                if one_key not in result_prod:
                    test_data += '\t'.join([str(one_key), '', str(result_dev[one_key]), one.replace('\n', '').replace('\t', '')]) + '\n'
                else:
                    if result_prod[one_key] != result_dev[one_key]:
                        test_data += '\t'.join([str(one_key), str(result_prod[one_key]), str(result_dev[one_key]), one.replace('\n', '').replace('\t', '')]) + '\n'
            for one_key in result_prod:
                if one_key not in result_dev:
                    test_data += '\t'.join([str(one_key), str(result_prod[one_key]), '', one.replace('\n', '').replace('\t', '')]) + '\n'
        except Exception as e:
            print(e)
    out_queue.put(test_data)


def multi_requests(user_agents, rules_dev, rules_prod, processes=128):
    """
    Функция для паралелльной обработки списка ua
    На вход принимает список ua, пути до папок с правилами и число одноврменных процессов
    """
    test_data = ''
    kount = len(user_agents)/processes+1
    out_queue = multiprocessing.Queue()
    # Делим список ua на processes частей и для каждого спика паралелльно запускаем проверку
    proc_all = [multiprocessing.Process(target=get_ua_data, args=[out_queue, user_agents[k*kount:(k+1)*kount], rules_dev, rules_prod]) for k in xrange(processes+1)]
    for proc in proc_all:
        proc.start()
    liveprocs = list(proc_all)
    # Цикл нужен, чтобы аккуратно считать все из очереди и не пытаться бесконечно прочитать пустую очередь
    while liveprocs:
        try:
            while 1:
                test_data += out_queue.get(False)
        except Queue.Empty:
            pass
        time.sleep(0.75)
        if not out_queue.empty():
            continue
        liveprocs = [p for p in liveprocs if p.is_alive()]
    return test_data


def test_data(data):
    """
    Функция для создания таблицы из списка с конфликтующими ua
    """
    header = 'Key\tOld value\tNew value\tUserAgent\n'

    final_data = header + data

    df_ua = pd.read_csv(StringIO(final_data), sep='\t')\
              .fillna('')\
              .groupby(['Key', 'Old value', 'New value'])\
              .agg({"UserAgent": [('Hits', lambda x: x.count()), ('UserAgentExample', lambda x: x.iloc[random.choice(range(0, len(x)))])]})\
              .reset_index()
    df_ua.columns = ['Key', 'Old value', 'New value', 'Hits', 'UserAgentExample']
    df_ua = df_ua.sort_values('Hits', ascending=False)
    result = df_ua.to_csv(sep='\t', index=False)
    return result


if __name__ == '__main__':
    rules_dev = os.path.expanduser('~/arcadia/metrika/uatraits/tests/')
    rules_prod = os.path.expanduser('~/arcadia/metrika/uatraits/data/')
    path_default = '//home/metrica-analytics/alexsingle/useragent_top_5M'

    parser = argparse.ArgumentParser(description='Options parser')
    parser.add_argument('-rd', '--rules_dev', action='store', default=rules_dev, help='Browser.xml from tools')
    parser.add_argument('-rp', '--rules_prod', action='store', default=rules_prod, help='Browser.xml from data')
    parser.add_argument('-p', '--path', action='store', default=path_default, help='Path for saved data')
    parser.add_argument('-l', '--limit', action='store', default='5000000', help='Number of useragents tested')
    parser.add_argument('-f', '--file', action='store', default='', help='File with user agents')
    parser.add_argument('-v', '--verbose', action='store_true',  help='Print all coflicted useragents')
    args = parser.parse_args()

    start = time.time()

    if args.file:
        with open(args.file, 'r') as f:
            ua_list = f.readlines()
    else:
        ua_list = get_ua_list(args.path, args.limit)

    final_data = multi_requests(ua_list, args.rules_dev, args.rules_prod)

    if args.verbose:
        print(final_data)
    if final_data:
        print(test_data(final_data))
    else:
        print('All good')

    end = time.time()
    print(end-start)
