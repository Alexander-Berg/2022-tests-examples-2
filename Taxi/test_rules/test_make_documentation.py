import os.path

from replication import settings
from replication.tools import make_documentation
from replication.tools.documentation import util
from replication.tools.documentation import yt_tables
from . import conftest


@conftest.dmp_rules_only
def test_make_documentation(monkeypatch, replication_ctx):
    master_rules = replication_ctx.rule_keeper.master_rules
    paths = set()

    def _write(path, data):
        assert path not in paths
        paths.add(path)
        assert data

    monkeypatch.setattr(util, 'write', _write)
    monkeypatch.setattr(os.path, 'exists', lambda val: True)

    all_tables = {}

    def dump(self, table_path, table_data):
        assert table_path not in all_tables
        all_tables[table_path] = table_data

    monkeypatch.setattr(yt_tables.TableDumper, 'dump', dump)

    make_documentation.main(
        ['--output-dir', '_out', '--output-yt-tables-dir', '_out_yt-tables'],
    )

    assert paths == {
        '_out/{}'.format(path)
        for path in (make_documentation.SERVICE_DESC_PATH,)
    }

    generated_all_tables = all_tables.copy()
    all_tables.clear()
    yt_tables.make_yaml_pages(
        {
            rule_name: master_rule
            for rule_name, master_rule in master_rules.items()
            if master_rule.rule_scope not in settings.EXAMPLE_RULE_SCOPES
        },
        '_out',
    )

    assert generated_all_tables == all_tables, 'Generated YT tables differ'
