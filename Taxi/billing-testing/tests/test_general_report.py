import os.path

from sibilla import reporter
from sibilla import storage


def test_empty(workdir, stg):
    fname = reporter.generate_general_report(outdir=workdir, stg=stg)
    assert fname
    assert os.path.exists(fname)
    report = open(fname, encoding='utf_8_sig', mode='rt').read()
    assert 'GENERAL OUTCOME: SKIPPED' in report


def test_ok(workdir, stg):
    sessions = [
        [  # session 1
            [  # testcase 1
                {
                    'name': 'testcase 1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['1', 2, [3]],
                },
                {
                    'name': 'testcase 1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': {},
                },
            ],
            [  # testcase 2
                {
                    'name': 'testcase 2',
                    'request': {'url': 'localhost/v1/resource2'},
                    'expected': {},
                },
            ],
            [  # testcase 3
                {
                    'name': 'testcase 3',
                    'request': {'url': 'localhost/v1/resource3'},
                    'expected': {},
                },
            ],
        ],
        [  # session 2
            [  # testcase 1
                {
                    'name': 'testcase 2.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['kaka'],
                },
                {
                    'name': 'testcase 2.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': {'byaka': ['Zaka', 'Lyaka']},
                },
            ],
            [  # testcase 2
                {
                    'name': 'testcase 2.2',
                    'request': {'url': 'localhost/v1/resource2'},
                    'expected': {},
                },
            ],
        ],
        [  # session 3
            [  # testcase 1
                {
                    'name': 'testcase 3.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['uuu'],
                },
            ],
        ],
    ]

    for session_ix, session in enumerate(sessions):
        session_uuid = stg.start_session(
            name=f'session{session_ix}', description=f'session #{session_ix}',
        )
        for testcase_ix, testcase in enumerate(session):
            stg.start_testcase(
                name=f'testcase{testcase_ix}',
                description=f'testcase {session_ix}.{testcase_ix}',
            )
            for test in testcase:
                stg.add(
                    request=test['request'],
                    expected=test['expected'],
                    response=test['expected'],
                    exc_info='',
                    outcome=storage.Outcome.PASSED,
                )
            stg.finish_testcase()
        stg.finish_session()
        reporter.generate_report(
            outdir=workdir, stg=stg, session_uuid=session_uuid,
        )
    fname = reporter.generate_general_report(outdir=workdir, stg=stg)
    assert fname
    assert os.path.exists(fname)
    report = open(fname, encoding='utf_8_sig', mode='rt').read()
    assert 'session0: PASSED' in report
    assert 'session1: PASSED' in report
    assert 'session2: PASSED' in report
    assert 'GENERAL OUTCOME: PASSED' in report


def test_bad(workdir, stg):
    sessions = [
        [  # session 1
            [  # testcase 1
                {
                    'name': 'testcase 1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['1', 2, [3]],
                    'response': {},
                    'outcome': storage.Outcome.FAILED,
                },
                {
                    'name': 'testcase 1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': {},
                    'response': {},
                    'outcome': storage.Outcome.PASSED,
                },
            ],
            [  # testcase 2
                {
                    'name': 'testcase 2',
                    'request': {'url': 'localhost/v1/resource2'},
                    'expected': {},
                    'response': {},
                    'outcome': storage.Outcome.PASSED,
                },
            ],
            [  # testcase 3
                {
                    'name': 'testcase 3',
                    'request': {'url': 'localhost/v1/resource3'},
                    'expected': {},
                    'response': {},
                    'outcome': storage.Outcome.PASSED,
                },
            ],
        ],
        [  # session 2
            [  # testcase 1
                {
                    'name': 'testcase 2.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['kaka'],
                    'response': ['byaka'],
                    'outcome': storage.Outcome.FAILED,
                },
                {
                    'name': 'testcase 2.2',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': {'byaka': ['Zaka', 'Lyaka']},
                    'response': {},
                    'outcome': storage.Outcome.FAILED,
                },
            ],
            [  # testcase 2
                {
                    'name': 'testcase 2.2',
                    'request': {'url': 'localhost/v1/resource2'},
                    'expected': {},
                    'response': {},
                    'outcome': storage.Outcome.PASSED,
                },
            ],
        ],
        [  # session 3
            [  # testcase 1
                {
                    'name': 'testcase 3.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['uuu'],
                    'response': ['uuu'],
                    'outcome': storage.Outcome.PASSED,
                },
            ],
        ],
    ]

    for session_ix, session in enumerate(sessions):
        session_uuid = stg.start_session(
            name=f'session{session_ix}', description=f'session #{session_ix}',
        )
        for testcase_ix, testcase in enumerate(session):
            stg.start_testcase(
                name=f'testcase{testcase_ix}',
                description=f'testcase {session_ix}.{testcase_ix}',
            )
            for test in testcase:
                stg.add(
                    request=test['request'],
                    expected=test['expected'],
                    response=test['response'],
                    outcome=test['outcome'],
                    exc_info='',
                )
            stg.finish_testcase()
        stg.finish_session()
        reporter.generate_report(
            outdir=workdir, stg=stg, session_uuid=session_uuid,
        )
    fname = reporter.generate_general_report(outdir=workdir, stg=stg)
    assert fname
    assert os.path.exists(fname)
    report = open(fname, encoding='utf_8_sig', mode='rt').read()
    assert 'session0: FAILED' in report
    assert 'session1: FAILED' in report
    assert 'session2: PASSED' in report
    assert 'GENERAL OUTCOME: FAILED' in report


def test_error(workdir, stg):
    sessions = [
        [  # session 3
            [  # testcase 1
                {
                    'name': 'testcase 3.1',
                    'request': {'url': 'localhost/v1/resource'},
                    'expected': ['1', 2, [3]],
                    'response': {},
                    'outcome': storage.Outcome.ERROR,
                },
            ],
            [  # testcase 2
                {
                    'name': 'testcase 3.2',
                    'request': {'url': 'localhost/v1/resource3'},
                    'expected': {},
                    'response': {},
                    'outcome': storage.Outcome.PASSED,
                },
            ],
        ],
    ]

    for session_ix, session in enumerate(sessions):
        session_uuid = stg.start_session(
            name=f'session{session_ix}', description=f'session #{session_ix}',
        )
        for testcase_ix, testcase in enumerate(session):
            stg.start_testcase(
                name=f'testcase{testcase_ix}',
                description=f'testcase {session_ix}.{testcase_ix}',
            )
            for test in testcase:
                stg.add(
                    request=test['request'],
                    expected=test['expected'],
                    response=test['response'],
                    outcome=test['outcome'],
                    exc_info='',
                )
            stg.finish_testcase()
        stg.finish_session()
        reporter.generate_report(
            outdir=workdir, stg=stg, session_uuid=session_uuid,
        )
    fname = reporter.generate_general_report(outdir=workdir, stg=stg)
    assert fname
    assert os.path.exists(fname)
    report = open(fname, encoding='utf_8_sig', mode='rt').read()
    assert 'session0: ERROR' in report
    assert 'GENERAL OUTCOME: ERROR' in report
