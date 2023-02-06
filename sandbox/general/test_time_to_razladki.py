#!/usr/bin/env python

import config
import datetime
import time
import urllib2
import xmlrpclib


def send_to_razladki(info):
    data = '&'.join([str(key) + '=' + str(info[key]) for key in info])
    print 'Trying to send ' + data
    try:
        urllib2.urlopen(config.RAZLADKI_MARKUP, data).read()
        print 'OK'
        return True
    except Exception:
        print 'ERROR'
        return False


def main():
    server = xmlrpclib.ServerProxy(config.SANDBOX_RPC, allow_none=True)
    task_list = server.list_tasks({'task_type': 'TEST_ALL_TDI_AND_REARRANGE', 'descr_mask': 'rearrange-dynamic', 'hidden': True})

    extracted = []
    for t in task_list:
        try:
            info = {}
            info['start'] = t["ctx"]["children_execution_timing"][0]
            info['end'] = t['ctx']['children_execution_timing'][-1]
            if info['start'] is not None and info['end'] is not None:
                info['start'] = int(info['start'])
                info['end'] = int(info['end'])
                info['duration_hrs'] = (info['end'] - info['start']) / 3600.0
                info['start_hr'] = datetime.datetime.fromtimestamp(info['start']).strftime('%Y-%m-%d %H:%M:%S')
                info['end_hr'] = datetime.datetime.fromtimestamp(info['end']).strftime('%Y-%m-%d %H:%M:%S')
                extracted += [info]
        except Exception:
            pass

    extracted.sort(key=lambda x: float(x['end']))

    extracted = [x for x in extracted if x['end'] not in config.BANNED_TS and x['end'] + config.PERIOD_SEC > time.time()]

    to_razladki = [{'ts': x['end'], 'rd_test_time': x['duration_hrs']} for x in extracted]

    for info in to_razladki:
        send_to_razladki(info)


if __name__ == '__main__':
    main()
