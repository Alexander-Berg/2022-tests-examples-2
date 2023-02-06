# pylint: skip-file
# flake8: noqa
import json
import re

import subprocess

import paramiko

from helpers.config import read_static_config, read_secret_config


def _clean_bash_formatting(string):
    return re.sub(r'\[.*?;.*?m', '', string)


def _generate_service_ticket_for_passport(qloud_client):
    stdin, stdout, stderr = qloud_client.exec_command(
        'curl -X GET '
        '"http://localhost:1/tvm/tickets?dsts=223&src=2016547" '
        '-H "Authorization: $QLOUD_TVM_TOKEN"',
    )
    service_ticket = json.loads(str(stdout.read())[2:-1])[
        'blackbox.yandex-team.ru'
    ]['ticket']
    return service_ticket


def _generate_user_ticket(
        qloud_client, service_ticket_for_passport, oauth_token, user_ip,
):
    stdin, stdout, stderr = qloud_client.exec_command(
        f'curl -X GET '
        f'"http://blackbox.yandex-team.ru/blackbox'
        f'?method=oauth&format=json&regname=yes&get_user_ticket=true'
        f'&oauth_token={oauth_token}&userip={user_ip}&get_user_ticket=true" '
        f'-H "X-Ya-Service-Ticket: {service_ticket_for_passport}"',
    )
    parsed_response = json.loads(str(stdout.read())[2:-3])
    yandex_uid = str(parsed_response['oauth']['uid'])
    user_ticket = str(parsed_response['user_ticket'])
    return user_ticket, yandex_uid


def generate_service_ticket():
    config = read_static_config()
    tvm_knife_response = subprocess.run(
        [
            config['ya_tool_path'],
            'tool',
            'tvmknife',
            'get_service_ticket',
            'sshkey',
            '--src',
            '2013636',
            '--dst',
            '2016267',
        ],
        capture_output=True,
    )
    if tvm_knife_response.returncode != 0:
        raise RuntimeError(
            f'tvmknife failed: {_clean_bash_formatting(tvm_knife_response.stderr)}',
        )
    return tvm_knife_response.stdout.decode('utf-8').strip('\n')


def generate_user_ticket_return_ticket_yandex_uid():
    config = read_static_config()
    secret_config = read_secret_config()
    qloud_client = paramiko.SSHClient()
    qloud_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    qloud_client.connect(hostname=config['qloud_host'], port=config['port'])
    service_ticket_for_passport = _generate_service_ticket_for_passport(
        qloud_client,
    )
    user_ticket, yandex_uid = _generate_user_ticket(
        qloud_client,
        service_ticket_for_passport,
        secret_config['oauth_token'],
        config['user_ip'],
    )
    qloud_client.close()
    return user_ticket, yandex_uid
