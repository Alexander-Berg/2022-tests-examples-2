import datetime

from mock import patch
import pytest
from yt.wrapper import YtHttpResponseError

from sandbox.projects.yabs.qa.utils.yt_utils import set_yt_node_ttl, set_node_attributes, set_yt_node_timeout


@pytest.fixture(scope='module')
def yt_client(yt_stuff):
    return yt_stuff.get_yt_client()


@pytest.fixture
def yt_node(yt_client):
    node_ypath = yt_client.find_free_subpath('//')
    yt_client.create('map_node', node_ypath)
    yield node_ypath
    yt_client.remove(node_ypath)


def test_set_yt_node_timeout(yt_client, yt_node):
    utcnow = datetime.datetime(year=3000, month=1, day=1)
    ttl = datetime.timedelta(days=1)
    expected_expiration_timeout = 86400000

    with patch('sandbox.projects.yabs.qa.utils.yt_utils.datetime.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = utcnow
        set_yt_node_timeout(yt_node, ttl.total_seconds(), yt_client)

    assert yt_client.get(yt_node + '/@expiration_timeout') == expected_expiration_timeout


def test_set_yt_node_ttl(yt_client, yt_node):
    utcnow = datetime.datetime(year=3000, month=1, day=1)
    ttl = datetime.timedelta(days=1)
    expected_expiration_time_str = '3000-01-02T00:00:00.000000Z'

    with patch('sandbox.projects.yabs.qa.utils.yt_utils.datetime.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = utcnow
        set_yt_node_ttl(yt_node, ttl.total_seconds(), yt_client)

    assert yt_client.get(yt_node + '/@expiration_time') == expected_expiration_time_str


def test_set_ttl_for_nonexistent_node(yt_client):
    node_ypath = '//nonexistent_node'
    ttl = datetime.timedelta(days=1)
    set_yt_node_ttl(node_ypath, ttl.total_seconds(), yt_client)


class TestSetNodeAttributes:
    def test_set_attributes(self, yt_client, yt_node):
        attributes = {
            'my_attribute': 'hello world',
            'my_other_attribute': 'foo bar',
            'expiration_time': '3000-01-01T00:00:00.000000Z',
        }

        set_node_attributes(yt_node, attributes, yt_client)

        for attribute_name, attribute_value in attributes.items():
            assert yt_client.get_attribute(yt_node, attribute_name) == attribute_value

    def test_set_builtin_attributes(self, yt_client, yt_node):
        attributes = {
            'type': 'table'
        }

        with pytest.raises(YtHttpResponseError):
            set_node_attributes(yt_node, attributes, yt_client)

    def test_set_attributes_not_changed_on_error(self, yt_client, yt_node):
        attributes = {
            'my_attribute': 'hello world',
            'type': 'table'
        }

        initial_attributes = {
            name: yt_client.get_attribute(yt_node, name, default=None)
            for name in attributes
        }

        with pytest.raises(YtHttpResponseError):
            set_node_attributes(yt_node, attributes, yt_client)

        for attribute_name, initial_attribute_value in initial_attributes.items():
            assert yt_client.get_attribute(yt_node, attribute_name, default=None) == initial_attribute_value
