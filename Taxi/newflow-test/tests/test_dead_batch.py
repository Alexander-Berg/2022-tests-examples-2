import pytest

from cargo_newflow import consts
from cargo_newflow import library
from cargo_newflow import utils


# corp segment_routers_config:
# "build_interval_seconds": 100,
# "create_before_due_seconds": 100

BASE_TEST_DATA = {
    'corp_client_id': consts.BATCH_ENABLED_CORP_CLIENT_ID,
    'yandex_uid': '123',
    'phone': '+70009998877',
    'claim_request': utils.get_project_root() / 'requests/batch.json',
    'taxi_class': 'courier',
    'dont_skip_confirmation': False,
    'post_payment': None,
    'case': 'default',
    'batch_size': 2,
}


@pytest.mark.parametrize(
    'cargo_client',
    (BASE_TEST_DATA, ),
    indirect=True,
)
@pytest.mark.parametrize(
    'test_data',
    (BASE_TEST_DATA, ),
)
def test_dead_batch(test_data, net_address, username, cargo_client,
                    journals_client, waybill_client, order_core_client,
                    cargo_order_client):

    for item in range(test_data['batch_size']):
        comment = library.build_comment(wait=0, comment='batch test')
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
            claim['id'], ('new', 'estimating'), wait=3)
        assert claim['status'] in ('new', 'estimating', 'ready_for_approval'), (
            'Invalid claim status')

        claim = cargo_client.wait_for_claim_status(
            claim['id'], ('ready_for_approval', ), wait=3)
        assert claim['status'] == 'ready_for_approval', 'Invalid claim status'

        cargo_client.accept_claim(claim['id'])

    orders = []
    for item in range(test_data['batch_size']):
        performer_states = (
            'performer_lookup', 'performer_draft', 'performer_found', )
        claim = cargo_client.wait_for_claim_status(
            claim['id'], performer_states, wait=10)
        assert claim['status'] in performer_states, ('Invalid claim status')

        segment_id = journals_client.wait_for_segment_id(claim['id'], wait=5)
        assert segment_id is not None, 'Segment not created in 5s.'

        segment = waybill_client.wait_for_segment_info(segment_id, wait=10)
        assert segment is not None, 'cargo-dispatch not received segment.'

        segment = waybill_client.wait_for_chosen_waybill(segment_id, wait=100)
        assert segment is not None, 'Waybill was not created in 300s.'

        waybill_id = segment['dispatch']['chosen_waybill']['external_ref']

        waybill = waybill_client.wait_for_taxi_order_info(waybill_id, wait=100)
        assert 'taxi_order_info' in waybill['execution'], 'No taxi_order_info'

        taxi_order_id = waybill['execution']['taxi_order_info']['order_id']
        assert taxi_order_id is not None, 'No taxi_order_id in waybill'
        orders.append(taxi_order_id)
    assert orders.count(orders[0]) == len(orders), 'Batch not happened'
