import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerPerformancePlotter.tables import write_data, merge_data, DIFF_RPS_UNSORTED_SCHEMA


def generate_datum(row_values, include_optional=False, schema=DIFF_RPS_UNSORTED_SCHEMA):
    datum = {}
    for idx, key in enumerate(DIFF_RPS_UNSORTED_SCHEMA):
        value = row_values[idx]
        if key['type_v3']['type_name'] != 'optional' or value is not None or include_optional:
            datum[key['name']] = value
    return datum


class TestWriteData(object):

    @pytest.mark.parametrize(
        ('row_values', 'include_optional'),
        (
            (
                ('stat', 'bs',  'full', 5, ['content', 'pmatch'], 1, 2, 100., 200., 123,),
                True,
            ),
            (
                ('meta', 'yabs', 'full', None, ['page', 'code'], 3, 4, 500., 600., 123,),
                True,
            ),
            (
                ('meta', 'bsrank', 'full', None, ['rank'], 5, 6, 700., 800., 123,),
                False
            ),
        )
    )
    def test_write_data(self, yt_client, table_path, row_values, include_optional):
        datum = generate_datum(row_values, include_optional=include_optional, schema=DIFF_RPS_UNSORTED_SCHEMA)
        expected_datum = generate_datum(row_values, include_optional=True, schema=DIFF_RPS_UNSORTED_SCHEMA)

        write_data(yt_client, table_path, [datum], schema=DIFF_RPS_UNSORTED_SCHEMA)
        rows = list(yt_client.read_table(table_path))
        assert len(rows) == 1
        assert rows == [expected_datum]


class TestMergeData(object):

    def test_merge_data_no_new_release(self, yt_client, table_path, prefix):
        yt_client.create('table', prefix.rstrip('/') + '/1')
        yt_client.create('table', table_path, attributes={'schema': DIFF_RPS_UNSORTED_SCHEMA})

        first = generate_datum(('stat', 'bs', 'full', 5, [], 1, 2, 100., 200., 123,))
        second = generate_datum(('stat', 'bs', 'full', 5, [], 2, 3, 150., 180., 123,))
        data = [first, second]

        merge_data(yt_client, data, table_path, prefix, {1: 2}, 2)

        new_trunk_data = list(yt_client.read_table(table_path))

        assert new_trunk_data == [first, second]

    def test_merge_data_new_release(self, yt_client, table_path, prefix):
        yt_client.create('table', table_path, attributes={'schema': DIFF_RPS_UNSORTED_SCHEMA})

        first = generate_datum(('stat', 'bs', 'full', 5, [], 1, 2, 100., 200., 123,))
        second = generate_datum(('stat', 'bs', 'full', 5, [], 2, 3, 150., 180., 123,))
        data = [first, second]

        merge_data(yt_client, data, table_path, prefix, {1: 2}, 2)

        new_trunk_data = list(yt_client.read_table(table_path))
        release_data = list(yt_client.read_table(prefix.rstrip('/') + '/1'))

        assert new_trunk_data == [second]
        assert release_data == [first]

    def test_merge_data_new_release_sort(self, yt_client, table_path, prefix):
        yt_client.create('table', table_path, attributes={'schema': DIFF_RPS_UNSORTED_SCHEMA})

        first = generate_datum(('stat', 'bs', 'full', 5, [], 1, 2, 100., 200., 123,))
        second = generate_datum(('stat', 'bs', 'full', 5, [], 2, 3, 150., 180., 123,))
        data = [second, first]

        merge_data(yt_client, data, table_path, prefix, {1: 3}, 3)

        new_trunk_data = list(yt_client.read_table(table_path))
        release_data = list(yt_client.read_table(prefix.rstrip('/') + '/1'))

        assert new_trunk_data == []
        assert release_data == [first, second]

    def test_merge_data_new_release_unchecked_interval(self, yt_client, table_path, prefix):
        yt_client.create('table', table_path, attributes={'schema': DIFF_RPS_UNSORTED_SCHEMA})

        first = generate_datum(('stat', 'bs', 'full', 5, [], 1, 2, 100., 200., 123,))
        second = generate_datum(('stat', 'bs', 'full', 5, [], 2, 3, 150., 180., 123,))
        data = [first, second]

        merge_data(yt_client, data, table_path, prefix, {1: 2}, 1)

        new_trunk_data = list(yt_client.read_table(table_path))

        assert new_trunk_data == [first, second]

    def test_merge_data_several_new_releases(self, yt_client, table_path, prefix):
        yt_client.create('table', table_path, attributes={'schema': DIFF_RPS_UNSORTED_SCHEMA})

        first = generate_datum(('stat', 'bs', 'full', 5, [], 1, 2, 100., 200., 123,))
        second = generate_datum(('stat', 'bs', 'full', 5, [], 2, 3, 150., 180., 123,))
        third = generate_datum(('stat', 'bs', 'full', 5, [], 3, 4, 150., 180., 123,))
        data = [first, second, third]

        merge_data(yt_client, data, table_path, prefix, {1: 2, 2: 3}, 3)

        new_trunk_data = list(yt_client.read_table(table_path))
        first_release_data = list(yt_client.read_table(prefix.rstrip('/') + '/1'))
        second_release_data = list(yt_client.read_table(prefix.rstrip('/') + '/2'))

        assert new_trunk_data == [third]
        assert first_release_data == [first]
        assert second_release_data == [second]
