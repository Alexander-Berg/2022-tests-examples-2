import pytest
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.report_utils import ELogChange, ELogFieldChange
from sandbox.projects.yabs.qa.tasks.YabsAutoResolveDiffs.process_smart_report import need_autoresolve


def gen_allowed_changes(
    allow_added_logs=False,
    allow_removed_logs=False,
    allow_added_log_fields=False,
    allow_removed_log_fields=False,
    allow_changed_log_fields=False,
):
    return {
        ELogChange.added_logs.name: allow_added_logs,
        ELogChange.removed_logs.name: allow_removed_logs,
        ELogChange.changed_logs.name: {
            ELogFieldChange.added_fields.name: allow_added_log_fields,
            ELogFieldChange.removed_fields.name: allow_removed_log_fields,
            ELogFieldChange.changed_fields.name: allow_changed_log_fields,
        }
    }


def gen_smart_report(diff_blocks):
    return {
        "diff_blocks": list(diff_blocks.keys()),
        "diff_blocks_detailed": diff_blocks,
    }


class TestNeedAutoresolve(object):
    @pytest.mark.parametrize(('allow_added_logs', 'added_logs', 'expected_need_autoresolve'), [
        (True, [], False),
        (True, ['my_log'], True),
        (False, [], False),
        (False, ['my_log'], False),
    ])
    def test_smart_report_added_logs(self, allow_added_logs, added_logs, expected_need_autoresolve):
        allowed_changes = gen_allowed_changes(allow_added_logs=allow_added_logs)
        smart_report = gen_smart_report({
            "logs_data": {
                "added_logs": added_logs,
                "removed_logs": [],
                "changed_logs": {},
            }
        })
        actual_need_autoresolve, _ = need_autoresolve(smart_report, allowed_changes)
        assert actual_need_autoresolve == expected_need_autoresolve

    @pytest.mark.parametrize(('allow_removed_logs', 'removed_logs', 'expected_need_autoresolve'), [
        (True, [], False),
        (True, ['my_log'], True),
        (False, [], False),
        (False, ['my_log'], False),
    ])
    def test_smart_report_removed_logs(self, allow_removed_logs, removed_logs, expected_need_autoresolve):
        allowed_changes = gen_allowed_changes(allow_removed_logs=allow_removed_logs)
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": removed_logs,
                "added_logs": [],
                "changed_logs": {},
            }
        })
        actual_need_autoresolve, _ = need_autoresolve(smart_report, allowed_changes)
        assert actual_need_autoresolve == expected_need_autoresolve

    @pytest.mark.parametrize(('allow_added_log_fields', 'added_fields', 'expected_need_autoresolve'), [
        (True, [], False),
        (True, ['my_field'], True),
        (False, [], False),
        (False, ['my_field'], False),
    ])
    def test_smart_report_added_log_fields(self, allow_added_log_fields, added_fields, expected_need_autoresolve):
        allowed_changes = gen_allowed_changes(allow_added_log_fields=allow_added_log_fields)
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": [],
                "added_logs": [],
                "changed_logs": {
                    'log': {
                        'added_fields': added_fields
                    }
                },
            }
        })
        actual_need_autoresolve, _ = need_autoresolve(smart_report, allowed_changes)
        assert actual_need_autoresolve == expected_need_autoresolve

    @pytest.mark.parametrize(('allow_removed_log_fields', 'removed_fields', 'expected_need_autoresolve'), [
        (True, [], False),
        (True, ['my_field'], True),
        (False, [], False),
        (False, ['my_field'], False),
    ])
    def test_smart_report_removed_log_fields(self, allow_removed_log_fields, removed_fields, expected_need_autoresolve):
        allowed_changes = gen_allowed_changes(allow_removed_log_fields=allow_removed_log_fields)
        smart_report = gen_smart_report({
            "logs_data": {
                "added_logs": [],
                "removed_logs": [],
                "changed_logs": {
                    'log': {
                        'removed_fields': removed_fields
                    }
                },
            }
        })
        actual_need_autoresolve, _ = need_autoresolve(smart_report, allowed_changes)
        assert actual_need_autoresolve == expected_need_autoresolve

    @pytest.mark.parametrize(('allow_changed_log_fields', 'changed_fields', 'expected_need_autoresolve'), [
        (True, [], False),
        (True, ['my_field'], True),
        (False, [], False),
        (False, ['my_field'], False),
    ])
    def test_smart_report_changed_log_fields(self, allow_changed_log_fields, changed_fields, expected_need_autoresolve):
        allowed_changes = gen_allowed_changes(allow_changed_log_fields=allow_changed_log_fields)
        smart_report = gen_smart_report({
            "logs_data": {
                "added_logs": [],
                "removed_logs": [],
                "changed_logs": {
                    'log': {
                        'changed_fields': changed_fields
                    }
                },
            }
        })
        actual_need_autoresolve, _ = need_autoresolve(smart_report, allowed_changes)
        assert actual_need_autoresolve == expected_need_autoresolve

    @pytest.mark.issue('BSEFFECTIVE-225')
    def test_smart_report_log_field_changes(self):
        allowed_changes = gen_allowed_changes(allow_added_logs=True, allow_added_log_fields=True)
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": [],
                "changed_logs": {
                    "hit_factors": {
                        "changed_fields": [
                            "MatchedPhraseInfos",
                        ],
                        "removed_fields": [],
                        "added_fields": [],
                        "max_len_change": 0
                    }
                },
                "added_logs": []
            }
        })
        assert need_autoresolve(smart_report, allowed_changes) == (False, [])

    @pytest.mark.issue('BSEFFECTIVE-209')
    def test_smart_report_empty_changes(self):
        allowed_changes = gen_allowed_changes(allow_added_logs=True, allow_added_log_fields=True)
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": [],
                "changed_logs": {
                    "hit_factors": {
                        "changed_fields": [],
                        "removed_fields": [],
                        "added_fields": [],
                        "max_len_change": 0
                    }
                },
                "added_logs": []
            }
        })
        assert need_autoresolve(smart_report, allowed_changes) == (False, [])


class TestAutoresolveChanges(object):
    def test_smart_report_added_log(self):
        allowed_changes = gen_allowed_changes(allow_added_logs=True)
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": [],
                "added_logs": ['log1'],
                "changed_logs": {},
            }
        })
        _, actual_diff_canges = need_autoresolve(smart_report, allowed_changes)
        assert actual_diff_canges == [
            'added_logs: log1',
        ]

    def test_smart_report_added_log_fields(self):
        allowed_changes = gen_allowed_changes(
            allow_added_log_fields=True,
            allow_removed_log_fields=True,
        )
        smart_report = gen_smart_report({
            "logs_data": {
                "removed_logs": [],
                "added_logs": [],
                "changed_logs": {
                    'log1': {
                        'added_fields': ['field1', 'field2'],
                        'removed_fields': ['field3'],
                    }
                },
            }
        })
        _, actual_diff_canges = need_autoresolve(smart_report, allowed_changes)
        assert actual_diff_canges == [
            'log1 added_fields: field1, field2',
            'log1 removed_fields: field3',
        ]
