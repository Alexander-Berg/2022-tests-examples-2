import pytest

from grocery_tasks.autoorder.calc import table_report

_FULL_CONFIG = {
    'fallback_allowed': False,
    'sum_field': 'foo',
    'trigger_sum': {'lower_bound': -0.5, 'upper_bound': 0.5},
    'trigger_count': {'lower_bound': -0.5, 'upper_bound': 0.5},
}


@pytest.mark.parametrize(
    'table_config,previous_stats,current_stats,expected_report',
    [
        (
            _FULL_CONFIG,
            table_report.TableStats('path_prev', True, 2, None),
            table_report.TableStats('path_curr', True, 3, None),
            {
                'config': _FULL_CONFIG,
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 3,
                },
                'decision_reason': 'all checks are ok',
                'diff_count': 0.5,
                'diff_sum': None,
                'name': 'name',
                'path_selected': 'path_curr',
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 2,
                },
                'status': True,
            },
        ),
        (
            _FULL_CONFIG,
            table_report.TableStats('path_prev', True, 100, 20000),
            table_report.TableStats('path_curr', True, 90, 20200),
            {
                'config': _FULL_CONFIG,
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 90,
                    'sum_by_field': 20200,
                },
                'decision_reason': 'all checks are ok',
                'diff_count': -0.1,
                'diff_sum': 0.01,
                'name': 'name',
                'path_selected': 'path_curr',
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 100,
                    'sum_by_field': 20000,
                },
                'status': True,
            },
        ),
        (
            _FULL_CONFIG,
            table_report.TableStats('path_prev', True, 100, 20000),
            table_report.TableStats('path_curr', True, 90, 30001),
            {
                'config': _FULL_CONFIG,
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 90,
                    'sum_by_field': 30001,
                },
                'decision_reason': (
                    'sum check trigger activated, fallback_allowed: false'
                ),
                'diff_count': -0.1,
                'diff_sum': 0.50005,
                'name': 'name',
                'path_selected': None,
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 100,
                    'sum_by_field': 20000,
                },
                'status': False,
            },
        ),
        (
            {
                'fallback_allowed': True,
                'sum_field': 'foo',
                'trigger_sum': {'lower_bound': -0.5, 'upper_bound': 0.5},
            },
            table_report.TableStats('path_prev', True, 100, 20000),
            table_report.TableStats('path_curr', True, 90, 30001),
            {
                'config': {
                    'fallback_allowed': True,
                    'sum_field': 'foo',
                    'trigger_sum': {'lower_bound': -0.5, 'upper_bound': 0.5},
                },
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 90,
                    'sum_by_field': 30001,
                },
                'decision_reason': (
                    'sum check trigger activated, fallback_allowed: true'
                ),
                'diff_count': -0.1,
                'diff_sum': 0.50005,
                'name': 'name',
                'path_selected': 'path_prev',
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 100,
                    'sum_by_field': 20000,
                },
                'status': False,
            },
        ),
        (
            {
                'fallback_allowed': False,
                'trigger_count': {'lower_bound': 0.5, 'upper_bound': 0.5},
            },
            table_report.TableStats('path_prev', True, 100, None),
            table_report.TableStats('path_curr', True, 49, None),
            {
                'config': {
                    'fallback_allowed': False,
                    'trigger_count': {'lower_bound': 0.5, 'upper_bound': 0.5},
                },
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 49,
                },
                'decision_reason': (
                    'row count trigger activated, fallback_allowed: false'
                ),
                'diff_count': -0.51,
                'diff_sum': None,
                'name': 'name',
                'path_selected': None,
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 100,
                },
                'status': False,
            },
        ),
        (
            {},
            table_report.TableStats('path_prev', False, None, None),
            table_report.TableStats('path_curr', True, 50, None),
            {
                'config': {'fallback_allowed': False},
                'current': {
                    'exists': True,
                    'path': 'path_curr',
                    'row_count': 50,
                },
                'decision_reason': (
                    'previous path is missing, fallback_allowed: false'
                ),
                'diff_count': None,
                'diff_sum': None,
                'name': 'name',
                'path_selected': 'path_curr',
                'previous': {'exists': False, 'path': 'path_prev'},
                'status': False,
            },
        ),
        (
            {},
            table_report.TableStats('path_prev', True, 50, None),
            table_report.TableStats('path_curr', False, None, None),
            {
                'config': {'fallback_allowed': False},
                'current': {'exists': False, 'path': 'path_curr'},
                'decision_reason': (
                    'current path is missing, fallback_allowed: false'
                ),
                'diff_count': None,
                'diff_sum': None,
                'name': 'name',
                'path_selected': None,
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 50,
                },
                'status': False,
            },
        ),
        (
            {'fallback_allowed': True},
            table_report.TableStats('path_prev', True, 50, None),
            table_report.TableStats('path_curr', False, None, None),
            {
                'config': {'fallback_allowed': True},
                'current': {'exists': False, 'path': 'path_curr'},
                'decision_reason': (
                    'current path is missing, fallback_allowed: true'
                ),
                'diff_count': None,
                'diff_sum': None,
                'name': 'name',
                'path_selected': 'path_prev',
                'previous': {
                    'exists': True,
                    'path': 'path_prev',
                    'row_count': 50,
                },
                'status': False,
            },
        ),
    ],
)
def test_table_report(
        cron_context,
        table_config,
        previous_stats,
        current_stats,
        expected_report,
):
    report = table_report.TableReport(
        name='name',
        config=table_report.DownloadConfig(**table_config),
        previous=previous_stats,
        current=current_stats,
    )
    assert report.make_report() == expected_report
