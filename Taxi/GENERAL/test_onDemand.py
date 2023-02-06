import uuid
from library.ds_create_requests import create_ds_request, send_change_order
from library.mocks.ds_common_body import CREATE_ON_DEMAND_EXPRESS, UPDATE_ORDER
from library.transfers import get_activation_landing, get_info_about_delivery, get_transfer_info, activate_transfer


def test_onDemand():
    request_id = str(uuid.uuid4())
    platform_request=create_ds_request(CREATE_ON_DEMAND_EXPRESS, 'ON_DEMAND', request_id)
    assert len(platform_request) > 0
    send_change_order(UPDATE_ORDER, platform_request)
    transfer_id = get_activation_landing(platform_request)
    assert len(transfer_id) > 0
    transfer_enabled = get_transfer_info(transfer_id)
    assert transfer_enabled == False
    activate_transfer(platform_request, transfer_id)
    taxi_order_id = get_info_about_delivery(platform_request)
    assert len(taxi_order_id) > 0
    transfer_enabled = get_transfer_info(transfer_id)


if __name__ == '__main__':
    test_onDemand()
