import glob
import os
import pathlib

import pytest
import yaml

from replication import replication_yaml as replication_yaml_module
from replication import settings
from replication.common import mongo_settings_parser

_SOURCES_DOC_LINK = (
    'https://pages.github.yandex-team.ru/taxi/schemas/Taxi_'
    'Documentation/replication-docs/replication-service/#_11'
)
_EXCLUDED_RULE_NAMES = ('plus_test_payment_history',)


def _get_safe_loader():
    if yaml.__with_libyaml__:
        return yaml.CSafeLoader
    return yaml.SafeLoader


def _get_mongo_sources(rules_dir):
    mongo_sources = []
    for subdir in os.listdir(rules_dir):
        if subdir == 'plugins':
            continue
        if subdir.startswith('.') or subdir.startswith('_'):
            continue
        rule_scope_path = os.path.join(rules_dir, subdir)
        for path in os.listdir(rule_scope_path):
            full_path = os.path.join(rule_scope_path, path)
            if os.path.isdir(full_path) or not full_path.endswith('.yaml'):
                continue
            with open(full_path, 'r') as stream:
                rule_raw = yaml.load(stream, Loader=_get_safe_loader())
            source = rule_raw['source']
            if source['type'] == 'mongo':
                rule_name = rule_raw['name']
                if rule_name in _EXCLUDED_RULE_NAMES:
                    continue

                # skip if connection params are in the rule itself
                rule_connection_params = source.get('connection', {})
                if (
                        'secdist_path' in rule_connection_params
                        and 'database' in rule_connection_params
                ):
                    continue

                mongo_sources.append((rule_name, source))
    return mongo_sources


def _parametrize_mongo_sources(rules_dir):
    mongo_sources = _get_mongo_sources(rules_dir)
    return pytest.mark.parametrize(
        'rule_name,source',
        mongo_sources,
        ids=[rule_name for rule_name, _ in mongo_sources],
    )


if settings.HAS_ENV_DMP_INSTALL_DIR:  # TODO: get rid of conditional
    _REPLICATION_YAML = replication_yaml_module.load(
        settings.REPLICATION_YAML_PATH,
    )
    _ROOT_PATH = pathlib.Path(_REPLICATION_YAML.get_root_path())
    _MONGO_SCHEMAS_DIR = _ROOT_PATH.joinpath('schemas', 'mongo', '*.yaml')
    _MONGO_DB_SETTINGS_DICT = (
        mongo_settings_parser.get_db_settings_collections(
            _REPLICATION_YAML, force=True,
        )
    )

    def test_db_settings_generation():
        for path in glob.glob(str(_MONGO_SCHEMAS_DIR)):
            file_name = os.path.basename(path)
            collection_name, _ = os.path.splitext(file_name)
            assert collection_name in _MONGO_DB_SETTINGS_DICT

    def test_every_schema_has_rules():
        used_collections = {
            source.get('collection_name')
            for _, source in _get_mongo_sources(
                _REPLICATION_YAML.get_rules_full_path(),
            )
        }
        unused_collections = {
            coll
            for coll in _MONGO_DB_SETTINGS_DICT
            if coll not in used_collections
        }

        if unused_collections:
            raise ValueError(
                'These collections in schemas/mongo are not used by any rule, '
                'they need to be removed: ' + str(unused_collections),
            )

    @_parametrize_mongo_sources(_REPLICATION_YAML.get_rules_full_path())
    def test_mongo_collection_in_schemas(rule_name, source):
        if source['collection_name'] not in _MONGO_DB_SETTINGS_DICT:
            raise ValueError(
                f'{rule_name} rule source collection is missing '
                f'in schemas/mongo/*. Add collection to schemas '
                f'repository and then update the schemas/mongo/*. '
                f'Details: {_SOURCES_DOC_LINK}, in mongo sources info',
            )
