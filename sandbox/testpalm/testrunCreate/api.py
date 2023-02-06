# -*- coding: utf-8 -*-
from sandbox.projects.adfox.adfox_ui.util.curl import CurlClient
import re

TESTPALM_API_HOST = 'https://testpalm-api.yandex-team.ru'
PROJ_PI = 'PI'
PROJ_ADFOX = 'ADFOX'


class TitledEntity:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title


class TestSuite(TitledEntity):
    pass


class Version(TitledEntity):
    pass


class TestCase:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.attributes = data['attributes']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_attributes(self):
        return {attribute[0]: attribute[1] for attribute in self.attributes.values()}

    def get_attribute(self, name):
        if name not in self.attributes:
            return []
        return self.attributes.get(name, [])[1]

    def get_feature(self):
        return self.get_attribute('feature')

    def get_keys(self):
        return self.get_attribute('params.key')

    def get_parent_keys(self):
        return self.get_attribute('params.parent')

    def get_tags(self):
        return self.get_attribute('tags')

    def is_unautomated(self):
        return u'not automated' in self.get_tags()

    def is_skipped(self):
        return u'skip' in self.get_tags()

    def is_needs_yml(self):
        '''
        тест нуждается в yaml-файле (требуется файл для запуска на асессорах)
        :return: bool
        '''
        return u'needs_yaml' in self.get_tags()

    def is_automation_only(self):
        '''
        только автоматизация (не запускать для асессорского тестирования)
        :return: bool
        '''
        return u'automation_only' in self.get_tags()

    def get_scope_of_work(self):
        params = self.get_attribute('params.scope_of_work')
        return params[0] if params else "1"

    def get_priority(self):
        params = self.get_attribute('priority')
        return params[0] if params else "low"

    def get_project(self):
        tags = self.get_tags()

        project = ''
        if PROJ_PI in tags:
            project = PROJ_PI
        elif PROJ_ADFOX in tags:
            project = PROJ_ADFOX

        return project


class Definition(TitledEntity):
    pass


class TestPalmApi:
    def __init__(self, token, project):
        self.curl = CurlClient(TESTPALM_API_HOST, default_headers={
            'Authorization': 'OAuth ' + token,
            'Content-Type': 'application/json'
        })
        self.project = project
        self.definitions = None

    def get_definition(self, id):
        self._load_definitions()
        return self.definitions[id]

    def get_definition_by_title(self, title):
        self._load_definitions()
        return next(x for x in self.definitions.values() if x.get_title() == title)

    def get_testcases(self):
        test_cases_raw = self._get('testcases', '?include=id,name,attributes')
        for test_case_raw in test_cases_raw:
            test_case_raw['attributes'] = {
                self.get_definition(key).get_title(): (key, value)
                for key, value in test_case_raw['attributes'].iteritems()
            }

        return map(TestCase, test_cases_raw)

    def modify_testcase(self, data):
        if data:
            self._patch('testcases', data, '/bulk')

    def create_version(self, ticket, testsuites):
        return Version(self._post('version', {
            'id': re.sub('\W', '', ticket),
            'suites': [testsuite.get_id() for testsuite in testsuites]
        }))

    def create_testsuite(self, feature, title_suffix=''):
        return TestSuite(
            self._post(
                'testsuite',
                {
                    'title': 'Release testsuit: ' + feature + title_suffix,
                    'filter': {
                        'expression': {
                            'left': {
                                'key': 'attributes.{}'.format(self.get_definition_by_title('feature').get_id()),
                                'value': feature,
                                'type': 'EQ',
                            },
                            'right': {
                                'key': 'attributes.{}'.format(self.get_definition_by_title('tags').get_id()),
                                'value': 'need run',
                                'type': 'EQ',
                            },
                            'type': 'AND'
                        }
                    }
                }
            )
        )

    def get_testsuites(self):
        return map(TestSuite, self._get('testsuite'))

    def delete_testsuites(self, ids):
        for id in ids:
            self._delete('testsuite', '/' + id)

    def create_testrun(self, testrun):
        return self._post('testrun', testrun, action='/create')[0]

    def update_testrun(self, testrun):
        self._patch('testrun', testrun)

    def order_testcases(self, testcase_ids):
        self._post('order', testcase_ids)

    def get_testrun(self, testrun_id):
        return self._get('/testrun/pi-palmsync/{}?include=testGroups'.format(testrun_id))

    def _load_definitions(self):
        if self.definitions is None:
            definitions = map(Definition, self._get('definition', '?include=id,title'))
            self.definitions = {d.get_id(): d for d in definitions}

    def _get(self, model, action=''):
        return self.curl.get('/{}/{}{}'.format(model, self.project, action)).json()

    def _post(self, model, data, action=''):
        return self.curl.post('/{}/{}{}'.format(model, self.project, action), json=data).json()

    def _patch(self, model, data, action=''):
        return self.curl.patch('/{}/{}{}'.format(model, self.project, action), json=data).json()

    def _delete(self, model, action=''):
        return self.curl.delete('/{}/{}{}'.format(model, self.project, action)).json()
