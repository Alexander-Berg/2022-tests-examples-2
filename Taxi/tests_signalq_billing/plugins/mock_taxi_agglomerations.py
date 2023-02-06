import pytest


@pytest.fixture(name='taxi_agglomerations', autouse=True)
def _mock_taxi_agglomerations(mockserver):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _mock_mvp(request):
        assert request.query['tariff_zone'] in ('Moscow', 'Omsk')
        if request.query['tariff_zone'] == 'Moscow':
            return {'oebs_mvp_id': 'mvp1'}
        return {'oebs_mvp_id': 'mvp2'}
