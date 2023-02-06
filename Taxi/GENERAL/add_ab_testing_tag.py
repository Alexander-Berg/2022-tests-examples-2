import argparse
import asyncio
import sys

sys.path.append('/usr/lib/yandex/taxi-exp/')  # noqa

from taxi_exp import web_context
from taxi_exp.util import pg_helpers

TAG = 'by-percentage'

GET_EXPERIMENTS_QUERY = """
    SELECT rev, id, name, is_config
    FROM
        clients_schema.experiments
    WHERE
        NOT ('{tag}' = ANY(trait_tags))
        AND (
            clauses::text LIKE ANY(
                ARRAY[
                    '%"type": "mod_sha1_with_salt"%',
                    '%"type": "segmentation"%'
                ]::text[]
            )
            OR predicate::text LIKE ANY(
                ARRAY[
                    '%"type": "mod_sha1_with_salt"%',
                    '%"type": "segmentation"%'
                ]::text[]
            )
        )
    LIMIT $1::BIGINT"""

UPDATE_EXPERIMENTS_QUERY = (
    """
WITH t_args AS (
    SELECT id as exp_id
    FROM
        clients_schema.experiments
    WHERE
        NOT ('{tag}' = ANY(trait_tags))
        AND (
            clauses::text LIKE ANY(
                ARRAY[
                    '%"type": "mod_sha1_with_salt"%',
                    '%"type": "segmentation"%'
                ]::text[]
            )
            OR predicate::text LIKE ANY(
                ARRAY[
                    '%"type": "mod_sha1_with_salt"%',
                    '%"type": "segmentation"%'
                ]::text[]
            )
        )
    LIMIT $1::BIGINT
), t AS (
    UPDATE clients_schema.experiments
    SET
        trait_tags=array_append(array_remove(trait_tags, '{tag}'), '{tag}'),
        rev = nextval('clients_schema.clients_rev'),
        last_manual_update = CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow'
    WHERE
        id IN (SELECT exp_id FROM t_args)
    RETURNING rev, id, name, is_config
)
SELECT pg_temp.add_experiments_history_item(rev, 'script') as result,
       id, name, is_config FROM t;
""".format(
        tag=TAG,
    )
)


async def main(event_loop, command_args):
    context = web_context.TaxiExpApplication(
        loop=event_loop, service_name='taxi-exp-script',
    )
    await context.startup()

    if command_args.dry_run:
        print('DRY RUN')
    print('id', 'name', 'is_config', sep='\t')

    while True:
        query = UPDATE_EXPERIMENTS_QUERY
        if command_args.dry_run:
            query = GET_EXPERIMENTS_QUERY

        updated = await pg_helpers.fetch(
            context['pool'], query, command_args.chunk,
        )
        if not updated:
            break
        for item in updated:
            print(item['id'], item['name'], item['is_config'], sep='\t')
        if command_args.run_once or command_args.dry_run:
            break

    await context.shutdown()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk', type=int, default=500)
    parser.add_argument('--run-once', type=bool, default=True)
    parser.add_argument('--dry-run', type=bool, default=False)

    return parser.parse_args()


if __name__ == '__main__':
    command_args = parse_args()
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main(event_loop, command_args))
