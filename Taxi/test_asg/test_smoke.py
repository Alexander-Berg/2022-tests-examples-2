from scripts.authproxy_schemas_generator import client_schema_set


def test_all_schemas_empty():
    schemas = client_schema_set.ClientSchemaSet('testing')
    assert schemas.by_hostname == {}
