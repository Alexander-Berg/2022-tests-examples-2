async def test_upload_ok(library_context, mockserver):
    content = b'qwe'
    project_id = 123
    url = f'/yandex-doc/v1/projects/{project_id}/async_deploy'

    @mockserver.handler(url)
    def _patched(request):
        assert request.method == 'POST'
        assert request.headers['Authorization'] == 'OAuth oauth-token'
        assert request.content_type == 'multipart/form-data'
        assert request.get_data().decode('utf-8').split('\r\n')[-3] == (
            content.decode('utf-8')
        )
        return mockserver.make_response('', status=200)

    await library_context.client_daas.upload(content, project_id)
