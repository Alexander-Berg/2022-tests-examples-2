import itertools
import time
import json

import pytest

from cargo_newflow.clients import cargo_orders_driver
from cargo_newflow import consts
from cargo_newflow import library
from cargo_newflow import utils

from . import lib


LD_TEST_DATA = {
    'corp_client_id': consts.BATCH_ENABLED_CORP_CLIENT_ID,
    'yandex_uid': consts.DEFAULT_YANDEX_UID,
    'phone': '+70009998877',
    'claim_request': utils.get_project_root() / 'requests/batch.json',
    'taxi_class': 'courier',
    'dont_skip_confirmation': False,
    'post_payment': None,
    'speed': 999,
    'wait': 60,
}

UD_TEST_DATA = {
    'corp_client_id': consts.BATCH_ENABLED_CORP_CLIENT_ID,
    'yandex_uid': consts.DEFAULT_YANDEX_UID,
    'phone': '+79269530091',
    'claim_request': utils.get_project_root() / 'requests/batch.json',
    'taxi_class': 'courier',
    'dont_skip_confirmation': False,
    'post_payment': None,
    'speed': 999,
    'wait': 0,
}


@pytest.mark.parametrize(
    'test_data', (LD_TEST_DATA, UD_TEST_DATA,), indirect=True,
)
def test_live_batch(
        test_data,
        username,
        cargo_client,
        journals_client,
        waybill_client,
):
    claims = []
    latest_segment_id=None
    for i in range(2):
        comment = library.build_comment(
            wait=test_data['wait'],
            speed=test_data['speed'],
            live_batch_with=latest_segment_id)

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

        claim = cargo_client.wait_for_claim_status(
            claim['id'], ('ready_for_approval'), wait=10)
        assert claim['status'] in ('ready_for_approval'), (
            'Invalid claim status')
        
        cargo_client.accept_claim(claim['id'])
        
        claim = cargo_client.wait_for_claim_status(
            claim['id'], ('performer_found'), wait=300)
        assert claim['status'] in ('performer_found'), ('Invalid claim status')
        
        latest_segment_id = journals_client.wait_for_segment_id(claim['id'], wait=10)
        assert latest_segment_id is not None, 'Segment not created in 10s.'

        claims.append(claim)

    orders = []
    for claim in claims:
        segment_id = journals_client.wait_for_segment_id(claim['id'], wait=10)
        assert segment_id is not None, 'Segment not created in 10s.'
        
        segment = waybill_client.wait_for_segment_info(segment_id, wait=100)
        assert segment is not None, 'cargo-dispatch not received segment.'

        segment = waybill_client.wait_for_chosen_waybill(segment_id, wait=100)
        assert segment is not None, 'Waybill was not created in 100s.'

        waybill_id = segment['dispatch']['chosen_waybill']['external_ref']

        waybill = waybill_client.wait_for_taxi_order_info(waybill_id, wait=100)
        assert 'taxi_order_info' in waybill['execution'], 'No taxi_order_info'

        taxi_order_id = waybill['execution']['taxi_order_info']['order_id']
        assert taxi_order_id is not None, 'No taxi_order_id in waybill'
        
        orders.append(taxi_order_id)
    assert orders.count(orders[0]) == len(orders), 'Live Batch not happened'
