from pahtest import errors
from pahtest.plugins.exec_js import exec_js
import pytest
from functools import partial

from pahtest import scheduler
from pahtest.base import BaseTest
from pahtest.fake import FakeResult, FakeTest
from pahtest.errors import FinishedTestError
from pahtest.results import TestResult
from pahtest.scheduler import Buffer

from tests.unit.utils import get_fake_result, get_test_result


def test_buffer_flush():
    # - create two folders with different test results
    # - set some results for both
    # - assert if one of the folders yielded well
    fr = get_fake_result
    tr = get_test_result
    buffer = Buffer()
    left = FakeTest(tag='1')
    right = FakeTest(tag='2')
    left_results = [
        *[fr(f'1{i}', test=left) for i in range(1, 3)],
        tr('14', test=left)
    ]
    hash(left_results[0])
    right_results = [
        *[fr(f'2{i}', test=right) for i in range(1, 3)],
        tr('24', test=left)
    ]
    buffer.put_all(left, left_results)
    buffer.put_all(right, right_results)
    # flush returns just appended results
    got_from_right = list(buffer._flush_it(right))
    assert set(got_from_right).issuperset(set(right_results))
    # the test slot is clear after flushing
    assert not buffer.store[right]
    # another test slots in a buffer are not affected
    assert buffer.store[left] == left_results


def test_buffer_finished_count():
    """Buffer counts finished tests correctly."""
    fr = get_fake_result
    tr = get_test_result
    size = 4
    buffer = Buffer()
    test = FakeTest(tag='1')
    results = [
        *[fr(f'1{i}', test=test) for i in range(1, size)],
        tr(f'1{size + 1}', test=test)
    ]
    # before flush there are not finished
    assert 0 == buffer.finished_count
    assert 0 == buffer.passed_count
    #
    # we have no FINISHED status, so test is not finished
    buffer.put_all(test, results)
    buffer._flush_it_run(test)
    assert 0 == buffer.finished_count
    assert 1 == buffer.passed_count
    #
    # we have no FINISHED status, so test is not finished
    # buffer.store[test].append(scheduler.STATUS_TEST_FINISHED)
    buffer.put(test, scheduler.STATUS_TEST_FINISHED)
    buffer._flush_it_run(test)
    assert 1 == buffer.finished_count


def test_buffer_failed_count():
    """Buffer counts failed tests correctly."""
    fr = get_fake_result
    tr = get_test_result
    size = 4
    buffer = Buffer()
    test = FakeTest(tag='1')
    result_bad = fr('10', test=test, success=False)
    results_good = [fr(f'1{i}', test=test) for i in range(1, size)]
    # finaal.success is False, because one of the fake results is falsy
    final_result = tr(f'1{size + 1}', test=test, success=False)
    results = [result_bad, *results_good, final_result]
    # before flush there are not finished
    assert 0 == buffer.failed_count
    #
    # we have no FINISHED status, so test is not marked as failed
    buffer.put_all(test, results)
    buffer._flush_it_run(test)
    assert 1 == buffer.failed_count
    #
    # we have no FINISHED status, so test is not marked as failed
    # buffer.store[test].append(scheduler.STATUS_TEST_FINISHED)
    buffer.put(test, scheduler.STATUS_TEST_FINISHED)
    buffer._flush_it_run(test)
    assert 1 == buffer.failed_count


def test_buffer_passed_count():
    """Buffer counts failed tests correctly."""
    def test_result(message: str, test: BaseTest, success=True) -> TestResult:
        return TestResult(
            name='sleep', success=success, message=message, test=test
        )
    def fake_result(message: str, test: BaseTest, success=True) -> FakeResult:
        return FakeResult(
            name='sleep', success=success, message=message, test=test
        )
    tr = test_result
    fr = fake_result
    size = 4
    buffer = Buffer()
    test_good = FakeTest(tag='1')
    test_bad = FakeTest(tag='2')
    results_bad = [
        fr('10', test=test_bad, success=False),
        # final.success is False, because one of the fake results is falsy
        tr(f'1{size + 1}', test=test_bad, success=False)
    ]
    results_good = [
        *[fr(f'1{i}', test=test_good) for i in range(1, size)],
        tr(f'1{size + 1}', test=test_good)
    ]
    # - before flush there are not passed
    assert 0 == buffer.passed_count
    #
    # - we have no FINISHED status, so test is not marked as failed
    buffer.put_all(test_good, results_good)
    buffer._flush_it_run(test_good)
    assert 0 == buffer.failed_count
    #
    # - when test is finished, it's PASSED is counted
    buffer.put(test_good, scheduler.STATUS_TEST_FINISHED)
    buffer._flush_it_run(test_good)
    assert 1 == buffer.passed_count
    #
    # - finished and failed test does not affect the passed count
    buffer.put_all(test_bad, results_bad)
    buffer.put(test_bad, scheduler.STATUS_TEST_FINISHED)
    buffer._flush_it_run(test_bad)
    assert 1 == buffer.passed_count


