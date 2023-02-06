async def test_idm(library_context, mockserver):
    @mockserver.json_handler('/idm/api/v1/rolerequests/')
    async def _mock_idm(request):
        data = {'path': '/read/', 'user': 'test_login', 'id': 'idm_request_id'}
        return data

    result = await library_context.client_idm.request_role(
        system='yt-cluster-hahn', path='/read/', user='test_login',
    )

    assert result == {
        'path': '/read/',
        'user': 'test_login',
        'id': 'idm_request_id',
    }
