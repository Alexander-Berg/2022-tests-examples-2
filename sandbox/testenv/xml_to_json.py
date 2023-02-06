#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import fnmatch
import xml.etree.ElementTree
import json
from collections import defaultdict
import logging
import string
import hashlib

from sandbox import sdk2
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import file_utils as fu
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk.channel import channel


JSON_V2_RESOURCE_FIELD_NAME = 'testenv_json_v2_resource_id'
LOGS_V2_RESOURCE_FIELD_NAME = 'testenv_logs_v2_resource_id'

TE_RESULTS_TYPE = 'TEST_ENVIRONMENT_JSON_V2'
TE_METATEST_LOGS_TYPE = 'TEST_ENVIRONMENT_METATEST_LOGS'


class TEST_ENVIRONMENT_JSON_V2_OLD(sdk2.resource.AbstractResource):
    """
        Файл с результатами метатеста, предназначенный для передачи в Test Environment
    """
    auto_backup = True
    share = True


def on_enqueue(task, opt=False, output_file_name='result2.json'):
    """
    Create resources for testenv metatest results
    """
    if task.ctx['tests_type'] == 'functional' and not opt:
        res_type = 'TEST_ENVIRONMENT_JSON_V2_OLD'
    else:
        res_type = TE_RESULTS_TYPE

    task.ctx[JSON_V2_RESOURCE_FIELD_NAME] = task.create_resource(
        task.descr,
        output_file_name,
        res_type,
        arch='any',
    ).id

    task.ctx[LOGS_V2_RESOURCE_FIELD_NAME] = task.create_resource(
        task.descr,
        'metatest_logs_v2',
        TE_METATEST_LOGS_TYPE,
        arch='any',
    ).id


def find_and_convert(task, path):
    """
    Convert xml results to json result (named as by resource name)
    :param path: source path to search for *.xml results
    """
    logging.info('find_and_convert at `%s`', path)

    xml_files = _find_files(path, '*.xml')
    eh.verify(xml_files, 'Cannot find any xml files in dir `{}`'.format(path))

    json_v2_resource = channel.sandbox.get_resource(task.ctx[JSON_V2_RESOURCE_FIELD_NAME])
    logs_v2_resource = channel.sandbox.get_resource(task.ctx[LOGS_V2_RESOURCE_FIELD_NAME])

    paths.make_folder(logs_v2_resource.path)
    fu.write_file(os.path.join(logs_v2_resource.path, 'empty.txt'), 'Just an empty file')

    testenv_job = task.ctx.get('testenv_job')
    convert_v2(xml_files, None, json_v2_resource.path, logs_v2_resource.path, logs_v2_resource.id, testenv_job)


def _find_files(directory, pattern):
    result = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                result.append(filename)
    return result


def convert_v2(
    xml_files,
    owners,
    output_json_v2_file,
    logs_v2_resource_path,
    logs_v2_resource_id,
    testenv_job,
    ts_properties=False,
):
    convertor_v2 = ConvertorV2(owners, logs_v2_resource_path, logs_v2_resource_id, testenv_job)
    if ts_properties:
        convertor_v2.include_properties()
    json_v2_str = convertor_v2.convert(xml_files)
    fu.write_file(output_json_v2_file, json_v2_str)


