#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
import sys

import dateutil.parser
import pytz

from taxi_buildagent import utils
from taxi_buildagent.clients import arcadia
from taxi_buildagent.clients import github
from taxi_buildagent.clients import teamcity

logger = logging.getLogger(__name__)

PRINT_UPDATED_AT_FORMAT = '%Y-%m-%d %H:%M:%SZ'
GITHUB_PR_PREFIXES = 'pull/'
GITHUB_PR_SUFFIXES = ('/merge', '/head')
ARCANUM_PR_SUFFIXES = ('/merge_pin', '/merge_head', '/head')
PROVIDERS = ('github', 'arcanum')


def main(argv=None):
    build_id = os.getenv('BUILD_ID')
    if build_id:
        build = teamcity.get_build_info(build_id, verify=False)
        if build['status'] == 'FAILURE':
            print('Already failed. Skip tests.', file=sys.stderr)
            teamcity.send_teamcity_multiattribute_message(
                'buildStop', comment='Build already failed before tests',
            )
            return

    args = parse_args(argv)
    if args.provider == 'github':
        if args.pr.endswith(GITHUB_PR_SUFFIXES):
            pull_req = args.pr.split('/')[-2]
        elif args.pr.startswith(GITHUB_PR_PREFIXES):
            pull_req = args.pr.split('/')[1]
        else:
            print('It is not Pull Request')
            return
    elif args.provider == 'arcanum':
        if args.pr.endswith(ARCANUM_PR_SUFFIXES):
            pull_req = args.pr.split('/')[-2]
        else:
            print('It is not Pull Request')
            return
    else:
        assert False, f'{args.provider} is not supported!'

    utils.init_logger()

    updated_at = get_pull_request_update(args.provider, pull_req)

    print(
        'Pull Request last update:',
        updated_at.strftime(PRINT_UPDATED_AT_FORMAT),
    )
    today = pytz.utc.localize(datetime.datetime.utcnow())

    if (today - updated_at).days >= args.days:
        print('Too old Pull Request. Skip tests.', file=sys.stderr)
        teamcity.report_build_problem(
            'Too old Pull Request', identity='old-pr',
        )
        sys.exit(1)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', required=True)
    parser.add_argument('--days', type=int, required=True)
    parser.add_argument('--provider', required=True, choices=PROVIDERS)
    return parser.parse_args(argv)


def get_pull_request_update(
        provider: str, pull_request_id: str,
) -> datetime.datetime:
    if provider == 'arcanum':
        updated = arcadia.get_pull_request(int(pull_request_id)).updated_at
    elif provider == 'github':
        updated = github.get_pull_request_by_id(pull_request_id).updated_at
    else:
        assert False, f'{provider} is not supported!'

    assert updated is not None  # to avoid mypy error
    return dateutil.parser.parse(updated)


if __name__ == '__main__':
    main()
