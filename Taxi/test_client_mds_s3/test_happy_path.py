async def test_mds_s3(library_context, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.delete_object')
    async def patched(key):
        return True

    assert await library_context.client_mds_s3.delete_object(1)
    assert patched.calls == [{'key': 1}]

    assert library_context.client_mds_s3.s3_settings == {
        'access_key_id': 'access-key-id',
        'bucket': 'bucket-name',
        'secret_key': 'secret-key',
        'url': 's3.nonexistent',
        'config': {},
    }
