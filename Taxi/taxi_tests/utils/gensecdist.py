import argparse
import copy

from taxi_tests import json_util
from taxi_tests.environment.services import postgresql
from taxi_tests.utils import json_variables
from taxi_tests.utils import mongo_schema
from taxi_tests.utils import service_config


class BaseError(Exception):
    """Base class for all exceptions in this module."""


class MongoSettingsError(BaseError):
    """Raise if there are errors while generate mongo_settings"""


def generate_secdist(service_desc,
                     mongo_host,
                     mongo_collections_settings,
                     redis_sentinels,
                     secdist_vars=None):
    secdist = create_secdist(
        secdist_dev=service_desc.secdist_dev,
        secdist_template=service_desc.secdist_template,
        source_dir=service_desc.source_dir,
        mongo_host=mongo_host,
        mongo_collections_settings=mongo_collections_settings,
        redis_sentinels=redis_sentinels,
        secdist_vars=secdist_vars,
    )
    dump_secdist(service_desc.output_secdist_path, secdist)


def create_secdist(secdist_dev,
                   secdist_template,
                   source_dir,
                   mongo_host,
                   mongo_collections_settings,
                   redis_sentinels,
                   secdist_vars=None):
    pre_secdist = _load_json(secdist_dev)
    secdist_template_doc = _load_json(secdist_template)

    settings_override = pre_secdist.get('settings_override', {})
    settings_override.update(secdist_template_doc.get('settings_override', {}))

    pre_secdist.update(secdist_template_doc)
    pre_secdist['settings_override'] = settings_override

    pre_secdist['mongo_settings'] = _get_mongo_settings(
        mongo_host,
        mongo_collections_settings,
        pre_secdist,
    )

    secdist_vars = _update_default_vars(
        secdist_vars if secdist_vars else {},
        redis_sentinels,
        source_dir,
    )
    pre_secdist = json_variables.substitute_vars(
        pre_secdist,
        **secdist_vars,
    )
    return pre_secdist


def dump_secdist(output_secdist_path, doc):
    data = json_util.dumps(doc)
    with open(output_secdist_path, 'w', encoding='utf-8') as fp:
        fp.write(data)
        fp.write('\n')


def _load_json(path):
    with open(path, 'r', encoding='utf-8') as fp:
        data = json_util.loads(fp.read())
        return data


def _get_mongo_settings(mongo_host, mongo_collections_settings, data):
    dev_aliases = _get_dev_secdist_mongo_collection_aliases(data)
    mongo_settings = {
        'stq': {'uri': '%s%s' % (mongo_host, 'dbstq')},
    }
    for name, (dbalias, dbname, colname) in mongo_collections_settings.items():
        if dbalias not in dev_aliases:
            continue
        mongo_settings[dbalias] = {
            'uri': '%s%s' % (mongo_host, dbname),
        }
    return mongo_settings


def _get_dev_secdist_mongo_collection_aliases(data):
    mongo_settings = data.get('mongo_settings', {})
    collection_aliases = list(mongo_settings.keys())
    return collection_aliases


def _update_default_vars(secdist_vars, redis_sentinels, source_dir):
    updated_vars = copy.deepcopy(secdist_vars)
    updated_vars['redis_sentinels'] = redis_sentinels
    updated_vars['source_dir'] = source_dir
    return updated_vars


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'service_desc',
        help='Path to service descriptor file (service.in).',
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path, default is stdout',
    )
    parser.add_argument(
        '--mongo-schema', default='schemas/mongo',
        help='Path to mongo schema directory',
    )
    parser.add_argument(
        '--mongo-uri', default='mongodb://localhost:27217/',
        help='Mongo base uri',
    )
    parser.add_argument(
        '--redis-sentinel-host', default='localhost',
        help='Redis sentinel hostname',
    )
    parser.add_argument(
        '--redis-sentinel-port', type=int, default=26379,
        help='Redis sentinel port',
    )
    parser.add_argument(
        '--mockserver-host', default='http://localhost:9999',
        help='Mockserver host for current worker',
    )
    args = parser.parse_args()

    service_desc = service_config.load_path(args.service_desc)
    mongo_settings = {
        alias: (
            doc['settings']['connection'],
            doc['settings']['database'],
            doc['settings']['collection'],
        )
        for alias, doc in mongo_schema.MongoSchema(args.mongo_schema).items()
    }

    doc = create_secdist(
        secdist_dev=service_desc.secdist_dev,
        secdist_template=service_desc.secdist_template,
        source_dir=service_desc.source_dir,
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

    if args.output:
        dump_secdist(args.output, doc)
    else:
        data = json_util.dumps(doc)
        print(data)


if __name__ == '__main__':
    main()
