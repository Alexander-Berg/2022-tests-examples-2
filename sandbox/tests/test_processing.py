# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function

from datetime import date, datetime, timedelta
from unittest import TestCase, main

from sandbox.projects.direct_internal_analytics.laborer.target_types.base import BaseTarget
from sandbox.projects.direct_internal_analytics.laborer_base.processing import get_data_path, get_expiration_time, \
    process_target_new, TargetProcessorFactory, TargetProcessor, TargetDependenciesNotReadyException


class TestTargetOne(BaseTarget):
    _namespace = 'tt_'
    title = 'test_title'


class TestTargetTwo(BaseTarget):
    _namespace = 'tt_'
    title = 'title/test'

    dependencies = [TestTargetOne]


class TestTargetThree(BaseTarget):
    _namespace = 'tt_'
    title = 'test_title/three'

    dependencies = [TestTargetTwo, TestTargetOne]
    final = True


class TestTargetThreeAndHalf(BaseTarget):
    _namespace = 'tt_'
    title = 'title/three_half'

    dependencies = [TestTargetTwo]


class TestTargetFour(BaseTarget):
    _namespace = 'tt_'
    title = 'test_title/four'

    dependencies = [TestTargetThree]


class TestTargetFive(BaseTarget):
    _namespace = 'tt_'
    title = 'test_title/five'

    dependencies = [TestTargetFour, TestTargetThreeAndHalf]
    final = True


class GetDataPathTestCase(TestCase):
    def test_get_data_path(self):
        self.assertEqual(
            get_data_path(TestTargetOne, {'token': 'asdfg', 'date': date(2017, 10, 1), 'home': 'tmp'}),
            '//tmp/asdfg/tt_test_title/tt_test_title-2017-10-01'
        )

    def test_get_data_path_title_with_slash(self):
        self.assertEqual(
            get_data_path(TestTargetTwo, {'token': 'asdfg', 'date': date(2017, 10, 1), 'home': 'tmp/user'}),
            '//tmp/user/asdfg/tt_title_test/tt_title_test-2017-10-01'
        )

    def test_get_data_path_with_extra_slash(self):
        self.assertEqual(
            get_data_path(TestTargetThree, {'token': 'asdfg', 'date': date(2017, 10, 1), 'home': 'tmp/user/'}),
            '//tmp/user/asdfg/tt_test_title_three/tt_test_title_three-2017-10-01'
        )

    def test_get_data_path_with_extra_slash_beginning(self):
        self.assertEqual(
            get_data_path(TestTargetThree, {'token': 'asdfg', 'date': date(2017, 10, 1), 'home': '/tmp/user/'}),
            '//tmp/user/asdfg/tt_test_title_three/tt_test_title_three-2017-10-01'
        )

    def test_get_data_path_with_two_extra_slash_beginning(self):
        self.assertEqual(
            get_data_path(TestTargetThree, {'token': 'asdfg', 'date': date(2017, 10, 1), 'home': '//tmp/user/'}),
            '//tmp/user/asdfg/tt_test_title_three/tt_test_title_three-2017-10-01'
        )


class GetExpirationTimeTestCase(TestCase):
    dt = datetime.utcnow()

    @staticmethod
    def exp_target(days):
        class ExpirationTestTarget(BaseTarget):
            expiration_days = days

        return ExpirationTestTarget

    @staticmethod
    def exp_context(days):
        return {'expiration_days': days}

    @staticmethod
    def generate_date(days, dt):
        return (dt + timedelta(days=days)).isoformat() + 'Z'

    def test_get_expiration_time_00(self):
        self.assertEqual(get_expiration_time(self.exp_target(0), self.exp_context(0)), None)

    def test_get_expiration_time_m1m1(self):
        self.assertEqual(get_expiration_time(self.exp_target(-1), self.exp_context(-1)), None)

    def test_get_expiration_time_10(self):
        self.assertEqual(
            self.generate_date(1, self.dt), get_expiration_time(self.exp_target(1), self.exp_context(0), self.dt))

    def test_get_expiration_time_01(self):
        self.assertEqual(
            self.generate_date(1, self.dt), get_expiration_time(self.exp_target(0), self.exp_context(1), self.dt))

    def test_get_expiration_time_23(self):
        self.assertEqual(
            self.generate_date(2, self.dt), get_expiration_time(self.exp_target(2), self.exp_context(3), self.dt))

    def test_get_expiration_time_32(self):
        self.assertEqual(
            self.generate_date(2, self.dt), get_expiration_time(self.exp_target(3), self.exp_context(2), self.dt))

    def test_get_expiration_time_1m1(self):
        self.assertEqual(
            self.generate_date(1, self.dt), get_expiration_time(self.exp_target(1), self.exp_context(-1), self.dt))

    def test_get_expiration_time_m11(self):
        self.assertEqual(
            self.generate_date(1, self.dt), get_expiration_time(self.exp_target(-1), self.exp_context(1), self.dt))


