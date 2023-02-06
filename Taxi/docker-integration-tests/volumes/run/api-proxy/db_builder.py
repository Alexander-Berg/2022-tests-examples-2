#!/usr/bin/env python3
import argparse
import time

import requests
import yaml


def main():
    args = _parse_args()
    with open(args.resources) as resources_file:
        resources = list(yaml.load_all(resources_file))
    with open(args.endpoints) as endpoints_file:
        endpoints = list(yaml.load_all(endpoints_file))

    # wait service to start

    print('waiting api-proxy-manager to up')
    ping_url = 'http://%s/ping' % args.host
    while not _check_url_get(ping_url, args.timeout):
        time.sleep(1)
    print('api-proxy is up')

    # upload resources
    url = 'http://%s/admin/v1/resources' % (args.host,)
    for resource in resources:
        resource_id = resource.pop('id')
        resource['revision'] = 0
        params = {
            'url': url,
            'params': {'id': resource_id},
            'json': resource,
            'timeout': args.timeout,
        }
        print('creating resource: %s' % params)
        response = requests.put(**params)
        print(f'result: {response.status_code}, {response.content}')

    # upload endpoints code
    url = 'http://%s/admin/v2/endpoints/code' % (args.host,)
    for endpoint in endpoints:
        endpoint['git_commit_hash'] = 'deadbeef'
        params = {
            'url': url,
            'params': {
                'cluster': 'api-proxy',
                'id': endpoint['id'],
                'revision': str(0),
            },
            'json': {
                'data': endpoint,
                'last_state_signature': {},
            },
            'timeout': args.timeout,
        }
        print('upload endpoint code: %s' % params)
        response = requests.put(**params)
        print(f'result: {response.status_code}, {response.content}')

    # enable endpoints
    url = 'http://%s/admin/v2/endpoints/control/stable/' % (args.host,)
    for endpoint in endpoints:
        params = {
            'url': url,
            'params': {
                'cluster': 'api-proxy',
                'id': endpoint['id'],
                'revision': str(1),
            },
            'json': {
                'data': {'code_revision': 0, 'enabled': True},
                'last_state_signature': {'stable_rev': 0},
            },
            'timeout': args.timeout,
        }
        print('enable endpoint: %s' % params)
        response = requests.put(**params)
        print(f'result: {response.status_code}, {response.content}')


def _check_url_get(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, type=str)
    parser.add_argument('--resources', required=True, type=str)
    parser.add_argument('--endpoints', required=True, type=str)
    parser.add_argument('--sleep', required=True, type=int)
    parser.add_argument('--timeout', required=True, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    main()
