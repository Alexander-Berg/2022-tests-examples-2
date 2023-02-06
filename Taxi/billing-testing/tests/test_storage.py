import os
import tempfile
import uuid

from sibilla import storage


def test_outcome_type():
    obj = storage.Outcome.PASSED
    assert isinstance(obj, storage.Outcome)


def test_outcome_names():
    assert isinstance(storage.Outcome.PASSED.name, str)
    assert storage.Outcome.PASSED.name == 'PASSED'
    assert storage.Outcome.SKIPPED.name == 'SKIPPED'
    assert storage.Outcome.FAILED.name == 'FAILED'
    assert storage.Outcome.ERROR.name == 'ERROR'


def test_outcome_parse():
    assert storage.Outcome.parse('PASSED') == storage.Outcome.PASSED
    assert storage.Outcome.parse('SKIPPED') == storage.Outcome.SKIPPED
    assert storage.Outcome.parse('FAILED') == storage.Outcome.FAILED
    assert storage.Outcome.parse('ERROR') == storage.Outcome.ERROR


def test_statistics_init():
    obj = storage.Statistics(passed=12, skipped=34, failed=56, error=78)
    assert obj[storage.Outcome.PASSED] == 12
    assert obj[storage.Outcome.SKIPPED] == 34
    assert obj[storage.Outcome.FAILED] == 56
    assert obj[storage.Outcome.ERROR] == 78
    assert obj[storage.Outcome.PASSED.name] == 12
    assert obj[storage.Outcome.SKIPPED.name] == 34
    assert obj[storage.Outcome.FAILED.name] == 56
    assert obj[storage.Outcome.ERROR.name] == 78
    cnts = obj.counts
    assert cnts[storage.Outcome.PASSED.name] == 12
    assert cnts[storage.Outcome.SKIPPED.name] == 34
    assert cnts[storage.Outcome.FAILED.name] == 56
    assert cnts[storage.Outcome.ERROR.name] == 78


def test_statistics_init0():
    obj = storage.Statistics()
    assert obj[storage.Outcome.PASSED] == 0
    assert obj[storage.Outcome.SKIPPED] == 0
    assert obj[storage.Outcome.FAILED] == 0
    assert obj[storage.Outcome.ERROR] == 0


def test_statistics_agg_count():
    obj = storage.Statistics(passed=12, skipped=34, failed=56, error=78)
    assert obj.aggregated_count == 12 + 34 + 56 + 78


def test_statistics_outcome():
    def out(
            passed: int, skipped: int, failed: int, error: int,
    ) -> storage.Outcome:
        return storage.Statistics(
            passed=passed, skipped=skipped, failed=failed, error=error,
        ).aggregated_outcome

    assert out(0, 0, 0, 0) == storage.Outcome.SKIPPED
    assert out(7, 0, 0, 0) == storage.Outcome.PASSED
    assert out(0, 7, 0, 0) == storage.Outcome.SKIPPED
    assert out(7, 7, 0, 0) == storage.Outcome.PASSED
    assert out(0, 0, 7, 0) == storage.Outcome.FAILED
    assert out(7, 0, 7, 0) == storage.Outcome.FAILED
    assert out(0, 7, 7, 0) == storage.Outcome.FAILED
    assert out(7, 7, 7, 0) == storage.Outcome.FAILED
    assert out(0, 0, 0, 7) == storage.Outcome.ERROR
    assert out(7, 0, 0, 7) == storage.Outcome.ERROR
    assert out(0, 7, 0, 7) == storage.Outcome.ERROR
    assert out(7, 7, 0, 7) == storage.Outcome.ERROR
    assert out(0, 0, 7, 7) == storage.Outcome.ERROR
    assert out(7, 0, 7, 7) == storage.Outcome.ERROR
    assert out(0, 7, 7, 7) == storage.Outcome.ERROR
    assert out(7, 7, 7, 7) == storage.Outcome.ERROR


