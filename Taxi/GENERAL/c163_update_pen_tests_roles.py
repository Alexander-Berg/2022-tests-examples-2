import argparse
import asyncio
import logging
import sys

import pymongo

from taxi import db as taxi_db
from taxi import secdist
from taxi.logs import auto_log_extra

logger = logging.getLogger('corp-update-pen-tests-roles')


async def update_roles_names(db, args, log_extra):
    roles = await db.corp_roles.find(
        {'client_id': args.client_id, 'is_cabinet_only': {'$exists': False}},
        projection=['_id'],
    ).to_list(None)
    roles_ids = [role['_id'] for role in roles]

    logger.info('Update roles %s', roles_ids, extra=log_extra)
    if args.dry_run:
        logger.info('Dry-run exit', extra=log_extra)
        return

    bulk = [
        pymongo.UpdateOne(
            {'_id': role_id},
            {'$set': {'name': role_id}, '$currentDate': {'updated': True}},
        )
        for role_id in roles_ids
    ]
    try:
        await db.corp_roles.bulk_write(bulk)
    except pymongo.errors.BulkWriteError as err:
        logger.error(err)

    logger.info('Upserted %s roles', len(roles_ids), extra=log_extra)


def init_db(loop):
    _secdist = secdist.load_secdist()
    _secdist_ro = secdist.load_secdist_ro()
    _db = taxi_db.create_db(
        _secdist.get('mongo_settings', {}),
        _secdist_ro.get('mongo_settings', {}),
        loop=loop,
    )
    return _db


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_id', type=str)
    parser.add_argument('--dry_run', action='store_true')
    parser.add_argument('--log', type=str, default='INFO')
    return parser.parse_args()


async def main():
    args = parse_args()
    logging.basicConfig(level=args.log)
    log_extra = auto_log_extra.get_log_extra()
    logger.info('start script: %r', args, extra=log_extra)

    loop = asyncio.get_event_loop()
    db = init_db(loop)

    try:
        await update_roles_names(db, args, log_extra=log_extra)
    except Exception as exc:
        logger.error(exc, exc_info=True, extra=log_extra)
        sys.exit(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
