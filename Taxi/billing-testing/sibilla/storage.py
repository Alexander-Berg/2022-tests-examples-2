import collections
import datetime
import enum
import json
import sqlite3
import typing
import uuid

# Outcome for every entity class:
# for Test Run:
#   PASSED  ::= request finished and response match to expected
#   SKIPPED ::= request was skipped. results are not counted in final stats
#   FAILED  ::= request finished but response does not match to expected
#   ERROR   ::= request execution was not finished normally for some reason
#   test priority: ERROR > FAILED = SKIPPED = PASSED
#
# for Testcase:
#   PASSED  ::= all test in testcase finished with PASSED or SKIPPED outcome
#   SKIPPED ::= all tests in testcase were SKIPPED or testcase was skipped
#   FAILED  ::= some tests in testcase have FAILED outcome
#   ERROR   ::= testcase not started or some tests have ERROR outcome
#   testcase priority: ERROR > FAILED > SKIPPED > PASSED
#
# for Testsuite/Session:
#   PASSED  ::= all testcases in testsuite finished with PASSED|SKIPPED outcome
#   SKIPPED ::= all testcases were SKIPPED or session is not complete
#   FAILED  ::= one or more testscase in testsuite has FAILED outcome
#   ERROR   ::= testsuite not started or some testcases have ERROR outcome
#   testsuite priority: ERROR > FAILED > SKIPPED > PASSED
@enum.unique
class Outcome(enum.Enum):
    PASSED = 'PASSED'
    SKIPPED = 'SKIPPED'
    FAILED = 'FAILED'
    ERROR = 'ERROR'

    @staticmethod
    def parse(text: str) -> 'Outcome':
        for variant in Outcome:
            if variant.name == text:
                return variant
        raise ValueError('bad value: {}'.format(text))


class Statistics:
    """
    Simple counter for PASSED/SKIPPED/FAILED/ERROR states
    """

    def __init__(
            self,
            *,
            passed: int = 0,
            skipped: int = 0,
            failed: int = 0,
            error: int = 0,
    ):
        self.__counts: collections.OrderedDict = collections.OrderedDict()
        self.assign(passed=passed, skipped=skipped, failed=failed, error=error)

    def assign(
            self,
            *,
            passed: int = 0,
            skipped: int = 0,
            failed: int = 0,
            error: int = 0,
    ):
        self.__counts[Outcome.PASSED] = passed
        self.__counts[Outcome.SKIPPED] = skipped
        self.__counts[Outcome.FAILED] = failed
        self.__counts[Outcome.ERROR] = error

    def reset(self):
        self.assign()

    def add(self, outcome: Outcome, count: int = 1) -> None:
        self.__counts[outcome] += count

    def add_all(self, substat: 'Statistics') -> None:
        for outcome in Outcome:
            self.add(outcome, substat[outcome])

    def __getitem__(self, item: typing.Union[str, Outcome]) -> int:
        return (
            self.__counts[item]
            if isinstance(item, Outcome)
            else self.counts[item]
        )

    @property
    def counts(self) -> collections.OrderedDict:
        ret: collections.OrderedDict = collections.OrderedDict()
        for outcome, value in self.__counts.items():
            ret[outcome.name] = value
        return ret

    @property
    def aggregated_count(self) -> int:
        return sum(self.__counts.values())

    @property
    def aggregated_outcome(self) -> Outcome:
        if self.__counts[Outcome.ERROR]:
            return Outcome.ERROR
        if self.__counts[Outcome.FAILED]:
            return Outcome.FAILED
        if self.__counts[Outcome.PASSED]:
            return Outcome.PASSED
        return Outcome.SKIPPED


class SessionRec(typing.NamedTuple):
    session_uuid: str
    start_ms: int
    finish_ms: int
    name: str
    description: str
    num_passed_testcases: int
    num_skipped_testcases: int
    num_failed_testcases: int
    num_error_testcases: int
    num_passed_tests: int
    num_skipped_tests: int
    num_failed_tests: int
    num_error_tests: int
    outcome: Outcome


