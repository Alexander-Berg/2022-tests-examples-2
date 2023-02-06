import typing as tp

import pytest

from taxi_billing_docs.cron.tasks import aggregate_yt_docs as tasks
from test_taxi_billing_docs import conftest as tst


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.config(BILLING_DOCS_PREPARE_AUDIT_DATA_CHUNK_SIZE=10)
@pytest.mark.parametrize(
    'yt_responses', [[[], []], [[[0, 10], [2, 20], [3, 50], [4, 70]], []]],
)
async def test_cron_usage(
        docs_cron_app, yt_responses: tp.List, mocked_yql: tp.List, patch,
):
    @patch('random.shuffle')
    def _shuffle(array: tp.List):
        pass

    for response in yt_responses:
        mocked_yql.append(
            tst.MockedRequest(
                tst.MockedResult(
                    tst.YT_STATUS_COMPLETED, [tst.MockedTable(response)],
                ),
            ),
        )

    task = tasks.AggregateYTDocs(context=docs_cron_app)
    await task.aggregate()
