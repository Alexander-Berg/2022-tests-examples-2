import aiohttp
import argparse
import asyncio
import logging

from taxi import settings


logger = logging.getLogger(__name__)


PP_URLS = {
    settings.PRODUCTION: 'http://persey-payments.taxi.yandex.net',
    settings.TESTING: 'http://persey-payments.taxi.tst.yandex.net',
}


async def _refund_basket(session, base_url, item):
    url = base_url + '/v1/order/refund'

    await session.post(
        url,
        json=item['request'],
        headers=item['headers'],
        raise_for_status=True,
    )


async def _create_basket(session, base_url, item):
    hold_url = base_url + '/v1/order/hold'
    clear_url = base_url + '/v1/order/clear'

    await session.post(
        hold_url, json=item['hold_request'], raise_for_status=True,
    )
    await session.post(
        clear_url, json=item['clear_request'], raise_for_status=True,
    )


async def _recreate_basket(session, base_url, item):
    url = base_url + '/v1/basket/recreate'

    response = await session.post(url, json=item['request'])

    if response.status == 400:
        response_json = await response.json()
        if response_json['code'] == 'ORDER_WRONG_STATE':
            logger.error(
                'order_id={} mark={} wrong state {}'.format(
                    item['request']['order_id'],
                    item['request']['mark'],
                    response_json['message'],
                ),
            )
        else:
            response.raise_for_status()
    else:
        response.raise_for_status()


ACTION_HANDLERS = {
    'refund': _refund_basket,
    'create': _create_basket,
    'recreate': _recreate_basket,
}


def parse_args():
    parser = argparse.ArgumentParser(description='Fix test costs')

    parser.add_argument(
        '--action',
        type=str,
        required=True,
        choices=list(ACTION_HANDLERS.keys()),
    )
    parser.add_argument('--data', type=str, required=True)

    return parser.parse_args()


async def _do_stuff(args, session, base_url):
    handler = ACTION_HANDLERS[args.action]
    response = await session.get(args.data, raise_for_status=True)
    data = await response.json(content_type=None)

    for item in data:
        await handler(session, base_url, item)


async def main():
    base_url = PP_URLS[settings.ENVIRONMENT]
    args = parse_args()

    async with aiohttp.ClientSession() as session:
        await _do_stuff(args, session, base_url)


if __name__ == '__main__':
    asyncio.run(main())
