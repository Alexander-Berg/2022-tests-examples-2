from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import argparse
import os
from sandbox.projects.yabs.partner_share.lib.ok_helper import OkHelper, iframe_text
from sandbox.projects.yabs.partner_share.lib.st_helper import StartrekHelper
from sandbox.projects.yabs.partner_share.lib.config.config import get_config

logging.basicConfig(level=logging.WARN)

STARTREK_API_ENDPOINT = 'https://st-api.yandex-team.ru'


def get_st_token():
    token = ''
    token_path = os.path.expanduser("~/.startrek/token")
    if os.path.exists(token_path):
        with open(token_path, 'r') as fil:
            token = fil.read().replace('\n', '')
            if token:
                print('Using ' + token_path + ' file for Startrek token')
    return token


def main():
    parser = argparse.ArgumentParser(description="Test ok helper")
    parser.add_argument("ok_token", help="OAuth OK token, get here: https://oauth.yandex-team.ru/authorize?response_type=token&client_id=0137c50bcf1e45afaa7a9fdd8d17fc72")
    parser.add_argument("st_ticket", help="St ticket, e.g. TESTTACCHANGES-95")
    args = parser.parse_args()

    st_helper = StartrekHelper(
        useragent="sandbox",
        startrek_api_url=STARTREK_API_ENDPOINT,
        st_token=get_st_token(),
        local_fields_prefix='',
    )

    followers = st_helper.get_followers(args.st_ticket)
    print(followers)
    followers.append('aark')
    st_helper.set_followers(args.st_ticket, list(set(followers)))

    author = st_helper.get_field(args.st_ticket, 'createdBy').id
    summary = st_helper.get_field(args.st_ticket, 'summary')
    uid = 1
    print('Author, summary:', author, summary)

    config = get_config()
    ok_helper = OkHelper(args.ok_token, config['approvals'])
    result = ok_helper.start_approve(
        ticket=args.st_ticket,
        uid=uid,
        author=author,
        approve_type='DEV',
        text=summary,
        admin_groups=[]
    )
    print('UUID', result.json().get('uuid'))

    result = ok_helper.resume_approve(
        ticket=args.st_ticket,
        uid=uid,
        author=author,
    )

    st_helper.add_comment(args.st_ticket, iframe_text(
        ticket=args.st_ticket,
        uid=uid,
        author=author
    ))

if __name__ == "__main__":
    main()