def test_testresult():
    obj = storage.TestResult(
        test_id=12345,
        testcase_id=54321,
        session_uuid='5daaaca9-f571-47e2-b301-6bc0d455f583',
        start_ms=1558702647785,
        finish_ms=1558702757785,
        request={'foo': 'bar', 'int': 121, 'dict': {'A': 0}},
        expected={'first': 1, 'last': 999},
        response={'first': 9, 'last': 999, 'extra': {}},
        exc_info='',
        outcome=storage.Outcome.SKIPPED,
    )
    assert isinstance(obj.test_id, int)
    assert obj.test_id == 12345
    assert isinstance(obj.testcase_id, int)
    assert obj.testcase_id == 54321
    assert isinstance(obj.session_uuid, str)
    assert obj.session_uuid == '5daaaca9-f571-47e2-b301-6bc0d455f583'
    assert isinstance(obj.start_ms, int)
    assert obj.start_ms == 1558702647785
    assert isinstance(obj.finish_ms, int)
    assert obj.finish_ms == 1558702757785
    assert isinstance(obj.request, dict)
    assert obj.request == {'foo': 'bar', 'int': 121, 'dict': {'A': 0}}
    assert isinstance(obj.expected, dict)
    assert obj.expected == {'first': 1, 'last': 999}
    assert isinstance(obj.response, dict)
    assert obj.response == {'first': 9, 'last': 999, 'extra': {}}
    assert isinstance(obj.exc_info, str)
    assert obj.exc_info == ''
    assert isinstance(obj.outcome, storage.Outcome)
    assert obj.outcome == storage.Outcome.SKIPPED


def test_storage_memory():
    stg = storage.Storage(':memory:')
    count = stg.count()
    assert count == 0


def test_storage_counters():
    stg = storage.Storage(':memory:')
    assert not stg.current_session_uuid()
    assert not stg.current_testcase_id()
    session_uuid = stg.start_session(name='testStorage', description='')
    assert session_uuid
    assert stg.current_session_uuid() == session_uuid
    assert not stg.current_testcase_id()
    stg.start_testcase(name='testcase 0')
    cur_testcase = stg.current_testcase_id()
    assert cur_testcase == 0
    assert stg.current_testcase_id() == cur_testcase
    assert stg.current_testcase_id() == cur_testcase  # must not be changed
    assert stg.next_test_id() == 0
    assert stg.next_test_id() == 1
    assert stg.next_test_id() == 2
    stg.finish_testcase()
    stg.start_testcase(name='testcase 1')
    assert stg.current_testcase_id() == cur_testcase + 1
    assert stg.next_test_id() == 0
    assert stg.next_test_id() == 1
    assert stg.next_test_id() == 2
    stg.finish_testcase()
    stg.finish_session()


def _assert_testresult_equality(
        obj1: storage.TestResult, obj2: storage.TestResult,
) -> None:
    assert obj1.test_id == obj2.test_id
    assert obj1.testcase_id == obj2.testcase_id
    assert obj1.session_uuid == obj2.session_uuid
    assert obj1.start_ms == obj2.start_ms
    assert obj1.finish_ms == obj2.finish_ms
    assert obj1.request == obj2.request
    assert obj1.expected == obj2.expected
    assert obj1.response == obj2.response
    assert obj1.exc_info == obj2.exc_info
    assert obj1.outcome == obj2.outcome


def _random_name() -> str:
    return str(uuid.uuid4())


def test_storage_test_persistence():
    # pylint: disable=too-many-statements
    fname = tempfile.mktemp()
    stg = storage.Storage(fname)
    s_name = _random_name()
    s_desc = _random_name()
    t_name = _random_name()
    t_desc = _random_name()

    session_uuid = stg.start_session(name=s_name, description=s_desc)
    stg.start_testcase(name=t_name, description=t_desc)
    assert stg.count() == 0
    assert stg.count(session_uuid) == 0
    obj = stg.add(
        request={'uri': '/v1/hello_kitty'},
        expected={'foo': ['1', 2, [3]], 'bar': 123, 'baz': 'kakabyaka'},
        response=[[3], '2', {'key': 'val'}],
        exc_info='abracadabra',
        outcome=storage.Outcome.ERROR,
    )
    assert obj
    stg.finish_testcase()
    stg.finish_session()
    assert stg.count() == 1
    assert stg.count(session_uuid) == 1
    retrieved = list(stg.results(session_uuid=session_uuid))
    assert len(retrieved) == 1
    for obj_got in retrieved:
        _assert_testresult_equality(obj, obj_got)
    stg.close_db()
    # now reopen
    stg = storage.Storage(fname)
    sessions = list(stg.get_sessions())
    assert len(sessions) == 1
    assert sessions[0].session_uuid == session_uuid
    retrieved = list(stg.results(session_uuid=session_uuid))
    assert len(retrieved) == 1
    for obj_got in retrieved:
        _assert_testresult_equality(obj, obj_got)
    s_rec = stg.get_session(session_uuid)
    assert s_rec.session_uuid == session_uuid
    assert s_rec.start_ms > 0
    assert s_rec.finish_ms >= s_rec.start_ms
    assert s_rec.name == s_name
    assert s_rec.description == s_desc
    assert s_rec.num_passed_testcases == 0
    assert s_rec.num_skipped_testcases == 0
    assert s_rec.num_failed_testcases == 0
    assert s_rec.num_error_testcases == 1
    assert s_rec.num_passed_tests == 0
    assert s_rec.num_skipped_tests == 0
    assert s_rec.num_failed_tests == 0
    assert s_rec.num_error_tests == 1
    assert s_rec.outcome == storage.Outcome.ERROR

    t_recs = list(stg.get_testcases(session_uuid))
    assert len(t_recs) == 1
    testcase = t_recs[0]
    assert testcase.testcase_id == 0
    assert testcase.session_uuid == session_uuid
    assert testcase.start_ms > 0
    assert testcase.finish_ms >= testcase.start_ms
    assert testcase.name == t_name
    assert testcase.description == t_desc
    assert testcase.num_passed_tests == 0
    assert testcase.num_skipped_tests == 0
    assert testcase.num_failed_tests == 0
    assert testcase.num_error_tests == 1
    assert testcase.outcome == storage.Outcome.ERROR

    stg.close_db()
    os.unlink(fname)


