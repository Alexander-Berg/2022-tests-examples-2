import collections
from typing import List
from typing import Mapping

from taxi.stq import async_worker_ng

from transactions.internal import archive


def match_many_dicts(dicts: List[Mapping], templates: List[Mapping]):
    assert len(dicts) == len(templates)
    for a_dict, template in zip(dicts, templates):
        match_dict(a_dict=a_dict, template=template)


def match_dict(a_dict: Mapping, template: Mapping):
    for key, value in template.items():
        assert a_dict[key] == value


def create_task_info(
        queue: str, reschedule_counter: int = 0,
) -> async_worker_ng.TaskInfo:
    return async_worker_ng.TaskInfo(
        id='some_id',
        exec_tries=0,
        reschedule_counter=reschedule_counter,
        queue=queue,
    )


def patch_safe_restore_invoice(patch, result, expected_invoice_ids):
    ids = collections.deque(expected_invoice_ids)

    @patch('transactions.internal.archive.safe_restore_invoice')
    async def _safe_restore_invoice(invoice_id, context):
        del context  # unused
        assert invoice_id == ids.popleft()
        return result

    return _safe_restore_invoice


def patch_fetch_invoice(patch, result, expected_invoice_id=None):
    @patch('transactions.internal.archive.fetch_invoice')
    async def _fetch_invoice(invoice_id, context):
        del context  # unused
        assert invoice_id == expected_invoice_id or result['_id']
        if result is None:
            raise archive.NotFoundError
        return result

    return _fetch_invoice
