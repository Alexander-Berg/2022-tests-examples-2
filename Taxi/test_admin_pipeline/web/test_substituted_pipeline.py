import pytest


@pytest.mark.now('2019-12-16T20:38:50+00:00')
async def test_enumerate(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f1',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
        ]

    expected = load_json('taxi_enumerate_expected.json')
    response = await web_app_client.post(
        '/v2/pipeline/enumerate',
        params={'consumer': 'taxi-surge', 'states': 'active'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == expected


@pytest.mark.now('2019-12-16T20:38:50+00:00')
async def test_cache_enumerate(web_app_client, mockserver, load_json):
    expected = load_json('taxi_enumerate_cache_expected.json')
    response = await web_app_client.get('/cache/taxi-surge/pipeline/enumerate')
    assert response.status == 200
    data = await response.json()
    assert data == expected


@pytest.mark.now('2019-12-16T20:38:50+00:00')
async def test_cache_enumerate_with_approved(
        web_app_client, mockserver, load_json,
):
    expected = load_json('taxi_enumerate_cache_with_approved_expected.json')
    response = await web_app_client.get(
        '/cache/taxi-surge/pipeline/enumerate?include_approved=true',
    )
    assert response.status == 200
    data = await response.json()
    assert data == expected
