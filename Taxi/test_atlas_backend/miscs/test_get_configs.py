async def test_get_configs(web_app_client):
    response = await web_app_client.get('/api/configs')
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['_id'])
    assert len(content) == 1
    assert content[0]['_id'] == 'atlas'
    assert (
        content[0]['tariffEditorHost']
        == 'https://tariff-editor.taxi.tst.yandex-team.ru'
    )
