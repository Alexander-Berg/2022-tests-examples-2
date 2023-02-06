#!/usr/bin/env python3
import datetime
import json
import random

MAX_AMMOS = 1000
MAX_SERVICES = 13
MAX_METRICS = 73

MAX_METRICS_PER_REQUEST = 10
MAX_VALUES = 30


def main():
    with open('/tmp/ammo', 'w') as ammo_file:
        now = datetime.datetime.utcnow()
        for item in range(MAX_AMMOS):
            service = item % MAX_SERVICES
            metric = item % MAX_METRICS

            headers = (
                'Host: statistics.taxi.yandex.net\r\n'
                + 'User-Agent: tank\r\n'
                + 'Accept: */*'
            )

            ammo_file.write(make_store_ammo(service, metric, headers, now))
            ammo_file.write(make_list_ammo(service, metric, headers, now))
            now += datetime.timedelta(seconds=0.1)


def make_store_ammo(service, metric, headers, now):
    metrics_len = int(random.uniform(0, MAX_METRICS_PER_REQUEST))
    body = {
        'service': str(service),
        'metrics': [
            {
                'name': str(metric + i),
                'value': int(random.uniform(0, MAX_VALUES)),
            }
            for i in range(metrics_len)
        ],
        'time_bucket': f'{now.replace(microsecond=0).isoformat()}Z',
    }
    return make_ammo('POST', '/v1/metrics/store', headers, 'post', body)


def make_list_ammo(service, metric, headers, now):
    metrics_len = int(random.uniform(0, MAX_METRICS_PER_REQUEST))
    body = {
        'service': str(service),
        'metric_names': [str(metric + i) for i in range(metrics_len)],
        'interval': 60,
        'timestamp': f'{now.isoformat()}Z',
    }
    return make_ammo('POST', '/v1/metrics/list', headers, 'list', body)


def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = '%s %s HTTP/1.1\r\n' '%s\r\n' '\r\n'

    # http request with entity body template
    req_template_w_entity_body = (
        '%s %s HTTP/1.1\r\n' '%s\r\n' 'Content-Length: %d\r\n' '\r\n' '%s\r\n'
    )

    if not body:
        req = req_template % (method, url, headers)
    else:
        body = json.dumps(body)
        req = req_template_w_entity_body % (
            method,
            url,
            headers,
            len(body),
            body,
        )

    # phantom ammo template
    ammo_template = '%d %s\n' '%s'

    return ammo_template % (len(req), case, req)


if __name__ == '__main__':
    main()
