#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Usage:
cd usevices/services/order-core/load-tests
python generate_ammo.py > /path/to/ammo/output/file

Data from ammo_in corresponds to orders stored in
testsuite/tests_taxi_order_core/static/test_service/db_order_proc.json
Keep this in mind if you want to change it.
"""

import sys

INPUT_FILE = 'ammo_in'


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


def main():
    with open(INPUT_FILE, 'r') as file:
        for line in file.readlines():
            try:
                method, url, case, body = line.split('||')
                body = body.strip()
            except ValueError:
                method, url, case = line.split('||')
                body = None

            method, url, case = method.strip(), url.strip(), case.strip()

            headers = (
                'Host: order-core.taxi.yandex.net\r\n'
                + 'User-Agent: tank\r\n'
                + 'Accept: */*\r\n'
                + 'Accept-Language:ru-Ru'
            )
            sys.stdout.write(make_ammo(method, url, headers, case, body))


if __name__ == '__main__':
    main()
