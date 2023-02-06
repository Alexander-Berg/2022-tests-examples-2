import pytest
import textwrap

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare_text import compare_text


@pytest.mark.parametrize(("pre", "test", "expected_diff"), [
    ("test", "test", ""),
    (
        "test",
        "text",
        textwrap.dedent("""
            --- pre
            +++ test
            @@ -1 +1 @@
            -test
            +text
        """).strip()
    ),
])
def test_compare_text(pre, test, expected_diff):
    has_diff, diff = compare_text(pre, test)
    assert has_diff == bool(expected_diff)
    assert diff == expected_diff
