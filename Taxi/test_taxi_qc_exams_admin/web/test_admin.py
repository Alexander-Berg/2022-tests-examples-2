async def test_get_pass_media(
        mockserver, web_app_client, mock_quality_control_py3, open_file,
):
    @mock_quality_control_py3('/admin/qc/v1/pass/media')
    def _mock_pass_media(request):
        assert request.query == {'pass_id': 'some_id', 'media_code': 'selfie'}

        with open_file('taxi_small.jpeg', mode='rb', encoding=None) as fp:
            image = fp.read()
        return mockserver.make_response(
            response=image, content_type='image/jpeg',
        )

    response = await web_app_client.get(
        '/qc-admin/v1/pass/media',
        headers={'X-Yandex-Login': 'yamishanya'},
        params={'exam': 'dkk', 'id': 'some_id', 'code': 'selfie'},
    )

    assert response.status == 200


async def test_pass_personal(web_app_client):
    response = await web_app_client.get(
        '/qc-admin/v1/pass/personal', params={'exam': 'dkk', 'id': 'some_id'},
    )

    assert response.status == 500
