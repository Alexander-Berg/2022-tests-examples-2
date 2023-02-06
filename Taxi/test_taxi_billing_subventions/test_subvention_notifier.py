from unittest import mock

import aiohttp
import pytest

from taxi import config
from taxi.clients import subvention_communications
from taxi.clients import tvm
from taxi.stq import async_worker_ng

from taxi_billing_subventions import subvention_notifier


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name='tvm_client')
async def make_tvm_client(session):
    yield tvm.TVMClient(
        service_name='test_billing_subventions',
        secdist={},
        config=config.Config,
        session=session,
    )


@pytest.fixture(name='subvention_communications_client')
async def make_subv_communications_client(session, tvm_client):
    cfg = config.Config()
    cfg.SUBVENTION_COMMUNICATIONS_CLIENT_QOS = {
        '__default__': {'attempts': 1, 'timeout-ms': 10000},
    }
    yield subvention_communications.Client(
        session=session, config=cfg, tvm_client=tvm_client,
    )


@pytest.mark.parametrize(
    'test_case_json',
    [
        'driver_fix_pay.json',
        'driver_fix_block.json',
        'geo_booking_pay.json',
        'nmfg_pay.json',
        'nmfg_block.json',
        'nmfg_block_reason.json',
    ],
)
async def test_notify_driver_fix(
        test_case_json,
        *,
        load_py_json,
        mock_subvention_communications,
        subvention_communications_client,  # pylint: disable=invalid-name
):
    test_case = load_py_json(test_case_json)
    af_decision = test_case['af_decision']
    af_reason = test_case.get('af_reason')
    rule_group = test_case['rule_group']
    expected_request = test_case['expected_request']
    context = mock.Mock(
        config=mock.Mock(
            BILLING_SUBVENTIONS_SEND_DRIVER_FIX_NOTIFICATION=True,
            BILLING_SUBVENTIONS_SEND_GEO_BOOKING_NOTIFICATION=True,
            BILLING_SUBVENTIONS_SEND_NMFG_NOTIFICATION=True,
        ),
        subvention_communications=subvention_communications_client,
    )
    task_info = async_worker_ng.TaskInfo('18', 0, 0, 'bs_subvention_notifier')
    await subvention_notifier.task.task(
        context,
        task_info,
        rule_group=rule_group,
        query=dict(
            af_decision=af_decision,
            af_reason=af_reason,
            park_id='some_park_id',
            driver_profile_id='some_driver_uuid',
            support_info_doc_id=6,
            agreement_ref=test_case['agreement_ref'],
            date='2020-01-02',
        ),
        log_extra={},
    )
    mock_sc = mock_subvention_communications
    endpoints = {
        ('pay', 'driver_fix'): mock_sc.v1_driver_fix_pay,
        ('block', 'driver_fix'): mock_sc.v1_driver_fix_block,
        ('pay', 'geobooking'): mock_sc.v1_rule_pay,
        ('pay', 'daily_guarantee'): mock_sc.v1_rule_pay,
        ('block', 'daily_guarantee'): mock_sc.v1_rule_fraud,
    }
    endpoint = endpoints[(af_decision, rule_group)]
    assert endpoint.times_called == 1
    assert endpoint.next_call()['request'].json == expected_request
