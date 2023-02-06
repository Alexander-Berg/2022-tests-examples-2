# Example:
# `python3 ./calc_extra_resources_testing.py
#  --cpu extra_cpu_services --ram extra_ram_services -v`
# Use sed command to extract services from digest:
# `sed -n '/Сервис:/{n;p;}' <digest_file>`
import argparse

import psycopg2
import requests as req

CPU_LIMIT_METRIC = 'quant(portoinst-cpu_limit_slot_hgram,max)'
RAM_LIMIT_METRIC = 'conv(quant(portoinst-memory_limit_slot_hgram, max), Gi)'

YASM_URL = 'http://yasm.yandex-team.ru/hist/series/'

HEJMDAL_DB_CONNECTION_DNS = ''  # <--- insert your connection string here

SERVICE_REQUEST = """
select * from services where name = '{}' and cluster_type = 'nanny'
 and deleted = false
"""
BRANCH_REQUEST = """
select * from branches where service_id = '{}' and env = '{}'
"""
HOSTS_REQUEST = """select host_name from branch_hosts where branch_id = {}"""

SERVICES_TO_EXCLUDE = ['buildagent-android']


def yasm_request(signal, host):
    response = req.post(
        YASM_URL,
        json={
            'headers': {},
            'ctxList': [
                {
                    'id': 'my_id',
                    'name': 'hist',
                    'st': 1602601541,  # <--- update start time manually
                    'et': 1602602041,  # <--- update end time manually
                    'period': 5,
                    'host': host,
                    'signals': [signal],
                },
            ],
        },
    )
    return response.json()


def get_limit(service, host, metric):
    signal = 'itype=' + service + ':' + metric
    resp = yasm_request(signal, host)
    if resp['status'] != 'ok':
        # retry
        resp = yasm_request(signal, host)
    vals = resp['response']['my_id']['content']['values'][signal]
    for value in vals:
        if value is not None:
            return value
    return None


def get_testing_hosts(service, cursor):
    cursor.execute(SERVICE_REQUEST.format(service))
    service_row = cursor.fetchone()
    if service_row is None:
        print('     Service {} not found in db'.format(service))
        return []
    if cursor.fetchone() is not None:
        print('     More than one service response for service ' + service)
    service_id = service_row[0]
    cursor.execute(BRANCH_REQUEST.format(service_id, 'testing'))
    hosts = []
    branch_rows = cursor.fetchall()
    for branch_row in branch_rows:
        branch_id = branch_row[0]
        cursor.execute(HOSTS_REQUEST.format(branch_id))
        host_rows = cursor.fetchall()
        for host_row in host_rows:
            hosts.append(host_row[0])

    return hosts


def get_extra(service, hosts, metric, nano_limit):
    limit = None
    hosts_size = len(hosts)
    i = 0
    while limit is None and i < hosts_size:
        limit = get_limit(service, hosts[i], metric)
        i += 1
    if limit is None:
        print('     FAILED TO FETCH LIMIT FROM YASM FOR SERVICE ' + service)
        return 0, limit
    if limit <= nano_limit:
        return 0, limit
    return (limit / 2) * hosts_size, limit


def get_cpu_extra(service, hosts):
    return get_extra(service, hosts, CPU_LIMIT_METRIC, 1.4)


def get_ram_extra(service, hosts):
    return get_extra(service, hosts, RAM_LIMIT_METRIC, 4)


def calc_total_extra(
        resource, filepath, metric, nano_limit, cursor, print_details,
):
    if print_details:
        print('{0} {0} {0}'.format(resource))
        print('{0} {0} {0}'.format(resource))
        print('{0} {0} {0}'.format(resource))
    total_extra = 0
    with open(filepath, 'r') as file_object:
        line = file_object.readline()
        while line:
            service_name = ' '.join(line.split())
            if service_name and service_name not in SERVICES_TO_EXCLUDE:
                testing_hosts = get_testing_hosts(service_name, cursor)
                if testing_hosts:
                    extra, limit = get_extra(
                        service_name, testing_hosts, metric, nano_limit,
                    )
                    if print_details and extra > 0:
                        print(' service: ' + service_name)
                        print('  testing hosts: {}'.format(len(testing_hosts)))
                        print('  limit:         {:.1f}'.format(limit))
                        print('  {} extra:     {:.1f}'.format(resource, extra))
                    total_extra += extra

            line = file_object.readline()
    return total_extra


def main():
    print('Hello')

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--cpu',
        '-c',
        type=str,
        help='extra cpu services filepath',
        required=True,
        dest='cpu',
    )
    parser.add_argument(
        '--ram',
        '-r',
        type=str,
        help='extra ram services filepath',
        required=True,
        dest='ram',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='print service details',
        action='store_true',
        dest='print_details',
    )

    args = parser.parse_args()

    conn = psycopg2.connect(HEJMDAL_DB_CONNECTION_DNS)
    cur = conn.cursor()

    cpu_extra = calc_total_extra(
        'CPU', args.cpu, CPU_LIMIT_METRIC, 1.4, cur, args.print_details,
    )
    ram_extra = calc_total_extra(
        'RAM', args.ram, RAM_LIMIT_METRIC, 4, cur, args.print_details,
    )

    if args.print_details:
        print(
            '---------------------\n--------TOTAL--------\n'
            '---------------------',
        )
    print('CPU extra: {:.1f}'.format(cpu_extra))
    print('RAM extra: {:.1f}'.format(ram_extra))


if __name__ == '__main__':
    main()
