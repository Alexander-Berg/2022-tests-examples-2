from pathlib import Path
from sandbox.projects.yabs.partner_share.lib.changes import changes
import json
import sys
import os

FILTER_TEMPLATE_PATH = '../jinja/filter.jinja'
CHANGES_TEMPLATE_PATH = '../jinja/changes.jinja'


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


def main():
    request_id = 'test6'
    query = changes.generate_changes_yql_query(
        cluster='hahn',
        filters=json.loads(Path('filter.json').read_text())['filters'],
        changes_table_path=f'//home/yabs/tac-manager/request/{request_id}/filter/changes',
        filter_template_txt=Path(FILTER_TEMPLATE_PATH).read_text(),
        changes_template_txt=Path(CHANGES_TEMPLATE_PATH).read_text(),
        yql_tmp_folder='//tmp',
    )
    Path('test_query.sql').write_text(query)

if __name__ == "__main__":
    main()
