#!/skynet/python/bin/python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
import json
import itertools
import urlparse

import xml_to_json


class TestenvTestCase(unittest.TestCase):
    def test_xml_to_json_converter_v2(self):
        tempdir = tempfile.mkdtemp(prefix='testenv')

        def test(xml_filename, json_filename):
            xml_path = os.path.abspath(xml_filename)
            json_out_path = os.path.join(tempdir, json_filename)
            xml_to_json.convert_v2([xml_path], ['owner1', 'owner2'], json_out_path, tempdir, 123456, None)
            print(json_out_path)
            with open(json_out_path) as j:
                json_out = json.load(j)
            with open(os.path.abspath(json_filename)) as j:
                json_reference = json.load(j)
            self.assertEqual(json_out, json_reference)

        test('file1.xml', 'file3.json')
        test('file2.xml', 'file4.json')
        test('kvm-xfstests-results.xml', 'kvm-xfstests-results.json')
        test('kvm-xfstests-results2.xml', 'kvm-xfstests-results2.json')

    def test_equal_converters(self):
        def test(json_path_1, json_path_2):
            with open(os.path.abspath(json_path_1)) as f:
                json_1 = json.load(f)
            with open(os.path.abspath(json_path_2)) as f:
                json_2 = json.load(f)

            def get_test_1(json_1):
                for group in json_1['groups']:
                    for test in group['tests']:
                        yield test

            def get_test_2(json_2):
                for result in json_2['results']:
                    yield result

            for test_1, test_2 in itertools.izip_longest(tuple(get_test_1(json_1)), tuple(get_test_2(json_2))):
                self.assertEqual(test_1.get('status'), test_2.get('status'))
                self.assertEqual(test_1.get('name'), test_2.get('subtest_name'))
                self.assertEqual(test_1.get('time'), test_2.get('duration'))

                def get_log_1(test_1):
                    for log in test_1.get('logs', ()):
                        yield log['name'], log['resource_id'], log['relative_path']

                def get_log_2(test_2):
                    for name, links in test_2.get('links', {}).iteritems():
                        for link in links:
                            parsed_url = urlparse.urlparse(link)
                            second_slash_index = parsed_url.path.find('/', 1)
                            resource_relative_path = parsed_url.path[second_slash_index+1:]
                            resource_id = int(parsed_url.path[1:second_slash_index])
                            yield name, resource_id, resource_relative_path

                for log_1, log_2 in itertools.izip_longest(tuple(get_log_1(test_1)), tuple(get_log_2(test_2))):
                    self.assertEqual(log_1, log_2)
                for attribute in test_1:
                    if attribute in ('source_path', 'time', 'logs'):
                        continue
                    self.assertIn(attribute, test_2)

        test('file1.json', 'file3.json')
        test('file2.json', 'file4.json')

    def test_truncate_subtest_name(self):
        convertor = xml_to_json.ConvertorV2(None, None, None, None)

        class EtreeMock(object):
            def __init__(self, **kwargs):
                self.attrib = kwargs

            def __getitem__(self, index):
                raise IndexError()

        mock_255 = EtreeMock(name='a' * 255)
        result = convertor._process_testcase_element('', mock_255)
        self.assertTrue(len(result['subtest_name']) == 255)
        mock_256 = EtreeMock(name='a' * 256)
        result = convertor._process_testcase_element('', mock_256)
        self.assertTrue(len(result['subtest_name']) == 255)
        self.assertTrue(result['subtest_name'].endswith('...'))


if __name__ == "__main__":
    unittest.main()
