import os

from sibilla import reporter
from sibilla import storage


def _assert_textify(obj, expected):
    result = reporter.textify(obj)
    assert result == expected


def test_textify():
    _assert_textify([], '[]\n')
    _assert_textify({}, '{}\n')
    _assert_textify(
        {'foo': 1, 'bar': [1, 2, 3]},
        """{
    "bar": [
        1,
        2,
        3
    ],
    "foo": 1
}
""",
    )


def _assert_diff(left, right, expected):
    diff = reporter.format_diff(left, right)
    got = diff.split('\n')
    need = expected.split('\n')
    assert len(got) == len(need)
    for line_num, (s_got, s_need) in enumerate(zip(got, need)):
        assert s_got == s_need, f'fail at line {line_num}'


def test_diff():
    _assert_diff([], [], '')
    _assert_diff({}, {}, '')
    _assert_diff(
        {
            'missing': 123,
            'shared1': 'aaa',
            'shared2': 'zzz',
            'wrong_arr': [1, 2, 3],
        },
        {
            'shared1': 'aaa',
            'shared2': 'zzz',
            'extra': 321,
            'wrong_arr': [4, 5, 6, {}],
        },
        """--- expected

+++ response

@@ -1,11 +1,12 @@

 {
-    "missing": 123,
+    "extra": 321,
     "shared1": "aaa",
     "shared2": "zzz",
     "wrong_arr": [
-        1,
-        2,
-        3
+        4,
+        5,
+        6,
+        {}
     ]
 }
 """,
    )


def test_empty(workdir, stg):
    retlist = reporter.generate_report(
        outdir=workdir, stg=stg, session_uuid='',
    )
    assert not retlist


def test_all_ok(workdir, stg):
    testsuite = [
        [
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
            {
                'name': 'testcase 1',
                'request': {'url': 'localhost/v1/resource'},
                'expected': [1, 2, 3],
            },
        ],
        [
            {
                'name': 'testcase 2',
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {},
            },
            {
                'name': 'testcase 2',
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {'foo': 'bar'},
            },
        ],
        [
            {
                'name': 'testcase 3',
                'request': {'url': 'localhost/v1/resource3'},
                'expected': {},
            },
            {
                'name': 'testcase 3',
                'request': {'url': 'localhost/v1/resource2'},
                'expected': {'foo': 'bar'},
            },
        ],
    ]
    session_uuid = stg.start_session(name='bzzz', description='pfff')
    for testcase in testsuite:
        stg.start_testcase(name='bzzz')
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
    fnames = reporter.generate_report(
        outdir=workdir, stg=stg, session_uuid=session_uuid,
    )
    assert fnames
    assert os.path.exists(fnames[0])
