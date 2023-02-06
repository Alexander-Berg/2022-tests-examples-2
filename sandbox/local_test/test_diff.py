from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
from sandbox.projects.yabs.partner_share.lib.diff import diff
from yql.api.v1.client import YqlClient

VALIDATE_TEMPLATE_PATH = '../jinja/validate_revert_history.jinja'


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
            with open(token_path, 'r') as f:
                token = f.read().replace('\n', '')
                if token:
                    print('Using ' + token_path + ' file for YQL token')
    if not token:
        sys.exit('Cannot find YQL token in environment variables YT_TOKEN or YQL_TOKEN or in file ~/.yt/token')
    return token


def main():
    yql_token=get_yql_token()
    res = diff.compare_changes_to_changes(
        cluster='hahn',
        issue='TESTTACCHANGES-1',
        changes1_path='//home/yabs/tac-manager/request/test2/filter/changes',
        changes2_path='//home/yabs/tac-manager/request/test2/test/changes',
        result_path='//home/yabs/tac-manager/request/test2/test/changes_dif',
        yql_tmp_folder='//home/yabs/tac-manager/yql_tmp',
        yql_token=yql_token
    )
    print(res)

    res = diff.compare_changes_to_history(
        cluster='hahn',
        issue='TESTTACCHANGES-1',
        changes_path='//home/yabs/tac-manager/request/test3/latest_changes',
        history_path='//home/yabs-cs-sandbox/input-archive-oneshots/07843570-75f5-4e4b-a55f-5e5c1a6300ff/home/yabs/overmind/PartherShareChangeHistory',
        result_path='//home/yabs/tac-manager/request/test3/test/history4_dif',
        yql_tmp_folder='//home/yabs/tac-manager/yql_tmp',
        yql_token=yql_token
    )
    print(res)

    res = diff.compare_history_to_changes(
        cluster='hahn',
        issue='TESTTACCHANGES-1',
        changes_path='//home/yabs/tac-manager/request/test3/latest_changes',
        history_path='//home/yabs-cs-sandbox/input-archive-oneshots/07843570-75f5-4e4b-a55f-5e5c1a6300ff/home/yabs/overmind/PartherShareChangeHistory',
        result_path='//home/yabs/tac-manager/request/test3/test/history5_dif',
        yql_tmp_folder='//home/yabs/tac-manager/yql_tmp',
        yql_token=yql_token
    )
    print(res)

    yql_client = YqlClient(token=yql_token)

    with open(VALIDATE_TEMPLATE_PATH, 'r') as f:
        validate_template_txt = f.read()
    diff.validate_revert_history(
        cluster='hahn',
        yql_client=yql_client,
        issue='TESTTACCHANGES-1',
        change_history_path='//home/yabs-cs-sandbox/input-archive-oneshots/4e7a3935-82e6-4e1d-aa63-1129a494f692/home/yabs/overmind/PartherShareChangeHistory',
        result_path='//home/yabs/tac-manager/request/test4/test',
        query_template_txt=validate_template_txt,
        yql_tmp_folder='//home/yabs/tac-manager/yql_tmp',
    )

if __name__ == "__main__":
    main()
