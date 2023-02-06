HEADERS = {'Accept-Language': 'ruRu'}


async def test_history_filters(web_app_client, load_json):
    response = await web_app_client.get(
        '/qc-admin/v1/history/filters', headers=HEADERS,
    )

    assert response.status == 200

    data = await response.json()

    data['types'] = sorted(data['types'], key=lambda v: v['type'])
    for item in data['types']:
        item['exams'] = sorted(item['exams'], key=lambda k: k['code'])
        for exam in item['exams']:
            exam['filters'] = sorted(exam['filters'], key=lambda k: k['field'])

    assert data == load_json('v1_history_filters.json')


async def test_settings(web_app_client, load_json):
    response = await web_app_client.get(
        '/qc-admin/v1/settings', headers=HEADERS,
    )

    assert response.status == 200
    data = await response.json()

    data['items'] = sorted(
        data['items'], key=lambda v: v['type'] + '_' + v['code'],
    )
    assert data == load_json('v1_settings.json')
