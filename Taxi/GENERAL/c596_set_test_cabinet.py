import argparse
import asyncio
import logging

from taxi import db as taxi_db
from taxi import secdist
from taxi.logs import auto_log_extra

logger = logging.getLogger('corp-client-set-test-cabinet')

SERVICE_NAME = 'taxi-corp-cabinet-py3-scripts'


class Context:
    def __init__(self):
        self.db = taxi_db.create_db(
            secdist.load_secdist().get('mongo_settings', {}),
            secdist.load_secdist_ro().get('mongo_settings', {}),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def set_taxi_is_test(ctx: Context):
    result = await ctx.db.corp_clients.update_many(
        {'services.taxi.is_test': {'$exists': False}},
        {'$set': {'services.taxi.is_test': False}},
    )

    logger.info(
        'Result: %s', result.raw_result, extra=auto_log_extra.get_log_extra(),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default='INFO')
    return parser.parse_args()


async def main():
    args = parse_args()
    logging.basicConfig(level=args.log)
    logger.info('Start script: %r', args, extra=auto_log_extra.get_log_extra())

    async with Context() as context:
        await set_taxi_is_test(context)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
