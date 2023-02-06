from taxi.clients import surger


async def test_surger(library_context, mockserver):
    url = '/surger-api/check_script'
    mocked_result = {'status': 'passed', 'message': ''}

    response_json = None

    @mockserver.json_handler(url)
    async def _mocked_response(request):
        nonlocal response_json
        assert request.method == 'PUT'
        assert str(request.url).endswith(url)
        response_json = request.json
        return mocked_result

    await library_context.client_surger.check_script(
        surger.ScriptType.BALANCE_EQUATION, '<source>',
    )

    assert response_json == {'type': 'balance_equation', 'source': '<source>'}
