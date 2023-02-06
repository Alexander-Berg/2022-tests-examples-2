import pytest
import textwrap

import demjson

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare_jsonp import compare_jsonp_strings


@pytest.mark.parametrize(("pre", "test", "expected_diff"), [
    (
        '{"test": 200}',
        '{"text": 200}',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             {
            -  "test": 200
            +  "text": 200
             }
        """).strip()
    ),
])
def test_compare_jsonp_allow_json(pre, test, expected_diff):
    has_diff, diff = compare_jsonp_strings(pre, test, allow_json=True)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff


@pytest.mark.parametrize(("pre", "test", "expected_diff"), [
    (
        '({"test": 200})',
        '({"text": 200})',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             {
            -  "test": 200
            +  "text": 200
             }
        """).strip()
    ),
    (
        'callback_pre({"test": 200})',
        'callback_test({"text": 200})',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
            -callback_pre({
            -  "test": 200
            +callback_test({
            +  "text": 200
             })
        """).strip()
    ),
    (
        'callback(\'{"test": 200}\')',
        'callback({"text": 200})',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             callback({
            -  "test": 200
            +  "text": 200
             })
        """).strip()
    ),
    (
        'callback(\'{"test": 200}\')',
        'callback(\'{"text": 200}\')',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             callback({
            -  "test": 200
            +  "text": 200
             })
        """).strip()
    ),
])
def test_compare_jsonp(pre, test, expected_diff):
    has_diff, diff = compare_jsonp_strings(pre, test, allow_json=True)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff


@pytest.mark.parametrize(("pre", "test", "expected_diff", "options"), [
    (
        '({test: 200})',
        '({text: 200})',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             {
            -  "test": 200
            +  "text": 200
             }
        """).strip(),
        {
            "allow_identifier_keys": True,
        },
    ),
    (
        '({"test": 20000000000000000000})',
        '({"text": 20000000000000000000})',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,3 +1,3 @@
             {
            -  "test": 20000000000000000000
            +  "text": 20000000000000000000
             }
        """).strip(),
        {
            "allow_non_portable": True,
        },
    ),
])
def test_compare_jsonp_with_options(pre, test, expected_diff, options):
    has_diff, diff = compare_jsonp_strings(pre, test, jsonp_parser=demjson.decode, jsonp_parser_options=options)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff


@pytest.mark.parametrize(("pre", "test", "expected_error_message", "options"), [
    (
        '({text: 2e900000000000000})',
        '({test: 2e900000000000000})',
        'Parsing timed out',
        {
            "allow_identifier_keys": True,
        },
    ),
])
def test_compare_jsonp_exception(pre, test, expected_error_message, options):
    has_diff, diff = None, None
    error = Exception("dummy")
    try:
        has_diff, diff = compare_jsonp_strings(pre, test, jsonp_parser=demjson.decode, jsonp_parser_options=options)
    except Exception as exc:
        error = exc
    assert has_diff is None
    assert diff is None
    assert error.message == expected_error_message
