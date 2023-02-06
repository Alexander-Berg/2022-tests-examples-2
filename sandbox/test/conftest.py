import uuid
import pytest


@pytest.fixture(scope='module')
def yt_client(yt_stuff):
    return yt_stuff.get_yt_client()


@pytest.fixture()
def input_prefix(yt_client):
    input_prefix = '//home/test/input_folder_{}'.format(uuid.uuid4())
    yt_client.create('map_node', input_prefix, recursive=True)
    return input_prefix


@pytest.fixture()
def output_prefix(yt_client):
    output_prefix = '//home/test/output_folder_{}'.format(uuid.uuid4())
    yt_client.create('map_node', output_prefix, recursive=True)
    return output_prefix


@pytest.fixture()
def input_table(input_prefix, yt_client):
    table_name = 'table_{}'.format(uuid.uuid4())
    input_table = input_prefix + '/' + table_name
    yt_client.create('table', input_table, recursive=True)
    return input_table


@pytest.fixture()
def sort_key():
    return ['PrimaryKey', 'SecondaryKey']


@pytest.fixture()
def event_join_key():
    return ['EventPrimaryKey']


@pytest.fixture()
def schema(sort_key, event_join_key):
    from sandbox.projects.yabs.qa.bases.sample_tables.test.misc import create_schema
    return create_schema(sort_key, event_join_key)


@pytest.fixture()
def static_table_config(input_prefix, output_prefix, sort_key, event_join_key, yt_client):
    from sandbox.projects.yabs.qa.bases.sample_tables.test.misc import create_test_table_config
    return create_test_table_config(input_prefix, output_prefix, 'static_table', sort_key, event_join_key, yt_client)


@pytest.fixture()
def dynamic_table_config(input_prefix, output_prefix, sort_key, event_join_key, yt_client):
    from sandbox.projects.yabs.qa.bases.sample_tables.test.misc import create_test_table_config
    return create_test_table_config(input_prefix, output_prefix, 'dynamic_table', sort_key, event_join_key, yt_client, is_dynamic=True)
