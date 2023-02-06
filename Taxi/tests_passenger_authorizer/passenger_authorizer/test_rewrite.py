import pytest

import utils


REWRITE_RULE = utils.make_rule(
    {
        'input': {'prefix': '/4.0'},
        'proxy': {'proxy_401': True},
        'output': {'rewrite_path_prefix': '/rewrite'},
    },
)


@pytest.mark.routing_rules([REWRITE_RULE])
async def test_rewrite(taxi_passenger_authorizer, mockserver):
    @mockserver.json_handler('/rewrite/proxy/abba')
    def _mock(request):
        assert request.query == {'a': 'b'}
        return {}

    response = await taxi_passenger_authorizer.post('4.0/proxy/abba?a=b')
    assert response.status_code == 200
    assert response.json() == {}

    assert _mock.times_called == 1
