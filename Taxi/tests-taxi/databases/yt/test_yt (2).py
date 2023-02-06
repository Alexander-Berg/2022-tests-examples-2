import pytest


def test_yt_basic(yt_client):
    table = '//home/testsuite/foo'
    yt_client.remove(table, force=True, recursive=True)
    yt_client.create(
        'table',
        table,
        attributes={
            'schema': [
                {'name': 'id', 'type': 'string', 'sort_order': 'ascending'},
                {'name': 'value', 'type': 'string'},
            ],
            'dynamic': True,
        },
        force=True,
        recursive=True,
    )
    yt_client.mount_table(table, sync=True)
    yt_client.insert_rows(table, [{'id': 'foo', 'value': 'bar'}])
    rows = list(yt_client.lookup_rows(table, [{'id': 'foo'}]))
    assert rows == [{'id': 'foo', 'value': 'bar'}]


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
def test_yt_lookup_rows(yt_client, yt_apply):
    rows = list(yt_client.lookup_rows('//home/testsuite/bar', [{'id': 'foo'}]))
    assert rows == [{'id': 'foo', 'value': 'abc'}]


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
def test_yt_select_rows(yt_client, yt_apply):
    rows = list(
        yt_client.select_rows(f'* FROM [//home/testsuite/bar] WHERE id="bar"'),
    )
    assert rows == [{'id': 'bar', 'value': 'def'}]
