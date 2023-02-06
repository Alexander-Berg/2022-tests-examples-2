import uuid
import pytest


@pytest.fixture(scope='module')
def yt_client(yt_stuff):
    return yt_stuff.get_yt_client()


@pytest.fixture()
def prefix(yt_client):
    prefix = '//home/test/folder_{}'.format(uuid.uuid4())
    yt_client.create('map_node', prefix, recursive=True)
    return prefix


@pytest.fixture()
def table_path(prefix, yt_client):
    table_name = 'table_{}'.format(uuid.uuid4())
    input_table = prefix + '/' + table_name
    return input_table
