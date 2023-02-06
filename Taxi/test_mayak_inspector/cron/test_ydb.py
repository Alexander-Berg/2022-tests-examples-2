def test_mock(patch):
    @patch(
        'mayak_inspector.generated.service'
        '.ydb_client.plugin.YdbClient.execute',
    )
    async def _execute(*args, **kwargs):
        return []
