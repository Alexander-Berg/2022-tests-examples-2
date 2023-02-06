import os

import pytest

from scripts.authproxy_schemas_generator import client_schema
from scripts.authproxy_schemas_generator import refs
from scripts.authproxy_schemas_generator.converters import garbage_collector


SCHEMA = {
    'components': {
        'schemas': {
            'TypeFrom': {'$ref': '#/components/schemas/TypeTo'},
            'TypeTo': {'type': 'integer'},
            'Type3': {'$ref': '#/components/schemas/TypeFrom'},
        },
    },
}

TYPE_FROM = SCHEMA['components']['schemas']['TypeFrom']
TYPE_3 = SCHEMA['components']['schemas']['Type3']


def test_location_from():
    location = refs.Location.from_ref_object(TYPE_FROM, '')

    assert location.is_local()
    assert location.fragment == '/components/schemas/TypeTo'


@pytest.mark.parametrize(
    'ref',
    [
        'def.yaml#/a/b/c',
        'x/../def.yaml#/a/b/c',
        'x/y/../../def.yaml#/a/b/c',
        '../rel/def.yaml#/a/b/c',
    ],
)
def test_relative(ref):
    location = refs.Location.from_ref_object({'$ref': ref}, '/rel/file.yaml')

    assert not location.is_local()
    assert location.path == '/rel/def.yaml'
    assert location.fragment == '/a/b/c'


def test_dfs_empty_graph(tempdir, load_fstree):
    load_fstree('empty')

    dirname = os.path.join(tempdir.name(), 'schemas', 'services', 'serviceX')
    client_schemas = client_schema.ClientSchema(
        name='serviceX',
        client_yaml_dirname=dirname,
        root_dirpath=tempdir.name(),
    )

    dfs = garbage_collector.Dfs(client_schemas)
    assert dfs.process() == {
        refs.Location(path='api/api1.yaml', fragment='/paths'),
        refs.Location(path='api/api2.yaml', fragment='/paths'),
        refs.Location(path='definitions.yaml', fragment='/paths'),
    }


def test_dfs_happy_path(tempdir, load_fstree):
    load_fstree('local_ref')

    dirname = os.path.join(tempdir.name(), 'schemas', 'services', 'serviceX')
    client_schemas = client_schema.ClientSchema(
        name='serviceX',
        client_yaml_dirname=dirname,
        root_dirpath=tempdir.name(),
    )

    dfs = garbage_collector.Dfs(client_schemas)
    assert dfs.process() == {
        refs.Location(path='api/api1.yaml', fragment=fragment)
        for fragment in [
            '/components/parameters/String',
            '/components/parameters/String2',
            '/components/parameters/String/in',
            '/components/parameters/String/name',
            '/components/parameters/String/required',
            '/components/parameters/String/schema',
            '/components/parameters/String/schema/type',
            '/components/parameters/X-Remote-IP',
            '/components/parameters/X-Remote-IP2',
            '/components/parameters/X-Remote-IP/in',
            '/components/parameters/X-Remote-IP/name',
            '/components/parameters/X-Remote-IP/required',
            '/components/parameters/X-Remote-IP/schema',
            '/components/parameters/X-Remote-IP/schema/type',
            '/paths',
            '/paths/_foo',
            '/paths/_foo/get',
            '/paths/_foo/get/description',
            '/paths/_foo/get/parameters',
            '/paths/_foo/get/parameters/[0]',
            '/paths/_foo/get/parameters/[1]',
            '/paths/_foo/get/parameters/[2]',
            '/paths/_foo/get/parameters/[3]',
            '/paths/_foo/get/responses',
            '/paths/_foo/get/responses/200',
            '/paths/_foo/get/responses/200/description',
        ]
    }


def test_dfs_recursive(tempdir, load_fstree):
    load_fstree('cycle')

    dirname = os.path.join(tempdir.name(), 'schemas', 'services', 'serviceX')
    client_schemas = client_schema.ClientSchema(
        name='serviceX',
        client_yaml_dirname=dirname,
        root_dirpath=tempdir.name(),
    )

    dfs = garbage_collector.Dfs(client_schemas)
    assert dfs.process() == {
        refs.Location(path='api/api1.yaml', fragment=fragment)
        for fragment in [
            '/components/schemas/Recursive',
            '/components/schemas/Recursive/properties',
            '/components/schemas/Recursive/properties/field',
            '/components/schemas/Recursive/type',
            '/paths',
            '/paths/_foo',
            '/paths/_foo/get',
            '/paths/_foo/get/description',
            '/paths/_foo/get/requestBody',
            '/paths/_foo/get/requestBody/content',
            '/paths/_foo/get/requestBody/content/application_json',
            '/paths/_foo/get/requestBody/content/application_json/schema',
            '/paths/_foo/get/responses',
            '/paths/_foo/get/responses/200',
            '/paths/_foo/get/responses/200/description',
        ]
    }