def test_storage_io1():
    stg = storage.Storage(':memory:', keep_old=False, store_all=True)
    session_uuid = stg.start_session(name='test session', description='')
    testcase_id = stg.start_testcase(name=_random_name())
    obj00 = stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700000999,
            finish_ms=1558700001999,
            request=[],
            expected=['1', 2, [3]],
            response=[[3], '2', {'key': 'val'}],
            exc_info='abracadabra',
            outcome=storage.Outcome.ERROR,
        ),
    )
    obj01 = stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700002999,
            finish_ms=1558700003999,
            request={'foo': 'bar', 'int': 121, 'dict': {'A': 0}},
            expected={'first': 1, 'last': 999},
            response={'first': 9, 'last': 999, 'extra': {}},
            exc_info='',
            outcome=storage.Outcome.SKIPPED,
        ),
    )
    stg.finish_testcase()
    testcase_id = stg.start_testcase(name=_random_name())
    obj10 = stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700004999,
            finish_ms=1558700005999,
            request={'kaka': 'byaka'},
            expected={},
            response={},
            exc_info='',
            outcome=storage.Outcome.PASSED,
        ),
    )
    stg.finish_testcase()
    stg.finish_session()
    assert stg.count() == 3
    got = list(stg.results(session_uuid=session_uuid))
    assert len(got) == 3
    _assert_testresult_equality(got[0], obj00)
    _assert_testresult_equality(got[1], obj01)
    _assert_testresult_equality(got[2], obj10)


def test_storage_io2():
    stg = storage.Storage(':memory:', keep_old=False, store_all=False)
    session_uuid = stg.start_session(name='test session', description='')
    testcase_id = stg.start_testcase(name=_random_name())
    obj00 = stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700000999,
            finish_ms=1558700001999,
            request=[],
            expected=['1', 2, [3]],
            response=[[3], '2', {'key': 'val'}],
            exc_info='abracadabra',
            outcome=storage.Outcome.ERROR,
        ),
    )
    stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700002999,
            finish_ms=1558700003999,
            request={'foo': 'bar', 'int': 121, 'dict': {'A': 0}},
            expected={'first': 1, 'last': 999},
            response={'first': 9, 'last': 999, 'extra': {}},
            exc_info='',
            outcome=storage.Outcome.SKIPPED,
        ),
    )
    stg.finish_testcase()
    testcase_id = stg.start_testcase(name=_random_name())
    stg.add_result(
        storage.TestResult(
            test_id=stg.next_test_id(),
            testcase_id=testcase_id,
            session_uuid=session_uuid,
            start_ms=1558700004999,
            finish_ms=1558700005999,
            request={'kaka': 'byaka'},
            expected={},
            response={},
            exc_info='',
            outcome=storage.Outcome.PASSED,
        ),
    )
    stg.finish_testcase()
    stg.finish_session()
    assert stg.count() == 1
    got = list(stg.results(session_uuid=session_uuid))
    assert len(got) == 1
    _assert_testresult_equality(got[0], obj00)


