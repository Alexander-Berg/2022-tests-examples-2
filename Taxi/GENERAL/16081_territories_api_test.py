# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import argparse
import time

from taxi.core import async
from taxi.external import territories

CALLS = 100
SLEEP_TIME = 0.5
RETRIES = 3
RETRY_INTERVAL = 1


@async.inline_callbacks
def _check(method, calls, sleep_time, *args):
    total = 0
    stat = []
    for _ in xrange(calls):
        start = time.time()
        yield method(*args)
        spent = (time.time() - start) * 1000
        stat.append(spent)
        total += spent
        async.sleep(sleep_time)
    print 'Количество запросов: {}'.format(calls)
    print 'Среднее время ответа: {} мс.'.format(total / calls)
    stat.sort()
    print 'Время ответа в 80% случаев не превышает: {} мс.'.format(
        stat[int(0.8*len(stat))]
    )
    print 'Время ответа в 95% случаев не превышает: {} мс.'.format(
        stat[int(0.95*len(stat))]
    )
    print 'Максимальное время ответа: {} мс.'.format(stat[-1])


@async.inline_callbacks
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calls', type=int, default=CALLS)
    parser.add_argument('--sleep_time', type=float, default=SLEEP_TIME)
    parser.add_argument('--retries', type=float, default=RETRIES)
    parser.add_argument('--retry_interval', type=float, default=RETRY_INTERVAL)
    args = parser.parse_args()
    print '--- /v1/countries/list ---'
    yield _check(
        territories.get_all_countries, args.calls, args.sleep_time,
        args.retries, args.retry_interval,
    )
    print
    print '--- /v1/countries/retrieve ---'
    yield _check(
        territories._perform_post, args.calls, args.sleep_time,
        'v1/countries/retrieve', {'_id': 'rus'}, args.retries,
        args.retry_interval,
    )


if __name__ == "__main__":
    main()
