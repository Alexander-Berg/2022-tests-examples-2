# pylint: disable=unused-argument,invalid-name,protected-access,unused-variable

from aiohttp import web
import asynctest
import pandas as pd
import pytest

from crm_admin.entity import error
from crm_admin.stq import user_activation


CRM_ADMIN_EFFICIENCY_SETTINGS = {'group_size': 1000}

CRM_ADMIN_SETTINGS = {
    'UserActivationSettings': {'yql_share_url': '//some/url/xxx'},
}

CRM_ADMIN_SETTINGS_DISABLED_SENDING = {
    'UserActivationSettings': {
        'sending_disabled': True,
        'yql_share_url': '//some/url/xxx',
    },
}


class TaskInfo:
    id = 'task_id'
    exec_tries = 0


@pytest.mark.parametrize('ok', [True, False])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_task(stq3_context, patch, ok):
    operation_id = 1
    start_id = 1

    @patch('crm_admin.stq.user_activation.UserActivationQuery.execute')
    async def execute(*args, **kwargs):
        if not ok:
            raise error.OperationError('error')

    await user_activation.task(
        stq3_context, TaskInfo(), operation_id, start_id,
    )
    assert execute.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.parametrize('status', ['COMPLETED', 'ERROR'])
async def test_user_activation_started(stq3_context, patch, status):
    @patch('crm_admin.stq.user_activation.yql.YqlOperationRequestBase')
    class YqlOperationRequestBase:
        def __init__(self, url):
            self.url = url
            self.executed = False
            self.json = {'status': status, 'queryData': {'content': 'query'}}

            self.run = asynctest.Mock()

    @patch(
        'crm_admin.stq.user_activation.UserActivationQuery._submit_pollable_yql_query',  # noqa: E501
    )
    async def submit_pollable_yql_query(query):
        pass

    operation_id = 1
    start_id = 123

    processor = user_activation.UserActivationQuery(
        stq3_context, operation_id, start_id, TaskInfo(),
    )
    assert processor.start_id == start_id

    if status == 'COMPLETED':
        await processor._on_started()
        assert submit_pollable_yql_query.calls
    else:
        with pytest.raises(error.OperationError):
            await processor._on_started()
        assert not submit_pollable_yql_query.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_user_activation_finished(stq3_context, patch, mock_crm_hub):
    class Result:
        def __init__(self):
            self._data = pd.DataFrame.from_dict(
                {
                    'campaign_id': [1, 2],
                    'yt_hahn_path': ['//path/1', '//path/2'],
                },
            )

        @property
        def table(self):
            return self

        @property
        def full_dataframe(self):
            return self._data

    @patch('crm_admin.stq.user_activation.rename')
    async def rename(*args, **kwargs):
        pass

    @mock_crm_hub('/v1/communication/bulk/new')
    async def bulk_new(request):
        return web.json_response({}, status=200)

    operation_id = 1
    start_id = 123
    processor = user_activation.UserActivationQuery(
        stq3_context, operation_id, start_id, TaskInfo(),
    )

    await processor._on_finished(True, Result())

    assert rename.calls
    assert bulk_new.has_calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS_DISABLED_SENDING)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_user_activation_disabled_sending(
        stq3_context, patch, mock_crm_hub,
):
    class Result:
        def __init__(self):
            self._data = pd.DataFrame.from_dict(
                {
                    'campaign_id': [1, 2],
                    'yt_hahn_path': ['//path/1', '//path/2'],
                },
            )

        @property
        def table(self):
            return self

        @property
        def full_dataframe(self):
            return self._data

    @patch('crm_admin.stq.user_activation.rename')
    async def rename(*args, **kwargs):
        pass

    @mock_crm_hub('/v1/communication/bulk/new')
    async def bulk_new(request):
        return web.json_response({}, status=200)

    operation_id = 1
    start_id = 123
    processor = user_activation.UserActivationQuery(
        stq3_context, operation_id, start_id, TaskInfo(),
    )

    await processor._on_finished(True, Result())

    assert rename.calls
    assert not bulk_new.has_calls


async def test_user_activation_error(stq3_context, caplog):
    operation_id = 1
    start_id = 123
    processor = user_activation.UserActivationQuery(
        stq3_context, operation_id, start_id, TaskInfo(),
    )

    await processor._on_finished(False, None)
    assert caplog.records[0].levelname == 'ERROR'
