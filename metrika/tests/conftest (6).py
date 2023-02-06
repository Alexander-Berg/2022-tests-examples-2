import logging
from unittest.mock import Mock

import pytest
from metrika.admin.python.clickhouse_restorer.lib.restorer import HostRestorer
from metrika.pylib.monitoring import juggler
from metrika.pylib.mtapi import cluster
from metrika.pylib.structures.dotdict import DotDict


class ChMock:
    def __init__(self):
        self.tables_info = {}
        self.db_engines = {}
        self.inner_table_views = set()
        self.created_databases = {}
        self.created_tables = []
        self.hosts = DotDict(hosts=['donor'])

    def get_tables_info(self):
        return self.tables_info, self.db_engines or {db: 'Ordinary' for db in self.tables_info}

    def get_inner_table_view(self, fullname_table):
        if fullname_table in self.inner_table_views:
            return [{'count': '1'}]

    def create_database(self, database, engine):
        self.created_databases[database] = engine

    def create_table(self, query):
        self.created_tables.append(query)


@pytest.fixture()
def mock_zk(monkeypatch):
    monkeypatch.setattr(HostRestorer, 'zk', Mock())


@pytest.fixture()
def mock_mtapi(monkeypatch):
    monkeypatch.setattr(cluster, 'ClusterAPI', Mock())
    monkeypatch.setattr(HostRestorer, '_get_mtapi_info', lambda s: {'type': 'restorer', 'layer': 1, 'shard': 1337, 'environment': 'testing', 'shard_id': 'testing-1337', 'index': 42})


@pytest.fixture()
def mock_donors_ch(monkeypatch):
    monkeypatch.setattr(HostRestorer, 'donors_ch', ChMock())


@pytest.fixture()
def mock_juggler(monkeypatch):
    monkeypatch.setattr(juggler, 'MonitoringSender', Mock())


@pytest.fixture()
def restorer(mock_zk, mock_mtapi, mock_donors_ch, monkeypatch, mock_juggler):
    restorer = HostRestorer(logger=logging.getLogger(__name__))
    restorer.new_shard = True
    monkeypatch.setattr(restorer, 'clickhouse', ChMock())
    return restorer
