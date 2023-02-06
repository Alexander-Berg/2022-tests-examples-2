import logging
import requests
import time
import sandbox.common.types.task as sb_task
from collections import defaultdict
from datetime import datetime, timedelta

TESTENV_UI_TEMPLATE = "https://testenv.yandex-team.ru/?screen=timeline&database={}"


class TestEnvException(Exception):
    pass


class TestEnvFailedTestException(TestEnvException):
    pass


class TestEnvClient(object):
    DEFAULT_SERVER = 'https://testenv.yandex-team.ru'

    def __init__(self, server=DEFAULT_SERVER):
        self.server = server
        self.session = requests.Session()

    def _get_base_info(self, base):
        url = self.server + '/handlers/systemInfo'
        payload = {'database': base}

        response = self.session.get(url, params=payload)
        response.raise_for_status()

        try:
            response_json = response.json()
        except:
            logging.error(response.text)
            raise

        return response_json

    def get_branch(self, base):
        base_info = self._get_base_info(base)
        return '/'.join(base_info['svn_ssh_url'].strip('/').split('/')[-2:])

    def last_test_results(self, base, requested_revision=None):
        url = self.server + '/handlers/dashboards/last_results'
        payload = {'database': base}

        response = self.session.get(url, params=payload)
        response.raise_for_status()

        try:
            response_json = response.json()
        except:
            logging.error(response.text)
            raise

        return TestResults(response_json, requested_revision)

    def wait_revision_test_success(
            self,
            base,
            revision=None,
            tests_to_check=(),
            tests_to_ignore=(),
            timeout=timedelta(hours=2),
            poll_delay=10,
            bad_code_retry_limit=10,
            connection_error_retry_limit=10,
    ):
        start_time = datetime.now()
        bad_code_retry_count = 0
        connection_error_retry = 0
        while True:
            test_results = None
            try:
                test_results = self.last_test_results(base, revision)
                bad_code_retry_count = 0
                connection_error_retry = 0
            except requests.exceptions.HTTPError:
                bad_code_retry_count += 1
                if bad_code_retry_count >= bad_code_retry_limit:
                    raise TestEnvException('Too many error HTTP codes, probably retries won\'t help.')
            except requests.exceptions.ConnectionError:
                connection_error_retry += 1
                if connection_error_retry >= connection_error_retry_limit:
                    raise TestEnvException('Too many connection errors, probably retries won\'t help.')

            if test_results:
                if not revision:
                    revision = test_results.requested_revision

                failed, test = test_results.check_revision_tests_has_failures(revision, tests_to_check, tests_to_ignore)
                if failed:
                    raise TestEnvFailedTestException(
                        '{} on fire\nCheck this out: {}'.format(
                            test, TESTENV_UI_TEMPLATE.format(base)))

                if test_results.check_revision_tests_finished(revision, tests_to_check, tests_to_ignore):
                    logging.debug('Requested tests completed successfully')
                    return test_results

            time.sleep(poll_delay)

            current_time = datetime.now()
            if current_time - start_time > timeout:
                raise TestEnvException('Waiting longer than {} for build and tests. Check this out \n{}\n'.format(
                    str(timeout),
                    TESTENV_UI_TEMPLATE.format(base)
                ))


