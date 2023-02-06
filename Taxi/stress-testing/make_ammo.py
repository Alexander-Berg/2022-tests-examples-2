# pylint: disable=using-constant-test
# pylint: disable=invalid-name

# see: https://yandextank.readthedocs.io/en/latest/tutorial.html#uri-post-style
# NB! use right 'ammo_type'

import argparse
from contextlib import contextmanager
from datetime import datetime
import fileinput
import json
import random
import sys


def _write_heading(out):
    out.write('[Host: billing-accounts.taxi.tst.yandex.net]\n')
    out.write('[User-Agent: Tank]\n')
    out.write('[Content-Type: application/json]\n')


def _entity_create(output, rec, args):
    external_id = rec['external_id']
    kind = rec['kind']
    body = f'{{"external_id": "{external_id}", "kind": "{kind}"}}'
    url = '/v1/entities/create'
    output.write(f'{len(body)} {url}\n{body}\n')


def _entity_search(output, rec, args):
    external_id = rec['external_id']
    body = f'{{"external_id": "{external_id}"}}'
    url = '/v1/entities/search'
    output.write(f'{len(body)} {url}\n{body}\n')


def _account_create(output, rec, args):
    external_id = rec['external_id']
    agreement_id = args.agreement_id
    currency = rec['currency']
    sub_account = args.sub_account
    body = (
        '{'
        f'"entity_external_id":"{external_id}",'
        f'"agreement_id":"{agreement_id}",'
        f'"currency":"{currency}",'
        f'"sub_account":"{sub_account}",'
        '"expired":"2118-01-01T00:00:00+00:00"'
        '}'
    )
    url = '/v1/accounts/create'
    output.write(f'{len(body)} {url}\n{body}\n')


def _account_search(output, rec, args):
    external_id = rec['external_id']
    agreement_id = args.agreement_id
    currency = rec['currency']
    sub_account = args.sub_account
    body = (
        '{'
        f'"entity_external_id":"{external_id}",'
        f'"agreement_id":"{agreement_id}",'
        f'"currency":"{currency}",'
        f'"sub_account":"{sub_account}"'
        '}'
    )
    url = '/v1/accounts/search'
    output.write(f'{len(body)} {url}\n{body}\n')


def _balances_select_by_account(output, rec, args):
    entity = random.choice(['driver_id', 'park_id', 'user_id'])
    external_id = rec[entity]
    agreement_id = args.agreement_id
    currency = rec['currency']
    sub_account = args.sub_account
    account = (
        '{'
        f'"entity_external_id":"{external_id}",'
        f'"agreement_id":"{agreement_id}",'
        f'"currency":"{currency}",'
        f'"sub_account":"{sub_account}"'
        '}'
    )
    if args.balances_on_date:
        due = args.balances_on_date
    else:
        due = datetime.utcfromtimestamp(rec['due']).isoformat()
    accrued_at = f'["{due}"]'

    body = (
        '{'
        f'"offset": 0, "limit": 1, "accounts": [{account}], '
        f'"accrued_at": {accrued_at}'
        '}'
    )
    url = '/v1/balances/select'
    output.write(f'{len(body)} {url}\n{body}\n')


def _generate(inp, out, args, func):
    _write_heading(out)
    cnt = 1
    for line in inp:
        if cnt > args.limit:
            break
        # skip random number of lines
        if random.getrandbits(5) == 7:
            cnt += 1
            func(out, json.loads(line), args)


def _generate_ammo(inp, out, args):
    if args.make_entities == 'create':
        _generate(inp, out, args, _entity_create)
    if args.make_entities == 'search':
        _generate(inp, out, args, _entity_search)
    if args.make_accounts == 'create':
        _generate(inp, out, args, _account_create)
    if args.make_accounts == 'search':
        _generate(inp, out, args, _account_search)
    if args.balances_select == 'account':
        _generate(inp, out, args, _balances_select_by_account)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', default='-', help='Input json file')
    parser.add_argument(
        '--make-entities', default='', help='Make entities request ammo',
    )
    parser.add_argument(
        '--make-accounts', default='', help='Make accounts request ammo',
    )
    parser.add_argument(
        '--agreement_id', default='STRESS', help='Accounts agreement',
    )
    parser.add_argument(
        '--sub-account', default='COST', help='Accounts sub-account',
    )
    parser.add_argument(
        '--balances-select',
        default='',
        help='Make select balances request ammo',
    )
    parser.add_argument(
        '--balances-on-date', default='', help='Select balances on date',
    )
    parser.add_argument(
        '--output',
        default='-',
        help='Output file name, default to standard out',
    )
    parser.add_argument(
        '--limit', type=int, default=100000, help='Limit rows in output file',
    )

    return parser.parse_args()


def _write(args, generator):
    @contextmanager
    def _open(filename):
        if filename != '-':
            with open(filename, 'w') as f:
                yield f
        else:
            yield sys.stdout

    with fileinput.input(args.input) as inp:
        with _open(args.output) as out:
            generator(inp, out, args)


def main():
    args = _parse_args()
    _write(args, _generate_ammo)


if __name__ == '__main__':
    main()
