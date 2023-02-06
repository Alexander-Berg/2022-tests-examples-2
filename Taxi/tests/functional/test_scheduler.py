import pytest
import time

from pahtest import typing as t
from pahtest.fake import FakeTest, FakeTestErrored
from pahtest.folder import Folder
from pahtest.results import Results, TapResult, TestResult
from pahtest.scheduler import Scheduler, STATUS_TEST_FINISHED, STATUS_PROC_FINISHED


def hash_it(results: t.Iterable[TapResult]) -> t.Set[str]:
    return set([str(r) for r in results])


def test_scheduler_is_parallel_really():
    granula = 0.1  # minimal step for every job
    jobs = 4
    groups = jobs  # number of tests with different lags
    overhead = 0.01  # overhead on multiprocessing switches
    tests = [
        FakeTest(tag=f'{i}{j}', lag=(groups + 1 - i) * granula)
        for i in range(1, groups + 1) for j in range(1, i + 1)
    ]
    s = Scheduler(njobs=jobs, tests=tests)
    before = time.time()
    s.run()
    spent = time.time() - before
    # tests launched at all
    assert spent > granula
    # max possible lag for the worst tasks distribution
    max_lag = ((groups + 1) / 2)**2 * granula
    assert spent < max_lag + overhead


def test_sheduler_with_single_proc():
    """
    Sheduler with single job should work correctly just as not parallel case.
    """
    t_left, t_right = [FakeTest('1'), FakeTest('2')]
    s = Scheduler(njobs=1, tests=[t_left, t_right])
    results = list(s._loop_as_parallel())
    out_ = [
        (t_left, TestResult(test=t_left)),
        (t_left, STATUS_TEST_FINISHED),
        (t_right, TestResult(test=t_right)),
        (t_right, STATUS_TEST_FINISHED),
    ]
    assert results == [*out_, (None, 1)]


def test_rotate_empty():
    # pass empty results to the rotate
    s = Scheduler(njobs=2, tests=[])
    with pytest.raises(StopIteration):
        next(s._rotate([]))


def test_rotate_plain():
    def test_result(message: str) -> TestResult:
        return TestResult(
            name='sleep', success=True, message=message, test=folder
        )
    folder = Folder()
    results = [(folder, test_result(message=str(i))) for i in range(1, 4)]
    s = Scheduler(njobs=2, tests=4*[folder])
    assert next(s._rotate(results))


def test_rotate_current():
    """Rotation plugs to the current test correctly."""
    def test_result(message, folder: Folder) -> TestResult:
        return TestResult(
            name='sleep', success=True, message=message, test=folder
        )
    tr = test_result
    first = Folder(index=1)
    second = Folder(index=2)
    results = {
        'first, one': tr(folder=first, message='first, one'),
        'second, one': tr(folder=first, message='second, one'),
        'first, two': tr(folder=first, message='first, two'),
        'second, two': tr(folder=first, message='second, two'),
    }
    in_ = [
        (first, results['first, one']),
        (second, results['second, one']),
        (second, results['second, two']),
        (second, STATUS_TEST_FINISHED),
        (second, STATUS_PROC_FINISHED),
        (first, results['first, two']),
        (first, STATUS_TEST_FINISHED),
        (first, STATUS_PROC_FINISHED),
    ]
    out_ = [
        results['first, one'],
        results['first, two'],
        results['second, one'],
        results['second, two'],
    ]
    scheduler = Scheduler(njobs=2, tests=[first, second])
    assert hash_it(Results(scheduler._rotate(in_)).filter(types=[TestResult])) == hash_it(out_)


def test_rotate_with_single_proc():
    """
    Sheduler with single job should work correctly just as not parallel case.
    """
    TR = TestResult
    t_left, t_right = [FakeTest('1'), FakeTest('2')]
    s = Scheduler(njobs=1, tests=[t_left, t_right])
    results_i = list(s._rotate(s._loop_as_parallel()))
    results = Results(results_i).filter(types=[TR])
    assert set(results) == set([TR(test=t_left), TR(test=t_right)])


def test_parallel_with_exceptions():
    """A crushed test does not hang it's process."""
    plain_t = FakeTest(tag='1')
    raising_t = FakeTestErrored(tag='2')
    s = Scheduler(njobs=2, tests=[plain_t, raising_t])
    rss = s.run()
    assert rss, rss
