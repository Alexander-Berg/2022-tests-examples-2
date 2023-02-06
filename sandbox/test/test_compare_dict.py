import pytest
import textwrap

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare_dict import compare_dicts


@pytest.mark.parametrize(("pre", "test", "expected_diff"), [
    ("test", "test", ""),
    (
        "test",
        "text",
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1 +1 @@
            -"test"
            +"text"
        """).strip()
    ),
    (
        ["test", 200],
        ["text", 200],
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
    (
        {"test": 100, "text": 200},
        {"text": 200, "test": 100},
        ""
    ),
    (
        {"test": 200, "text": 100},
        {"text": 200, "test": 100},
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,4 +1,4 @@
             {
            -  "test": 200,
            -  "text": 100
            +  "test": 100,
            +  "text": 200
             }
        """).strip()
    ),
    (
        [{"test": 200}],
        {"test": 100},
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,5 +1,3 @@
            -[
            -  {
            -    "test": 200
            -  }
            -]
            +{
            +  "test": 100
            +}
        """).strip()
    ),
    (
        ["test", 200],
        {"test": 100},
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1,4 +1,3 @@
            -[
            -  "test",
            -  200
            -]
            +{
            +  "test": 100
            +}
        """).strip()
    ),
])
def test_compare_dict(pre, test, expected_diff):
    has_diff, diff = compare_dicts(pre, test)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff
