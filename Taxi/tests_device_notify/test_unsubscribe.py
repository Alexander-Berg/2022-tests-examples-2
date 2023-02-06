import pytest


@pytest.fixture(name='iid_service')
def _iid_service(mockserver):
    @mockserver.json_handler('/iid/v1:batchAdd')
    def _iid_batch_add(request):
        return {'results': [{}]}

    @mockserver.json_handler('/iid/v1:batchRemove')
    def _iid_batch_remove(request):
        return {'results': [{}]}


# @pytest.mark.filldb()
async def test_unsubscribe(taxi_device_notify, iid_service):
    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {'uid': 'driver:1', 'service': k_service_name1}

    response = await taxi_device_notify.post(
        'v1/unsubscribe', params=params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
