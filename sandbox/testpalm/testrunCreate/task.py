# -*- coding: utf-8 -*-
from .api import TestPalmApi, PROJ_PI, PROJ_ADFOX
from logging import getLogger
from datetime import datetime


# кол-во сфейленных автотестов
STAT_FAILED_TESTS = 'failed_autotests'
# кол-во тесткейсов, добавленных из-за фейла автотестов (либо из-за того, что автотесты не запустились)
STAT_CASES_REASON_TEST_FAILURE = 'failed_tests_cases'
# кол-во тесткейсов, добавленных из-за того, что на них нет автотестов
STAT_CASES_REASON_NOT_AUTOMATED = 'not_automated_cases'
# общее кол-во доступный тесткейсов
STAT_CASES_AVAILABLE = 'total_cases_available'
# общее кол-во уникальных тесткейсов, отправленных асессорам (без учета разделения по браузерам)
STAT_CASES_SENT = 'total_cases_sent'


class AdfoxTestRunCreateTask:
    def __init__(self, testpalm_token, report, project):
        self.api = TestPalmApi(token=testpalm_token, project=project)
        self.report = report
        self.logger = getLogger()

        # assessors cases stats
        self.stats = {
            PROJ_ADFOX: self._init_stat(PROJ_ADFOX),
            PROJ_PI: self._init_stat(PROJ_PI),
        }
        # Основная версия
        self.version_id = ''
        # Дополнительная версия - упавшие (или незапущенные) автоматизированные кейсы
        self.version_id_failed = ''
        # assessors cases
        self.assessors_cases = []

    def execute(self):
        # clear testsuites
        testsuites = self.api.get_testsuites()

        ids = []
        for testsuite in testsuites:
            if testsuite.get_title().find('Release testsuit:') > -1:
                ids.append(testsuite.get_id())

        self.api.delete_testsuites(ids)

        # find and mark need run testcases
        (testcases_unautomated, testcases_failed) = self._get_run_testcases()

        self._add_stat(
            PROJ_PI,
            STAT_CASES_SENT,
            self._get_stat(PROJ_PI, STAT_CASES_REASON_TEST_FAILURE) +
            self._get_stat(PROJ_PI, STAT_CASES_REASON_NOT_AUTOMATED)
        )

        self._add_stat(
            PROJ_ADFOX,
            STAT_CASES_SENT,
            self._get_stat(PROJ_ADFOX, STAT_CASES_REASON_TEST_FAILURE) +
            self._get_stat(PROJ_ADFOX, STAT_CASES_REASON_NOT_AUTOMATED)
        )

        self.logger.info('STATS: {}'.format(self.stats))

        version = self._create_testrun(testcases_unautomated)
        if version:
            self.version_id = version.id

        version_failed = self._create_testrun(testcases_failed, '_failed_autotests')
        if version_failed:
            self.version_id_failed = version_failed.id

    def _create_testrun(self, testcases, name_suffix=''):
        """
        :param testcases: Список кейсов в ран
        :type testcases: list(TestPalmApi.TestCase)
        :param str name_suffix: Суффикс к имени версии рана
        :return TestPalmApi.Version | None: Структура описания версии из Testpalm API
        """
        if not testcases:
            return

        feature_keys = self._get_feature_keys(testcases)

        definition_tag_id = self.api.get_definition_by_title('tags').get_id()
        definition_feature_id = self.api.get_definition_by_title('feature').get_id()

        modify_testcase_data = []
        for testcase in testcases:
            attributes = {key: value for key, value in testcase.get_attributes().iteritems()}

            features = attributes[definition_feature_id]

            for key in testcase.get_keys():
                for feature in feature_keys.get(key, []):
                    features.append(feature)

            current_tags = attributes[definition_tag_id] if definition_tag_id in attributes else []
            attributes[definition_tag_id] = list(set(['need run'] + current_tags))
            attributes[definition_feature_id] = list(set(features))

            modify_testcase_data.append({
                'id': testcase.get_id(),
                'attributes': attributes
            })

        self.api.modify_testcase(modify_testcase_data)

        # order testcases
        ordered_testcases = [
            testcase.get_id() for testcase in self._get_ordered_testcases(testcases)
        ]

        self.api.order_testcases(ordered_testcases)

        # create testsuites
        testsuites_names = {feature for testcase in testcases for feature in testcase.get_attribute('feature')}

        testsuites = []
        for testsuite_name in testsuites_names:
            suffix = ' [%s]' % name_suffix.replace('_', ' ').strip() if name_suffix else ''
            testsuites.append(self.api.create_testsuite(testsuite_name, suffix))

        # create version
        version = self.api.create_version(self._generate_version_name(name_suffix), testsuites)

        for env in ['Yandex Browser']:
            for testsuite in testsuites:
                testrun = self.api.create_testrun({
                    'title': u'{} {}'.format(testsuite.get_title(), env),
                    'version': version.get_id(),
                    'testSuite': {
                        'id': testsuite.get_id(),
                    },
                    'environments': [
                        {'title': env},
                    ],
                })
                new_test_cases = []
                for testcase_id in ordered_testcases:
                    for testcase in testrun['testGroups'][0]['testCases']:
                        if testcase['testCase']['id'] == testcase_id:
                            new_test_cases.append(testcase)
                            break

                testrun['testGroups'][0]['testCases'] = new_test_cases
                self.api.update_testrun(testrun)

        return version

    def get_coverage_maps_metric(self):
        testcases = self.api.get_testcases()
        coverage_maps_stat = []

        for testcase in testcases:
            coverage_maps_stat.append({
                'feature': ','.join(testcase.get_feature()),
                'case_name': testcase.get_name(),
                'scope_of_work': testcase.get_scope_of_work(),
                'priority': testcase.get_priority(),
                'project': testcase.get_project(),
                'tags': ',{},'.format(','.join(testcase.get_tags()))
            })

        self.logger.info('COVERAGE_MAPS_STAT count: {}'.format(len(coverage_maps_stat)))
        return coverage_maps_stat

    def _get_run_testcases(self):
        testcases = self.api.get_testcases()

        run_testcases = {}
        unautomated_run_testcases = {}
        failed_run_testcases = {}
        failed_testcases = self._get_failed_testcases(testcases)

        def add_testcase_to_run(testcase, is_failed, not_automated):
            """
            Добавить кейс в один или оба из ранов.
            Один и тот же кейс может добавляться в оба рана, если он является предусловием
            обоих типов кейсов.
            :param testcase:
            :type testcase: TestPalmApi.TestCase
            :param is_failed: Автоматизированный кейс и автотест провален или не запустился
            :type is_failed: bool
            :param not_automated: Неавтоматизированный кейс
            :type not_automated: bool
            """
            name = testcase.get_name()
            run_testcases[name] = testcase
            if not_automated:
                unautomated_run_testcases[name] = testcase
            if is_failed:
                failed_run_testcases[name] = testcase

        def add_total_stat(proj, is_failed, not_automated):
            if proj:
                if is_failed:
                    self._inc_stat(proj, STAT_CASES_REASON_TEST_FAILURE)
                elif not_automated:
                    self._inc_stat(proj, STAT_CASES_REASON_NOT_AUTOMATED)

        def add_parents(key, proj, is_failed, not_automated):
            for testcase in testcases:
                if key in testcase.get_keys() and not testcase.is_skipped():
                    if not run_testcases.get(testcase.get_name()):
                        add_total_stat(proj, is_failed, not_automated)
                        self._add_assessors_case(proj, testcase.get_name())

                    add_testcase_to_run(testcase, is_failed, not_automated)

                    for parent_key in testcase.get_parent_keys():
                        add_parents(parent_key, proj, is_failed, not_automated)

        def __is_need_to_run_assessor(testcase):
            if testcase.is_skipped():
                return False

            elif testcase.is_needs_yml():
                return False

            elif testcase.is_automation_only():
                return False
            return True

        for testcase in testcases:
            if __is_need_to_run_assessor(testcase) is False:
                continue

            testcase_name = testcase.get_name()

            proj = testcase.get_project()
            if proj:
                self._inc_stat(proj, STAT_CASES_AVAILABLE)

            not_automated = testcase.is_unautomated()
            is_failed = testcase_name in failed_testcases

            if not_automated or is_failed:
                if not run_testcases.get(testcase_name):
                    add_total_stat(proj, is_failed, not_automated)
                    self._add_assessors_case(proj, testcase_name)

                add_testcase_to_run(testcase, is_failed, not_automated)

                for key in testcase.get_parent_keys():
                    add_parents(key, proj, is_failed, not_automated)

        return (
            unautomated_run_testcases.values(),
            failed_run_testcases.values()
        )

    def _get_feature_keys(self, testcases):
        feature_keys = {}

        def _add_key(key, feature):
            if key not in feature_keys:
                feature_keys[key] = {}
            feature_keys[key][feature] = 1

            for testcase in testcases:
                if key in testcase.get_keys():
                    for parent_key in testcase.get_parent_keys():
                        _add_key(parent_key, feature)

        for testcase in testcases:
            for parent_key in testcase.get_parent_keys():
                for feature in testcase.get_feature():
                    _add_key(parent_key, feature)

        return feature_keys

    def _collect_autotests_statuses(self):
        test_statuses = dict()
        for testcase in self.report.values():
            status = testcase['status']
            names = []
            # meta отсутствует у пропущенных тестов
            if 'meta' in testcase and 'palmSyncNames' in testcase['meta']:
                for palmsync_name in testcase['meta']['palmSyncNames']:
                    names.append(' '.join(testcase['suitePath'][:-1] + [palmsync_name]))
            else:
                names.append(' '.join(testcase['suitePath']))
            test_statuses.update({
                name: status for name in names
            })
        return test_statuses

    def _get_failed_testcases(self, testcases):
        """
        :param testcases:  Список всех кейсов проекта
        :type testcases: list(TestPalmApi.TestCase)
        :return list(str):  Список имен непройденных автотестов
        """
        failed_testcases = []

        test_statuses = self._collect_autotests_statuses()

        for testcase in testcases:
            if testcase.is_unautomated() or testcase.is_skipped():
                continue
            name = testcase.get_name()
            # None означает, что кейс не найден в отчете (скорее всего, отчет не указан)
            if test_statuses.get(name) not in [None, 'fail']:
                continue
            proj = testcase.get_project()
            if proj:
                self._inc_stat(proj, STAT_FAILED_TESTS)
            failed_testcases.append(name)

        return failed_testcases

    def _get_ordered_testcases(self, testcases):
        """
        Сортируем тесткейсы.
        На каждом шаге запоминаем, какие ключи мы уже добавили в сортированный список.
        Если для тесткейса уже есть все обработанные ключи, которые ему нужны,
        то кейс добавляем иначе пропускаем
        :param testcases:
        :type list(TestPalmApi.TestCase): testcases
        :return list(TestPalmApi.TestCase):
        """
        ordered_keys = {}
        ordered_testcases = []
        ordered_testcases_ids = {}

        iteration = 0

        while len(ordered_testcases) < len(testcases):
            iteration += 1
            has_progress = False
            for testcase in testcases:
                case_id = testcase.get_id()
                if case_id in ordered_testcases_ids:
                    continue
                if all(x in ordered_keys for x in testcase.get_parent_keys()):
                    ordered_testcases.append(testcase)
                    ordered_testcases_ids[case_id] = 1
                    has_progress = True
                    for key in testcase.get_keys():
                        ordered_keys[key] = 1

            if not has_progress:
                failed_tests = [x for x in testcases if x.get_id() not in ordered_testcases_ids]
                self.logger.debug('_get_ordered_testcases %d test with incorrect dependencies' % len(failed_tests))
                for x in failed_tests:
                    self.logger.debug(
                        '_get_ordered_testcases failed test %d(%s) - %s' %
                        (x.get_id(), x.get_parent_keys().__str__(), x.get_name())
                    )
                raise Exception('Failed to order tests %s after %d iterations' % (
                    map(lambda x: x.get_id(), failed_tests).__str__(),
                    iteration
                ))

        return ordered_testcases

    def _init_stat(self, proj):
        return {
            'project': proj,
            STAT_FAILED_TESTS: 0,
            STAT_CASES_REASON_TEST_FAILURE: 0,
            STAT_CASES_REASON_NOT_AUTOMATED: 0,
            STAT_CASES_AVAILABLE: 0,
            STAT_CASES_SENT: 0
        }

    def _get_stat(self, proj, key):
        if proj in self.stats and key in self.stats[proj]:
            return self.stats[proj][key]

        return None

    def _add_stat(self, proj, key, value):
        if proj in self.stats:
            self.stats[proj][key] = value

    def _inc_stat(self, proj, key):
        if proj in self.stats:
            self.stats[proj][key] += 1

    def _add_assessors_case(self, proj, name):
        self.assessors_cases.append({
            'project': proj,
            'case_name': name,
        })

    def _generate_version_name(self, suffix):
        base = datetime.now().strftime('RELEASE-%Y-%m-%d-%H-%M-%S')
        if suffix:
            return base + '-' + suffix
        return base
