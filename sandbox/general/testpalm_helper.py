import json
import logging
import re
import urlparse
import uuid
from collections import defaultdict

import sandbox
from sandbox.common.utils import Enum
from sandbox.projects.browser.autotests.regression.conf import DEFAULT_TESTCASE_ESTIMATE, MAX_TESTCASE_STAT_ESTIMATE
from sandbox.projects.browser.autotests_qa_tools.common import pretty_time_delta
from sandbox.projects.common import decorators

TESTPALM_BASE_URL = 'https://testpalm.yandex-team.ru'


class TestpalmClientWrapper(object):
    def __init__(self, testpalm_client):
        self._client = testpalm_client

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._client, attr)

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_definitions(self, project):
        definitions = self._client.get_definitions(project)
        return definitions

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def definition_map(self, project):
        definitions = self._client.get_definitions(project, params={'include': 'id,title'})
        return {v['id']: v['title'] for v in definitions}

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_testsuite_cases(self, suite, project, include_fields=None):
        testcases = self._client.get_testsuite_cases(suite, project, params={'include': ','.join(include_fields)})
        return [
            TestCase(case, project, self.definition_map(project))
            for case in testcases
        ]

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_cases(self, project, include_fields=None):
        testcases = self._client.get_testcases(project, params={'include': ','.join(include_fields)})
        return [
            TestCase(case, project, self.definition_map(project))
            for case in testcases
        ]

    @sandbox.common.utils.singleton
    def get_case(self, project, case_id, include_fields=None):
        expression = {'type': 'EQ', 'key': 'id', 'value': case_id}

        testcases = self._client.get_testcases(
            project,
            params={'include': ','.join(include_fields),
                    'expression': json.dumps(expression),
                    }
        )
        if not testcases:
            return None
        else:
            return TestCase(testcases[0], project, self.definition_map(project))

    @sandbox.common.utils.singleton
    @decorators.retries(10, delay=1, backoff=2)
    def create_unique_version(self, project, version, description=None):
        """
        :return: new version. if provided version exists a number will be appended in the end
        """

        def unique_version(existing, version_prefix):
            suffix = 1
            while '{}_{}'.format(version_prefix, suffix) in existing:
                suffix += 1
            return '{}_{}'.format(version_prefix, suffix)

        from testpalm_api_client.entities.version.version import Version
        version = re.sub(r'[^\w.]', '_', version)
        existing_versions = self._client.get_versions(project, params={'include': 'id'})
        version = unique_version({v['id'] for v in existing_versions}, version)
        self._client.create_version(
            project,
            Version(version, version, description=description))
        return version

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_or_create_version(self, version_id, project, description=None):
        from testpalm_api_client.entities.version.version import Version
        version = re.sub(r'[^\w.]', '_', version_id)
        existing_versions = self._client.get_versions(project, params={'include': 'id'})
        if version not in {v['id'] for v in existing_versions}:
            self._client.create_version(project, Version(version, version, description=description))
        return version

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_testrun(self, testrun, project, include_fields=None):
        return TestRun(
            self._client.get_testrun_info(
                testrun, project, params={'include': ','.join(include_fields)} if include_fields else None
            ), project, self.definition_map(project)
        )

    def _create_test_run(self, project, testrun_info, params):
        our_run_id = str(uuid.uuid4())
        uuid_dict = {'key': 'uuid', 'value': our_run_id}
        if testrun_info['properties'] is None:
            testrun_info['properties'] = []
        testrun_info['properties'].append(uuid_dict)

        @decorators.retries(10, delay=1, backoff=2)
        def retry(project, testrun_info):
            logging.debug('Retry creating run #%s', our_run_id)
            existing_runs = self._client.get_testruns(
                project, params={'include': 'id,properties', 'createdTimeSort': 'desc', 'limit': 100})
            this_run = next((run for run in existing_runs if uuid_dict in run['properties']), None)
            if this_run:
                result = this_run['id']
            else:
                result = self._client.create_testrun(project=project, testrun=testrun_info, params=params)[0]['id']
            logging.debug('Created run #%s', our_run_id)
            return result

        try:
            logging.debug('Creating run #%s', our_run_id)
            res = self._client.create_testrun(project=project, testrun=testrun_info, params=params)[0]['id']
            logging.debug('Created run #%s', our_run_id)
            return res
        except:
            return retry(project, testrun_info)

    def _get_run_test_groups(self, cases, cases_statuses):

        groups = {}
        if not cases_statuses:
            cases_statuses = defaultdict(lambda: CaseStatuses.CREATED)

        # now = int(time.time()) * 1000
        for case in cases:
            case_id = case['id'] if isinstance(case, dict) else case.id
            _case_group = case.get('case_grouping_fields') if isinstance(case, dict) else None
            case_group = tuple(_case_group or [])
            status = cases_statuses[case_id]
            groups.setdefault(case_group, []).append(
                {
                    'status': status.upper(), 'testCase': {'id': case_id},
                    # 'startedTime': now if status != CaseStatuses.CREATED else 0,
                    # 'finishedTime': now if status != CaseStatuses.CREATED else 0
                }
            )

        max_groupping_fields_count = max(len(i) for i in groups.keys())
        result = []
        for _path in sorted(groups.keys()):
            _result_path = [_path[i] if len(_path) > i else None for i in range(0, max_groupping_fields_count)]
            result.append(
                {
                    'path': list(_result_path),
                    'testCases': groups[_path],
                    'defaultOrder': True,
                }
            )
        return result

    def create_testrun(self, project, title, cases, version=None, ticket=None,
                       current_environment=None, properties=None, cases_statuses=None, tags=None,
                       include_only_existed=True):
        """
        :param include_only_existed (bool): analog of import in old api.
         If true you can pass only ids of cases and testpalm will do the rest.
         If false than whole testcases body is needed.
        :param project (str):
        :param title (str):
        :param cases (list):  TestCase objects or dicts. dicts must contain 'id' element
        :param version (str):
        :param ticket (str): QUEUE-1234
        :param current_environment:
        :param properties (dict):
        :param cases_statuses (dict): id : status
        :return: (str) id of created run
        """
        properties = properties or {}
        test_groups = self._get_run_test_groups(cases, cases_statuses)
        testrun_info = {
            'testGroups': test_groups,
            'title': title,
            'properties': [{'key': k, 'value': v} for k, v in properties.iteritems()],
            'tags': tags or [],
        }
        if version:
            testrun_info['version'] = version
        if current_environment:
            testrun_info['currentEnvironment'] = {
                'title': current_environment,
            }
        if ticket:
            testrun_info['parentIssue'] = {'id': ticket,
                                           'trackerId': 'Startrek',
                                           'groupId': ticket.split('-')[0]}

        # FIXME This and commented lines above were used as crunch for testpalm to correctly show
        # runs created already finished. But now it results in 500 response "startedTime can't be less then createdTime"

        # if cases_statuses:
        #     testrun_info['startedTime'] = now
        params = {}
        if include_only_existed:
            params['includeOnlyExisted'] = 1
        return self._create_test_run(project=project, testrun_info=testrun_info, params=params)

    @sandbox.common.utils.singleton
    @decorators.retries(5, delay=1, backoff=2)
    def get_testsuite(self, id, project):
        return TestSuite(self._client.get_testsuite(id, project=project),
                         project, self.definition_map(project))

    def update_cases_attribute(self, cases, attributes_values=None, add_tags=None):
        projects = {}
        for case in cases:
            if attributes_values:
                for attr_name, value in attributes_values.iteritems():
                    attr_id = case.get_definition_map_id(attr_name)
                    if value is not None:
                        case.case_data["attributes"][attr_id] = value
                    else:
                        case.case_data["attributes"].pop(attr_id, None)

            if add_tags:
                tags_attr_id = case.get_definition_map_id('Tags')
                tags = case.case_data["attributes"].get(tags_attr_id, [])
                case.case_data["attributes"][tags_attr_id] = list(set(tags).union(set(add_tags)))

            projects.setdefault(case.project, []).append(case.case_data)

        for project, project_cases in projects.iteritems():
            self.update_project_cases(project_cases, project)

    @decorators.retries(5, delay=1, backoff=2)
    def update_project_cases(self, cases_data, project):
        self._client.update_testcases(cases_data, project)