def test_storage_backported_io():
    testsuite = [
        [
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': ['1', 2, [3]],
                'response': [[3], '2', {'key': 'val'}],
                'exc_info': '',
                'outcome': storage.Outcome.FAILED,
            },
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': {},
                'response': {},
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': [1, 2, 3],
                'response': [1, 2, 3],
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
        ],
        [
            {
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {},
                'response': {},
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
            {
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {'foo': 'bar'},
                'response': {'foo': 'bar'},
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
        ],
        [
            {
                'request': {'url': 'localhost/v1/resource3'},
                'expected': {},
                'response': {},
                'exc_info': 'something went wrong',
                'outcome': storage.Outcome.ERROR,
            },
            {
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {'foo': 'bar'},
                'response': {},
                'exc_info': '',
                'outcome': storage.Outcome.SKIPPED,
            },
        ],
    ]

    stg = storage.Storage(':memory:', store_all=True)
    stg.start_session(name=_random_name(), description='')
    stored = []
    for testcase in testsuite:
        stg.start_testcase(name=_random_name())
        for test in testcase:
            obj = stg.add(
                request=test['request'],
                expected=test['expected'],
                response=test['response'],
                exc_info=test['exc_info'],
                outcome=test['outcome'],
            )
            assert obj.request == test['request']
            assert obj.expected == test['expected']
            assert obj.response == test['response']
            assert obj.exc_info == test['exc_info']
            assert obj.outcome == test['outcome']
            stored.append(obj)
        stg.finish_testcase()
    stg.finish_session()
    assert stg.count() == len(stored)
    retrieved = list(stg.results(session_uuid=stg.current_session_uuid()))
    assert len(retrieved) == len(stored)
    for obj_put, obj_got in zip(stored, retrieved):
        _assert_testresult_equality(obj_put, obj_got)


def test_storage_statistic():
    testsuite = [
        [
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': ['1', 2, [3]],
                'response': [[3], 2, '1'],
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': {},
                'response': {},
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
            {
                'request': {'url': 'localhost/v1/resource'},
                'expected': [1, 2, 3],
                'response': [1, 2, 3],
                'exc_info': '',
                'outcome': storage.Outcome.PASSED,
            },
        ],
        [
            {
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {},
                'response': [],
                'exc_info': '',
                'outcome': storage.Outcome.FAILED,
            },
            {
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {'foo': 'bar'},
                'response': {'foo': 'bar2'},
                'exc_info': '',
                'outcome': storage.Outcome.FAILED,
            },
        ],
        [
            {
                'request': {'url': 'localhost/v1/resource3'},
                'expected': {},
                'response': {},
                'exc_info': '',
                'outcome': storage.Outcome.SKIPPED,
            },
        ],
    ]

    stg = storage.Storage(':memory:', store_all=True)
    s_name = _random_name()
    s_desc = _random_name() + _random_name()
    session_uuid = stg.start_session(name=s_name, description=s_desc)
    for testcase in testsuite:
        stg.start_testcase(name=_random_name())
        for test in testcase:
            stg.add(
                request=test['request'],
                expected=test['expected'],
                response=test['response'],
                exc_info=test['exc_info'],
                outcome=test['outcome'],
            )
        stg.finish_testcase()
    stg.finish_session()
    sess_stat = stg.get_session(session_uuid)

    assert sess_stat

    assert sess_stat.name == s_name
    assert sess_stat.description == s_desc
    assert sess_stat.start_ms > 0
    assert sess_stat.finish_ms >= sess_stat.start_ms

    assert sess_stat.outcome == storage.Outcome.FAILED
    assert sess_stat.num_passed_tests == 3
    assert sess_stat.num_failed_tests == 2
    assert sess_stat.num_skipped_tests == 1
    assert sess_stat.num_error_tests == 0

    assert sess_stat.num_passed_testcases == 1
    assert sess_stat.num_failed_testcases == 1
    assert sess_stat.num_skipped_testcases == 1
    assert sess_stat.num_error_testcases == 0

    cases = list(stg.get_testcases(stg.current_session_uuid()))

    assert len(cases) == 3
    assert cases[0].num_passed_tests == 3
    assert cases[0].num_skipped_tests == 0
    assert cases[0].num_failed_tests == 0
    assert cases[0].num_error_tests == 0

    assert cases[1].num_passed_tests == 0
    assert cases[1].num_skipped_tests == 0
    assert cases[1].num_failed_tests == 2
    assert cases[1].num_error_tests == 0

    assert cases[2].num_passed_tests == 0
    assert cases[2].num_skipped_tests == 1
    assert cases[2].num_failed_tests == 0
    assert cases[2].num_error_tests == 0
