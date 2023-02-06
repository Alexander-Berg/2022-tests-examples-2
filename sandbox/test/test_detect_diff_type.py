import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.diff_methods import detect_diff_method, DiffMethods


@pytest.mark.parametrize(
    ("pre_diff_method_str", "test_diff_method_str", "expected_diff_method"),
    [
        ("text_diff", "text_diff", DiffMethods.text_diff),
        ("log_diff", "log_diff", DiffMethods.log_diff),
        ("json_string_diff", "json_string_diff", DiffMethods.json_string_diff),
        ("jsonp_string_diff", "jsonp_string_diff", DiffMethods.jsonp_string_diff),
        ("json_string_diff", "jsonp_diff", DiffMethods.json_string_diff),
        ("jsonp_string_diff", "jsonp_diff", DiffMethods.jsonp_string_diff),
        ("no_diff", "no_diff", DiffMethods.no_diff),
        ("no_diff", "text_diff", DiffMethods.text_diff),
        ("jsonp_string_diff", "json_string_diff", DiffMethods.json_string_diff),
    ]
)
def test_detect_diff_method(pre_diff_method_str, test_diff_method_str, expected_diff_method):
    detected_diff_method = detect_diff_method(pre_diff_method_str, test_diff_method_str)
    assert detected_diff_method == expected_diff_method
