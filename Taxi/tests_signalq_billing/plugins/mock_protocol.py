# encoding=utf-8
import pytest


@pytest.fixture(name='protocol', autouse=True)
def _mock_protocol(mockserver):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearest_zone(request):
        assert request.json['point'] == [23.1102, 12.0002]
        return {'nearest_zone': 'Omsk'}
