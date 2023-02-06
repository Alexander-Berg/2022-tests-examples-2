import os

from scripts.authproxy_schemas_generator import client_schema
from scripts.authproxy_schemas_generator import openapi_schema


def test_api_is_empty():
    schema = openapi_schema.ApiSchema(
        rel_path='/', raw={'openapi': '3.0.0', 'paths': 'foo'},
    )
    assert not schema.is_empty()

    assert 'paths' in schema.raw
    schema.raw['paths'] = {}

    assert schema.is_empty()


def test_client_load_no_api(tempdir, load_fstree):
    load_fstree('no-api')

    dirname = os.path.join(tempdir.name(), 'schemas', 'services', 'no_api')
    client_schemas = client_schema.ClientSchema(
        name='no_api',
        client_yaml_dirname=dirname,
        root_dirpath=tempdir.name(),
    )

    # no api/* files => empty
    assert list(client_schemas.nonempty_api_schemas()) == []
    assert list(client_schemas.api_schemas) == []


def test_client_load_one_api(tempdir, load_fstree):
    load_fstree('one_api')

    dirname = os.path.join(tempdir.name(), 'schemas', 'services', 'one_api')
    client_schemas = client_schema.ClientSchema(
        name='one_api',
        client_yaml_dirname=dirname,
        root_dirpath=tempdir.name(),
    )

    # no non-empty api/* files => empty
    assert not list(client_schemas.nonempty_api_schemas())

    api_schema1 = {
        'info': {'title': 'x', 'version': '1.0'},
        'openapi': '3.0.0',
        'paths': {},
    }

    new_openapi_schemas = list(client_schemas.api_schemas)
    assert len(new_openapi_schemas) == 1
    assert new_openapi_schemas[0][1].raw == api_schema1


def test_store_and_load_with_comments(tempdir, load_fstree, validate_filetree):
    load_fstree('comments')

    client_schemas = client_schema.ClientSchema(
        name='test-client',
        client_yaml_dirname=os.path.join(
            tempdir.name(), 'schemas', 'services', 'serviceX',
        ),
        root_dirpath=tempdir.name(),
    )

    assert len(list(client_schemas.nonempty_api_schemas())) == 1
    assert len(list(client_schemas.api_schemas)) == 1

    conv_dirname = os.path.join(
        tempdir.name(), 'schemas', 'external-api', 'serviceX',
    )
    os.makedirs(conv_dirname)
    dumper = client_schema.ClientSchemaDumper(client_schemas)
    dumper.store_schema(conv_dirname)

    # The core structure is not changed,
    # but a header comment is added.
    validate_filetree('comments_result')


# TODO: libraries, definitions.yaml
