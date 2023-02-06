import pytest


@pytest.mark.yt(static_table_data=['yt_metrics_sample.yaml'])
def test_yt_read_table_metrics(yt_client, yt_apply):
    """
    Static tables don't support queries.
    Iterator is built-in.
    """
    rows = list(yt_client.read_table('//home/testsuite/metrics'))
    ids = {r['unique_driver_id'] for r in rows}
    assert ids == {
        '59a3b9a489216ea4ee2a02d4',
        '59a3ba1d89216ea4ee2a2d47',
        '59a5479189216ea4ee96ca75',
    }


@pytest.mark.yt(static_table_data=['yt_metrics_sample.yaml'])
def test_yt_get_tables(yt_client, yt_apply):
    path = '//home/testsuite'
    assert yt_client.exists(path)

    node = yt_client.get(path)
    tables = set(str(val) for val in node.keys())
    assert tables == {'bar', 'metrics'}

    tables = list(yt_client.search(path, node_type='table'))
    assert tables == ['//home/testsuite/bar', '//home/testsuite/metrics']
