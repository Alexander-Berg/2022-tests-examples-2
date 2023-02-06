from library.mocks.add_simple import BASE_ADD_SIMPLE_PAYLOAD
from library.add_simple_request import add_simple_request
from library.ds_create_requests import create_ds_request
from library.mocks.ds_common_body import DEFERRED_COURIER


def test_deferred_courier():
    request_id = add_simple_request(BASE_ADD_SIMPLE_PAYLOAD)
    assert len(request_id) > 0
    platform_request = create_ds_request(DEFERRED_COURIER, 'DEFERRED_COURIER', request_id)
    assert len(platform_request) > 0



if __name__ == '__main__':
    test_deferred_courier()
