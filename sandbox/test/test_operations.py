from __future__ import unicode_literals
from __future__ import print_function

import sys
import json
from sandbox.common import fs
from sandbox.projects.yabs.partner_share.lib.config.config import (
    get_config,
    render_spec
)
from sandbox.projects.yabs.partner_share.lib.operations import run_imported_operation
import logging

logger = logging.getLogger(__name__)


class TestTask:
    def set_info(self, *args, **kwargs):
        print(*args, file=sys.stderr)


def run_operation(config, stage_name, operation_name):
    spec = render_spec(
        config=config,
        stage_name=stage_name,
        operation_name=operation_name,
        task=TestTask(),

        yql_token='',
        yt_cluster='hahn',
        chyt_cluster='chyt.hahn/lelby_ckique',
        yt_root='//',

        issue='TESTTACCHANGES-21',
        direct_issue='TESTTACCHANGES-21',
        filters=json.loads(
            fs.read_file('filter.json')
        ),
        ignore_partner_share_above=1000000,

        dont_run_yql=True,
    )

    if 'function' in spec:
        function_name = spec['function']
    else:
        function_name = operation_name

    run_imported_operation(function_name, spec)


def test_operations():
    config = get_config()
    stage_name = 'TEST'
    stage = config['stages'][stage_name]

    for operation_name in stage['operations']:
        if operation_name in (
            'set_max_partner_share_in_ticket',
            'direct_oneshot',
            'revert_oneshot',
        ):
            continue

        run_operation(config, stage_name, operation_name)