class Convertor(object):
    def __init__(self, owners, logs_resource_path, logs_resource_id):
        self.owners = owners
        self.logs_resource_path = logs_resource_path
        self.logs_resource_id = logs_resource_id
        self.ts_properties = False

    def include_properties(self):
        self.ts_properties = True

    def convert(self, xml_files):
        groups = []
        js_result = {'groups': groups}

        for file_name in xml_files:
            logging.info('parsing file: "%s"' % file_name)

            xml_string = open(file_name).read()
            self._parse_single_xml(xml_string, groups)

        return json.dumps(js_result, indent=4)

    def _parse_single_xml(self, xml_string, groups):
        testsuite_element_list = xml.etree.ElementTree.fromstring(xml_string)

        if testsuite_element_list.tag == 'testsuite':
            group = self._process_testsuite_element(testsuite_element_list)
            groups.append(group)
        else:
            for child_element in testsuite_element_list:
                if child_element.tag != 'testsuite':
                    raise Exception('unknown element: "%s". expected testsuite element' % child_element.tag)
                group = self._process_testsuite_element(child_element)
                groups.append(group)

    def _process_testsuite_element(self, testsuite_element):
        name = testsuite_element.attrib['name']
        logging.info('testsuite: "%s"' % name)

        tests = []

        group = {
            'name': name,
            'tests': tests
        }

        t = _string_to_float(testsuite_element.attrib.get('time'))
        if t is not None:
            group['time'] = t

        for child_element in testsuite_element:
            if child_element.tag != 'testcase':
                continue
            test_result = self._process_testcase_element(name, child_element)
            tests.append(test_result)

        return group

    def _process_testcase_element(self, testsuite_name, testcase_element):
        name = testcase_element.attrib['name']
        logging.info('testcase: "%s"' % name)

        logs = []

        test_result = {
            'name': name,
            'source_path': ' '
        }

        if self.owners:
            test_result['owners'] = ','.join(self.owners)

        t = _string_to_float(testcase_element.attrib.get('time'))
        if t is not None:
            test_result['time'] = t

        status = self._group_and_process_child_elements(testsuite_name, name, testcase_element, logs)
        test_result['status'] = status

        if logs:
            test_result['logs'] = logs

        return test_result

    def _group_and_process_child_elements(self, testsuite_name, testcase_name, testcase_element, logs):
        status = 'OK'

        elements = defaultdict(list)

        for child_element in testcase_element:
            status = self._process_testcase_child_element(child_element, status)
            elements[child_element.tag].append(child_element)

        self._create_logs(testsuite_name, testcase_name, elements, logs)

        return status

    def _process_testcase_child_element(self, element, status):
        if element.tag == 'skipped':
            status = 'SKIPPED'
        elif element.tag == 'failure' or \
                element.tag == 'error':
            if not element.text and not element.attrib.get('message'):
                raise ValueError(
                    '<failure> element without text: {}'.format(
                        xml.etree.ElementTree.tostring(element)
                    )
                )
            status = 'FAILED'
        elif element.tag == 'system-out':
            pass
        elif element.tag == 'system-err':
            pass
        else:
            raise Exception('unknown xml element: "%s"' % element.tag)

        return status

    def _create_logs(self, testsuite_name, testcase_name, grouped_elements, logs):
        for tag_name, elements in grouped_elements.iteritems():
            file_content = self._get_log_file_content(elements)
            if file_content:
                log = self._create_log(testsuite_name, testcase_name, tag_name, file_content)
                logs.append(log)

    def _get_log_file_content(self, elements):
        file_content = []

        for element in elements:
            message = element.attrib.get('message')
            if message:
                file_content.append(message.strip())

            text = element.text
            if text:
                file_content.append(text.strip())

        return ('\n' + '-' * 100 + '\n\n').join(file_content)

    def _create_log(self, testsuite_name, testcase_name, tag_name, file_content):
        filename_parts = []
        for filename_part in (testsuite_name, testcase_name, tag_name):
            if len(filename_part) > 50:
                filename_parts.append(hashlib.md5(filename_part.encode('utf-8')).hexdigest())
            else:
                filename_parts.append(filename_part)
        file_name = '%s_%s_%s.txt' % (filename_parts[0], filename_parts[1], filename_parts[2])
        file_name = ''.join(x for x in file_name if x in _valid_chars)
        logging.info('log file name: "%s"' % file_name)

        file_full_path = os.path.join(self.logs_resource_path, file_name)

        with codecs.open(file_full_path, 'wt', encoding='utf-8') as file:
            file.write(file_content)

        return {
            'name': tag_name,
            'resource_id': self.logs_resource_id,
            'relative_path': file_name
        }


