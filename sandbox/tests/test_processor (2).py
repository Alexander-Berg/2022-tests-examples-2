import unittest

import mock
import pytest

from sandbox.projects.browser.monitoring import processor

TEST_VERSION_DATA_TABLE = processor.VersionDataTable(123456, [
    processor.VersionDataPoint(111, '1.0', 110, {'errors': 101}),
    processor.VersionDataPoint(111, '1.1', 111, {'errors': 111}),
    processor.VersionDataPoint(111, '1.2', 112, {'errors': 121}),
    processor.VersionDataPoint(222, '1.0', 210, {'errors': 102}),
    processor.VersionDataPoint(222, '1.1', 211, {'errors': 112}),
    processor.VersionDataPoint(222, '1.2', 212, {'errors': 122}),
    processor.VersionDataPoint(333, '1.0', 310, {'errors': 103}),
    processor.VersionDataPoint(333, '1.1', 311, {'errors': 113}),
    processor.VersionDataPoint(333, '1.2', 312, {'errors': 123}),
])


class TestVersionDataTable(unittest.TestCase):
    def test_init(self):
        points = [
            processor.VersionDataPoint(111, '1.0', 110, {'errors': 101}),
            processor.VersionDataPoint(222, '1.1', 211, {'errors': 112}),
            processor.VersionDataPoint(222, '1.2', 212, {'errors': 122}),
            processor.VersionDataPoint(333, '1.0', 310, {'errors': 103}),
            processor.VersionDataPoint(333, '1.1', 311, {'errors': 113}),
            processor.VersionDataPoint(333, '1.2', 312, {'errors': 123}),
        ]
        version_data_table = processor.VersionDataTable(123456, points)
        assert version_data_table.query_timestamp == 123456
        assert version_data_table.timestamps == [111, 222, 333]
        assert version_data_table.versions == ['1.0', '1.1', '1.2']
        assert version_data_table.points == points

        point_tuples = [
            (111, '1.0', 110, {'errors': 101}),
            (222, '1.1', 211, {'errors': 112}),
            (222, '1.2', 212, {'errors': 122}),
            (333, '1.0', 310, {'errors': 103}),
            (333, '1.1', 311, {'errors': 113}),
            (333, '1.2', 312, {'errors': 123}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in version_data_table.points] == point_tuples

        assert sorted(version_data_table.data.keys()) == version_data_table.versions
        points = []
        for version_name in version_data_table.data.keys():
            version_data = version_data_table.data[version_name]
            for timestamp, point in version_data.iteritems():
                assert timestamp == point.report_timestamp
                assert version_name == point.version_name
                points.append(point)
        assert version_data_table.points == sorted(
            points, key=lambda p: [p.report_timestamp, p.version_name])

    def test_build_without_versions(self):
        new_table = TEST_VERSION_DATA_TABLE.build_without_versions(['1.1'])
        assert TEST_VERSION_DATA_TABLE.query_timestamp == new_table.query_timestamp

        point_tuples = [
            (111, '1.0', 110, {'errors': 101}),
            (111, '1.2', 112, {'errors': 121}),
            (222, '1.0', 210, {'errors': 102}),
            (222, '1.2', 212, {'errors': 122}),
            (333, '1.0', 310, {'errors': 103}),
            (333, '1.2', 312, {'errors': 123}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in new_table.points] == point_tuples

    def test_build_with_version_mapping(self):
        mapping = {'a': '1.0', 'b': '1.2', 'c': '1.0'}
        new_table = TEST_VERSION_DATA_TABLE.build_with_version_mapping(mapping)
        assert TEST_VERSION_DATA_TABLE.query_timestamp == new_table.query_timestamp

        point_tuples = [
            (111, 'a', 110, {'errors': 101}),
            (111, 'b', 112, {'errors': 121}),
            (111, 'c', 110, {'errors': 101}),
            (222, 'a', 210, {'errors': 102}),
            (222, 'b', 212, {'errors': 122}),
            (222, 'c', 210, {'errors': 102}),
            (333, 'a', 310, {'errors': 103}),
            (333, 'b', 312, {'errors': 123}),
            (333, 'c', 310, {'errors': 103}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in new_table.points] == point_tuples

    def test_build_sum(self):
        new_table = TEST_VERSION_DATA_TABLE.build_sum('sum')
        assert TEST_VERSION_DATA_TABLE.query_timestamp == new_table.query_timestamp

        point_tuples = [
            (111, 'sum', 333, {'errors': 333}),
            (222, 'sum', 633, {'errors': 336}),
            (333, 'sum', 933, {'errors': 339}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in new_table.points] == point_tuples

    def test_build_merged_with(self):
        merged = TEST_VERSION_DATA_TABLE.build_merged_with(processor.VersionDataTable(123456, [
            processor.VersionDataPoint(111, '1.1', 111, {'errors': 222}),
            processor.VersionDataPoint(111, '1.5', 321, {'errors': 234, 'sensor': 123}),
            processor.VersionDataPoint(222, '1.1', 211, {'errors': 224}),
            processor.VersionDataPoint(222, '1.5', 432, {'errors': 345}),
        ]))
        point_tuples = [
            (111, '1.0', 110, {'errors': 101}),
            (111, '1.1', 111, {'errors': 222}),
            (111, '1.2', 112, {'errors': 121}),
            (111, '1.5', 321, {'errors': 234, 'sensor': 123}),
            (222, '1.0', 210, {'errors': 102}),
            (222, '1.1', 211, {'errors': 224}),
            (222, '1.2', 212, {'errors': 122}),
            (222, '1.5', 432, {'errors': 345}),
            (333, '1.0', 310, {'errors': 103}),
            (333, '1.1', 311, {'errors': 113}),
            (333, '1.2', 312, {'errors': 123}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in merged.points] == point_tuples


class TestVersionDataManager(unittest.TestCase):
    def test_load_version_data_table(self):
        column_names = [
            processor.VersionDataManager._COLUMN_REPORT_TIMESTAMP,
            processor.VersionDataManager._COLUMN_VERSION_NAME,
            'sessions', 'errors',
        ]
        rows = [
            [111, '1.0', 100, 1],
            [111, '2.0', 200, 2],
            [222, '1.0', 110, 3],
            [222, '2.0', 220, 4],
        ]
        monitor_values = processor.MonitorValues(0, column_names, rows)
        version_data_table = processor.VersionDataManager.load_version_data_table(
            monitor_values, 'sessions')

        point_tuples = [
            (111, '1.0', 100, {'errors': 1, 'sessions': 100}),
            (111, '2.0', 200, {'errors': 2, 'sessions': 200}),
            (222, '1.0', 110, {'errors': 3, 'sessions': 110}),
            (222, '2.0', 220, {'errors': 4, 'sessions': 220}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in version_data_table.points] == point_tuples

    def test_get_wrong_versions(self):
        versions = ['1.23', '2.34-SNAPSHOT', '123456', '34.56', '4.5', '6.7.8.9']
        wrong_versions = ['2.34-SNAPSHOT', '123456', '4.5', '6.7.8.9']
        assert wrong_versions == processor.VersionDataManager.get_wrong_versions(versions, r'^\d+\.\d{2}$')

    def test_get_version_weights(self):
        column_names = [
            processor.VersionDataManager._COLUMN_REPORT_TIMESTAMP,
            processor.VersionDataManager._COLUMN_VERSION_NAME,
            'navigates',
        ]
        version_weight_dict = {
            0: processor.MonitorValues(0, column_names, [
                [111, '1.0', 100],
                [111, '2.0', 200],
                [222, '1.0', 110],
                [222, '2.0', 220],
            ]),
            1: None,
            2: processor.MonitorValues(2, column_names, [
                [111, '1.0', 1000],
                [222, '2.0', 2000],
            ]),
        }
        version_weight_dict = processor.VersionDataManager.get_version_weights(
            version_weight_dict, 'navigates')
        assert version_weight_dict == {
            '1.0': (100 + 110 + 1000) * 3 / 2,
            '2.0': (200 + 220 + 2000) * 3 / 2,
        }

    def test_create_version_weights_table(self):
        version_weights = {'1.0': 20, '2.0': 30, '3.0': 40, '4.0': 50, '5.0': 10}
        weight_table = processor.VersionDataManager.create_version_weights_table(123456, version_weights)
        assert weight_table.query_timestamp == 123456

        point_tuples = [
            (123456, '4.0', 50, {'_daily_weight': 50}),
            (123456, '3.0', 40, {'_daily_weight': 40}),
            (123456, '2.0', 30, {'_daily_weight': 30}),
            (123456, '1.0', 20, {'_daily_weight': 20}),
            (123456, '5.0', 10, {'_daily_weight': 10}),
        ]
        assert [(p.report_timestamp, p.version_name, p.weight, p.values)
                for p in weight_table.points] == point_tuples

    def test_create_solomon_metrics(self):
        version_data_table = processor.VersionDataTable(123456, [
            processor.VersionDataPoint(111, '1.0', 110, {'errors': 101, 'loads': 1}),
            processor.VersionDataPoint(111, '1.1', 111, {'errors': 111, 'loads': 2}),
            processor.VersionDataPoint(222, '1.0', 210, {'errors': 102, 'loads': 11}),
            processor.VersionDataPoint(222, '1.1', 211, {'errors': 112, 'loads': 22}),
            processor.VersionDataPoint(333, '1.0', 310, {'errors': 103, 'loads': 111}),
            processor.VersionDataPoint(333, '1.1', 311, {'errors': 113, 'loads': 222}),
        ])
        version_labels = {
            '1.0': {'version': '1.0.0'},
            '7.0': {'release': 'yes'},
        }

        solomon_metrics = processor.VersionDataManager.create_solomon_metrics(
            version_data_table, version_labels)
        assert solomon_metrics == [
            {'ts': 111, 'labels': {'version': '1.0', 'sensor': 'loads'}, 'value': 1},
            {'ts': 111, 'labels': {'version': '1.0', 'sensor': 'errors'}, 'value': 101},
            {'ts': 111, 'labels': {'version': '1.1', 'sensor': 'loads'}, 'value': 2},
            {'ts': 111, 'labels': {'version': '1.1', 'sensor': 'errors'}, 'value': 111},
            {'ts': 222, 'labels': {'version': '1.0', 'sensor': 'loads'}, 'value': 11},
            {'ts': 222, 'labels': {'version': '1.0', 'sensor': 'errors'}, 'value': 102},
            {'ts': 222, 'labels': {'version': '1.1', 'sensor': 'loads'}, 'value': 22},
            {'ts': 222, 'labels': {'version': '1.1', 'sensor': 'errors'}, 'value': 112},
            {'ts': 333, 'labels': {'version': '1.0', 'sensor': 'loads'}, 'value': 111},
            {'ts': 333, 'labels': {'version': '1.0', 'sensor': 'errors'}, 'value': 103},
            {'ts': 333, 'labels': {'version': '1.1', 'sensor': 'loads'}, 'value': 222},
            {'ts': 333, 'labels': {'version': '1.1', 'sensor': 'errors'}, 'value': 113},
        ]


@pytest.mark.parametrize(('version', 'components'), [
    ('', ['']),
    ('123', [123]),
    ('1.2.3', [1, 2, 3]),
    ('1.2.3.abc', [1, 2, 3, 'abc']),
])
def test_parse_version(version, components):
    assert components == processor.parse_version(version)


@pytest.mark.parametrize(('res', 'version1', 'version2'), [
    (0, '', ''),

    (0, '1', '1'),
    (-1, '1', '2'),
    (+1, '2', '1'),

    (0, 'a', 'a'),
    (-1, 'a', 'b'),
    (+1, 'b', 'a'),

    (-1, '1', 'a'),
    (+1, 'a', '1'),
])
def test_compare_versions(res, version1, version2):
    assert res == processor.compare_versions(version1, version2)


class TestWeightAnalyser(unittest.TestCase):
    def test_get_significant_versions(self):
        version_weights = {'1.0': 10, '2.0': 20, '3.0': 30}
        assert processor.WeightAnalyser.get_significant_versions(
            20, version_weights) == {'2.0', '3.0'}

    def test_get_sorted_releases(self):
        versions = [
            '1.0',
            '2.0',
            '1.2.3',
            '2.3.4',
            '1.2.3-SNAPSHOT',
            '123',
            '234',
            'abc',
            '1.B.3',
            'A.2.3',
            '12.3',
        ]
        assert processor.WeightAnalyser.get_sorted_releases(versions) == [
            '1.0',
            '1.2.3',
            '1.2.3-SNAPSHOT',
            '1.B.3',
            '2.0',
            '2.3.4',
            '12.3',
            '123',
            '234',
            'A.2.3',
            'abc',
        ]

    def test_find_release_version(self):
        version_weights = {'1.0': 20, '2.0': 30, '3.0': 40, '4.0': 10}
        assert processor.WeightAnalyser.find_release_version(20, version_weights) == '3.0'
        assert processor.WeightAnalyser.find_release_version(10, version_weights) == '4.0'
        assert processor.WeightAnalyser.find_release_version(50, version_weights) is None

    def test_get_leader_versions(self):
        versions_navigates = {'1.0': 10, '2.0': 20, '3.0': 30, '4.0': 40, '5.0': 50}
        assert processor.WeightAnalyser.get_leader_versions(
            70, versions_navigates) == {'3.0', '4.0', '5.0'}

    def test_update_version_labels_with_hardcoded_metrics(self):
        versions_labels = {
            '1.0': {'a': 'AAA'},
            '2.0': {'b': 'BBB'},
            '3.0': {'c': 'CCC'},
        }

        monitor_config = mock.MagicMock(
            metrics_default={'important': 'NO'},
            metrics_values={
                'important': {'YES': ['3.0']},
                'name': {'MY': ['2.0']},
            },
        )

        processor.WeightAnalyser.update_version_labels_with_hardcoded_metrics(versions_labels, monitor_config)
        assert versions_labels == {
            '1.0': {'a': 'AAA', 'important': 'NO'},
            '2.0': {'b': 'BBB', 'important': 'NO', 'name': 'MY'},
            '3.0': {'c': 'CCC', 'important': 'YES'},
        }

    def test_get_version_labels(self):
        monitor_config = mock.MagicMock(
            metrics_default={'important': 'NO'},
            metrics_values={
                'important': {'YES': ['3.0']},
                'name': {'MY': ['2.0']},
            },
            significant_daily_weight_threshold=35,
            release_daily_weight_threshold=15,
            leaders_daily_weight_percent=70,
        )

        version_weights = {'1.0': 20, '2.0': 30, '3.0': 40, '4.0': 50, '5.0': 10}

        assert processor.WeightAnalyser.get_version_labels(monitor_config, version_weights) == {
            '1.0': {'leader': 'no', 'release': 'no', 'significant': 'no', 'important': 'NO'},
            '2.0': {'leader': 'yes', 'release': 'no', 'significant': 'no', 'important': 'NO', 'name': 'MY'},
            '3.0': {'leader': 'yes', 'release': 'no', 'significant': 'yes', 'important': 'YES'},
            '4.0': {'leader': 'yes', 'release': 'yes', 'significant': 'yes', 'important': 'NO'},
            '5.0': {'leader': 'no', 'release': 'no', 'significant': 'no', 'important': 'NO'},
        }

    def test_get_generated_versions_mapping(self):
        monitor_config = mock.MagicMock(
            release_daily_weight_threshold=15,
            top_versions_count=3,
        )

        version_weights = {'1.0': 20, '2.0': 30, '3.0': 40, '4.0': 50, '5.0': 10}

        assert processor.WeightAnalyser.get_generated_versions_mapping(monitor_config, version_weights) == {
            'release': '4.0',
            'top-1': '4.0',
            'top-2': '3.0',
            'top-3': '2.0',
        }


def test_none_version_in_monitor_values():
    column_names = [
        processor.VersionDataManager._COLUMN_REPORT_TIMESTAMP,
        processor.VersionDataManager._COLUMN_VERSION_NAME,
        'sessions', 'errors',
    ]
    rows = [
        [111, '00', 100, 1],
        [111, None, 200, 2],
        [222, '00', 300, 3],
    ]
    monitor_values = processor.MonitorValues(0, column_names, rows)

    version_data_table = processor.VersionDataManager.load_version_data_table(
        monitor_values, 'sessions')
    assert version_data_table.versions == ['00']
    assert len(version_data_table.points) == 2

    version_weights = processor.VersionDataManager.get_version_weights(
        {0: monitor_values}, 'sessions')
    assert version_weights == {'00': 400}
