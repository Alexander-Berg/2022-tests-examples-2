import argparse
import asyncio

import aiohttp

RETRY_SLEEP_TIME = 0.1  # 100ms
RETRIES_COUNT = 100  # max wait 10s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--monitor-port', required=True, type=int)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_monitor(args))


async def wait_monitor(args):
    retries = 0
    while True:
        ready = await check_ready_safe(args)
        if ready:
            break
        retries += 1
        if retries > RETRIES_COUNT:
            raise RuntimeError('Wait for YDB error: timeout')
        await asyncio.sleep(RETRY_SLEEP_TIME)


async def check_ready_safe(args):
    try:
        return await check_ready(args)
    except:  # noqa pylint: disable=bare-except
        return False


async def check_ready(args):
    ready_label = {
        'counters': 'tablets',
        'sensor': 'Tx(all)',
        'type': 'BSController',
        'category': 'executor',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
                'http://{}:{}/counters/json'.format(
                    args.host, args.monitor_port,
                ),
        ) as resp:
            data = await resp.json()
            for sensor in data['sensors']:
                if ready_label == sensor['labels']:
                    ready = sensor['value'] is not None
                    return ready
    return False


if __name__ == '__main__':
    main()
