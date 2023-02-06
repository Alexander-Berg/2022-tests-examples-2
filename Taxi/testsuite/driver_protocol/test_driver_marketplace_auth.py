import json

import pytest


@pytest.mark.config(MARKETPLACE_AUTH_URL='test_url#')
@pytest.mark.now('2017-04-29T12:00:00+0300')
def test_driver_marketplace_auth_base(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'test_session_id_123FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c459',
    )

    @mockserver.json_handler('/marketplace-api/v1/service/driver/auth')
    def mock_marketplace_api(request):
        return {'code': 'test_code'}

    @mockserver.json_handler('/parks/driver-profiles/search')
    def mock_parks(request):
        data = json.loads(request.data)
        assert data['query']['driver']['id'] == [
            '2eaf04fe6dec4330a6f29a6a7701c459',
        ]
        assert data['query']['park']['id'] == [
            '16de978d526e40c0bf91e847245af741',
        ]
        return {'profiles': [{'driver': {'phones': ['+79161234567']}}]}

    response = taxi_driver_protocol.post(
        'driver/marketplace/auth',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': 'test_session_id_123FFFF',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'marketplace_url': 'test_url#code=test_code'}
