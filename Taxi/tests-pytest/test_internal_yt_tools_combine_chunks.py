import os

import jsonschema
import pytest
import yt.wrapper.errors


from taxi.internal.data_manager import loader_utils
from taxi.internal.yt_replication.schema import loaders
from taxi.internal.yt_tools.combine_chunks import combine
from taxi.internal.yt_tools.combine_chunks import schema


class _DummyYtClient(object):
    def __init__(self, prefix='//home/taxi/env/'):
        self.config = {'prefix': prefix,
                       'proxy': {'url': ''}}

    class Transaction(object):
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def get(self, path, *args, **kwargs):
        assert path.split('@', 1)[1] == 'revision'
        return 123456

    def lock(self, *args, **kwargs):
        raise yt.wrapper.errors.YtConcurrentTransactionLockConflict(
            error={'code': 1, 'message': 'error'}, url='',
            headers={}, params={},
        )

    def run_merge(self, *args, **kwargs):
        pass


TABLES = (
    'data/node-1/table_to_combine',
    'data/node-1/table_to_combine_2',
    'data/node-2/table_to_combine',
    'data/node-3/table_to_combine',
    'data/node-recursive-case/table',
    'data/node-1/another-data/table_to_combine',
    'data/node-1/another-data-recursive-case/table',
    '//home/taxi/home/table',
    '//home/taxi/home/my/tables/table',
    'data/node-4/recursive/table',
    'data/node-5/table',
)


@pytest.mark.parametrize(
    'schema_filename,expected_nodes,expected_combined_tables',
    [
        (
            'schema_normal.yaml',
            ['', '//home/taxi/home'],
            {
                'hahn_combine_chunks': [
                    '//home/taxi/home/table',
                    'data/node-1/another-data-recursive-case/table',
                    'data/node-5/table',
                    'data/node-recursive-case/table',
                ],
                'hahn_combine_chunks_with_compression': [
                    '//home/taxi/home/my/tables/table',
                    'data/node-1/table_to_combine',
                    'data/node-1/table_to_combine_2',
                    'data/node-2/table_to_combine',
                ],
                'hahn_combine_chunks_with_high_compression': [
                    'data/node-1/another-data/table_to_combine',
                    'data/node-3/table_to_combine',
                ],
                'hahn_combine_chunks_recursive_codecs': [
                    'data/node-4/recursive/table',
                ]
            },
        ),
        (
            'schema_dummy.yaml',
            ['data/node-1',
             'data/node-2',
             'data/node-1/another-data',
             'data/node-3',
             'data/node-4'],
            {
                'hahn_combine_chunks_with_compression': [
                    'data/node-1/table_to_combine',
                    'data/node-1/table_to_combine_2',
                    'data/node-2/table_to_combine',
                ],
                'hahn_combine_chunks_with_high_compression': [
                    'data/node-1/another-data/table_to_combine',
                    'data/node-3/table_to_combine',
                ],
            },
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_schema(monkeypatch, patch, schema_filename, expected_nodes,
                expected_combined_tables):
    clients = {
        'hahn': _DummyYtClient(),
        'arnold': _DummyYtClient('//another/')
    }

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, *args, **kwargs):
        return clients[name]
    _patch_rules(monkeypatch, schema_filename)
    jsonschema.validate(
        loader_utils.load_yaml(schema.RULES_PATH),
        _load_schema(),
    )
    combine_rules = schema.load_rules(fail=True)
    assert len(combine_rules) == 2

    for combine_rule in combine_rules:
        assert expected_nodes == combine_rule.nodes_to_combine

        for tables in (TABLES, reversed(TABLES)):
            combined = {}
            for table in tables:
                rule = combine_rule.get_appropriate_combine_rule(table)
                if rule is not None:
                    combined.setdefault(rule.name, []).append(table)
            for combined_list in combined.itervalues():
                combined_list.sort()

            assert combined == expected_combined_tables


def _patch_rules(monkeypatch, filename):
    tests_static_basedir = os.path.join(
        os.path.dirname(__file__), 'static',
        os.path.splitext(os.path.basename(__file__))[0]
    )
    monkeypatch.setattr(
        schema, 'RULES_PATH',
        os.path.join(tests_static_basedir, filename),
    )


def _load_schema():
    schema_path = os.path.join(
        loaders.STATIC_BASEDIR, 'json_schemas', 'combine_chunks_rules.yaml'
    )
    return loader_utils.load_yaml(schema_path)


def test_errors(monkeypatch):
    with pytest.raises(combine.YtExclusiveLockConflictError):
        combine.merge(_DummyYtClient(), '', '', {})
