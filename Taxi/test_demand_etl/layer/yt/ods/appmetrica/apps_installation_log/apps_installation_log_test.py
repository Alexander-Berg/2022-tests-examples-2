from unittest import TestCase

import pytest
from nile.api.v1 import Record
from nile.processing.stream import RecordsIterator

from dmp_suite import datetime_utils as dtu
from demand_etl.layer.yt.ods.appmetrica_app_install.apps_installation_log.impl import (
    DeviceStateLog, get_event_apps_mapping_from_json_with_mapping
)
UNIX_START_DATE_STR = dtu.format_datetime(dtu.UNIX_START_DATE)


@pytest.mark.parametrize(
    'raw_value, mapping, expected_app_list',
    [
        ('{"dfid": {"apps": {"a": "true", "b": "false"}}}', {'a': 'fancy_a'}, None),
        (
                '{"dfid": {"apps": {"names": ["raw.a", "raw.b", "raw.c"]}}}',
                {'raw.a': 'a', 'raw.b': 'b', 'raw.c': 'c'},
                {'raw.a': 'a', 'raw.b': 'b', 'raw.c': 'c'},
        ),
        (
                '{"dfid": {"apps": {"names": ["raw.a", "raw.b", "raw.c", "raw.d"]}}}',
                {'raw.a': 'a', 'raw.b': 'b', 'raw.c': 'c'},
                {'raw.a': 'a', 'raw.b': 'b', 'raw.c': 'c'},
        ),
        ('{"dfid": {"apps": {"names": {"a": true, "b": true, "c": true}}}}', {'a': 'fancy_a'}, None)
    ]
)
def test_get_event_app_mapping_android(raw_value, mapping, expected_app_list):
    platform = 'android'
    assert get_event_apps_mapping_from_json_with_mapping(raw_value, platform, mapping) == expected_app_list


@pytest.mark.parametrize(
    'raw_value, mapping, expected_app_list',
    [('{"dfid": {"apps": {"a": "true", "b": "false"}}}', {'a': 'fancy_a', 'b': 'fancy_b'}, None),
     ('{"a": "true", "b": "true"}', {'a': 'fancy_a', 'b': 'fancy_b'}, {'a': 'fancy_a', 'b': 'fancy_b'}),
     (
             '{"a": "true", "b": "true", "c": "false"}',
             {'a': 'fancy_a', 'b': 'fancy_b', 'c': 'fancy_c'},
             {'a': 'fancy_a', 'b': 'fancy_b'},
     ),
     ('{"a": "true", "b": "true", "c": "false"}', {'a': 'fancy_a'},  {'a': 'fancy_a', 'b': 'b'}),
     ('{"a": "true", "b": "true", "c": "false"', {'a': 'fancy_a', 'b': 'fancy_b', 'c': 'fancy_c'},  None),
     (
             '{"dfid": {"apps": {"names": {"a": true, "b": true, "c": true}}}}',
             {'a': 'fancy_a', 'b': 'fancy_b', 'c': 'fancy_c'},
             None
     )
     ]
)
def test_get_event_app_mapping_ios(raw_value, mapping, expected_app_list):
    platform = 'ios'
    assert get_event_apps_mapping_from_json_with_mapping(raw_value, platform, mapping) == expected_app_list


class MockOutputStream(list):
    def __call__(self, *args, **kwargs):
        self.append(args[0].to_dict())


