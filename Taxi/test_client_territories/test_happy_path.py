async def test_territories(library_context, patch, mockserver):
    mocked_result = {'some': 'tome'}

    @mockserver.json_handler('/territories/v1/countries/retrieve')
    def _mock(request):
        assert request.method == 'POST'
        assert request.json == {'_id': 1}
        assert request.headers['X-YaRequestId']
        assert request.headers['X-Ya-Service-Ticket'] == '123'
        return mocked_result

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers(*args, **kwargs):
        return {'X-Ya-Service-Ticket': '123'}

    result = await library_context.client_territories.get_country(
        1, log_extra={'_link': '123'},
    )

    assert result == mocked_result
