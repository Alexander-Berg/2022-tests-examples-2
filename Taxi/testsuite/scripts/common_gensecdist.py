import argparse
import os

from taxi_tests.environment.services import postgresql
from taxi_tests.utils import gensecdist
from taxi_tests.utils import mongo_schema


DIRNAME = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(DIRNAME, os.pardir, os.pardir)
SECDIST_DEV = os.path.join(SOURCE_DIR, 'manual', 'secdist.json')
SECDIST_TEMPLATE = os.path.join(DIRNAME, os.pardir, 'secdist_template.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--secdist-dev', default=SECDIST_DEV, help='Path to dev_secdist file.',
    )
    parser.add_argument(
        '--secdist-template',
        default=SECDIST_TEMPLATE,
        help='Path to secdist-template file (secdist_template.json).',
    )
    parser.add_argument(
        '--source-dir', default=SOURCE_DIR, help='Path to backend-cpp dir',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output file path, default is stdout',
        required=True,
    )
    parser.add_argument(
        '--mongo-schema',
        default='schemas/mongo',
        help='Path to mongo schema directory',
    )
    parser.add_argument(
        '--mongo-uri',
        default='mongodb://localhost:27217/',
        help='Mongo base uri',
    )
    parser.add_argument(
        '--redis-sentinel-host',
        default='localhost',
        help='Redis sentinel hostname',
    )
    parser.add_argument(
        '--redis-sentinel-port',
        type=int,
        default=26379,
        help='Redis sentinel port',
    )
    parser.add_argument(
        '--mockserver-host',
        default='http://localhost:9999',
        help='Mockserver host for current worker',
    )
    args = parser.parse_args()

    mongo_settings = {
        alias: (
            doc['settings']['connection'],
            doc['settings']['database'],
            doc['settings']['collection'],
        )
        for alias, doc in mongo_schema.MongoSchema(args.mongo_schema).items()
    }

    doc = gensecdist.create_secdist(
        secdist_dev=args.secdist_dev,
        secdist_template=args.secdist_template,
        source_dir=args.source_dir,
        mongo_collections_settings=mongo_settings,
        mongo_host=args.mongo_uri,
        redis_sentinels=[
            {
                'host': args.redis_sentinel_host,
                'port': args.redis_sentinel_port,
            },
        ],
        secdist_vars={
            'mockserver_host': args.mockserver_host,
            'pg_connstring': postgresql.get_connection_string(),
        },
    )
    gensecdist.dump_secdist(args.output, doc)


if __name__ == '__main__':
    main()
