import uuid
import pytest


@pytest.fixture(scope='module')
def yt_client(yt_stuff):
    return yt_stuff.get_yt_client()


@pytest.fixture
def input_prefix(yt_client):
    input_prefix = '//home/test/input/{}'.format(uuid.uuid4())
    yt_client.create('map_node', input_prefix, recursive=True)
    return input_prefix


@pytest.fixture
def output_prefix(yt_client):
    output_prefix = '//home/test/output/{}'.format(uuid.uuid4())
    yt_client.create('map_node', output_prefix, recursive=True)
    return output_prefix


@pytest.fixture
def input_data():
    return [{
        'my_column_name': str(uuid.uuid4())
    }]


@pytest.fixture
def input_table_name():
    table_name = 'input_table_{}'.format(uuid.uuid4())
    return table_name


@pytest.fixture
def input_table(yt_client, input_prefix, input_data, input_table_name):
    table_path = input_prefix + '/' + input_table_name
    yt_client.create('table', table_path, ignore_existing=True)
    yt_client.write_table(table_path, input_data)
    return table_path


@pytest.fixture
def output_table(yt_client, output_prefix):
    table_name = 'output_table_{}'.format(uuid.uuid4())
    table_path = output_prefix + '/' + table_name
    return table_path
