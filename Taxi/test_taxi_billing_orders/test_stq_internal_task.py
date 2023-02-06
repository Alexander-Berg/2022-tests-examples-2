import datetime as dt

import pytest

from taxi import discovery
from taxi.stq import async_worker_ng

from taxi_billing_orders.stq.internal import task as stq_internal_task


TASK_ID = 'task_id'


@pytest.mark.now('2019-06-01T10:00:00Z')
@pytest.mark.parametrize(
    'kind,calc_calls,subv_calls',
    [
        ('antifraud_action', 0, 1),
        ('b2b_trip_payment', 1, 0),
        ('driver_geoarea_activity', 0, 1),
        ('driver_referral_payment', 0, 1),
        ('manual_subvention', 0, 1),
        ('order_amended', 0, 1),
        ('order_completed', 0, 1),
        ('order_paid', 1, 0),
        ('rebill_order', 0, 1),
        ('taximeter_open_account', 1, 0),
        ('taximeter_payment', 1, 0),
        ('tlog_workshift_bought', 1, 0),
        ('workshift_bought', 1, 0),
    ],
)
async def test_process_doc(
        kind,
        calc_calls,
        subv_calls,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_stq_internal_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'search' in url:
            return response_mock(
                json={
                    'docs': [
                        {
                            'doc_id': 125,
                            'kind': kind,
                            'data': {},
                            'external_obj_id': 'topic',
                            'external_event_ref': 'event/1',
                            'event_at': dt.datetime(
                                2019, 6, 1, 9, 55, tzinfo=None,
                            ),
                        },
                    ],
                },
            )
        raise NotImplementedError

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        assert json['doc']['id'] == 125
        return response_mock(json=json)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(
            method, url, headers, json, **kwargs,
    ):
        assert json['doc']['id'] == 125
        return response_mock(json=json)

    await stq_internal_task.process_doc(
        taxi_billing_orders_stq_internal_ctx,
        task_info=_create_task_info(),
        topic='topic',
        external_ref='event/1',
        created_at=dt.datetime(2019, 6, 1, 9, 59, tzinfo=None),
        process_at=None,
    )

    assert len(_patch_billing_docs_request.calls) == 1
    assert len(_patch_billing_calculators_request.calls) == calc_calls
    assert len(_patch_billing_subventions_request.calls) == subv_calls


@pytest.mark.now('2019-07-01T00:00:00Z')
async def test_discard_old_events(taxi_billing_orders_stq_internal_ctx):

    await stq_internal_task.process_doc(
        taxi_billing_orders_stq_internal_ctx,
        task_info=_create_task_info(),
        topic='topic',
        external_ref='event/1',
        created_at=dt.datetime(2019, 6, 1, 9, 59, tzinfo=None),
        process_at=None,
    )


@pytest.mark.config(BILLING_ORDERS_USE_STQ_RESCHEDULE=True)
@pytest.mark.now('2019-06-01T10:00:00Z')
async def test_process_doc_not_found(
        mockserver,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_stq_internal_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'search' in url:
            return response_mock(json={'docs': []})
        raise NotImplementedError

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _patch_stq_agent_reschedule(request):
        return {}

    await stq_internal_task.process_doc(
        taxi_billing_orders_stq_internal_ctx,
        task_info=_create_task_info(),
        topic='topic',
        external_ref='event/1',
        created_at=dt.datetime(2019, 6, 1, 9, 59, tzinfo=None),
        process_at=None,
    )

    assert len(_patch_billing_docs_request.calls) == 2
    assert _patch_stq_agent_reschedule.times_called == 1


def _create_task_info(exec_tries=0, reschedule_counter=0):
    return async_worker_ng.TaskInfo(
        id=TASK_ID,
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
        queue='',
    )
