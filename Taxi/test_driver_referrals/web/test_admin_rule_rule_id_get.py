async def test_admin_rule_rule_id_get(web_app_client, load_json):
    response = await web_app_client.get('/admin/rule/not_found')
    assert response.status == 404

    rules = load_json('rules.json')
    rules_by_id = {rule['rule_id']: rule for rule in rules}
    for rules_id, rule in rules_by_id.items():
        response = await web_app_client.get(f'/admin/rule/{rules_id}')
        assert response.status == 200
        content = await response.json()
        assert content == rule
