import pytest


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
def test_yt_select_rows(yt_client, yt_apply):
    rows = list(
        yt_client.select_rows(f'* FROM [//home/testsuite/bar] WHERE id="bar"'),
    )
    assert rows == [{'id': 'bar', 'value': 'def'}]


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
async def test_yt_lookup_rows(yt_apply, stq3_context):
    yt_client = stq3_context.yt_wrapper.hahn
    rows = list(
        (await yt_client.lookup_rows('//home/testsuite/bar', [{'id': 'bar'}])),
    )
    assert rows == [{'id': 'bar', 'value': 'def'}]


@pytest.mark.yt(dyn_table_data=['yt_bar_values.yaml'])
async def test_yt_map(yt_apply, stq3_context):
    yt_client = stq3_context.yt_wrapper.hahn

    path = '//home/testsuite/bar'

    path_mapped = path + '_mapped'
    await yt_client.remove(path_mapped, force=True)

    # flush dyn data
    await yt_client.unmount_table(path, sync=True)
    await yt_client.mount_table(path, sync=True)

    def _mapper(value):
        yield {'id_value': value['id'] + '_' + value['value']}

    await yt_client.run_map(_mapper, path, path_mapped)
    output = sorted(
        (await yt_client.read_table(path_mapped)), key=lambda v: v['id_value'],
    )
    assert output == [{'id_value': 'bar_def'}, {'id_value': 'foo_abc'}]

    await yt_client.remove(path_mapped, force=True)
