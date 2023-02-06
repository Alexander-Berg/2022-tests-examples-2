import itertools
import time
import json

import pytest

from cargo_newflow.clients import cargo_orders_driver
from cargo_newflow import consts
from cargo_newflow import library
from cargo_newflow import utils

from . import lib


UD_TEST_DATA = {
    'corp_client_id': consts.AUTOTEST_CORP_CLIENT_ID,
    'yandex_uid': '123',
    'phone': '+79996548791',
    'claim_request': utils.get_project_root() / 'requests/multipoints.json',
    'taxi_class': 'courier',
    'dont_skip_confirmation': False,
    'post_payment': None,
    'case': 'default',
    'router': 'United Dispatch',
    'claim_type': 'multipoints',
}


@pytest.mark.parametrize(
    'test_data', (UD_TEST_DATA, ), indirect=True,
)
def test_base_scenario(
        request,
        test_data,
        net_address,
        username,
        cargo_client,
        journals_client,
        waybill_client,
        order_core_client,
        cargo_order_client,
):

    comment = library.build_comment()
    claim = cargo_client.create_claim(
        json=library.build_request(
            username=username,
            phone=test_data['phone'],
            comment=comment,
            request=test_data['claim_request'],
            corp_client_id=test_data['corp_client_id'],
            taxi_class=test_data['taxi_class'],
            dont_skip_confirmation=test_data['dont_skip_confirmation'],
            post_payment=test_data['post_payment'],
        ),
    )
    claim_link = library.get_claim_link(claim['id'])
    report = json.dumps({'Claim': claim_link, 'Router': test_data['router'],
                         'Claim type': test_data['claim_type']})
    request.node._report_sections.append(('call', 'Claim link', report))

    claim = cargo_client.wait_for_claim_status(
        claim['id'], ('new', 'estimating'), wait=3,
    )
    assert claim['status'] in (
        'new',
        'estimating',
        'ready_for_approval',
    ), 'Invalid claim status'

    claim = cargo_client.wait_for_claim_status(
        claim['id'], ('ready_for_approval',), wait=3,
    )
    assert claim['status'] == 'ready_for_approval', 'Invalid claim status'

    cargo_client.accept_claim(claim['id'])
    performer_states = (
        'performer_lookup',
        'performer_draft',
        'performer_found',
    )
    claim = cargo_client.wait_for_claim_status(
        claim['id'], performer_states, wait=10,
    )
    assert claim['status'] in performer_states, 'Invalid claim status'

    segment_id = journals_client.wait_for_segment_id(claim['id'], wait=5)
    assert segment_id is not None, 'Segment not created in 5s.'

    segment = waybill_client.wait_for_segment_info(segment_id, wait=10)
    assert segment is not None, 'cargo-dispatch not received segment.'

    segment = waybill_client.wait_for_chosen_waybill(segment_id, wait=300)
    assert segment is not None, 'Waybill was not created in 300s.'

    waybill_id = segment['dispatch']['chosen_waybill']['external_ref']

    waybill = waybill_client.wait_for_taxi_order_info(waybill_id, wait=100)
    assert 'taxi_order_info' in waybill['execution'], 'No taxi_order_info'

    resolution = waybill['dispatch'].get('resolution')
    revision = waybill['dispatch']['revision']

    taxi_order_id = waybill['execution']['taxi_order_info']['order_id']
    assert taxi_order_id is not None, 'No taxi_order_id in waybill'

    order_logs_link = library.get_order_logs_link(taxi_order_id)
    order_logs = json.dumps({'Order logs': order_logs_link})
    request.node._report_sections.append(('call', 'Order logs', order_logs))

    cargo_order_id = waybill['diagnostics']['order_id']
    assert cargo_order_id is not None, 'No cargo_order_id in waybill'

    segment = cargo_client.wait_for_segment_status(
        segment_id, 'performer_found', wait=300,
    )
    assert segment['status'] == 'performer_found'

    dispatch_segment = waybill_client.segment_info(segment_id)
    waybill_ref = dispatch_segment['dispatch']['chosen_waybill'][
        'external_ref'
    ]
    waybill = waybill_client.waybill_info(waybill_ref)
    cargo_order_id = waybill['diagnostics']['order_id']

    performer = cargo_order_client.get_performer_info(cargo_order_id)

    orders_client = cargo_orders_driver.CargoOrdersDriverClient(
        corp_client_id=test_data['corp_client_id'],
        user=username,
        performer=performer,
        dispatch_client=waybill_client,
        waybill_ref=waybill_id,
        cargo_order_id=cargo_order_id,
        net_address=net_address,
    )

    if test_data['case'] == 'default':
        case = itertools.cycle([{}])
    elif test_data['case'] == 'return':
        case = itertools.chain(
            [{}, {'do_return': True}], itertools.cycle([{}]),
        )
    elif test_data['case'] == 'create-only':
        return

    for kwargs in case:
        try:
            if orders_client.iteration(**kwargs):
                break
        except lib.NoPointsLeft:
            break
        time.sleep(2)  # deal with esignature 429

    status = cargo_client.get_claim_status(claim['id'])['status']
    assert status == 'delivered', 'Invalid claim status'

    # waybill = waybill_client.waybill_info(waybill_id)
    # assert waybill['dispatch']['status'] == 'resolved'

    taxi_order_info = waybill['execution']['taxi_order_info']
    taxi_order_id = taxi_order_info['order_id']

    for _ in range(10):
        order_proc = order_core_client.get_order_fields(
            taxi_order_id, ['order.status', 'order.taxi_status'],
        )['fields']
    assert (
        order_proc['order']['taxi_status'] == 'transporting'
    ), 'Invalid order status'