class TestcaseRec(typing.NamedTuple):
    testcase_id: int
    session_uuid: str
    start_ms: int
    finish_ms: int
    name: str
    description: str
    num_passed_tests: int
    num_skipped_tests: int
    num_failed_tests: int
    num_error_tests: int
    outcome: Outcome


class TestResult(typing.NamedTuple):
    test_id: int
    testcase_id: int
    session_uuid: str
    start_ms: int
    finish_ms: int
    request: typing.Union[
        typing.List[typing.Any], typing.Dict[str, typing.Any],
    ]
    expected: typing.Union[
        typing.List[typing.Any], typing.Dict[str, typing.Any],
    ]
    response: typing.Union[
        typing.List[typing.Any], typing.Dict[str, typing.Any],
    ]
    exc_info: str
    outcome: Outcome


def now_ms() -> int:
    """
    unix timestamp in microseconds
    :return: time in microseconds since 1970-01-01 00:00:00.000 UTC
    """
    return int(
        (
            datetime.datetime.now() - datetime.datetime.fromtimestamp(0)
        ).total_seconds()
        * 1000,
    )


# pylint:disable=too-many-instance-attributes
class Storage:
    def __init__(
            self,
            filename: str,
            *,
            store_all: bool = False,
            keep_old: bool = True,
    ):
        """

        :param filename: file name for sqlite database
        :param store_all: False ::= only ERROR and FAIL events will be stored
                          True ::= all events will be stored
        :param keep_old:  False ::= clean up database before start work
                          True ::= keep info about old runs
        """
        super().__init__()
        self.__filename = filename
        self.__store_all = store_all
        self.__db = sqlite3.connect(self.__filename)
        self.create_db(keep_old)
        self.__session_uuid = ''
        self.__session_start_ms = 0
        self.__by_tests = Statistics()
        self.__by_cases = Statistics()
        self.__for_case = Statistics()
        self.__testcase_id = 0
        self.__testcase_started = False
        self.__test_id = 0
        self.__start_ms = 0

    def create_db(self, keep_old: bool = True) -> None:
        cur = self.__db.cursor()
        if not keep_old:
            cur.executescript(
                """
                BEGIN EXCLUSIVE TRANSACTION;
                DROP TABLE IF EXISTS results;
                DROP TABLE IF EXISTS testcases;
                DROP INDEX IF EXISTS testcase_start_ms_idx;
                DROP TABLE IF EXISTS sessions;
                DROP INDEX IF EXISTS session_start_ms_idx;
                COMMIT TRANSACTION;
            """,
            )
        cur.executescript(
            """
            BEGIN EXCLUSIVE TRANSACTION;
            CREATE TABLE IF NOT EXISTS results (
                test_id       INTEGER NOT NULL,
                testcase_id   INTEGER NOT NULL,
                session_uuid  TEXT NOT NULL,
                start_ms      INTEGER NOT NULL,
                finish_ms     INTEGER NOT NULL,
                request       TEXT NOT NULL,
                expected      TEXT NOT NULL,
                response      TEXT NOT NULL,
                exc_info      TEXT NOT NULL,
                outcome       TEXT NOT NULL,
                PRIMARY KEY (session_uuid, testcase_id, test_id)
            );
            CREATE TABLE IF NOT EXISTS testcases (
                testcase_id       INTEGER NOT NULL,
                session_uuid      TEXT NOT NULL,
                start_ms          INTEGER NOT NULL,
                finish_ms         INTEGER NOT NULL,
                name              TEXT NOT NULL,
                description       TEXT NOT NULL,
                num_passed_tests  INTEGER NOT NULL,
                num_skipped_tests INTEGER NOT NULL,
                num_failed_tests  INTEGER NOT NULL,
                num_error_tests  INTEGER NOT NULL,
                outcome           TEXT NOT NULL,
                PRIMARY KEY (session_uuid, testcase_id)
            );
            CREATE INDEX IF NOT EXISTS testcase_start_ms_idx
                ON testcases (start_ms);
            CREATE TABLE IF NOT EXISTS sessions (
                session_uuid          TEXT NOT NULL,
                start_ms              INTEGER NOT NULL,
                finish_ms             INTEGER NOT NULL,
                name                  TEXT NOT NULL,
                description           TEXT NOT NULL,
                num_passed_testcases  INTEGER NOT NULL,
                num_skipped_testcases INTEGER NOT NULL,
                num_failed_testcases  INTEGER NOT NULL,
                num_error_testcases  INTEGER NOT NULL,
                num_passed_tests      INTEGER NOT NULL,
                num_skipped_tests     INTEGER NOT NULL,
                num_failed_tests      INTEGER NOT NULL,
                num_error_tests      INTEGER NOT NULL,
                outcome               TEXT NOT NULL,
                PRIMARY KEY (session_uuid)
            );
            CREATE INDEX IF NOT EXISTS session_start_ms_idx
                ON sessions (start_ms);
            COMMIT TRANSACTION;
        """,
        )
        cur.close()

    def sync(self):
        self.__db.commit()

    def close_db(self):
        self.sync()
        self.__db.close()

    def start_session(self, name: str, description: str = '') -> str:
        self.__session_uuid = str(uuid.uuid4())
        self.__session_start_ms = now_ms()
        self.__testcase_id = 0
        self.__test_id = 0
        self.__by_cases.reset()
        self.__by_tests.reset()
        self.__for_case.reset()
        cur = self.__db.cursor()
        cur.execute(
            """
            INSERT INTO sessions (
                session_uuid,
                start_ms,
                finish_ms,
                name,
                description,
                num_passed_testcases,
                num_skipped_testcases,
                num_failed_testcases,
                num_error_testcases,
                num_passed_tests,
                num_skipped_tests,
                num_failed_tests,
                num_error_tests,
                outcome
            )
            VALUES (
                :session_uuid,
                :start_ms,
                :finish_ms,
                :name,
                :description,
                :num_passed_testcases,
                :num_skipped_testcases,
                :num_failed_testcases,
                :num_error_testcases,
                :num_passed_tests,
                :num_skipped_tests,
                :num_failed_tests,
                :num_error_tests,
                :outcome)
        """,
            {
                'session_uuid': self.current_session_uuid(),
                'start_ms': self.__session_start_ms,
                'finish_ms': 0,
                'name': name,
                'description': description,
                'num_passed_testcases': 0,
                'num_skipped_testcases': 0,
                'num_failed_testcases': 0,
                'num_error_testcases': 0,
                'num_passed_tests': 0,
                'num_skipped_tests': 0,
                'num_failed_tests': 0,
                'num_error_tests': 0,
                'outcome': Outcome.SKIPPED.name,
            },
        )
        cur.close()
        self.sync()
        return self.current_session_uuid()

    def finish_session(self) -> None:
        self.finish_testcase()
        finish_ms = now_ms()
        session_outcome = self.__by_cases.aggregated_outcome
        cur = self.__db.cursor()
        cur.execute(
            """
            UPDATE sessions
               SET finish_ms=:finish_ms,
                   num_passed_testcases = :num_passed_testcases,
                   num_skipped_testcases = :num_skipped_testcases,
                   num_failed_testcases = :num_failed_testcases,
                   num_error_testcases = :num_error_testcases,
                   num_passed_tests = :num_passed_tests,
                   num_skipped_tests = :num_skipped_tests,
                   num_failed_tests = :num_failed_tests,
                   num_error_tests = :num_error_tests,
                   outcome = :outcome
             WHERE session_uuid=:session_uuid
        """,
            {
                'finish_ms': finish_ms,
                'num_passed_testcases': self.__by_cases[Outcome.PASSED],
                'num_skipped_testcases': self.__by_cases[Outcome.SKIPPED],
                'num_failed_testcases': self.__by_cases[Outcome.FAILED],
                'num_error_testcases': self.__by_cases[Outcome.ERROR],
                'num_passed_tests': self.__by_tests[Outcome.PASSED],
                'num_skipped_tests': self.__by_tests[Outcome.SKIPPED],
                'num_failed_tests': self.__by_tests[Outcome.FAILED],
                'num_error_tests': self.__by_tests[Outcome.ERROR],
                'outcome': session_outcome.name,
                'session_uuid': self.current_session_uuid(),
            },
        )
        cur.close()
        self.sync()

    def start_testcase(self, name: str, description: str = '') -> int:
        if self.__testcase_started:
            self.finish_testcase()
        self.__start_ms = now_ms()
        cur = self.__db.cursor()
        cur.execute(
            """
            INSERT INTO testcases (
                testcase_id,
                session_uuid,
                start_ms,
                finish_ms,
                name,
                description,
                num_passed_tests,
                num_skipped_tests,
                num_failed_tests,
                num_error_tests,
                outcome
            ) VALUES (
                :testcase_id,
                :session_uuid,
                :start_ms,
                :finish_ms,
                :name,
                :description,
                :num_passed_tests,
                :num_skipped_tests,
                :num_failed_tests,
                :num_error_tests,
                :outcome
            )
        """,
            {
                'testcase_id': self.current_testcase_id(),
                'session_uuid': self.current_session_uuid(),
                'start_ms': self.__start_ms,
                'finish_ms': 0,
                'name': name,
                'description': description,
                'num_passed_tests': 0,
                'num_skipped_tests': 0,
                'num_failed_tests': 0,
                'num_error_tests': 0,
                'outcome': Outcome.SKIPPED.name,
            },
        )
        cur.close()
        self.sync()
        self.__for_case.reset()
        self.__test_id = 0
        self.__testcase_started = True
        return self.current_testcase_id()

    def finish_testcase(self) -> None:
        if not self.__testcase_started:
            return
        finish_ms = now_ms()
        testcase_outcome = self.__for_case.aggregated_outcome
        self.__by_tests.add_all(self.__for_case)
        self.__by_cases.add(testcase_outcome)
        cur = self.__db.cursor()
        cur.execute(
            """
            UPDATE testcases
               SET finish_ms = :finish_ms,
                   num_passed_tests = :num_passed_tests,
                   num_skipped_tests = :num_skipped_tests,
                   num_failed_tests = :num_failed_tests,
                   num_error_tests = :num_error_tests,
                   outcome = :outcome
             WHERE session_uuid = :session_uuid
               AND testcase_id = :testcase_id
        """,
            {
                'finish_ms': finish_ms,
                'num_passed_tests': self.__for_case[Outcome.PASSED],
                'num_skipped_tests': self.__for_case[Outcome.SKIPPED],
                'num_failed_tests': self.__for_case[Outcome.FAILED],
                'num_error_tests': self.__for_case[Outcome.ERROR],
                'outcome': testcase_outcome.name,
                'session_uuid': self.current_session_uuid(),
                'testcase_id': self.current_testcase_id(),
            },
        )
        cur.close()
        self.sync()

        self.__testcase_started = False
        self.__testcase_id += 1

    def current_session_uuid(self) -> str:
        return self.__session_uuid

    def current_testcase_id(self) -> int:
        return self.__testcase_id

    def next_test_id(self) -> int:
        ret = self.__test_id
        self.__test_id += 1
        return ret

    def add(
            self,
            *,
            request: typing.Union[
                typing.List[typing.Any], typing.Dict[str, typing.Any],
            ],
            expected: typing.Union[
                typing.List[typing.Any], typing.Dict[str, typing.Any],
            ],
            response: typing.Union[
                typing.List[typing.Any], typing.Dict[str, typing.Any],
            ],
            exc_info: str,
            outcome: Outcome,
    ) -> TestResult:
        obj = TestResult(
            test_id=self.next_test_id(),
            testcase_id=self.current_testcase_id(),
            session_uuid=self.current_session_uuid(),
            start_ms=self.__start_ms,
            finish_ms=now_ms(),
            request=request,
            expected=expected,
            response=response,
            exc_info=exc_info,
            outcome=outcome,
        )
        return self.add_result(obj)

    def add_result(self, test_result: TestResult) -> TestResult:
        if self.__store_all or test_result.outcome not in (
                Outcome.PASSED,
                Outcome.SKIPPED,
        ):
            cur = self.__db.cursor()
            cur.execute(
                """
                INSERT INTO results (
                    test_id,
                    testcase_id,
                    session_uuid,
                    start_ms,
                    finish_ms,
                    request,
                    expected,
                    response,
                    exc_info,
                    outcome
                ) VALUES (
                    :test_id,
                    :testcase_id,
                    :session_uuid,
                    :start_ms,
                    :finish_ms,
                    :request,
                    :expected,
                    :response,
                    :exc_info,
                    :outcome
                )
            """,
                {
                    'test_id': test_result.test_id,
                    'testcase_id': test_result.testcase_id,
                    'session_uuid': test_result.session_uuid,
                    'start_ms': test_result.start_ms,
                    'finish_ms': test_result.finish_ms,
                    'request': json.dumps(test_result.request),
                    'expected': json.dumps(test_result.expected),
                    'response': json.dumps(test_result.response),
                    'exc_info': test_result.exc_info,
                    'outcome': test_result.outcome.name,
                },
            )
            cur.close()
            self.sync()
        self.__for_case.add(test_result.outcome)
        return test_result

    def count(self, session_uuid: typing.Optional[str] = None) -> int:
        cur = self.__db.cursor()
        if session_uuid:
            cur.execute(
                """
                SELECT COUNT(*) FROM results
                 WHERE session_uuid=:session_uuid
                 """,
                {'session_uuid': session_uuid},
            )
        else:
            cur.execute('SELECT COUNT(*) FROM results')
        row = cur.fetchone()
        count = row[0]
        cur.close()
        return count

    def results(
            self,
            session_uuid: str,
            *,
            testcase_id: typing.Optional[int] = None,
    ) -> typing.Generator[TestResult, None, None]:
        cur = self.__db.cursor()
        if testcase_id is not None:
            cur.execute(
                """
                SELECT test_id,
                       testcase_id,
                       session_uuid,
                       start_ms,
                       finish_ms,
                       request,
                       expected,
                       response,
                       exc_info,
                       outcome
                  FROM results
                 WHERE session_uuid=:session_uuid
                   AND testcase_id=:testcase_id
                ORDER BY test_id
                """,
                {'session_uuid': session_uuid, 'testcase_id': testcase_id},
            )
        else:
            cur.execute(
                """
                SELECT test_id,
                       testcase_id,
                       session_uuid,
                       start_ms,
                       finish_ms,
                       request,
                       expected,
                       response,
                       exc_info,
                       outcome
                  FROM results
                 WHERE session_uuid=:session_uuid
                ORDER BY testcase_id, test_id
                """,
                {'session_uuid': session_uuid},
            )
        keymap = {x[0]: ix for ix, x in enumerate(cur.description)}
        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                obj = TestResult(
                    test_id=row[keymap['test_id']],
                    testcase_id=row[keymap['testcase_id']],
                    session_uuid=row[keymap['session_uuid']],
                    start_ms=row[keymap['start_ms']],
                    finish_ms=row[keymap['finish_ms']],
                    request=json.loads(row[keymap['request']]),
                    expected=json.loads(row[keymap['expected']]),
                    response=json.loads(row[keymap['response']]),
                    exc_info=row[keymap['exc_info']],
                    outcome=Outcome.parse(row[keymap['outcome']]),
                )
                yield obj
        cur.close()

    def get_sessions(self) -> typing.Generator[SessionRec, None, None]:
        cur = self.__db.cursor()
        cur.execute(
            """
            SELECT session_uuid,
                   start_ms,
                   finish_ms,
                   name,
                   description,
                   num_passed_testcases,
                   num_skipped_testcases,
                   num_failed_testcases,
                   num_error_testcases,
                   num_passed_tests,
                   num_skipped_tests,
                   num_failed_tests,
                   num_error_tests,
                   outcome
              FROM sessions
             ORDER BY start_ms
            """,
        )
        keymap = {x[0]: ix for ix, x in enumerate(cur.description)}
        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                obj = SessionRec(
                    session_uuid=row[keymap['session_uuid']],
                    start_ms=row[keymap['start_ms']],
                    finish_ms=row[keymap['finish_ms']],
                    name=row[keymap['name']],
                    description=row[keymap['description']],
                    num_passed_testcases=row[keymap['num_passed_testcases']],
                    num_skipped_testcases=row[keymap['num_skipped_testcases']],
                    num_failed_testcases=row[keymap['num_failed_testcases']],
                    num_error_testcases=row[keymap['num_error_testcases']],
                    num_passed_tests=row[keymap['num_passed_tests']],
                    num_skipped_tests=row[keymap['num_skipped_tests']],
                    num_failed_tests=row[keymap['num_failed_tests']],
                    num_error_tests=row[keymap['num_error_tests']],
                    outcome=Outcome.parse(row[keymap['outcome']]),
                )
                yield obj
        cur.close()

    def get_session(self, session_uuid: str) -> typing.Optional[SessionRec]:
        cur = self.__db.cursor()
        cur.execute(
            """
            SELECT session_uuid,
                   start_ms,
                   finish_ms,
                   name,
                   description,
                   num_passed_testcases,
                   num_skipped_testcases,
                   num_failed_testcases,
                   num_error_testcases,
                   num_passed_tests,
                   num_skipped_tests,
                   num_failed_tests,
                   num_error_tests,
                   outcome
              FROM sessions
             WHERE session_uuid=:session_uuid
            """,
            {'session_uuid': session_uuid},
        )
        keymap = {x[0]: ix for ix, x in enumerate(cur.description)}
        row = cur.fetchone()
        if row:
            ret: typing.Optional[SessionRec] = SessionRec(
                session_uuid=row[keymap['session_uuid']],
                start_ms=row[keymap['start_ms']],
                finish_ms=row[keymap['finish_ms']],
                name=row[keymap['name']],
                description=row[keymap['description']],
                num_passed_testcases=row[keymap['num_passed_testcases']],
                num_skipped_testcases=row[keymap['num_skipped_testcases']],
                num_failed_testcases=row[keymap['num_failed_testcases']],
                num_error_testcases=row[keymap['num_error_testcases']],
                num_passed_tests=row[keymap['num_passed_tests']],
                num_skipped_tests=row[keymap['num_skipped_tests']],
                num_failed_tests=row[keymap['num_failed_tests']],
                num_error_tests=row[keymap['num_error_tests']],
                outcome=Outcome.parse(row[keymap['outcome']]),
            )
        else:
            ret = None
        cur.close()
        return ret

    def get_testcases(
            self, session_uuid: str,
    ) -> typing.Generator[TestcaseRec, None, None]:
        cur = self.__db.cursor()
        cur.execute(
            """
            SELECT testcase_id,
                   session_uuid,
                   start_ms,
                   finish_ms,
                   name,
                   description,
                   num_passed_tests,
                   num_skipped_tests,
                   num_failed_tests,
                   num_error_tests,
                   outcome
              FROM testcases
             WHERE session_uuid = :session_uuid
             ORDER BY testcase_id
        """,
            {'session_uuid': session_uuid},
        )
        keymap = {x[0]: ix for ix, x in enumerate(cur.description)}
        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                obj = TestcaseRec(
                    testcase_id=row[keymap['testcase_id']],
                    session_uuid=row[keymap['session_uuid']],
                    start_ms=row[keymap['start_ms']],
                    finish_ms=row[keymap['finish_ms']],
                    name=row[keymap['name']],
                    description=row[keymap['description']],
                    num_passed_tests=row[keymap['num_passed_tests']],
                    num_skipped_tests=row[keymap['num_skipped_tests']],
                    num_failed_tests=row[keymap['num_failed_tests']],
                    num_error_tests=row[keymap['num_error_tests']],
                    outcome=Outcome.parse(row[keymap['outcome']]),
                )
                yield obj
        cur.close()
