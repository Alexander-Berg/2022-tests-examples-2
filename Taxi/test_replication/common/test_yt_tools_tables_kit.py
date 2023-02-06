import pytest

from replication.common.yt_tools import tables_kit


class _DummyClient:
    def __init__(self, cluster, prefix='//home/taxi/testing/'):
        self.config = {
            'prefix': prefix,
            'token': '123',
            'proxy': {'url': '%s.xxx' % cluster},
        }


_TMP_PREFIX = '//home/taxi/testing/tmp'


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'table,result',
    [
        ('', False),
        ('//home/taxi/testing/', False),
        ('//home/taxi/testing/tmp', False),
        ('//home/taxi/testing/tmp/', False),
        ('//home/taxi/production/tmp/table', False),
        ('/home/taxi/testing/tmp/table', False),
        ('home/taxi/testing/tmp/table', False),
        ('//home/taxi/testing/tmp/table', True),
    ],
)
def test_is_table_from_client_tmp(table, result):
    assert (
        tables_kit.is_table_from_client_tmp(
            _DummyClient(''), table, tmp_prefix=_TMP_PREFIX,
        )
        == result
    ), table


# pylint: disable=protected-access
@pytest.mark.nofilldb()
def test_garbage_collector():
    hahn = _DummyClient('hahn')
    also_hahn = _DummyClient('hahn', prefix='//backups/')

    collector = tables_kit._GarbageCollector()

    collector.update(
        hahn, ('table', 'table2', 'table3'), tmp_prefix=_TMP_PREFIX,
    )
    collector.update(also_hahn, ('table', 'table2'), tmp_prefix=_TMP_PREFIX)

    collector.discard(hahn, 'table2')
    collector.discard(also_hahn, 'table')

    assert collector._tables_by_client_ids == {
        ('hahn', '//home/taxi/testing/'): {'table', 'table3'},
        ('hahn', '//backups/'): {'table2'},
    }
