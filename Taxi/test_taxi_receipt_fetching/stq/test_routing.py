import collections
import copy
import dataclasses

import pytest

from taxi_receipt_fetching.stq import task


@dataclasses.dataclass
class CallsMocks:
    def __init__(
            self,
            test_settings,
            archive_mock,
            order_proc_retrieve_mock,
            br_person_mock,
            br_contracts_mock,
            load_json,
    ):
        self.archive_proc_mock = order_proc_retrieve_mock({})
        self.archive_order_mock = archive_mock(
            load_json(test_settings['order']), 'get_order_by_id',
        )
        self.person_mock = br_person_mock({})
        self.contract_mock = br_contracts_mock([], [])


def _check_calls(test_settings, calls_mocks, stq_calls):
    expected_calls = test_settings['expected_calls']

    assert (
        len(calls_mocks.archive_proc_mock.calls)
        == expected_calls['archive_proc']
    )
    assert (
        len(calls_mocks.archive_order_mock.calls)
        == expected_calls['archive_order']
    )
    assert (
        len(calls_mocks.person_mock.calls)
        == expected_calls['billing_replication_person']
    )
    assert (
        len(calls_mocks.contract_mock.calls)
        == expected_calls['billing_replication_contract']
    )

    assert stq_calls == test_settings['expected_stq_calls']


@pytest.mark.parametrize('test_json', ['kaz.json', 'mda.json', 'rus.json'])
@pytest.mark.config(
    RECEIPT_REGISTRATION_ENABLED={'__default__': True},
    RECEIPT_QUEUE_ROUTING={
        '__default__': {'__default__': False},
        'kaz': {'__default__': True},
        'mda': {'__default__': True},
    },
)
async def test_routing(
        stq3_context,
        fetch_receipt_task_info,
        load_json,
        mockserver,
        archive_mock,
        order_proc_retrieve_mock,
        br_person_mock,
        br_contracts_mock,
        client_session_request_mock,
        test_json,
):
    test_settings = load_json(test_json)
    order_id = test_settings['order_id']

    calls_mocks = CallsMocks(
        test_settings,
        archive_mock,
        order_proc_retrieve_mock,
        br_person_mock,
        br_contracts_mock,
        load_json,
    )

    stq_calls = collections.defaultdict(list)

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        call = copy.deepcopy(request.json['kwargs'])
        call.pop('log_extra')
        stq_calls[queue_name].append(call)

    await task.fetch_receipt(stq3_context, fetch_receipt_task_info, order_id)
    _check_calls(test_settings, calls_mocks, stq_calls)
