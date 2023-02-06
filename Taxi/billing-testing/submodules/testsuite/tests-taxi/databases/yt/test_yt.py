import pytest
import yt.yson


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


@pytest.mark.yt(dyn_table_data=['yt_hash_values.yaml'])
@pytest.mark.parametrize('_dummy_parametrize', [1, 2])
def test_yt_lookup_rows_hash_table(yt_client, yt_apply, _dummy_parametrize):
    rows = list(
        yt_client.lookup_rows(
            '//home/testsuite/hash',
            [{'id': 'foo'}],
            column_names=['id', 'value'],
        ),
    )
    assert rows == [{'id': 'foo', 'value': 'abc'}]


@pytest.mark.yt(
    dyn_table_data=[
        {
            'path': '//home/testsuite/bar',
            'values': [{'id': 'bin', 'value': b'binary\x00\x00\x00\x02'}],
            'format': {'encoding': None},
        },
    ],
)
def test_yt_binary_string(yt_client, yt_apply):
    rows = list(yt_client.lookup_rows('//home/testsuite/bar', [{'id': 'bin'}]))
    assert rows == [{'id': 'bin', 'value': 'binary\x00\x00\x00\x02'}]


@pytest.mark.yt(
    dyn_table_data=[
        {
            'path': '//home/testsuite/binary',
            'values': [
                {'id': 'bin', 'value': {'items': [b'\x00\x01', b'\x00\x02']}},
            ],
            'format': {'encoding': None},
        },
    ],
)
def test_yt_binary_complex(yt_client, yt_apply):
    rows = list(
        yt_client.lookup_rows('//home/testsuite/binary', [{'id': 'bin'}]),
    )
    assert rows == [
        {'id': 'bin', 'value': {'items': ['\x00\x01', '\x00\x02']}},
    ]


@pytest.mark.yt(dyn_table_data=['yt_ordered.yaml'])
def test_yt_select_rows_from_ordered(yt_client):
    rows = list(
        yt_client.select_rows(
            '* FROM [//home/testsuite/ordered_dynamic_table]',
        ),
    )
    rows.sort(key=lambda value: value['$row_index'])
    assert rows == [
        {'id': 'foo', 'value': 'abc', '$row_index': 0, '$tablet_index': 0},
        {'id': 'bar', 'value': 'def', '$row_index': 1, '$tablet_index': 0},
    ]


@pytest.mark.yt(dyn_table_data=['yt_attributes.yaml'])
def test_yt_select_rows_attributes(yt_client):
    rows = list(yt_client.select_rows('* FROM [//home/testsuite/attributes]'))
    assert rows == [
        {
            'id': 'foo',
            'value': {
                'bar': yt.yson.to_yson_type(
                    'string_value', attributes={'attr_key': 'attr_value'},
                ),
            },
        },
    ]


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
def test_yt_map(yt_apply, yt_client):
    path = '//home/testsuite/bar'

    path_mapped = path + '_mapped'
    yt_client.remove(path_mapped, force=True)

    # flush dyn data
    yt_client.unmount_table(path, sync=True)
    yt_client.mount_table(path, sync=True)

    def _mapper(value):
        yield {'id_value': value['id'] + '_' + value['value']}

    yt_client.run_map(_mapper, path, path_mapped)
    output = sorted(
        yt_client.read_table(path_mapped), key=lambda v: v['id_value'],
    )
    assert output == [{'id_value': 'bar_def'}, {'id_value': 'foo_abc'}]

    yt_client.remove(path_mapped, force=True)
