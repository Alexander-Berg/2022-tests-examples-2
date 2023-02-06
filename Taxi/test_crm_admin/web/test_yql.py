import pytest
import yql.client.issue as yql_issue

import crm_admin.utils.yql as yql_util


async def test_validate(patch):
    @patch('yql.client.explain.YqlSqlValidateRequest')
    def _get_yql_request(*args, **kwargs):
        class YQLRequest:
            is_success = True
            share_url = 'shared_url'

            def run(self):
                pass

            def get_results(self, wait):
                pass

        return YQLRequest()

    assert yql_util.validate('something') == 'shared_url'


async def test_validate_fail(patch):
    @patch('yql.client.explain.YqlSqlValidateRequest')
    def _get_yql_request(*args, **kwargs):
        class YQLRequest:
            is_success = False
            share_url = 'shared_url'
            errors = [yql_issue.YqlIssue()]

            def run(self):
                pass

            def get_results(self, wait):
                pass

        return YQLRequest()

    with pytest.raises(yql_util.YqlError):
        yql_util.validate('something')
