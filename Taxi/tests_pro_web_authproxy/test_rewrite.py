import pytest


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_rewrite(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/rewritten')
    def _mock(request):
        assert request.query == {'a': 'b'}
        return {}

    response = await taxi_pro_web_authproxy.post(
        'rewritetest?a=b', headers={'Cookie': 'Session_id=session1'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert _mock.times_called == 1
