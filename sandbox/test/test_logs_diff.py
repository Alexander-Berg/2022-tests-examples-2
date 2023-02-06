import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.logs_diff import diff_log


class TestDiffLogs(object):
    @pytest.mark.parametrize(('pre', 'test', 'expected_diff'), [
        (
            [{'___MD5___': "general1"}],
            [{'___MD5___': "general1"}],
            ''
        ),
        (
            # if general MD5 are equal, no additional comparison is performed
            [{'___MD5___': "2"}, {'___MD5___': "general1"}],
            [{'___MD5___': "3"}, {'___MD5___': "general1"}],
            ''
        ),
        (
            [{'___MD5___': "2"}, {'___MD5___': "general1"}],
            [{'___MD5___': "2"}, {'___MD5___': "general2"}],
            '\n'
        ),
    ])
    def test_diff_logs_no_diff(self, pre, test, expected_diff):
        diff, changes = diff_log(pre, test, 'hit')
        assert diff == expected_diff
        assert changes == {'+': set(), '-': set(), '!': set(), 'len': 0}

    @pytest.mark.issue('BSEFFECTIVE-209')
    def test_diff_logs_duplicate_log_entry(self):
        pre = [
            {"___MD5___": "1"},
            {"___MD5___": "general1"},
        ]
        test = [
            {"___MD5___": "1"},
            {"___MD5___": "1"},
            {"___MD5___": "general2"},
        ]
        diff, changes = diff_log(pre, test, 'hit')
        assert diff == u'\n'
        assert changes == {'+': set(), '-': set(), '!': set(), 'len': 1}
