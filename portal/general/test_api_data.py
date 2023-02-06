# encoding: utf-8
"""
Import data from YT to achievements database.

Не забыть про токен в ~/.yt/token !!
"""

from __future__ import print_function
import json
import yt.wrapper as yt
import MySQLdb
import argparse
import sys
from datetime import datetime, timedelta

YT_TABLE = '//statbox/heavy-report/achievments/final_v2/states_to_bd_v2'


def get_yandexuid_age(yandexuid):
    yuid = yandexuid.split('y')[1]
    yuid_timestamp = int(yuid[-10:])
    yuid_time = datetime.fromtimestamp(yuid_timestamp)
    if yuid_time > datetime.now():
        return 0
    if datetime.now() - yuid_time > timedelta(days=3650):
        return 0
    # print(datetime.now().timestamp())
    return (datetime.now() - yuid_time).total_seconds()


def read_from_yt(num_from, num_to):
    client = yt.YtClient(proxy='hahn')
    return client.read_table('{}[#{}:#{}]'.format(YT_TABLE, num_from, num_to), format="json")


def main(args):
    total_yuids = 0
    total_age = 0

    for record in read_from_yt(args.row_from, args.row_to):
        age = get_yandexuid_age(record['yuid'])
        if age > 0:
            total_yuids += 1
            total_age += age
    print('total_yuids:', total_yuids, 'total_age:', total_age)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy from YT table to mysql")
    parser.add_argument("-f", "--row_from", help="row number to copy from", required=True)
    parser.add_argument("-t", "--row_to", help="row number to copy to", required=True)
    parser.add_argument("-d", "--dev", help="dev-instance mode", action='store_true')
    main(parser.parse_args())
