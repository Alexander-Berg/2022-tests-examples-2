import argparse
import asyncio
from datetime import datetime
import fileinput
import itertools
import json
import logging
import time

import async_timeout
import uvloop

from taxi.util import client_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

HOST = 'http://xenial-target.taxi.load.yandex.net'


def _chunks(iterable, chunk_size):
    """Splits iterable into chunks of specified size.

    Example:
    >>> list(chunks([1, 2, 3, 4, 5, 6], 4))
    [[1, 2, 3, 4], [5, 6]]

    The same works for generators:
    >>> list(chunks(xrange(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    :param iterable: Something iterable.
    :param chunk_size: Integer specifies the size of chunks.
    :return: Generator of chunks.
    """
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if chunk:
            yield chunk
        else:
            break


async def _entities_create(session, rec, args):
    external_id = rec['external_id']
    kind = rec['kind']
    body = f'{{"external_id": "{external_id}", "kind": "{kind}"}}'
    url = f'{args.host}/v1/entities/create'
    with async_timeout.timeout(args.async_timeout):
        async with session.post(url, data=body) as response:
            await response.release()


async def _accounts_create(session, rec, args):
    external_id = rec['external_id']
    agreement_id = args.agreement_id
    currency = rec['currency']
    subaccount = args.subaccount
    body = (
        '{'
        f'"entity_external_id":"{external_id}",'
        f'"agreement_id":"{agreement_id}",'
        f'"currency":"{currency}",'
        f'"sub_account":"{subaccount}",'
        '"expired":"2118-01-01T00:00:00+00:00"'
        '}'
    )
    url = f'{args.host}/v1/accounts/create'
    with async_timeout.timeout(args.async_timeout):
        async with session.post(url, data=body) as response:
            await response.release()


async def _journal_append(session, rec, args):
    def account(external_id, agreement_id, currency, subaccount):
        return (
            '{'
            f'"entity_external_id":"{external_id}",'
            f'"agreement_id":"{agreement_id}",'
            f'"currency":"{currency}",'
            f'"sub_account":"{subaccount}"'
            '}'
        )

    user_id = rec['user_id']
    driver_id = rec['driver_id']
    park_id = rec['park_id']
    order_id = rec['order_id']
    agreement_id = args.agreement_id
    currency = rec['currency']
    subaccount = args.subaccount
    cost = rec['cost']
    event_at = datetime.utcfromtimestamp(rec['due']).isoformat()
    # {"account":{"entity_external_id":"clid_uuid/1_111",
    # "agreement_id":"AG-001","currency":"RUB","sub_account":"RIDE"},
    # "amount":"1001.12","doc_ref":"uniq_doc_ref",
    # "reason":"any comment",
    # "event_at":"2018-07-18T17:26:31.0+00:00"}
    url = f'{args.host}/v1/journal/append'
    acc = account(park_id, agreement_id, currency, subaccount)
    body = (
        '{'
        f'"account":{acc},'
        f'"amount":"{cost * 0.8}",'
        f'"doc_ref":"{order_id}",'
        f'"reason":"stress test",'
        f'"event_at":"{event_at}"'
        '}'
    )
    async with async_timeout.timeout(args.async_timeout):
        async with session.post(url, data=body) as response:
            await response.release()

    acc = account(driver_id, agreement_id, currency, subaccount)
    body = (
        '{'
        f'"account":{acc},'
        f'"amount":"{cost * 0.6}",'
        f'"doc_ref":"{order_id}",'
        f'"reason":"stress test",'
        f'"event_at":"{event_at}"'
        '}'
    )
    async with async_timeout.timeout(args.async_timeout):
        async with session.post(url, data=body) as response:
            await response.release()

    acc = account(user_id, agreement_id, currency, subaccount)
    body = (
        '{'
        f'"account":{acc},'
        f'"amount":"{cost}",'
        f'"doc_ref":"{order_id}",'
        f'"reason":"stress test",'
        f'"event_at":"{event_at}"'
        '}'
    )
    async with async_timeout.timeout(args.async_timeout):
        async with session.post(url, data=body) as response:
            await response.release()


async def _load(filename, task, args):
    headers = {
        'Host': 'billing-accounts.taxi.tst.yandex.net',
        'User-Agent': 'load',
        'Content-Type': 'application/json',
    }
    chunk_size = args.batch_size
    cnt = 0
    async with client_session.get_client_session(headers=headers) as session:
        with fileinput.input(filename) as inp:
            for chunk in _chunks(inp, chunk_size):
                start = time.perf_counter()
                tasks = [
                    task(session, json.loads(line), args) for line in chunk
                ]
                await asyncio.gather(*tasks)
                cnt += len(tasks)
                rps = len(tasks) // (time.perf_counter() - start)
                logger.info(f'Sent {cnt} requests, {rps} RPS')


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--entities', default='', help='Input file with entities',
    )
    parser.add_argument(
        '--accounts', default='', help='Input file with accounts',
    )
    parser.add_argument(
        '--journal', default='', help='Input file with journal records',
    )
    parser.add_argument(
        '--agreement_id', default='STRESS', help='Accounts agreement',
    )
    parser.add_argument(
        '--subaccount', default='COST', help='Accounts sub-account',
    )
    parser.add_argument(
        '--async-timeout', default=30, type=int, help='Async timeout',
    )
    parser.add_argument(
        '--batch-size', default=3000, type=int, help='Task batch size',
    )
    parser.add_argument('--host', default=HOST, help='Target host name')
    return parser.parse_args()


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    args = _parse_args()
    if args.entities:
        # Expects input json string
        # {"kind":"park","external_id":"clid/1632340"}
        loop.run_until_complete(_load(args.entities, _entities_create, args))

    if args.accounts:
        # Expects input json string
        # {"currency":"RUB","kind":"park","external_id":"clid/1946871"}
        loop.run_until_complete(_load(args.accounts, _accounts_create, args))

    if args.journal:
        loop.run_until_complete(_load(args.journal, _journal_append, args))


if __name__ == '__main__':
    main()
