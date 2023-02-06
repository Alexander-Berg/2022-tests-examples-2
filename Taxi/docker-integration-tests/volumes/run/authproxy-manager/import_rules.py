#!/usr/bin/env python3
import argparse
import json
import time

import requests


def main():
    args = _parse_args()
    with open(args.rules) as rules_file:
        rules = list(json.load(rules_file))

    # wait service to start

    print('waiting authproxy-manager to up')
    ping_url = 'http://%s/ping' % args.host
    while not _check_url_get(ping_url, args.timeout):
        time.sleep(1)
    print('authproxy-manager is up')

    # upload resources
    url = 'http://%s/v1/rules/by-name' % (args.host,)
    params = {
        'proxy': 'passenger-authorizer',
    }
    for rule in rules:
        name = rule['input']['rule_name']
        params['rule-name'] = name
        params['maintained-by'] = rule['input']['maintained_by']
        print('creating rule: %s' % name)

        response = requests.put(url, params=params, json=rule)
        print(f'result: {response.status_code}, {response.content}')
        response.raise_for_status()


def _check_url_get(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, type=str)
    parser.add_argument('--rules', required=True, type=str)
    parser.add_argument('--sleep', required=True, type=int)
    parser.add_argument('--timeout', required=True, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    main()
