from unittest.mock import MagicMock

from metrika.pylib.monitoring import juggler

import metrika.pylib.config.parsers.yaml_parser as yaml_parser
import pytest
from metrika.admin.python.scripts.clickhouse_parts_cleaner import lib


class TestConfig:
    @pytest.mark.parametrize('cfg_fixture, parts', [
        ('cfg_with_cluster_parts', 3),
        ('cfg_with_db_parts', 5),
        ('cfg_with_table_parts', 7)
    ])
    def test_parts(self, request, cfg_fixture, parts):
        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(request.getfixturevalue(cfg_fixture)))
        assert {part for tables in ch_cleaner.databases.values() for part in tables.values()} == {parts}

    @pytest.mark.parametrize('cfg_fixture, port', [
        ('cfg_with_cluster_port', 1337),
        ('cfg_with_cluster_port', 1337)
    ])
    def test_port(self, request, cfg_fixture, port):
        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(request.getfixturevalue(cfg_fixture)))
        assert {host_params.port for host_params in ch_cleaner.hosts.values()} == {1337}

    def test_all_tables(self, cfg_with_all_tables):
        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(cfg_with_all_tables))
        assert ch_cleaner.databases == {'test': 3}


class TestCHCleaner:
    PARTS_QUERY = "SELECT DISTINCT partition FROM system.parts WHERE table = '{}' and active"

    def _test_parts(self, ch, table, parts):
        result = ch.execute(self.PARTS_QUERY.format(table))
        assert {row.partition for row in result.data} == parts

    @pytest.fixture(autouse=True)
    def mock_juggler(self):
        juggler.MonitoringSender.send_event = MagicMock()

    @pytest.mark.parametrize('table, parts_count', [
        ('test_table_3parts', 3),
        ('test_table_6parts', 6),
        ('test_empty_table', 0),
    ])
    def test_partitions_to_drop(self, ch, test_ch_cfg, table, parts_count):
        assert ch.execute(self.PARTS_QUERY.format(table)).rows == parts_count

    @pytest.mark.parametrize('table, before, after', [
        ('test_table_3parts', {'2019-01-01', '2019-01-02', '2019-01-03'}, {'2019-01-01', '2019-01-02', '2019-01-03'}),
        ('test_table_6parts', {'2020-01-01', '2020-01-02', '2020-01-03', '2019-01-04', '2019-01-05', '2019-01-06'}, {'2020-01-01', '2020-01-02', '2020-01-03'}),
        ('test_empty_table', set(), set()),
    ])
    @pytest.mark.parametrize('dry', [True, False])
    def test_remaining_partitions(self, ch, test_ch_cfg, table, before, after, dry):
        self._test_parts(ch, table, before)

        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(test_ch_cfg(table)))
        ch_cleaner.clean(dry=dry)

        self._test_parts(ch, table, before if dry else after)

    def test_multiple_tables(self, ch, test_ch_cfg):
        tables = [
            ('test_table_3parts', {'2019-01-01', '2019-01-02', '2019-01-03'}, {'2019-01-02', '2019-01-03'}),
            ('test_table_6parts', {'2020-01-01', '2020-01-02', '2020-01-03', '2019-01-04', '2019-01-05', '2019-01-06'}, {'2020-01-02', '2020-01-03'})
        ]
        for table, before, _ in tables:
            self._test_parts(ch, table, before)

        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(test_ch_cfg(*(t[0] for t in tables), parts=2)))
        ch_cleaner.clean()

        for table, _, after in tables:
            self._test_parts(ch, table, after)

    def test_regexp_tables(self, ch, test_ch_cfg):
        tables = [
            ('test_table_3parts', {'2019-01-01', '2019-01-02', '2019-01-03'}, {'2019-01-01', '2019-01-02', '2019-01-03'}),
            ('test_table_6parts', {'2020-01-01', '2020-01-02', '2020-01-03', '2019-01-04', '2019-01-05', '2019-01-06'}, {'2020-01-03'})
        ]
        for table, before, _ in tables:
            self._test_parts(ch, table, before)

        ch_cleaner = lib.CHCleaner(yaml_parser.YamlParser().parse(test_ch_cfg(regexp='.*6parts', parts=1)))
        ch_cleaner.clean()

        for table, _, after in tables:
            self._test_parts(ch, table, after)