class ConvertorV2(Convertor):
    def __init__(self, owners, logs_resource_path, logs_resource_id, testenv_job):
        super(ConvertorV2, self).__init__(owners, logs_resource_path, logs_resource_id)
        self.testenv_job = testenv_job

    def convert(self, xml_files):
        results = []
        js_result = {'results': results}

        for file_name in xml_files:
            logging.info('parsing file: "%s"' % file_name)

            with open(file_name) as xml_file:
                xml_string = xml_file.read()
            self._parse_single_xml(xml_string, results)

        return json.dumps(js_result, indent=4)

    def _parse_single_xml(self, xml_string, results):
        testsuite_element_list = xml.etree.ElementTree.fromstring(xml_string)

        if testsuite_element_list.tag == 'testsuite':
            testsuite_results = self._process_testsuite_element(testsuite_element_list)
            results.extend(testsuite_results)
        else:
            for child_element in testsuite_element_list:
                if child_element.tag != 'testsuite':
                    raise Exception('unknown element: "%s". expected testsuite element' % child_element.tag)
                testsuite_results = self._process_testsuite_element(child_element)
                results.extend(testsuite_results)

    def _process_properties_element(self, properties):
        ret = {}
        for p in properties:
            name = p.attrib['name']
            value = p.attrib['value']
            ret[name] = value
        return ret

    def _gen_properties_str(self, testsuite_element):
        properties = {}
        for child_element in testsuite_element:
            if child_element.tag == 'properties':
                p = self._process_properties_element(child_element)
                properties.update(p)

        if not len(properties):
            return ""

        p_str = ""
        sep = ";"
        for k in properties:
            p_str += "%s%s=%s" % (sep, k, properties[k])
            sep = ","
        return p_str

    def _process_testsuite_element(self, testsuite_element):
        name = testsuite_element.attrib['name']
        logging.info('testsuite: "%s"' % name)
        xattr_name = ""
        if self.ts_properties:
            xattr_name = self._gen_properties_str(testsuite_element)
            name += "-" + hashlib.md5(xattr_name.encode('utf-8')).hexdigest()[0:7]
        tests = []

        for child_element in testsuite_element:
            if child_element.tag != 'testcase':
                continue
            test_result = self._process_testcase_element(name, child_element, xattr_name)
            tests.append(test_result)

        return tests

    def _process_testcase_element(self, testsuite_name, testcase_element, xattr_name=""):
        testcase_name = testcase_element.attrib['name']
        testcase_classname = testcase_element.attrib.get('classname', '')
        if self.testenv_job:
            hash_fields = (
                self.testenv_job.encode('utf-8'),
                testsuite_name.encode('utf-8'),
                testcase_name.encode('utf-8'),
                testcase_classname.encode('utf-8')
            )
        else:
            hash_fields = (
                testsuite_name.encode('utf-8'),
                testcase_name.encode('utf-8'),
                testcase_classname.encode('utf-8'),
            )
        if len(testcase_name) > 255:
            testcase_name = testcase_name[:252] + '...'
        name = testcase_classname if testcase_classname else testsuite_name
        result = {
            'id': hashlib.md5('\x00'.join(hash_fields)).hexdigest(),
            'type': 'test',
            'name': name + xattr_name,
            'subtest_name': testcase_name,
            'duration': _string_to_float(testcase_element.attrib.get('time')),
            'owners': {
                'logins': [],
                'groups': []
            },
            'toolchain': 'linux',
        }
        logs = []
        status = self._group_and_process_child_elements(testsuite_name, testcase_name, testcase_element, logs)
        result['status'] = status
        if status == 'FAILED':
            result['error_type'] = 'REGULAR'
        links = defaultdict(list)
        for log in logs:
            links[log['name']].append(
                'http://proxy.sandbox.yandex-team.ru/%s/%s' % (log['resource_id'], log['relative_path'])
            )
        result['links'] = links
        return result


def _string_to_float(string):
    if string:
        return float(string)
    else:
        return None


_valid_chars = frozenset("-_.() %s%s" % (string.ascii_letters, string.digits))
