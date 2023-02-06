import json
import os

import pytest

from scripts.authproxy_schemas_generator import client_schema_set
from scripts.authproxy_schemas_generator import client_schemas_with_am_rules
from scripts.authproxy_schemas_generator import convert
from scripts.authproxy_schemas_generator.rules import rules


def test_convert_empty_rules(tempdir, load_fstree):
    tempdir.write(
        'services/old/client.yaml',
        json.dumps({'host': {'testing': 'testing.com'}}),
    )
    tempdir.write('services/old/api/api1.yaml', json.dumps({'paths': {}}))

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'services'), env='testing',
    )
    assert css.clients_count() == 1

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css, route_rules=[],
    )
    assert result.client_schemas_count() == 0


META = {
    'headers_info': {
        'input_urls': [{'url': 'https://aaa.ru'}],
        'variants': [
            {
                'upstream_data': {
                    'parameters': [
                        {'type': 'header', 'name': 'x-yandex-uid'},
                        {'type': 'header', 'name': 'x-yataxi-user'},
                        {'type': 'header', 'name': 'x-remote-ip'},
                    ],
                },
                'input_data': {
                    'parameters': [{'type': 'header', 'name': 'xxx'}],
                },
            },
        ],
    },
}

DEFAULT_RULES = [
    rules.AmRoutingRule(
        {
            'input': {'prefix': '/foo', 'rule_name': 'foo'},
            'output': {'upstream': 'http://testing.com'},
        },
        META,
    ),
]

ROOT_RULES = [
    rules.AmRoutingRule(
        {
            'input': {'prefix': '/foo/bar', 'rule_name': 'foo'},
            'output': {'upstream': 'http://testing.com'},
        },
        META,
    ),
]


def test_prefix(tempdir, load_fstree, validate_filetree):
    # /foo & /bar
    # rule prefix matches only /foo
    load_fstree('rule_prefix')

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'schemas', 'services'), env='testing',
    )
    assert css.clients_count() == 1

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css, route_rules=DEFAULT_RULES,
    )

    client_schemas_with_am_rules.Dumper().store_schemas(
        result, os.path.join(tempdir.name(), 'schemas', 'external-api'),
    )

    # no /bar
    validate_filetree('rule_prefix_result')


def test_basepath(tempdir, load_fstree, validate_filetree):
    load_fstree('base_path')

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'schemas', 'services'), env='testing',
    )

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css, route_rules=ROOT_RULES,
    )

    client_schemas_with_am_rules.Dumper().store_schemas(
        result, os.path.join(tempdir.name(), 'schemas', 'external-api'),
    )

    validate_filetree('base_path_result')


def test_prefix_in_client_yaml(tempdir, load_fstree, validate_filetree):
    load_fstree('clientyaml_prefix')

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'schemas', 'services'), env='testing',
    )

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css,
        route_rules=[
            rules.AmRoutingRule(
                {
                    'input': {'prefix': '/prefix', 'rule_name': 'prefix'},
                    'output': {'upstream': 'http://testing.com'},
                },
                META,
            ),
        ],
    )
    client_schemas_with_am_rules.Dumper().store_schemas(
        result, os.path.join(tempdir.name(), 'schemas', 'external-api'),
    )

    validate_filetree('clientyaml_prefix')


@pytest.mark.parametrize(
    'name', ['headers', 'local_ref', 'external_ref', 'empty'],
)
def test_remove_headers(tempdir, load_fstree, validate_filetree, name):
    load_fstree(name)

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'schemas', 'services'), env='testing',
    )

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css, route_rules=DEFAULT_RULES,
    )

    client_schemas_with_am_rules.Dumper().store_schemas(
        result, os.path.join(tempdir.name(), 'schemas', 'external-api'),
    )

    validate_filetree(f'{name}_result')


def test_dir_without_client_yaml(tempdir, load_fstree, validate_filetree):
    load_fstree('no_client_yaml')

    loader = client_schema_set.ClientSchemaSetLoader()
    css = loader.read_from_fs(
        os.path.join(tempdir.name(), 'schemas', 'services'), env='testing',
    )

    result, _stats = convert.make_authproxy_schemas(
        client_schemas=css, route_rules=DEFAULT_RULES,
    )

    client_schemas_with_am_rules.Dumper().store_schemas(
        result, os.path.join(tempdir.name(), 'schemas', 'external-api'),
    )

    validate_filetree(f'empty')
