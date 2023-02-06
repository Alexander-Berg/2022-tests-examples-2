import pytest

from taxi.internal.yt_tools import temp_tables


class _DummyClient(object):
    def __init__(self, cluster, prefix='//home/taxi/unstable/'):
        self.config = {
            'prefix': prefix,
            'token': '123',
            'proxy': {'url': '%s.xxx' % cluster},
        }


@pytest.mark.parametrize('table,result', [
    (
        '', False
    ),
    (
        '//home/taxi/unstable/', False
    ),
    (
        '//home/taxi/unstable/tmp', False
    ),
    (
        '//home/taxi/unstable/tmp/', False
    ),
    (
        '//home/taxi/testing/tmp/table', False
    ),
    (
        '/home/taxi/unstable/tmp/table', False
    ),
    (
        'home/taxi/unstable/tmp/table', False
    ),
    (
        '//home/taxi/unstable/tmp/table', True
    ),
])
def test_is_table_from_client_tmp(table, result):
    assert temp_tables.is_table_from_client_tmp(
        _DummyClient(''), table
    ) == result


def test_garbage_collector(monkeypatch):
    hahn = _DummyClient('hahn')
    also_hahn = _DummyClient('hahn', prefix='//backups/')
    monkeypatch.setattr('taxi.external.yt_wrapper._environments', {
        'hahn': hahn,
        'hahn-backups': also_hahn,
    })

    collector = temp_tables.GarbageCollector()

    collector.update(hahn, ('table', 'table2', 'table3',))
    collector.update(also_hahn, ('table', 'table2',))

    collector.discard(hahn, 'table2')
    collector.discard(also_hahn, 'table')

    assert collector.tables_by_client_names == {
        'hahn': {'table', 'table3'},
        'hahn-backups': {'table2'}
    }