class TestCase(object):
    def __init__(self, data, project, definition_map):
        self.project = project
        self.definition_map = definition_map
        self.case_data = data
        for key in data:
            setattr(self, key, data[key])

    @sandbox.common.utils.singleton_property
    def mapped_attributes(self):
        return {self.definition_map[k]: v for k, v in self.attributes.iteritems()
                if k in self.definition_map}

    @sandbox.common.utils.singleton
    def get_definition_map_id(self, name):
        attr_id = None
        for _id in self.definition_map:
            if self.definition_map[_id] == name:
                attr_id = _id
                break
        return attr_id

    @property
    def component(self):
        return self.mapped_attributes['Component'][0]

    @property
    def oses(self):
        return self.mapped_attributes.get('OS', [])

    @property
    def url(self):
        return testcase_url(self.id, self.project)

    @property
    def estimate(self):
        return getattr(self, 'estimatedTime', 0) or DEFAULT_TESTCASE_ESTIMATE

    @property
    def fixed_average_duration(self):
        return max(min(self.stats['avgRunDuration'], MAX_TESTCASE_STAT_ESTIMATE), DEFAULT_TESTCASE_ESTIMATE)

    @property
    def automated_oses(self):
        return self.mapped_attributes.get('Automated OS', [])

    @property
    def priority(self):
        return self.mapped_attributes.get('Priority', [])


