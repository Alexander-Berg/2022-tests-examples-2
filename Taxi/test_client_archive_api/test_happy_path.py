async def test_archive_api(mockserver, library_context):
    mocked_result = {'some': 'tome'}

    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _lookup_rows(request):
        return {'items': mocked_result}

    result = await library_context.client_archive_api.lookup_rows(
        'my_query', 'my_rule_name',
    )

    assert result == mocked_result
