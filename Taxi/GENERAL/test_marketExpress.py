import uuid
from library.ds_create_requests import create_ds_request, send_change_order
from library.mocks.ds_common_body import CREATE_ON_DEMAND_EXPRESS,  UPDATE_ORDER, CALL_COURIER


def test_market_express():
    request_id = str(uuid.uuid4())
    platform_request = create_ds_request(CREATE_ON_DEMAND_EXPRESS, 'EXPRESS', request_id)
    assert len(platform_request) > 0
    send_change_order(UPDATE_ORDER, platform_request)
    send_change_order(CALL_COURIER, platform_request)


if __name__ == '__main__':
    test_market_express()