class TestTP(TargetProcessor):
    def __init__(self, target, call_order, clear_data_order, clear_locks_order, ready=False):
        self._target = target
        self._call_order = call_order
        self._clear_data_order = clear_data_order
        self._clear_locks_order = clear_locks_order
        self._ready = ready

    def clear_data(self):
        self._clear_data_order.append(self._target)

    def clear_locks(self):
        self._clear_locks_order.append(self._target)

    def get_lock(self):
        return self._target

    def is_already_processed(self):
        return self._ready or self._target in self._call_order

    def run_processing(self, dependencies_locks):
        self._call_order.append(self._target)


class TestTPF(TargetProcessorFactory):
    def __init__(self, ready_list=None):
        self._call_order = []
        self._clear_data_order = []
        self._clear_locks_order = []
        self._ready_list = ready_list or []

    def get_processor_for(self, target):
        return TestTP(target, self._call_order, self._clear_data_order, self._clear_locks_order,
                      ready=target in self._ready_list)

    def get_call_order(self):
        return self._call_order

    def get_clear_data_order(self):
        return self._clear_data_order

    def get_clear_locks_order(self):
        return self._clear_locks_order


class ProcessTargetNewTestCase(TestCase):
    def test_process_target_without_deps(self):
        tpf = TestTPF(ready_list=[TestTargetThree])
        process_target_new(TestTargetFour, tpf, with_dependencies=False, force=False)
        self.assertEqual(tpf.get_call_order(), [TestTargetFour])

    def test_process_target_without_deps_when_already_processed(self):
        tpf = TestTPF(ready_list=[TestTargetFour])
        process_target_new(TestTargetFour, tpf, with_dependencies=False, force=False)
        self.assertEqual(tpf.get_call_order(), [])

    def test_process_target_without_deps_when_already_processed_and_force(self):
        tpf = TestTPF(ready_list=[TestTargetThree, TestTargetFour])
        process_target_new(TestTargetFour, tpf, with_dependencies=False, force=True)
        self.assertEqual(tpf.get_call_order(), [TestTargetFour])

    def test_process_target_without_deps_when_deps_not_ready(self):
        tpf = TestTPF()
        self.assertRaises(TargetDependenciesNotReadyException, process_target_new, TestTargetFour, tpf,
                          with_dependencies=False, force=False)
        self.assertEqual(tpf.get_call_order(), [])

    def test_process_target_without_deps_when_already_processed_and_force_and_no_deps_ready(self):
        tpf = TestTPF(ready_list=[TestTargetFour])
        self.assertRaises(TargetDependenciesNotReadyException, process_target_new, TestTargetFour, tpf,
                          with_dependencies=False, force=True)
        self.assertEqual(tpf.get_call_order(), [])

    def test_process_target_with_deps(self):
        tpf = TestTPF()
        process_target_new(TestTargetThree, tpf, with_dependencies=True, force=False)
        self.assertEqual(tpf.get_call_order(), [TestTargetOne, TestTargetTwo, TestTargetThree])

    def test_process_target_with_deps_partly_ready(self):
        tpf = TestTPF(ready_list=[TestTargetFour, TestTargetTwo])
        process_target_new(TestTargetFive, tpf, with_dependencies=True, force=False)
        self.assertEqual(tpf.get_call_order(), [TestTargetThreeAndHalf, TestTargetFive])

    def test_process_target_with_deps_partly_ready_force(self):
        tpf = TestTPF(ready_list=[TestTargetFour, TestTargetTwo])
        process_target_new(TestTargetFive, tpf, with_dependencies=True, force=True)
        self.assertEqual(tpf.get_call_order(), [TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                                                TestTargetThreeAndHalf, TestTargetFive])
        self.assertEqual(tpf.get_clear_data_order(), [TestTargetFour, TestTargetTwo])
        self.assertEqual(tpf.get_clear_locks_order(), [TestTargetFour, TestTargetTwo])

    def test_process_target_with_deps_all_ready_force(self):
        tpf = TestTPF(ready_list=[TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                                  TestTargetThreeAndHalf, TestTargetFive])
        process_target_new(TestTargetFive, tpf, with_dependencies=True, force=True)
        self.assertEqual(tpf.get_call_order(), [TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                                                TestTargetThreeAndHalf, TestTargetFive])
        self.assertEqual(set(tpf.get_clear_data_order()),
                         {TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                          TestTargetThreeAndHalf, TestTargetFive})
        self.assertEqual(set(tpf.get_clear_locks_order()),
                         {TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                          TestTargetThreeAndHalf, TestTargetFive})

    def test_process_target_with_deps_no_ready_force(self):
        tpf = TestTPF()
        process_target_new(TestTargetFive, tpf, with_dependencies=True, force=True)
        self.assertEqual(tpf.get_call_order(), [TestTargetOne, TestTargetTwo, TestTargetThree, TestTargetFour,
                                                TestTargetThreeAndHalf, TestTargetFive])
        self.assertEqual(tpf.get_clear_data_order(), [])
        self.assertEqual(tpf.get_clear_locks_order(), [])

    def test_process_target_with_already_processed(self):
        tpf = TestTPF()
        already_processed = {TestTargetOne: TestTargetOne}
        process_target_new(TestTargetThree, tpf, with_dependencies=True, force=False,
                           already_processed=already_processed)
        self.assertEqual(tpf.get_call_order(), [TestTargetTwo, TestTargetThree])

    def test_process_target_clean_up_only(self):
        tpf = TestTPF(ready_list=[TestTargetOne, TestTargetThree, TestTargetFour,
                                  TestTargetThreeAndHalf, TestTargetFive])
        process_target_new(TestTargetFive, tpf, with_dependencies=False, force=False, clean_up_only=True)
        self.assertEqual(tpf.get_call_order(), [])
        self.assertEqual(set(tpf.get_clear_data_order()), {TestTargetOne, TestTargetFour, TestTargetThreeAndHalf})
        self.assertEqual(tpf.get_clear_locks_order(), [])

    def test_process_target_clean_up_only_with_force(self):
        tpf = TestTPF(ready_list=[TestTargetOne, TestTargetThree, TestTargetFour,
                                  TestTargetThreeAndHalf, TestTargetFive])
        process_target_new(TestTargetFive, tpf, with_dependencies=False, force=True, clean_up_only=True)
        self.assertEqual(tpf.get_call_order(), [])
        self.assertEqual(set(tpf.get_clear_data_order()), {TestTargetOne, TestTargetFour, TestTargetThreeAndHalf,
                                                           TestTargetThree, TestTargetFive})
        self.assertEqual(tpf.get_clear_locks_order(), [])

    def test_process_target_clean_up_only_with_deps(self):
        tpf = TestTPF(ready_list=[TestTargetOne, TestTargetThree, TestTargetFour,
                                  TestTargetThreeAndHalf, TestTargetFive])
        process_target_new(TestTargetFive, tpf, with_dependencies=True, force=False, clean_up_only=True)
        self.assertEqual(tpf.get_call_order(), [])
        self.assertEqual(set(tpf.get_clear_data_order()), {TestTargetOne, TestTargetFour, TestTargetThreeAndHalf})
        self.assertEqual(tpf.get_clear_locks_order(), [])

    def test_process_target_clean_up_only_not_final(self):
        tpf = TestTPF(ready_list=[TestTargetOne, TestTargetThree, TestTargetFour])
        process_target_new(TestTargetFour, tpf, with_dependencies=True, force=False, clean_up_only=True)
        self.assertEqual(tpf.get_call_order(), [])
        self.assertEqual(set(tpf.get_clear_data_order()), {TestTargetOne})
        self.assertEqual(tpf.get_clear_locks_order(), [])


if __name__ == '__main__':
    main()