def test_buffer_failed_no():
    """Buffer counts zero failed tests correctly."""
    fr = get_fake_result
    tr = get_test_result
    size = 4
    buffer = Buffer()
    test = FakeTest(tag='1')
    results = [
        *[fr(f'1{i}', test=test) for i in range(1, size)],
        tr(f'1{size + 1}', test=test)
    ]
    # before flush there are not finished
    assert 0 == buffer.failed_count
    #
    # we have no FINISHED status, so test is not finished
    buffer.put_all(test, results)
    buffer._flush_it_run(test)
    assert 0 == buffer.failed_count
    #
    # - flush with finished
    # we have no FINISHED status, so test is not finished
    # buffer.store[test].append(scheduler.STATUS_TEST_FINISHED)
    buffer.put(test, scheduler.STATUS_TEST_FINISHED)
    buffer._flush_it_run(test)
    assert 0 == buffer.failed_count


def test_buffer_put():
    """Buffer put changes buffer state correctly."""
    b = Buffer()
    test = FakeTest(tag='1')
    tr = partial(get_test_result, test=test)
    # empty buffer has empty inner sets
    assert not b.store.keys()
    assert not b.finished
    assert not b.failed
    #
    # common result putting changes inner storage, but does not affect inner set
    test = FakeTest(tag='1')
    result = tr(message='11')
    b.put(test, result)
    assert b.store[test] == [tr(message='11')]
    assert not b.finished
    assert not b.failed
    #
    # finished result affects the finished set
    test = FakeTest(tag='1')
    b.put(test, result=scheduler.STATUS_TEST_FINISHED)
    assert b.store[test] == [result]
    assert test in b.finished
    assert not b.failed
    #
    # failed result affects the failed set
    test_to_fail = FakeTest(tag='2')
    result_failed = tr(message='21', success=False)
    b.put(test_to_fail, result_failed)
    assert b.store[test_to_fail] == [result_failed]
    assert test_to_fail not in b.finished
    assert test_to_fail in b.failed
    #
    # get an error with flush after finished
    b.put(test_to_fail, scheduler.STATUS_TEST_FINISHED)
    with pytest.raises(FinishedTestError):
        b.put(test_to_fail, scheduler.STATUS_TEST_FINISHED)


def test_get_most_ready():
    # - no ready, get None
    b = Buffer()
    assert not b._get_most_ready()
    # - two ones ready, get the most one
    b = Buffer()
    test_left = FakeTest(tag='1')
    test_right = FakeTest(tag='1')
    tr_left = partial(get_test_result, test=test_left)
    b.put(test_left, tr_left(message='11'))
    b.put(test_left, tr_left(message='12'))
    b.put(test_right, get_test_result(test=test_right, message='2'))
    assert b._get_most_ready() == test_left


def test_flush_finished():
    # - two finished with some results are flushed
    b = Buffer()
    test_left = FakeTest(tag='1')
    test_right = FakeTest(tag='2')
    result_left = get_test_result(test=test_left, message='11')
    result_right = get_test_result(test=test_right, message='21')
    b.put(test_left, result_left)
    b.put(test_left, scheduler.STATUS_TEST_FINISHED)
    b.put(test_right, result_right)
    b.put(test_right, scheduler.STATUS_TEST_FINISHED)
    got_set = set([str(t) for t in b._flush_finished()])
    expected_set = {str(result_left), str(result_right)}
    assert not (expected_set - got_set)


def test_log_result_str():
    b = Buffer(total=1)
    test = FakeTest(tag='1')
    #
    fr = get_fake_result
    tr = get_test_result
    r_good = fr(test=test, message='11')
    r_final_good = tr(test=test, message='12')
    r_bad = fr(test=test, message='21', success=False)
    r_final_bad = tr(test=test, message='22', success=False)
    b.put_all(test, [r_good, r_final_good])
    assert 'PASSED/FAILED/TOTAL 0/0/1' in b.log_result
    b.put(test, scheduler.STATUS_TEST_FINISHED)
    b.flush_run()
    assert 'PASSED/FAILED/TOTAL 1/0/1' in b.log_result
    #
    b = Buffer(total=1)
    b.put_all(test, [r_bad, r_final_bad])
    assert 'PASSED/FAILED/TOTAL 0/0/1' in b.log_result
    b.put(test, scheduler.STATUS_TEST_FINISHED)
    b.flush_run()
    assert 'PASSED/FAILED/TOTAL 0/1/1' in b.log_result
