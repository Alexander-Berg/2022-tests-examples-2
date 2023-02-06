import logging

from . import TestPalmClientWrapper

logger = logging.getLogger(__name__)


class TestpalmTestcase:
    def __init__(self, id, uuid):
        self._id = id
        self._uuid = uuid

    @property
    def id(self):
        return self._id

    @property
    def uuid(self):
        return self._uuid

    @staticmethod
    def _validate(d):
        try:
            assert (
                'uuid' in d
            ), '\'uuid\' should be exist in Testpalm Testcase object'
            assert isinstance(d['uuid'], unicode), '\'uuid\' should be str'
            assert (
                'testCase' in d
            ), '\'testCase\' should be exist in Testpalm Testcase object'
            assert isinstance(
                d['testCase'], dict,
            ), '\'testCase\' should be dict'
            assert (
                'id' in d['testCase']
            ), '\'id\' should be exist in Testpalm Testcase object'
            assert isinstance(
                d['testCase']['id'], int,
            ), '\'testCases\' should be int'
        except AssertionError as e:
            logger.error(e)
            raise e

    @classmethod
    def from_dict(cls, d):
        TestpalmTestcase._validate(d)
        return cls(id=d['testCase']['id'], uuid=d['uuid'])


class TestpalmTestgroup:
    def __init__(self, testcases):
        self._testcases = testcases

    @property
    def testcases(self):
        return self._testcases

    @staticmethod
    def _validate(d):
        try:
            assert (
                'testCases' in d
            ), '\'testCases\' should be exist in Testpalm Testgroup object'
            assert isinstance(
                d['testCases'], list,
            ), '\'testCases\' should be list'
        except AssertionError as e:
            logger.error(e)
            raise e

    @classmethod
    def from_dict(cls, d):
        TestpalmTestgroup._validate(d)
        testcases = []
        for testcase in d['testCases']:
            testcases.append(TestpalmTestcase.from_dict(testcase))
        return cls(testcases=testcases)


class TestpalmTestrun:
    testpalm_api = None

    def __init__(self, project_id, testrun_id, status, test_groups):
        self.project_id = project_id
        self._id = testrun_id
        self._status = status
        self._test_groups = test_groups

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def test_groups(self):
        return self._test_groups

    @staticmethod
    def _validate(data):
        try:
            assert isinstance(data, dict), 'data should be dict-like object'
            assert (
                'id' in data
            ), '\'id\' should be exist in Testpalm Testrun object'
            assert (
                'status' in data
            ), '\'status\' should be exist in Testpalm Testrun object'
            assert (
                'testGroups' in data
            ), '\'links\' should be exist in Testpalm Testrun object'
            assert isinstance(data['id'], unicode), '\'id\' should be string'
            assert isinstance(
                data['status'], unicode,
            ), '\'status\' should be string'
            assert isinstance(
                data['testGroups'], list,
            ), '\'testGroups\' should be list'
        except AssertionError as e:
            logger.error(e)
            raise e

    @classmethod
    def init_by_api(
            cls,
            testpalm_client,
            project_id,
            testrun_id,
            testsuite_id,
            testrun_title,
            assignee,
            created_by,
    ):
        cls.testpalm_api = TestPalmClientWrapper(testpalm_client)
        # if testrun_id is passed to init, decide the run is created already
        # just get its structure, will create it otherwise
        if testrun_id:
            logger.info('Receiving testrun info')
            data = cls.testpalm_api.get_testrun_info(
                project_id=project_id, testrun_id=testrun_id,
            )
        else:
            logger.info('Creating testrun')
            data = cls.testpalm_api.create_testrun(
                project_id, testsuite_id, testrun_title, assignee, created_by,
            )
            logger.info('Testrun created successfully')

        cls._validate(data)
        test_groups = []

        run_id = data['id']
        run_status = data['status']
        for test_group in data['testGroups']:
            test_groups.append(TestpalmTestgroup.from_dict(test_group))
        run_test_groups = test_groups
        return cls(project_id, run_id, run_status, run_test_groups)

    def update_from_allure_cases(self, testcases):
        statuses = []
        for group in self.test_groups:
            for testcase in group.testcases:
                status = testcases.get(testcase.id)
                if status:
                    statuses.append(
                        {'runTestCaseUuid': testcase.uuid, 'status': status},
                    )
        logger.info('Updating testrun')
        self.testpalm_api.bulk_update_statuses(
            self.id, self.project_id, statuses,
        )
