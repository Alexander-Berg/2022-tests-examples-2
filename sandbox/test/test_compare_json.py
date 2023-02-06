import pytest
import textwrap

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare_json import compare_json_strings


@pytest.mark.parametrize(("pre", "test", "expected_diff"), [
    ('"test"', '"test"', ""),
    (
        '"test"',
        '"text"',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1 +1 @@
            -"test"
            +"text"
        """).strip()
    ),
    (
        '["test", 200]',
        '["text", 200]',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,4 +1,4 @@
             [
            -  "test",
            +  "text",
               200
             ]
        """).strip()
    ),
])
def test_compare_json_strings(pre, test, expected_diff):
    has_diff, diff = compare_json_strings(pre, test)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff


@pytest.mark.parametrize(("pre", "test", "expected_diff", "ignore_blocks_order"), [
    (
        '{"test": 200}// yandex-splitter{"text": 200}',
        '{"text": 200}// yandex-splitter{"test": 200}',
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,8 +1,8 @@
             [
               {
            -    "test": 200
            +    "text": 200
               },
               {
            -    "text": 200
            +    "test": 200
               }
             ]
        """).strip(),
        False,
    ),
    (
        '{"test": 200}// yandex-splitter{"text": 200}',
        '{"text": 200}// yandex-splitter{"test": 200}',
        "",
        True,
    ),
])
def test_compare_json_strings_serp(pre, test, expected_diff, ignore_blocks_order):
    has_diff, diff = compare_json_strings(pre, test, ignore_blocks_order=ignore_blocks_order)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff
