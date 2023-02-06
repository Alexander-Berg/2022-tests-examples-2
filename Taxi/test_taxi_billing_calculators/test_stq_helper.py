from taxi import discovery

from taxi_billing_calculators.stq.main import task as stq_main_task
from . import common


# pylint: disable=invalid-name
async def test_not_ready_for_processing(
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_main_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'is_ready_for_processing' in url:
            return response_mock(json={'ready': False})
        return None

    await stq_main_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=common.create_task_info(),
        doc_id=123,
    )

    assert len(_patch_billing_docs_request.calls) == 1
