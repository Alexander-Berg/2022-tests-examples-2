#!/usr/bin/env python3
import argparse
import collections
import json
import typing

import requests

import get_services


OAUTH_TOKEN_REQUEST = (
    'https://oauth.yandex-team.ru/authorize?'
    'response_type=token&client_id=ed682c8c3e9c489cb0734062fc675a3d'
)


def _request(
        resource: str,
        auth_token: str,
        url: str,
) -> typing.Dict:
    response = requests.get(
        url=f'{url}/api/admin/configs-admin/v1/configs/{resource}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {auth_token}',
        },
        verify=False,
    )
    if response.status_code != 200:
        raise RuntimeError(f'Failed to get from {url}:\n' f'{response.text}')
    return response.json().get('value')


def get_tvm_rules(
        token: str,
        admin_url: str,
) -> typing.Dict:
    resource = 'TVM_RULES'
    return _request(resource, token, admin_url)


def get_tvm_services(
        token: str,
        admin_url: str,
) -> typing.Dict:
    resource = 'TVM_SERVICES'
    return _request(resource, token, admin_url)


def get_taxi_secdist_json(file: str) -> typing.Dict:
    with open(file, 'r') as stream:
        content = json.load(stream)
    return content['settings_override']['TVM_SERVICES']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compose-file', type=str, required=True)
    parser.add_argument(
        '--taxi-json',
        type=str,
        default='volumes/taxi-secdist/taxi.json',
        help='path to taxi.json file',
    )
    parser.add_argument(
        '--token',
        type=str,
        required=True,
        help='OAuth token to access to tariff-editor:\n'
        f'to get token follow {OAUTH_TOKEN_REQUEST}',
    )
    parser.add_argument(
        '--taxi-admin-url',
        type=str,
        default='http://tariff-editor.taxi.yandex-team.ru',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    taxi_json = args.taxi_json
    compose_file = args.compose_file
    auth_token = args.token
    admin_url = args.taxi_admin_url

    services = get_services.load_services(docker_compose_files=(compose_file,))
    tvm_rules = get_tvm_rules(auth_token, admin_url)
    tvm_keys = get_tvm_services(auth_token, admin_url)
    tvm_services = get_taxi_secdist_json(taxi_json)

    for service in services:
        related = [
            entry['src'] for entry in tvm_rules if entry['dst'] == service
        ]
        for serv in related:
            if serv not in tvm_services:
                _id = tvm_keys.get(serv)
                if _id is not None:
                    tvm_services[serv] = {'id': _id, 'secret': 'secret'}

    with open(taxi_json, 'r+') as json_file:
        json_obj = collections.OrderedDict(json.load(json_file))
        json_file.seek(0)
        json_obj['settings_override']['TVM_SERVICES'] = {
            key: value for key, value in sorted(tvm_services.items())
        }
        json.dump(json_obj, json_file, indent=2)
        json_file.truncate()


if __name__ == '__main__':
    main()