class TestNewRecords(TestCase):
    def processing_assert(self, record_list, expected_output, expected_orphaned):
        output, orphaned = MockOutputStream(), MockOutputStream()
        d = DeviceStateLog(output, orphaned)
        d.process_records(RecordsIterator(iter(record_list)))
        self.compare_two_lists(output, expected_output)
        self.compare_two_lists(orphaned, expected_orphaned)

    def test_primitive_case(self):
        records = [Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-03 02:03:31')]
        expected_result = [dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-03 02:03:31',
                                status_name='install', install_seq=1, previous_install_dict=None),
                           dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-03 02:03:31',
                                status_name='install', install_seq=1, previous_install_dict=None)
                           ]
        self.processing_assert(records, expected_result, [])

    def test_delete_case(self):
        records = [
            Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-03 02:03:31'),
            Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-06 02:06:31')]
        install_a = dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-03 02:03:31',
                         status_name='install', install_seq=1, previous_install_dict=None)
        delete_a = dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-06 02:06:31',
                        status_name='delete', install_seq=1, previous_install_dict=install_a)
        install_b = dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-06 02:06:31',
                         status_name='install', install_seq=1, previous_install_dict=None)
        expected_result = [install_a, delete_a, install_b]

        self.processing_assert(records, expected_result, [])

    def test_nondeleted_case(self):
        records = [Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-03 02:03:31'),
                   Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-05 02:06:31')]
        install_a = dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-03 02:03:31',
                         status_name='install', install_seq=1, previous_install_dict=None)
        install_b = dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-05 02:06:31',
                         status_name='install', install_seq=1, previous_install_dict=None)
        delete_a = dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-05 02:06:31',
                        status_name='delete', install_seq=1, previous_install_dict=install_a)
        expected_result = [install_a, install_b, delete_a]
        self.processing_assert(records, expected_result, [])

    def test_short_reinstall_case(self):
        records = [Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-03 02:03:31'),
                   Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-06 02:06:31'),
                   Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-07 02:06:31')]
        expected_result = [dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-03 02:03:31',
                                status_name='install', install_seq=1, previous_install_dict=None),
                           dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-06 02:06:31',
                                status_name='install', install_seq=1, previous_install_dict=None)]
        self.processing_assert(records, expected_result, [])

    def test_long_reinstall_case(self):
        records = [Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-03 02:03:31'),
                   Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-06 02:06:31'),
                   Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-10 02:06:31')]
        install_a = dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-03 02:03:31',
                         status_name='install', install_seq=1, previous_install_dict=None)
        expected_result = [install_a,
                           dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-06 02:06:31',
                                status_name='delete', install_seq=1, previous_install_dict=install_a),
                           dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-06 02:06:31',
                                status_name='install', install_seq=1, previous_install_dict=None),
                           dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-10 02:06:31',
                                status_name='install', install_seq=2, previous_install_dict=None),
                           ]
        self.processing_assert(records, expected_result, [])

    def test_previous_day_state_case(self):
        delete_a = {'app_name': 'a', 'app_raw_name': 'raw_a', 'utc_event_dttm': '2018-02-05 18:32:21',
                    'install_seq': 1, 'status_name': 'delete', 'previous_install_dict': None}
        install_b = {'app_name': 'b', 'app_raw_name': 'raw_b', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_c = {'app_name': 'c', 'app_raw_name': 'raw_c', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_d = {'app_name': 'd', 'app_raw_name': 'raw_d', 'utc_event_dttm': '2018-02-06 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        previous_day_state = [install_b, delete_a, install_c, install_d]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-09 02:06:31')
        ]
        expected_result = [
            dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='install', install_seq=2, previous_install_dict=None),
            dict(app_name='c', app_raw_name='raw_c', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='delete', install_seq=1,
                 previous_install_dict=install_c),
            dict(app_name='d', app_raw_name='raw_d', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='delete', install_seq=1,
                 previous_install_dict=install_d)
        ]

        self.processing_assert(records, expected_result, [])

    def test_same_day_different_lists_case_with_previous_day_state(self):
        delete_a = {'app_name': 'a', 'app_raw_name': 'raw_a', 'utc_event_dttm': '2018-02-05 18:32:21',
                    'install_seq': 1, 'status_name': 'delete', 'previous_install_dict': None}
        install_b = {'app_name': 'b', 'app_raw_name': 'raw_b', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_c = {'app_name': 'c', 'app_raw_name': 'raw_c', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_d = {'app_name': 'd', 'app_raw_name': 'raw_d', 'utc_event_dttm': '2018-02-06 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        previous_day_state = [delete_a, install_b, install_c, install_d]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-09 02:06:31'),
            Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-09 02:06:31'),
            Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-09 02:06:31'),
            Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-09 02:06:31'),
        ]
        expected_result = [
            dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='install', install_seq=2, previous_install_dict=None),
            dict(app_name='c', app_raw_name='raw_c', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='delete', install_seq=1,
                 previous_install_dict=install_c),
            dict(app_name='d', app_raw_name='raw_d', utc_event_dttm='2018-02-09 02:06:31',
                 status_name='delete', install_seq=1,
                 previous_install_dict=install_d),
        ]
        self.processing_assert(records, expected_result, [])

    def test_same_day_different_lists_case_without_previous_day_state(self):
        records = [Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-05 02:03:31'),
                   Record(event_apps_mapping={'raw_b': 'b'}, utc_event_dttm='2018-02-05 02:06:31'),
                   Record(event_apps_mapping={'raw_a': 'a', 'raw_b': 'b'}, utc_event_dttm='2018-02-05 02:06:31')]
        expected_result = [dict(app_name='a', app_raw_name='raw_a', utc_event_dttm='2018-02-05 02:03:31',
                                status_name='install', install_seq=1, previous_install_dict=None),
                           dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-05 02:06:31',
                                status_name='install', install_seq=1, previous_install_dict=None),
                           ]

        self.processing_assert(records, expected_result, [])

    def test_orphaned(self):
        delete_a = {'app_name': 'a', 'app_raw_name': 'raw_a', 'utc_event_dttm': '2018-02-05 18:32:21',
                    'install_seq': 1, 'status_name': 'delete', 'previous_install_dict': None,
                    'appmetrica_device_id': 'dev_0'}
        previous_day_state = [delete_a]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_a': 'a'}, utc_event_dttm='2018-02-07 02:06:31')
        ]
        expected_orphaned = [
            {field: delete_a[field] for field in delete_a if field not in ['previous_install_dict', 'app_raw_name']}
        ]
        self.processing_assert(records, [], expected_orphaned)

    def test_many_deletes(self):
        install_b = {'app_name': 'b', 'app_raw_name': 'raw_b', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_c = {'app_name': 'c', 'app_raw_name': 'raw_c', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        previous_day_state = [install_b, install_c]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_c': 'c'}, utc_event_dttm='2018-02-07 02:06:31'),
            Record(event_apps_mapping={'raw_c': 'c'}, utc_event_dttm='2018-02-07 02:07:31')
        ]
        expected_result = [dict(app_name='b', app_raw_name='raw_b', utc_event_dttm='2018-02-07 02:06:31',
                                status_name='delete', install_seq=1, previous_install_dict=install_b)
                           ]
        self.processing_assert(records, expected_result, [])

    def test_same_second_many_events_right_order(self):
        install_b = {'app_name': 'b', 'app_raw_name': 'raw_b', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_c = {'app_name': 'c', 'app_raw_name': 'raw_c', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        previous_day_state = [install_b, install_c]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_c': 'c'}, utc_event_dttm='2018-02-07 02:06:31'),
            Record(event_apps_mapping={'raw_c': 'c', 'raw_b': 'b'}, utc_event_dttm='2018-02-07 02:06:31'),
        ]
        expected_result = []
        self.processing_assert(records, expected_result, [])

    def test_same_second_many_events_reversed_order(self):
        install_b = {'app_name': 'b', 'app_raw_name': 'raw_b', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        install_c = {'app_name': 'c', 'app_raw_name': 'raw_c', 'utc_event_dttm': '2018-02-05 18:32:21',
                     'install_seq': 1, 'status_name': 'install', 'previous_install_dict': None}
        previous_day_state = [install_b, install_c]
        records = [
            Record(previous_day_state=previous_day_state, utc_event_dttm=UNIX_START_DATE_STR),
            Record(event_apps_mapping={'raw_c': 'c', 'raw_b': 'b'}, utc_event_dttm='2018-02-07 02:06:31'),
            Record(event_apps_mapping={'raw_c': 'c'}, utc_event_dttm='2018-02-07 02:06:31'),
        ]
        expected_result = []
        self.processing_assert(records, expected_result, [])


    def compare_two_lists(self, result, expected):
        def sorting_func(x):
            return x.get('app_name'), x.get('utc_event_dttm')

        self.assertListEqual(sorted(result, key=sorting_func), sorted(expected, key=sorting_func))
