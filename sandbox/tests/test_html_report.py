import json
import pytest
import re

import yatest.common

from sandbox.projects.devtools.reports import html_report

TEST_DATA = {
    "empty_results": [],
    "test_configure_error": [
        {
            "status": "FAILED",
            "rich-snippet": "Trying to use [[imp]]$S/junk/ya.make[[rst]] from the prohibited directory [[alt1]]junk[[rst]]",
            "path": "At top level",
            "toolchain": "linux",
            "error_type": "REGULAR",
            "messages": [
                {
                    "path": "At top level",
                    "type": "ERROR",
                    "text": "Trying to use [[imp]]$S/junk/path/ya.make[[rst]] from the prohibited directory [[alt1]]junk[[rst]]",
                }
            ],
            "type": "configure",
        }
    ],
    "test_configure_ok": [
        {
            "status": "OK",
            "uid": "9fccaacf04325f474acd8415542ae656",
            "path": "build/platform/java/jacoco-agent",
            "toolchain": "linux",
            "type": "configure",
        },
    ],
    "test_build_error": [
        {
            "status": "FAILED",
            "rich-snippet": "command gccfilter.pl -c \n1 error generated.",
            "path": "devtools/dummy_arcadia/test/broken_by_depends/lib3",
            "toolchain": "ALLOCATOR=LF-AUTOCHECK=yes-DEBUGINFO_LINES_ONLY=yes-NO_DEBUGINFO=no-USE_EAT_MY_DATA=yes-musl",
            "error_type": "REGULAR",
            "type": "build",
        },
    ],
    "test_before_suite": [
        {
            "status": "OK",
            "metrics": {
                "ru_rss": 0,
            },
            "links": {
                "logsdir": ["http://proxy.sandbox.yandex-team.ru"],
                "log": ["http://proxy.sandbox.yandex-team.ru"],
            },
            "tags": ["parametrize"],
            "subtest_name": "test_returncode[exit(0)-0]",
            "rich-snippet": "[[bad]][[rst]]",
            "suite_id": "1dbef30d2b4bdaebe7c8a8be50b6830b",
            "duration": 0.169806957244873,
            "path": "devtools/executor/tests/ut",
            "size": "medium",
            "type": "test",
            "name": "test.py",
        },
        {
            "status": "OK",
            "links": {
                "stderr_run1": ["http://proxy.sandbox.yandex-team.ru"],
            },
            "rich-snippet": "16 tests: [[good]]16 - GOOD[[rst]][[rst]]",
            "suite": True,
            "path": "devtools/executor/tests/ut",
            "size": "medium",
            "type": "test",
            "name": "pytest",
        },
    ],
    "test_failed": [
        {
            "status": "FAILED",
            "metrics": {
                "ru_isrss": 0,
            },
            "links": {
                "log": [
                    "http://proxy.sandbox.yandex-team.ru"
                ],
            },
            "error_type": "REGULAR",
            "requirements": {"ram_disk": 1},
            "rich-snippet": "1 test: [[bad]]1 - FAIL[[rst]][[rst]]",
            "suite": True,
            "path": "devtools/dummy_arcadia/test/tmpfs/exectest",
            "size": "medium",
            "type": "test",
            "name": "exectest",
        },
        {
            "status": "FAILED",
            "metrics": {
                "ru_minor_pagefaults": 2171,
            },
            "links": {
                "logsdir": [
                    "http://proxy.sandbox.yandex-team.ru"
                ],
                "log": [
                    "http://proxy.sandbox.yandex-team.ru"
                ],
            },
            "tags": ["parametrize"],
            "error_type": "REGULAR",
            "requirements": {"ram_disk": 1},
            "subtest_name": "run[check_tmpfs]",
            "rich-snippet": "[[imp]][[bad]]E   ExecutionError: Command 'check_tmpfs' has failed with code 1.[[rst]]\n    AssertionError[[rst]][[rst]]",
            "duration": 0.074490308761597,
            "path": "devtools/dummy_arcadia/test/tmpfs/exectest",
            "size": "medium",
            "type": "test",
            "name": "exectest",
        },
    ],
    "build_and_configure_are_not_counted_as_suites": [
        {
            "status": "OK",
            "rich-snippet": "command gccfilter.pl -c \n1 error generated.",
            "path": "devtools/dummy_arcadia/test/broken_by_depends/lib3",
            "toolchain": "ALLOCATOR=LF-AUTOCHECK=yes-DEBUGINFO_LINES_ONLY=yes-NO_DEBUGINFO=no-USE_EAT_MY_DATA=yes-musl",
            "type": "build",
        },
        {
            "status": "OK",
            "rich-snippet": "Trying to use [[imp]]$S/junk/ya.make[[rst]] from the prohibited directory [[alt1]]junk[[rst]]",
            "path": "At top level",
            "toolchain": "linux",
            "messages": [
                {
                    "path": "At top level",
                    "type": "ERROR",
                    "text": "Trying to use [[imp]]$S/junk/path/ya.make[[rst]] from the prohibited directory [[alt1]]junk[[rst]]",
                }
            ],
            "type": "configure",
        },
        {
            "status": "OK",
            "rich-snippet": "1 test: [[bad]]1 - FAIL[[rst]][[rst]]",
            "suite": True,
            "path": "devtools/dummy_arcadia/test/tmpfs/exectest",
            "size": "medium",
            "type": "test",
            "name": "exectest",
        },
    ]
    # TODO prettyboy cases with chunks
}


@pytest.mark.parametrize(
    "casename, data", [(x, TEST_DATA[x]) for x in sorted(TEST_DATA.keys())], ids=sorted(TEST_DATA.keys())
)
def test_html_report_generator(casename, data):
    filename = casename + '.json'
    with open(filename, 'w') as afile:
        json.dump({'results': data}, afile)

    canon = casename + '.html'
    with open(canon, 'w') as afile:
        data = html_report.gen_html_from_results(filename)
        # simplify
        afile.write(re.sub(r'(<!--.*?-->|<[^>]*>)', '', data))
    return yatest.common.canonical_file(canon, local=True)
