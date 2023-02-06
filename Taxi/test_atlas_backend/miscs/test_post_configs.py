async def test_post_configs(web_app_client, db):
    new_config = {
        '_id': 'atlas2',
        'tariffEditorHost': 'https://tariff-editor.taxi.yandex-team.ru',
    }
    response = await web_app_client.post('/api/configs', json=new_config)
    assert response.status == 200

    content = await response.json()

    assert content == {'status': 'ok', 'desc': 'created'}

    created_config = await db.atlas_configs_frontend.find_one(
        {'_id': 'atlas2'},
    )

    assert created_config['tariffEditorHost'] == new_config['tariffEditorHost']


async def test_post_configs_updated(web_app_client, db):
    new_config = {
        '_id': 'atlas',
        'tariffEditorHost': 'https://tariff-editor.taxi.yandex-team.ru',
        'ololo_field': 'ololo',
    }
    response = await web_app_client.post('/api/configs', json=new_config)
    assert response.status == 200

    content = await response.json()

    assert content == {'status': 'ok', 'desc': 'updated'}

    created_config = await db.atlas_configs_frontend.find_one({'_id': 'atlas'})

    assert created_config['tariffEditorHost'] == new_config['tariffEditorHost']
    assert created_config['ololo_field'] == 'ololo'
    assert created_config.get('env') is None
