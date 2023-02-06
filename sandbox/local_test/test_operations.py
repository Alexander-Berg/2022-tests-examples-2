from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import json
from sandbox.common import fs
from sandbox.projects.yabs.partner_share.lib.config.config import (
    get_config,
    render_spec
)
from sandbox.projects.yabs.partner_share.lib.create_tables.create_tables import create_output_tables
from sandbox.projects.yabs.partner_share.lib.st_helper import StartrekHelper
from sandbox.projects.yabs.partner_share.lib.operations import run_imported_operation
import logging

logger = logging.getLogger(__name__)


def get_yql_token():
    token = os.environ.get('YQL_TOKEN')
    if token:
        print('Using YQL_TOKEN environment variable for YQL token')
    if not token:
        token = os.environ.get('YT_TOKEN')
        if token:
            print('Using YT_TOKEN environment variable for YQL token')
    if not token:
        token_path = os.path.expanduser("~/.yt/token")
        if os.path.exists(token_path):
            with open(token_path, 'r') as fil:
                token = fil.read().replace('\n', '')
                if token:
                    print('Using ' + token_path + ' file for YQL token')
    if not token:
        sys.exit('Cannot find YQL token in environment variables YT_TOKEN or YQL_TOKEN or in file ~/.yt/token')
    return token


class TestTask:
    def set_info(self, *args, **kwargs):
        logger.info(*args, file=sys.stderr)


def printt(v):
    print(type(v), v)


STARTREK_API_ENDPOINT = 'https://st-api.yandex-team.ru'


def run_operation(config, stage, operation_name):
    spec = render_spec(
        config['operations'][operation_name],
        task=TestTask(),
        constants=config['constants'],

        yql_token=get_yql_token(),
        yt_cluster='hahn',
        chyt_cluster='chyt.hahn/lelby_ckique',

        issue='TESTTACCHANGES-21',
        direct_issue='TESTTACCHANGES-21',
        filters=json.loads(
            fs.read_file('sandbox/projects/yabs/partner_share/lib/config/local_test/filter.json')
        ),
        ignore_partner_share_above=1000000,

        stage_folder=stage['stage_folder'],
        execute_folder=stage['execute_folder'],
        previous_folder=stage['previous_folder'],
        yt_root='//',
    )

    if spec.get('clickhouse'):
        create_output_tables(spec)

    if 'function' in spec:
        function_name = spec['function']
    else:
        function_name = operation_name

    run_imported_operation(function_name, spec)


def test_operations():
    config = get_config()
    stage = config['stages']['TEST']

    for operation_name in stage['operations']:
        if operation_name in (
            'set_max_partner_share_in_ticket',
            'direct_oneshot',
            'revert_oneshot',
        ):
            continue

        run_operation(config, stage, operation_name)

def main():
    test_operations()

if __name__ == "__main__":
    main()
