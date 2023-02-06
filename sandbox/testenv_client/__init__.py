"""
Helpers for easy usage of TestEnv web server handlers.

Intended basically for release-machine purposes.
"""

import json
import uuid
import logging
import posixpath
import re
import requests
from six.moves.urllib import parse
from requests import exceptions as requests_exceptions

from sandbox.projects.common import decorators
from sandbox.projects.common import requests_wrapper
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.common.testenv_client import api_client as te_api_client


logger = logging.getLogger(__name__)
RETRIABLE_EXCEPTIONS = (
    requests_wrapper.ServerError,
    requests_exceptions.Timeout,
    requests_exceptions.ConnectionError,
    requests_exceptions.ChunkedEncodingError,
)


class TEClient(object):

    TE_DIFF_SCREEN = "?screen=problem&database={te_db}&id={diff_id}"
    TE_REV_DIFF_SCREEN = "?screen=revision_problems&database={te_db}&revision={rev}"

    SYSTEM_INFO_HANDLER = "handlers/systemInfo"
    AUX_RUNS = "handlers/grids/auxiliaryRuns"
    PROBLEMS_HANDLER = "handlers/grids/problems?database={db}&start=0"
    CLONE_DB_HANDLER = "handlers/cloneDb"
    CLEANUP_DB_HANDLER = "handlers/cleanupDb"
    ADD_DB_OWNER_HANDLER = "handlers/addDbOwner"
    STOP_JOB_HANDLER = "handlers/stopTest"
    CREATE_DB_HANDLER = "handlers/createDb"
    GET_TESTS_HANDLER = "handlers/getTests"
    DELETE_TEST_HANDLER = "handlers/deleteTest"
    ADD_TEST_HANDLER = "handlers/addTests"
    SET_DB_OPTION_HANDLER = "handlers/setDbOption"
    START_DB_HANDLER = "handlers/startdb"
    STOP_DB_HANDLER = "handlers/stopdb"
    SWITCH_OWNER_PARAM = "handlers/switchOwnerParam"
    GET_LAST_GOOD_REVISION_HANDLER = (
        "handlers/get_last_good_revision?database={db}&ignore_release_jobs={ignore_release_jobs}"
    )
    GET_LAST_SANDBOX_TASK_IDS_HANDLER = "handlers/get_last_sandbox_task_ids"
    GET_ALL_SANDBOX_TASK_IDS_HANDLER = "handlers/get_all_sandbox_task_ids"
    PRE_RELEASE_HANDLER = "handlers/release/pre_release"
    PRE_RELEASE_ACTION_HANDLER = "handlers/release/pre_release_action"
    TEST_RESULTS_HANDLER = "handlers/grids/testResults"
    CHECKED_INTERVALS_HANDLER = "handlers/grids/checkedIntervals"  # Internal API, use with care!
    LAST_RESULTS_HANDLER = "handlers/dashboards/last_results"
    COMMIT_MARKERS_HANDLER = "handlers/commitMarkers"
    TEST_DIFFS_HANDLER = "handlers/grids/testDiffs"
    LAST_SVN_REVISIONS = "handlers/grids/lastSvnRevisions"
    RESOURCES_HANDLER = "handlers/grids/resources"

    def __init__(self, oauth_token=None):
        """
        Initialize client.

        :param oauth_token: OAuth token that will be used for all methods requiring authorization.
        """
        if oauth_token is None:
            logging.warning('TEClient: OAuth token is not set, authorized calls will fail')
        self._oauth_token = oauth_token

    @classmethod
    def testenv_database_exists(cls, database_name):
        logging.info('Check database `%s` existence', database_name)
        response = cls.get_sys_info(database_name)
        if response.status_code == 200:
            logging.info('Database `%s` exists', database_name)
            return True

        if response.status_code == 404:
            logging.warning('Database `%s` was not found', database_name)
            return False

        logging.error(
            '[testenv_database_exists]: status code: %s, response:\n%s\n\n',
            response.status_code, response.text,
        )
        raise Exception('Invalid response from TestEnv system info handler (see logs for details). ')

    @classmethod
    def te_diff_screen(cls, te_db, diff_id, wiki=True):
        link = rm_const.Urls.TESTENV + cls.TE_DIFF_SCREEN.format(te_db=te_db, diff_id=diff_id)
        if wiki:
            return "(({} {}))".format(link, diff_id)
        return link

    @decorators.retries(3, delay=5, exceptions=(requests_wrapper.ServerError, ))
    def set_db_option(self, database_name, option_name, enable=True):
        url = rm_const.Urls.TESTENV + self.SET_DB_OPTION_HANDLER
        response = requests_wrapper.get_r(
            url,
            params={"database": database_name, "option": option_name, "enable": "True" if enable else ""},
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
        )
        requests_wrapper.check_status_code(response)

    @decorators.retries(3, delay=5, exceptions=(requests_wrapper.ServerError, ))
    def switch_owner_param_in_db(self, database_name, login, param_name):
        url = rm_const.Urls.TESTENV + self.SWITCH_OWNER_PARAM
        response = requests_wrapper.get_r(
            url,
            params={"database": database_name, "login": login, "param": param_name},
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
        )
        requests_wrapper.check_status_code(response)

    @classmethod
    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_resources(cls, database_name):
        url = rm_const.Urls.TESTENV + cls.RESOURCES_HANDLER
        response = requests_wrapper.get(url, params={'database': database_name})
        requests_wrapper.check_status_code(response)
        return response.json()['rows']

    @classmethod
    def te_rev_diff_screen(cls, te_db, rev):
        return rm_const.Urls.TESTENV + cls.TE_REV_DIFF_SCREEN.format(te_db=te_db, rev=rev)

    @classmethod
    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_te_problems(cls, te_db, unresolved_only=False):
        url = rm_const.Urls.TESTENV + cls.PROBLEMS_HANDLER.format(db=te_db)
        if unresolved_only:
            url += "&only_unresolved=1"
        logger.info("TE problems url: %s", url)
        response = requests_wrapper.get(url, verify=False)
        requests_wrapper.check_status_code(response)
        return response.json()

    @classmethod
    @decorators.retries(3, delay=10, backoff=1, exceptions=RETRIABLE_EXCEPTIONS)
    def get_all_jobs(cls, db=None):
        url = rm_const.Urls.TESTENV + "handlers/grids/tests"
        logger.info("RM jobs url: %s", url)
        if db:
            response = requests_wrapper.post(url, data={"database": db})
        else:
            response = requests_wrapper.get(url)
        requests_wrapper.check_status_code(response)
        return response.json()["rows"]

    @classmethod
    def get_jobs(cls, database_name, exclude_jobs=(), only_turned_on=True):
        def filter_job(job):
            return all([
                job["name"] not in exclude_jobs,
                job["is_on"] or not only_turned_on,
            ])
        jobs = cls.get_all_jobs(database_name)
        return filter(filter_job, jobs)

    @decorators.retries(3, delay=5, exceptions=(requests_wrapper.ServerError, ))
    def stop_job(self, db, job_name, comment="Stop from sandbox"):
        url = rm_const.Urls.TESTENV + self.STOP_JOB_HANDLER
        response = requests_wrapper.get(
            url,
            params={
                "database": db,
                "test_name": job_name,
                "comment": comment,
            },
            headers={"Authorization": "OAuth {}".format(self._oauth_token)}
        )
        requests_wrapper.check_status_code(response)
        logging.info("Job %s was stopped successfully", job_name)

    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_aux_runs(self, db):
        url = rm_const.Urls.TESTENV + self.AUX_RUNS
        response = requests_wrapper.post(
            url, params={"database": db}, headers={"Authorization": "OAuth {}".format(self._oauth_token)}
        )
        if response.status_code == 500:
            logging.warning("Response [500]: %s", response.text)
        requests_wrapper.check_status_code(response)
        aux_runs = response.json()["rows"]
        logging.debug("Aux runs for %s db:\n%s", db, json.dumps(aux_runs, indent=2))
        return aux_runs

    @classmethod
    def get_flaky_jobs(cls, db):
        url = rm_const.Urls.TESTENV + "handlers/grids/metatestsFlaky?database={}&show_all=true".format(db)
        return requests_wrapper.get(url, timeout=40).json()["rows"]

    @classmethod
    @decorators.retries(3, delay=30)
    def clone_db(cls, params, return_bool=True):
        """Clone TestEnv database (aka project)."""
        return cls.clone_db_no_retries(params, return_bool=return_bool)

    @classmethod
    def clone_db_no_retries(cls, params, return_bool=True, timeout=180, perform_cleanup_on_failure=True):

        response = cls._post(
            action="clone_db",
            url=rm_const.Urls.TESTENV + cls.CLONE_DB_HANDLER,
            params=params,
            timeout=timeout,
        )

        clone_success = response.status_code == 200

        if not clone_success:
            logger.info("Database cloning failed, try to cleanup")

            if perform_cleanup_on_failure:
                cls.cleanup_db({"drop_database_names": params["new_db_name"]})

        return clone_success if return_bool else response

    @decorators.retries(3, delay=5, exceptions=(requests_wrapper.ServerError, ))
    def add_db_owner(self, db_name, new_owner):
        url = rm_const.Urls.TESTENV + self.ADD_DB_OWNER_HANDLER
        data = {'database': db_name, 'login': new_owner}
        r = requests_wrapper.post(url, data=data, headers={"Authorization": "OAuth {}".format(self._oauth_token)})
        requests_wrapper.check_status_code(r)
        logger.debug("Owner %s added in database %s", new_owner, db_name)

    @decorators.retries(3, delay=5, exceptions=(requests_wrapper.ServerError, ))
    def create_db(
        self,
        db_name,
        task_owner,
        release_machine_shard=False,
        use_api_client=False,
        login='robot-srch-releaser',
    ):
        rm_shard_str = '1' if release_machine_shard else '0'  # TESTENV-3978
        if use_api_client:
            te_api_client.TestenvApiClient(token=self._oauth_token).projects.POST(
                json=dict(
                    type='custom_check',
                    status='stopped',
                    project_name=db_name,
                    svn_server='arcadia.yandex.ru/arc',
                    svn_path='trunk',
                    task_owner=task_owner,
                    owners=[
                        {
                            'login': login,
                            'is_default_problem_owner': False,
                            'receive_database_warnings': False,
                            'receive_personal_notifications': False,
                            'receive_other_user_notifications': False,
                        },
                    ],
                    release_machine_shard=rm_shard_str,
                ),
                timeout=120,
            )
            return

        url = rm_const.Urls.TESTENV + self.CREATE_DB_HANDLER
        data = {
            'new_db_name': db_name,
            'svn_server': 'arcadia.yandex.ru/arc',
            'svn_path': 'trunk',
            'task_owner': task_owner,
            'release_machine_shard': rm_shard_str,
        }
        r = requests_wrapper.post(
            url,
            params=data,
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
            timeout=120,
        )
        requests_wrapper.check_status_code(r)
        logger.debug("Database created successfully")

    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_tests(self, db_name):
        url = rm_const.Urls.TESTENV + self.GET_TESTS_HANDLER
        data = {'database': db_name}
        r = requests_wrapper.get(url, params=data, headers={"Authorization": "OAuth {}".format(self._oauth_token)})
        requests_wrapper.check_status_code(r)
        content = r.content
        if isinstance(content, bytes):
            content = content.decode()
        logger.debug("Got tests %s from database %s", content.split(','), db_name)
        return content.split(',')

    @decorators.retries(3, delay=5)
    def add_test(
        self, db_name, test_name, start_revision,
        frequency=rm_const.TestFrequency.LAZY,
        max_exec_task_count=1,
    ):
        url = rm_const.Urls.TESTENV + self.ADD_TEST_HANDLER
        data = {
            'database': db_name,
            'names': test_name,
            'frequency': frequency,
            'start_revision': start_revision,
            'max_exec_task_count': max_exec_task_count,
            'frequency_param': '',
            'origin_database': '',
        }
        logging.debug(data)
        r = requests_wrapper.post(
            url,
            data=data,
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
        )
        r.raise_for_status()
        logger.debug("Test %s added to database %s", test_name, db_name)

    @decorators.retries(3, delay=5)
    def add_tests(self, db_name, tests_names, start_revision, frequencies=[], max_exec_task_count=1):
        if not frequencies:
            frequencies = [rm_const.TestFrequency.LAZY for i in range(len(tests_names))]
        if len(frequencies) != len(tests_names):
            logger.error("Tests_names and frequencies don't have same length")
        logging.debug("Tests_names %s\n Freqs %s", ', '.join(tests_names), ', '.join(map(str, frequencies)))
        for test_name, frequency in zip(tests_names, frequencies):
            self.add_test(db_name, test_name, start_revision, frequency, max_exec_task_count)
        logger.debug("All tests added in database %s", db_name)

    @decorators.retries(3, delay=5)
    def delete_test(self, db_name, test_name):
        url = rm_const.Urls.TESTENV + self.DELETE_TEST_HANDLER
        data = {
            'database': db_name,
            'test_name': test_name,
        }
        r = requests_wrapper.post(url, data=data, headers={"Authorization": "OAuth {}".format(self._oauth_token)})
        r.raise_for_status()
        logger.debug("Test %s was deleted from database %s", test_name, db_name)

    @classmethod
    def get_sys_info(cls, db=None):
        """
        Obtain TestEnv system info, such as engine revision, etc.

        Can be used without authorization.
        @param db: project (database) name
        """
        url = parse.urljoin(rm_const.Urls.TESTENV, cls.SYSTEM_INFO_HANDLER)
        params = {'database': db} if db is not None else None
        # SYSTEM_INFO_HANDLER is a fast request, benchmark says [0.3s..22s]
        return requests_wrapper.get_r(
            url,
            params=params,
            timeout=30,
            no_retry_on_http_codes=requests_wrapper.NO_RETRY_CODES,
        )

    @decorators.retries(3, delay=5)
    def get_last_svn_revisions(
        self,
        svn_server=rm_const.Urls.SVN_ARCADIA_URL,
        svn_ssh_path="trunk",
        count=1,
        format_commit_messages=True,
        db_name="",
    ):
        """
        Get latest revision info.

        :param svn_server: SVN server (default is OK for most cases)
        :param svn_ssh_path: SVN path, defaults to 'trunk'
        :param count: the amount of revisions to be retrieved
        :param format_commit_messages: format commit messages
        :param db_name: if provided retrieves revisions processed by the given database only
        """
        url = rm_const.Urls.TESTENV + self.LAST_SVN_REVISIONS
        data = {
            'svnServer': svn_server,
            'svnSshPath': svn_ssh_path,
            'count': count,
            'formatCommitMessages': format_commit_messages,
            'db_name': db_name,
        }

        response = requests_wrapper.get_r(
            url,
            params=data,
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
            no_retry_on_http_codes=requests_wrapper.NO_RETRY_CODES,
        )
        requests_wrapper.check_status_code(response)
        rows = response.json()['rows']

        logger.debug(
            "Got the following %s latest revisions for svn %s path %s (db_name = '%s'): %s",
            count,
            svn_server,
            svn_ssh_path,
            db_name,
            rows,
        )

        return rows

    @decorators.retries(3, delay=5)
    def start_db(self, db_name):
        url = rm_const.Urls.TESTENV + self.START_DB_HANDLER
        r = requests_wrapper.post(
            url,
            data={'database': db_name},
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
        )
        r.raise_for_status()
        logger.debug("Database %s successfully started", db_name)

    @decorators.retries(3, delay=5)
    def stop_db(self, db_name):
        url = rm_const.Urls.TESTENV + self.STOP_DB_HANDLER
        r = requests_wrapper.post(
            url,
            data={'database': db_name},
            headers={"Authorization": "OAuth {}".format(self._oauth_token)},
        )
        r.raise_for_status()
        logger.debug("Database %s successfully stopped", db_name)

    def create_db_and_add_tests(
        self,
        db_name,
        owners,
        tests,
        frequencies,
        svn_revision,
        task_owner,
        release_machine_shard=False,
        use_api_client=True,
        login='robot-srch-releaser',
    ):
        if len(frequencies) < len(tests):
            frequencies = [rm_const.TestFrequency.LAZY for i in range(len(tests))]
        else:
            frequencies = [
                rm_const.TestFrequency.CHECK_EACH_REVISION if freq == 'each_commit' else rm_const.TestFrequency.LAZY
                for freq in frequencies
            ]

        if self.testenv_database_exists(db_name):
            logger.info('Project `%s` already exists', db_name)
        else:
            logger.info('We should create project `%s`', db_name)
            self.create_db(
                db_name=db_name,
                task_owner=task_owner,
                release_machine_shard=release_machine_shard,
                use_api_client=use_api_client,
                login=login,
            )

        # duplicate owners will raise MySQL integrity error and HTTP 500 response from TestEnv
        # so we filter it.
        owners = [owner for owner in owners if owner != login]

        self.add_tests_and_owners_in_db(db_name, owners, tests, frequencies, svn_revision, task_owner)

    def add_tests_and_owners_in_db(self, db_name, owners, tests, frequencies, svn_revision, task_owner):
        try:
            existing_tests = set(self.get_tests(db_name))
        except Exception as exc:
            logger.exception("Couldn't get tests from database %s", db_name)
            raise exc
        add_tests = []
        new_freq = []
        for i, test in enumerate(tests):
            if test not in existing_tests:
                add_tests.append(test)
                new_freq.append(frequencies[i])

        tests = set(tests)
        delete_tests = existing_tests - tests
        logger.debug('Need to add tests: {}'.format(','.join(add_tests)))
        logger.debug('Need to remove tests: {}'.format(','.join(list(delete_tests))))
        if not add_tests and not delete_tests:
            return
        self.stop_db(db_name)
        if add_tests:
            self.add_tests(db_name, add_tests, svn_revision, new_freq)
        if delete_tests:
            for test in delete_tests:
                self.delete_test(db_name, test)
        for owner in owners:
            self.add_db_owner(db_name, owner)
        self.start_db(db_name)

    @classmethod
    @decorators.retries(3, delay=5)
    def cleanup_db(cls, params):
        """Cleanup databases."""
        response = cls._post(
            action="cleanup_db",
            url=rm_const.Urls.TESTENV + cls.CLEANUP_DB_HANDLER,
            params=params,
        )
        return response.status_code == 200

    @classmethod
    @decorators.retries(3, delay=5)
    def get_last_good_revision_info(cls, te_db, ignore_release_jobs=False):
        r = requests_wrapper.get(rm_const.Urls.TESTENV + cls.GET_LAST_GOOD_REVISION_HANDLER.format(
            db=te_db, ignore_release_jobs=ignore_release_jobs
        ))
        r.raise_for_status()
        return r.json()

    @classmethod
    @decorators.retries(3, delay=5)
    def get_last_sandbox_task_ids(
        cls, te_db, job_names_list,
        success=False, start_rev=None, finish_rev=None,
        hours_limit=None,
        timestamp_since=None
    ):
        req = rm_const.Urls.TESTENV + cls.GET_LAST_SANDBOX_TASK_IDS_HANDLER
        params = {
            "database": te_db,
            "job_names": ",".join(job_names_list),
        }
        if hours_limit is not None:
            params["hours_limit"] = hours_limit
        elif timestamp_since is not None:
            params["timestamp_since"] = timestamp_since
        if start_rev is not None:
            params["revision1"] = start_rev
        if finish_rev is not None:
            params["revision2"] = finish_rev
        if success:
            params["success"] = "1"

        logger.debug("Get last sb task ids url: %s. Params: %s", req, params)
        r = requests_wrapper.get(req, params=params)
        r.raise_for_status()
        items = r.json()["items"]
        logging.debug("Got %s task ids", len(items))
        return items

    @classmethod
    @decorators.retries(3, delay=5)
    def get_all_sandbox_task_ids(cls, database, job_names_list=None, timestamp_since=None):
        """
        Obtain ALL sandbox task launches for the given TestEnv project (database).

        :param database: project (database) name
        :param job_names_list: retrieve only the specified jobs (set to None to get all jobs)
        :param timestamp_since: retrieve only launches since this value (leave None for no time restrictions)

        :return: a list of {'job_name': '<JOB_NAME>', 'task_id': <task_id>} dicts
        """
        params = {
            'database': database,
            'job_names': ','.join(job_names_list) if job_names_list else '',
            'timestamp_since': timestamp_since or '',
        }
        url = rm_const.Urls.TESTENV + cls.GET_ALL_SANDBOX_TASK_IDS_HANDLER

        logger.debug("Get all sb task ids url: %s. Params: %s", url, params)

        response = requests_wrapper.get(url, params=params)

        if response.status_code >= 400:
            logger.error(
                "Got status %s from %s\n"
                "Headers: %s\n"
                "Content: %s",
                response.status_code,
                url,
                response.headers,
                response.content,
            )

        response.raise_for_status()

        items = response.json().get('items', [])
        logging.debug("Got %s items", len(items))

        return items

    @classmethod
    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_last_results(cls, te_db):
        req_url = rm_const.Urls.TESTENV + cls.LAST_RESULTS_HANDLER
        params = {"database": te_db}
        logger.debug("Get last results, url: %s. Params: %s", req_url, params)
        r = requests_wrapper.get(req_url, params=params)
        requests_wrapper.check_status_code(r)
        rows = r.json()["rows"]

        # First 2 items in this handler are markers and blank row
        if len(rows) <= 2:
            return []
        else:
            return rows[2:]

    @classmethod
    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_test_results(cls, database_name, test_name, start=0, limit=50, hide_not_checked=True, hide_filtered=True):
        params = {
            "database": database_name,
            "hide_not_checked": str(hide_not_checked).lower(),
            "hide_filtered": str(hide_filtered).lower(),
            "test_name": test_name,
            "limit": limit,
            "start": start,
        }
        url = posixpath.join(rm_const.Urls.TESTENV, cls.TEST_RESULTS_HANDLER)
        r = requests_wrapper.get(url, params=params)
        requests_wrapper.check_status_code(r)
        return r.json()["rows"]

    @classmethod
    def get_commit_markers(cls, database_name, start_revision):
        params = {
            "database": database_name,
            "start_revision": start_revision,
        }
        url = posixpath.join(rm_const.Urls.TESTENV, cls.COMMIT_MARKERS_HANDLER)
        r = requests_wrapper.get_r(url, params=params)
        r.raise_for_status()
        return r.json()

    @classmethod
    def get_ok_test_tasks(cls, database_name, test_name, start_revision, hide_not_checked=True, hide_filtered=True):
        offset = 0
        limit = 100
        ok_tasks = []
        while True:
            logger.debug("Get test results: %s", {
                "test_name": test_name,
                "start": offset,
                "limit": limit,
            })
            tasks_batch = cls.get_test_results(
                database_name,
                test_name,
                start=offset,
                limit=limit,
                hide_not_checked=hide_not_checked,
                hide_filtered=hide_filtered
            )
            if not tasks_batch:
                break

            ok_tasks += [
                task
                for task in tasks_batch
                if task["status"] == "OK"
            ]

            min_ok_tests_revision = None
            if ok_tasks:
                min_ok_tests_revision = min(task["revision"] for task in ok_tasks)
            logger.debug({
                "test_name": test_name,
                "min_ok_tests_revision": min_ok_tests_revision,
                "start_revision": start_revision
            })

            min_revision = min(task["revision"] for task in tasks_batch)
            if min_revision <= start_revision:
                break
            offset += limit

        return [task for task in ok_tasks if task["revision"] > start_revision]

    @classmethod
    def get_ok_test_revisions(cls, database_name, test_name, start_revision, hide_not_checked=True, hide_filtered=True):
        ok_tasks = cls.get_ok_test_tasks(database_name, test_name, start_revision, hide_not_checked, hide_filtered)
        return [task["revision"] for task in ok_tasks]

    @classmethod
    def get_checked_intervals_chunk(cls, database_name, test_name, start=0, limit=50):
        params = {
            "database": database_name,
            "test_name": test_name,
            "limit": limit,
            "start": start,
        }
        url = posixpath.join(rm_const.Urls.TESTENV, cls.CHECKED_INTERVALS_HANDLER)
        r = requests_wrapper.get_r(url, params=params)
        r.raise_for_status()
        return r.json()["rows"]

    @classmethod
    def iter_checked_intervals(cls, database_name, test_name, start_revision):
        start = 0
        limit = 100
        checked_intervals_info = cls.get_checked_intervals_chunk(
            database_name, test_name,
            start=start, limit=limit
        )
        if len(checked_intervals_info) == 0:
            raise StopIteration
        while min([int(interval["revision"]) for interval in checked_intervals_info]) > start_revision:
            start += limit
            _checked_intervals_info = cls.get_checked_intervals_chunk(
                database_name, test_name,
                start=start, limit=limit
            )
            if len(_checked_intervals_info) == 0:
                break
            checked_intervals_info.extend(_checked_intervals_info)
        checked_intervals_info.sort(key=lambda x: int(x["revision"]), reverse=True)
        prev = None
        for curr in checked_intervals_info:
            if prev is not None:
                yield {
                    "first_revision": int(curr["revision"]),
                    "last_revision": int(prev["revision"]),
                    "is_checked": prev["is_checked"],
                    "test_name": test_name,
                }
            prev = curr

    @decorators.retries(3, delay=5, exceptions=RETRIABLE_EXCEPTIONS)
    def get_test_diffs_chunk(self, database_name, test_name, start=0, limit=50):
        params = {
            "database": database_name,
            "test_name": test_name,
            "limit": limit,
            "start": start,
        }
        url = posixpath.join(rm_const.Urls.TESTENV, self.TEST_DIFFS_HANDLER)
        r = requests_wrapper.post(
            url,
            params=params,
            headers={
                "Authorization": "OAuth {}".format(self._oauth_token)
            }
        )
        requests_wrapper.check_status_code(r)
        logger.debug(r.content)
        return r.json()["rows"]

    def get_test_diffs(self, database_name, test_name, start_revision, finish_revision, limit=100):
        start = 0
        diffs = []
        min_processed_revision = finish_revision

        while min_processed_revision >= start_revision:
            response = self.get_test_diffs_chunk(database_name, test_name, start=start, limit=limit)
            if not response:
                break

            diffs_chunk = []
            for diff in response:
                if (
                    start_revision <= diff["revision1"] <= finish_revision
                    and start_revision <= diff["revision2"] <= finish_revision
                ):
                    diffs_chunk.append(diff)

                min_processed_revision = min(min_processed_revision, diff["revision1"])

            diffs.extend(diffs_chunk)
            start += limit

        return diffs

    @classmethod
    def get_unchecked_intervals(cls, database_name, test_name, start_revision):
        return filter(
            lambda x: not x["is_checked"],
            cls.iter_checked_intervals(database_name, test_name, start_revision)
        )

    @decorators.retries(3, delay=5)
    def pre_release(self, te_db, revision, component=None):
        """
        Launch pre-release sequence automatically (Release Machine specific).

        :return: True if requests is ok and pre_release has been launched, False in other cases
        """
        url = rm_const.Urls.TESTENV + self.PRE_RELEASE_ACTION_HANDLER
        params = {"database": te_db, "revision": revision}
        if component:
            params["component"] = component
        msg = "New pre release process has started.\n"
        response = self._pre_release(url, params)
        if response.ok:
            return True, msg
        url = rm_const.Urls.TESTENV + self.PRE_RELEASE_HANDLER
        response = self._pre_release(url, params)
        if response.ok:
            return True, msg
        # TODO: check that new manual run is created
        msg = "Failed to start new pre release process.\n"
        if response.status_code == requests.codes.bad_request:
            wrong_user = re.findall(r'User "([^"]+)" does not belong to the group "([^"]+)"', response.text)
            if wrong_user:
                msg += (
                    "User '{user}' doesn't belong to '{group}'. "
                    "Please add it to the group: https://sandbox.yandex-team.ru/admin/groups\n"
                ).format(user=wrong_user[0][0], group=wrong_user[0][1])
            else:
                msg += "Bad request, see logs for details."
        return False, msg

    def _pre_release(self, url, params):
        logger.info(
            "Try to start pre release sequence for %s at revision %s\nUrl: %s",
            params["database"], params["revision"], url
        )
        response = requests_wrapper.get(
            url, params=params, headers={"Authorization": "OAuth {}".format(self._oauth_token)}, verify=False
        )
        logger.debug("Params: '%s', code: %s, response: '%s'", params, response.status_code, response.text)
        return response

    @classmethod
    def _post(cls, action, url, params, timeout=None):
        request_id = "TE-SB-Client:{}".format(uuid.uuid4())
        logger.info(
            "CALL TE `%s` [POST %s, X-Request-Id: %s]:\n%s\n\n",
            action, url, request_id, json.dumps(params, indent=2),
        )
        response = requests_wrapper.post(
            url,
            data=params,
            verify=False,
            headers={
                "X-Request-Id": request_id,
            },
            timeout=timeout if timeout else 30,
        )
        logger.debug("`%s` url: `%s`", action, response.url)
        logger.debug("`%s` status code: `%s`", action, response.status_code)
        logger.debug("`%s` response:\n%s\n\n", response.text)
        if response.status_code == 200:
            logger.info("Action `%s` completed successfully [%s]", action, request_id)
        else:
            logger.info("Action `%s`attempt FAILED [%s]", action, request_id)
        return response
