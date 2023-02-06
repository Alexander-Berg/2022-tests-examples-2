#!/usr/lib/yandex/taxi-py3-2/bin/python3.7

import asyncio
import datetime
import random

import aiohttp

from taxi.util import client_session


def urlify(path):
    return 'http://placeholder/{}'.format(path)


class RequestMaker:
    def __init__(self, session):
        self.__session = session

    async def get_json(self, path):
        _sc = self.__session.get(urlify(path), headers=self._headers())
        async with _sc as response:
            return await response.json()

    async def get_text(self, path):
        _sc = self.__session.get(urlify(path), headers=self._headers())
        async with _sc as response:
            return await response.text()

    async def post(self, path, payload):
        _sc = self.__session.post(
            urlify(path), headers=self._headers(), json=payload,
        )
        async with _sc as response:
            return await response.text()

    @staticmethod
    def _headers():
        return {
            'Request-Id': 'test_request_id_%08x' % random.randrange(16 ** 8),
        }


def now_str():
    return datetime.datetime.strftime(
        datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f',
    )


async def amain():
    unix_path = '/tmp/taxi_billing_accounts_0.sock'
    connector = aiohttp.UnixConnector(path=unix_path)
    _cm = client_session.get_client_session(connector=connector)
    async with _cm as session:
        rmk = RequestMaker(session)
        print(await rmk.get_text('ping'))
        print(await rmk.get_json('ping_db'))
        print(await rmk.get_json('ping_db?type=all'))
        print(await rmk.get_json('ping_db?type=some&shard_id=0'))
        print(
            await rmk.post(
                'entities', payload={'external_id': '666', 'kind': 'yandex'},
            ),
        )
        print(
            await rmk.post(
                'entities', payload={'external_id': '0', 'kind': 'driver'},
            ),
        )
        print(
            await rmk.post(
                'entities', payload={'external_id': '1', 'kind': 'park'},
            ),
        )
        print(await rmk.get_text('entities?external_id=0'))
        print(await rmk.get_text('entities?external_id=1'))
        print(
            await rmk.post(
                'accounts',
                payload={
                    'entity': {'external_id': '666'},
                    'agreement': 'AGR-666',
                    'currency': 'RUB',
                    'number': '0',
                },
            ),
        )
        print(
            await rmk.post(
                'accounts',
                payload={
                    'entity': {'external_id': '0'},
                    'agreement': 'AGR-0',
                    'currency': 'RUB',
                    'number': '0',
                },
            ),
        )
        print(
            await rmk.post(
                'accounts',
                payload={
                    'entity': {'external_id': '1'},
                    'agreement': 'AGR-1',
                    'currency': 'RUB',
                    'number': '0',
                },
            ),
        )
        print(
            await rmk.post(
                'journal',
                payload={
                    'dt_account_id': {
                        'entity': {'external_id': '0'},
                        'agreement': 'AGR-0',
                        'currency': 'RUB',
                        'number': '0',
                    },
                    'ct_account_id': {
                        'entity': {'external_id': '1'},
                        'agreement': 'AGR-1',
                        'currency': 'RUB',
                        'number': '0',
                    },
                    'amount': 0,
                    'ref_doc': 'ref_doc',
                    'event_ts': now_str(),
                },
            ),
        )
        print(
            await rmk.post(
                'journal',
                payload={
                    'dt_account_id': {
                        'entity': {'external_id': '666'},
                        'agreement': 'AGR-666',
                        'currency': 'RUB',
                        'number': '0',
                    },
                    'ct_account_id': {
                        'entity': {'external_id': '1'},
                        'agreement': 'AGR-1',
                        'currency': 'RUB',
                        'number': '0',
                    },
                    'amount': 0,
                    'ref_doc': 'ref_doc',
                    'event_ts': now_str(),
                },
            ),
        )


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain())


if __name__ == '__main__':
    main()
