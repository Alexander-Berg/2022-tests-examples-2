async def test_enumerate(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f0',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f1',
                ),
                'status': 'succeeded',
                'created_by': 'islam-boziev',
            },
        ]

    expected = load_json('taxi_enumerate_expected.json')
    response = await web_app_client.post(
        '/v2/pipeline/enumerate', params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200
    data = await response.json()
    data = sorted(data, key=lambda x: x['id'])

    assert data == expected

    # enumerate with 'name' filter
    expected = [load_json('taxi_enumerate_expected.json')[0]]
    response = await web_app_client.post(
        '/v2/pipeline/enumerate',
        params={'consumer': 'taxi-surge', 'name': 'taxi_default'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == expected

    # enumerate with 'states' filter
    expected = load_json('taxi_enumerate_expected.json')
    response = await web_app_client.post(
        '/v2/pipeline/enumerate',
        params={'consumer': 'taxi-surge', 'states': 'active,valid'},
    )
    assert response.status == 200
    data = await response.json()
    data = sorted(data, key=lambda x: x['id'])

    assert data == expected

    expected = []
    response = await web_app_client.post(
        '/v2/pipeline/enumerate',
        params={'consumer': 'taxi-surge', 'states': 'draft'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == expected


async def test_child_id(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        pipelines = load_json('db_admin_pipeline_pipelines.json')
        return [
            {
                'change_doc_id': 'admin_pipeline/pipelines_{}'.format(
                    pipeline['_id'],
                ),
                'status': 'succeeded',
                'created_by': 'username',
            }
            for pipeline in pipelines
        ]

    response = await web_app_client.post(
        'v2/pipeline/enumerate',
        params={
            'consumer': 'eda-surge',
            'child_id': '5de7baf5eb70bf332afa2603',
        },
    )
    assert response.status == 200
    data = await response.json()

    expected_ids = [
        '5de7baf5eb70bf332afa2601',
        '5de7baf5eb70bf332afa2600',
        '5de7baf5eb70bf332afa25f1',
    ]

    assert len(data) == 3
    for i, expected in enumerate(expected_ids):
        assert data[i]['id'] == expected


async def test_bad(web_app_client, mockserver, load_json):
    response = await web_app_client.post(
        'v2/pipeline/enumerate',
        params={
            'consumer': 'eda-surge',
            'child_id': '5de7baf5eb70bf332afa2603',
            'name': 'some',
        },
    )

    assert response.status == 400
    assert await response.text() == (
        '400: child_id should be specified without name and states'
    )
