from sandbox.projects.autocheck.lib import problems_analyzer as pa

import pytest


@pytest.mark.parametrize('ctx, expected', [
    ({}, None),
    ({'task_error_message': 'some text'}, None),
    ({'task_error_message': 'prefix1 AutocheckBuildError: prefix2 failed to obtain suffix'}, 'DISTBS_FAILED_DOWNLOAD'),
    ({'task_error_message': 'prefix1 AutocheckBuildError: prefix2 Build return code is -9 suffix'}, 'SB_YA_KILLED'),
    ({'task_error_message': 'prefix1 AutocheckBuildError: prefix2 Cannot allocate memory suffix'}, 'SB_MEMORY_ALLOCATION_PROBLEM'),
])
def test_analyze_context(ctx, expected):
    assert pa.analyze_context(ctx) == expected


@pytest.mark.parametrize('audit, expected', [
    ([], None),
    ([{'message': 'rejected task: Client is shutting down.'}], 'SB_REJECT_TASK'),
])
def test_analyze_audit(audit, expected):
    assert pa.analyze_audit(audit) == expected


@pytest.mark.parametrize('ctx, read_audit, expected', [
    ({'task_error_message': 'prefix1 AutocheckBuildError: prefix2 Build return code is -9 suffix'}, lambda: [], 'SB_YA_KILLED'),
    ({}, lambda: [{'message': 'rejected task: Client is shutting down.'}], 'SB_REJECT_TASK'),
    ({}, lambda: [{'message': 'Switched to FAILURE instead of TIMEOUT.'}], 'UN_TIMEOUT'),
    ({'is_pessimized': False}, lambda: [{'message': 'Switched to FAILURE instead of TIMEOUT.'}], 'UN_TIMEOUT'),
    ({'is_pessimized': True}, lambda: [{'message': 'Switched to FAILURE instead of TIMEOUT.'}], 'UN_PESSIMIZED_TASK_TIMEOUT'),
])
def test_analyze_task(ctx, read_audit, expected):
    assert pa.analyze_task(ctx, read_audit) == pa.tag_name(expected)
