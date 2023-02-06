import argparse
import six

from nile.api.v1 import clusters
from nile.api.v1 import aggregators as na
from nile.api.v1 import extractors as ne

from projects.common.nile.environment import configure_environment

################################################################################

def get_day(dttm):
    dttm = six.ensure_str(dttm)
    return dttm.split(' ')[0]

def get_hour(dttm):
    dttm = six.ensure_str(dttm)
    return dttm.split()[1].split(':')[0]

def has_order(order_id_paid_list):
    if order_id_paid_list is None:
        return False
    return len(order_id_paid_list) > 0

def get_time(day, hour):
    return '{} {}:00:00'.format(six.ensure_str(day), six.ensure_str(hour))

################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description='Conversion calculator')
    parser.add_argument('--cluster', default='hahn.yt.yandex.net')
    parser.add_argument('--user-sessions',
                        default='home/taxi-dwh/dds/food/eda_user_appsession')
    parser.add_argument('--from-date', required=True)
    parser.add_argument('--to-date', required=True)
    parser.add_argument('--out-table', required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    
    cluster = clusters.YT(args.cluster)
    job = configure_environment(cluster.job('conversion calculator'))

    dates = '{{{}..{}}}'.format(args.from_date, args.to_date)
    tables = '{}/{}'.format(args.user_sessions, dates)
    sessions = job.table(tables)

    tmp = sessions.project(day=ne.custom(get_day, 'utc_session_start_dttm'),
                           hour=ne.custom(get_hour, 'utc_session_start_dttm'),
                           has_order=ne.custom(has_order, 'order_id_paid_list'))
    tmp = tmp.groupby('day', 'hour').aggregate(conversion=na.mean('has_order'))
    result = tmp.project('conversion', time=ne.custom(get_time, 'day', 'hour'))
    result.put(args.out_table)
    job.run()

################################################################################

if __name__ == '__main__':
    main()

################################################################################
