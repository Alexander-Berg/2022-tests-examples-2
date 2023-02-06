# pylint: disable=line-too-long
# flake8: noqa
import datetime

import pytest

from logs_from_yt.components import query_buider
from logs_from_yt.components import service_schema as ss
from logs_from_yt.components import task as task_module


@pytest.mark.parametrize(
    ['task_request', 'expected_query'],
    [
        pytest.param(
            task_module.Request(
                start_time=datetime.datetime(2019, 6, 8, 19, 30, 0),
                end_time=datetime.datetime(2019, 6, 8, 22, 30, 0),
                filters=[
                    task_module.FilterItem(
                        key='meta_order_id',
                        value='9d058848f0932f45a5392e8e0ab6e33a',
                        service_names=['protocol', 'stq'],
                    ),
                    task_module.FilterItem(
                        key='meta_user_id',
                        value='57f20a933dbbf216565aaf3fe2c17c07',
                        service_names=['protocol'],
                    ),
                ],
            ),
            'expected_query_routestats_links.yql',
            marks=pytest.mark.config(
                LOGS_FROM_YT_FEATURES={'use_routstats_link_query': True},
            ),
        ),
        pytest.param(
            task_module.Request(
                start_time=datetime.datetime(2019, 6, 8, 19, 30, 0),
                end_time=datetime.datetime(2019, 6, 8, 22, 30, 0),
                filters=[
                    task_module.FilterItem(
                        key='meta_user_id',
                        value='57f20a933dbbf216565aaf3fe2c17c07',
                        service_names=['protocol'],
                    ),
                ],
            ),
            'expected_query_simple.yql',
            marks=pytest.mark.config(
                LOGS_FROM_YT_FEATURES={'use_routstats_link_query': True},
            ),
        ),
        pytest.param(
            task_module.Request(
                start_time=datetime.datetime(2019, 6, 8, 19, 30, 0),
                end_time=datetime.datetime(2019, 6, 8, 22, 30, 0),
                filters=[
                    task_module.FilterItem(
                        key='meta_user_id',
                        value='57f20a933dbbf216565aaf3fe2c17c07',
                        service_names=['protocol'],
                    ),
                ],
            ),
            'expected_query_limits.yql',
            marks=pytest.mark.config(
                LOGS_FROM_YT_LIMITS={
                    'service_limit': 666,
                    'link_limit': 777,
                    'upload_batch_size': 10,
                },
            ),
        ),
    ],
)
async def test_query_buider(cron_context, load, task_request, expected_query):
    task = task_module.Task(
        task_id='test_id',
        status=task_module.Status.STARTED,
        request=task_request,
        yql_operation=None,
        author='',
        created_at=datetime.datetime(2019, 6, 8, 19, 20, 0),
        started_at=None,
        finished_at=None,
        message='',
        log_count=None,
        config=cron_context.config,
    )
    query = await query_buider.build(
        jinja2_env=cron_context.jinja2_env,
        task=task,
        schemas_by_service_name=ss.get_schemas_by_service_name(
            cron_context.config,
        ),
    )

    assert query == load(expected_query)
