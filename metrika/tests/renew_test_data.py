# coding=utf-8
__author__ = 'alexsingle'

"""
Создает таблицу с тестовыми юзерагентами. Таблица строится по даннм метрики и выбирает топ-N устройств по трафику
Всего уникальных юзерагентов в день 17M. Top-100k покрывает 93.5% хитов, top-1M - 98.5%, top-5M - 99.7%, top-10M 99.93% (2020-09-23)

Пример использования:
python renew_test_data.py -d 2020-09-23 -p home/metrica-analytics/alexsingle/useragent_top_5M -l 5000000

Опции запуска:
-d, --date - Дата, по умолчанию вчера
-p, --path - Путь, куда будет сохранятся таблица
-l, --limit - Top-l юзерагентов, 1000000 по умолчанию

Необходимы дополнительные библиотеки:
yql
"""

import os
import sys
import datetime
import argparse
from yql.api.v1.client import YqlClient
reload(sys)
sys.setdefaultencoding('utf8')

TOP = 5000000


def generate_ua_list(date, path, limit):

    with open(os.path.expanduser('~/.yql/token')) as f:
        token = f.read()

    yql_query = """
        insert into hahn.`{path}` WITH TRUNCATE

        select
            useragent,
            count(*) as hits
        from
            `logs/bs-watch-log/1d/{date}`
        where
            useragent!=''
        group by
            useragent
        order by
            hits desc
        limit {limit};

    """

    with YqlClient(db="hahn", token=token) as client:
        yql_data = client.query(yql_query.format(date=date, path=path, limit=limit), syntax_version=1)
        yql_data.run()
    print(yql_data)


if __name__ == '__main__':
    yesterday = str((datetime.datetime.now()-datetime.timedelta(days=1)).date())
    parser = argparse.ArgumentParser(description='Options parser')
    parser.add_argument('-d', '--date', action='store', default=yesterday, help='Date for data')
    parser.add_argument('-p', '--path', action='store', default='', help='Path for saved data')
    parser.add_argument('-l', '--limit', action='store', default=str(TOP), help='Path for saved data')
    args = parser.parse_args()

    generate_ua_list(args.date, args.path, args.limit)