class CaseStatuses(Enum):
    Enum.preserve_order()

    STARTED = 'started'
    FAILED = 'failed'
    KNOWN_BUG = 'knownbug'
    BROKEN = 'broken'
    BLOCKED = 'blocked'
    SKIPPED = 'skipped'
    PASSED = 'passed'
    CREATED = 'created'


CASE_STATUS_COLORS = {
    CaseStatuses.PASSED: '#449d44',
    CaseStatuses.FAILED: '#c9302c',
    CaseStatuses.KNOWN_BUG: '#eb8f95',
    CaseStatuses.BROKEN: '#ec971f',
    CaseStatuses.BLOCKED: '#790000',
    CaseStatuses.CREATED: '#f5f5f5',
    CaseStatuses.SKIPPED: '#999999',
    CaseStatuses.STARTED: '#337ab7'
}

CASE_TEXT_COLORS = defaultdict(lambda: 'white', {CaseStatuses.CREATED: 'black'})


def testcase_url(id, project):
    return urlparse.urljoin(TESTPALM_BASE_URL, 'testcase/{}-{}'.format(project, id))


def testsuite_url(id, project):
    return urlparse.urljoin(TESTPALM_BASE_URL, '{}/testsuite/{}'.format(project, id))


def testrun_url(id, project):
    return urlparse.urljoin(TESTPALM_BASE_URL, '{}/testrun/{}'.format(project, id))


def version_url(project, version):
    return urlparse.urljoin(TESTPALM_BASE_URL, '{}/version/{}'.format(project, version))


class TestSuite(object):
    def __init__(self, data, project, definition_map):
        self.project = project
        self.definition_map = definition_map
        for key in data:
            setattr(self, key, data[key])

    def pretty_str(self):
        return u'<a href="{url}">{title}</a>'.format(url=testsuite_url(self.id, self.project), title=self.title)


class TestRun(object):
    def __init__(self, data, project, definition_map):
        self.project = project
        self.definition_map = definition_map
        for key in data:
            setattr(self, key, data[key])

    @property
    def estimate_with_default(self):
        return self.estimate['estimatedTime'] + self.estimate[
            'testcasesWithoutEstimatedTime'] * DEFAULT_TESTCASE_ESTIMATE

    @sandbox.common.utils.singleton_property
    def testcases(self):
        return [
            TestCase(case_info['testCase'], self.project, self.definition_map)
            for group in self.testGroups
            for case_info in group['testCases']
        ]

    @sandbox.common.utils.singleton_property
    def testcase_statuses(self):
        return {
            case_info['testCase']['id']: case_info['status']
            for group in self.testGroups
            for case_info in group['testCases']
        }

    @property
    def average_duration_with_default(self):
        return self.estimate['avgDuration'] + self.estimate['testcasesWithoutRuns'] * DEFAULT_TESTCASE_ESTIMATE

    @sandbox.common.utils.singleton_property
    def fixed_average_duration(self):
        return sum(case.fixed_average_duration for case in self.testcases)

    @property
    def statistic(self):
        return {k: v for k, v in self.resolution['counter'].iteritems() if k != 'total'}

    @property
    def url(self):
        return testrun_url(self.id, self.project)

    @property
    def finished(self):
        return (self.archived or
                self.statistic[CaseStatuses.CREATED] + self.statistic[CaseStatuses.STARTED] == 0)

    def pretty_str(self, print_case_statuses=False, show_estimate=False):
        def pretty_status(status, color, cases_numb):
            return u'<span style="background-color: {color}; color:{text_color}">&nbsp;{cases_numb}&nbsp;</span>'.format(
                color=color, cases_numb=cases_numb, text_color=CASE_TEXT_COLORS[status]
            )

        return ' '.join(filter(None, (
            u'<a href="{url}">{title}</a>'.format(url=testrun_url(self.id, self.project), title=self.title),
            pretty_time_delta(self.estimate_with_default) if show_estimate else None,
            ''.join(pretty_status(status, CASE_STATUS_COLORS[status], self.statistic[status])
                    for status in CaseStatuses if self.statistic[status] > 0) if print_case_statuses else None
        )))

    def get_propetry(self, name):
        for _p in self.properties:
            if _p["key"] == name:
                return _p["value"]
        return None