class TestResults(object):
    def __init__(self, testenv_json, requested_revision=None):
        self.revision_statuses = defaultdict(dict)
        revisions = testenv_json['revisions']

        for row in testenv_json['rows']:
            if 'in_ok_state' in row[0]:
                test_name = row[0]['name']
                for revision, test_status in zip(revisions, row[1:]):
                    if 'revision' in test_status:
                        if test_status['revision'] != revision:
                            raise TestEnvException(
                                'Wow, that was unxpected %s != %s', revision, test_status['revision'])
                    else:
                        test_status = {'status': 'NO_TEST_ENV_STATUS', 'name': test_name, 'revision': revision}

                    self.revision_statuses[revision][test_name] = test_status

        self.requested_revision = requested_revision or self.get_head_revision()

    @staticmethod
    def check_test_filters(tests_to_check, tests_to_ignore):
        if not tests_to_check and not tests_to_ignore:
            raise TestEnvException('Need tests_to_check or tests_to_ignore specified.')

    @staticmethod
    def _revision_ok(status_dict, verbose=True):
        if verbose:
            logging.debug('Checking test %s in revision %s is ok', status_dict['name'], status_dict['revision'])
        test_env_success_statuses = set(sb_task.Status.Group.SUCCEED)
        test_env_success_statuses.add('OK')
        if status_dict['status'] not in test_env_success_statuses:
            return False
        elif 'metatest_counters' in status_dict and status_dict['metatest_counters']['FAILED'] != 0:
            return False
        else:
            return True

    @staticmethod
    def _revision_not_ok(status_dict, verbose=True):
        if verbose:
            logging.debug('Checking test %s in revision %s is broken', status_dict['name'], status_dict['revision'])
        test_env_failure_statuses = set(sb_task.Status.Group.BREAK)
        test_env_failure_statuses.add('ERROR')
        test_env_failure_statuses.add(sb_task.Status.FAILURE)
        if status_dict['status'] in test_env_failure_statuses:
            return True
        elif 'metatest_counters' in status_dict and status_dict['metatest_counters']['FAILED'] != 0:
            return True
        else:
            return False

    @staticmethod
    def _revision_tests_finished(status_dict, verbose=True):
        if verbose:
            logging.debug(
                'Checking test %s in revision %s finished executing', status_dict['name'], status_dict['revision'])

        test_env_in_progress_statuses = set(
            sb_task.Status.Group.EXECUTE + sb_task.Status.Group.WAIT + sb_task.Status.Group.QUEUE)
        test_env_in_progress_statuses.update(('WAIT_PARENT', 'NO_TEST_ENV_STATUS'))
        return not status_dict['status'] in test_env_in_progress_statuses

    def _any(self, revision, check_results):
        for test, check_result in check_results.items():
            if check_result:
                logging.debug('Found test %s in required status:\n%s', test, self.revision_statuses[revision][test])
                return (True, test)
        return (False, None)

    def _all(self, revision, check_results):
        for test, check_result in check_results.items():
            if not check_result:
                logging.debug('Test %s condition check failed:\n%s', test, self.revision_statuses[revision][test])
                return (False, test)
        return (True, None)

    def _check_revision_with_condition(
            self,
            revision,
            condition,
            tests_to_check,
            tests_to_ignore,
            check_policy=_all,
            verbose=True
    ):
        TestResults.check_test_filters(tests_to_check, tests_to_ignore)
        test_condition_check_result = {}

        if not revision:
            revision = self.get_head_revision()

        for test, status_dict in self.revision_statuses[revision].items():
            if (
                    test in tests_to_ignore or
                    tests_to_check and test not in tests_to_check
            ):
                continue

            if not condition(status_dict, verbose):
                test_condition_check_result[test] = False
            else:
                test_condition_check_result[test] = True

        return check_policy(self, revision, test_condition_check_result)

    def check_revision_tests_finished(self, revision=None, tests_to_check=(), tests_to_ignore=()):
        logging.debug('Check selected tests for revision are finished')
        return self._check_revision_with_condition(
            revision, self._revision_tests_finished, tests_to_check, tests_to_ignore, verbose=False)[0]

    def check_revision_tests_ok(self, revision=None, tests_to_check=(), tests_to_ignore=()):
        return self._check_revision_with_condition(revision, self._revision_ok, tests_to_check, tests_to_ignore)

    def check_revision_tests_has_failures(self, revision=None, tests_to_check=(), tests_to_ignore=()):
        return self._check_revision_with_condition(
            revision, self._revision_not_ok, tests_to_check, tests_to_ignore, TestResults._any)

    def get_last_successfull_revision(self, tests_to_check=(), tests_to_ignore=()):
        if not self.revision_statuses:
            raise TestEnvException('No tests in database. Doesn\'t seem right to me.')

        self.check_test_filters(tests_to_check, tests_to_ignore)

        for revision in sorted(self.revision_statuses.iterkeys(), reverse=True):
            if self.check_revision_tests_ok(revision, tests_to_check, tests_to_ignore):
                return revision

        raise TestEnvException('Every single revision is on fire. I hope you already know it otherwise.')

    def get_task_id(self, revision, test_name):
        return self.revision_statuses[revision][test_name]['task_id']

    def get_head_revision(self):
        revision = max(self.revision_statuses.keys())
        logging.debug('Got head revision %s', revision)
        return revision
