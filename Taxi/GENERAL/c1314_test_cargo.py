import argparse
import asyncio
import logging

from taxi import db as taxi_db
from taxi import secdist
from taxi.util import itertools_ext

logger = logging.getLogger('corp-test-cargo')

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


async def migrate_test_cargo(ctx: Context, args: argparse.Namespace) -> None:
    collection = ctx.db.corp_clients

    query = {
        'features': 'cargo',
        '$or': [
            {'services.taxi.deactivate_threshold_date': {'$ne': None}},
            {'services.taxi.deactivate_threshold_ride': {'$ne': None}},
        ],
    }
    if args.client_ids:
        query['_id'] = {'$in': args.client_ids}

    clients = await collection.find(
        query, projection=['services.taxi'],
    ).to_list(None)

    for chunk in itertools_ext.chunks(clients, args.chunk_size):

        bulk = None

        for client in chunk:

            bulk = bulk or collection.initialize_unordered_bulk_op()

            taxi_service = client['services']['taxi']
            is_test = taxi_service.get('is_test')
            date = taxi_service.get('deactivate_threshold_date')
            ride = taxi_service.get('deactivate_threshold_ride')

            logger.info(
                'Client %s, '
                'is_test %s, '
                'deactivate_threshold_date %s,'
                'deactivate_threshold_ride %s,',
                client['_id'],
                is_test,
                date,
                ride,
            )

            bulk.find({'_id': client['_id']}).update(
                {
                    '$set': {
                        'services.cargo.is_test': is_test,
                        'services.cargo.deactivate_threshold_date': date,
                        'services.cargo.deactivate_threshold_ride': ride,
                    },
                    '$currentDate': {
                        'updated': True,
                        'updated_at': {'$type': 'timestamp'},
                    },
                },
            )

        if not args.dry_run:
            if bulk:
                result = await bulk.execute()
                logger.info('Bulk executed, result: %r', result)
            else:
                logger.info('Nothing to, bulk is empty')
        else:
            logger.info('Nothing to do, dry-run')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk_size', type=int, default=1000)
    parser.add_argument('--chunk_timeout', type=int, default=3)
    parser.add_argument('--client_ids', type=str, nargs='+')
    parser.add_argument('--log', type=str, default='INFO')
    parser.add_argument('--dry_run', action='store_true')
    return parser.parse_args()


async def main():
    args = parse_args()
    logging.basicConfig(level=args.log)
    logger.info('Start script: %r', args)

    async with Context() as context:
        await migrate_test_cargo(context, args)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
