async def test_admin_get(web_app_client, load_json):
    response = await web_app_client.get('/admin')
    assert response.status == 200
    content = await response.json()
    assert sorted(
        content['rules'], key=lambda rule: rule['rule_id'],
    ) == sorted(load_json('rules.json'), key=lambda rule: rule['rule_id'])
    assert content['settings'] == load_json('settings.json')
