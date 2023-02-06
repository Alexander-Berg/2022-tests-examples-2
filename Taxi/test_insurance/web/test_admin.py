import pytest

LIST_EXPECTED_RESPONSE = {
    'items': [
        {
            'contract_date_finish': '2020-08-02',
            'contract_date_start': '2020-01-02',
            'country': 'rus',
            'id': '1',
            'name': 'Allianz',
            'weight': 10,
        },
        {
            'contract_date_finish': '2020-08-02',
            'contract_date_start': '2020-01-02',
            'country': 'rus',
            'id': '2',
            'name': 'ВТБ Страхование',
        },
    ],
}

INSURER_DATA = {
    'name': 'НовыйСтрах',
    'weight': 20,
    'country': 'rus',
    'contract_date_finish': '2020-08-27',
    'contract_date_start': '2020-08-26',
}


async def test_list(web_app_client):
    response = await web_app_client.get('/v1/admin/list')
    assert response.status == 200
    content = await response.json()
    assert content == LIST_EXPECTED_RESPONSE


@pytest.mark.parametrize(
    'insurer_id, expect_code, expect_content',
    [
        pytest.param(
            '1',
            200,
            {
                'contract_date_finish': '2020-08-02',
                'contract_date_start': '2020-01-02',
                'country': 'rus',
                'id': '1',
                'name': 'Allianz',
                'weight': 10,
            },
            id='simple test',
        ),
        pytest.param('666', 404, None, id='insurer not found'),
    ],
)
async def test_details(
        web_app_client, insurer_id, expect_code, expect_content,
):
    response = await web_app_client.get(
        '/v1/admin/detail', params={'insurer_id': insurer_id},
    )
    assert response.status == expect_code
    if response.status == 404:
        return

    content = await response.json()
    assert content == expect_content


@pytest.mark.config(INSURANCE_CAMPAIGN_SLUG='test_slug')
async def test_create(web_app_client, patch, mock_uuid_uuid4):
    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _send(slug, email, **kwargs):
        assert slug == 'test_slug'
        assert email == 'login@yandex-team.ru'
        assert kwargs['template_vars'] == {
            'api_key': '00000000000040008000000000000000',
            'insurer_name': 'НовыйСтрах',
        }

    response = await web_app_client.post(
        '/v1/admin/create',
        json=INSURER_DATA,
        headers={'X-Yandex-Login': 'login'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'id': '00000000000040008000000000000000',
        'status': 'ok',
    }


async def test_update(web_app_client):
    response = await web_app_client.put(
        '/v1/admin/update', params={'insurer_id': '1'}, json=INSURER_DATA,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'insurer': {'id': '1', **INSURER_DATA}, 'status': 'ok'}


@pytest.mark.parametrize(
    'insurer_id, expect_code, expect_content',
    [
        pytest.param(
            '1',
            200,
            {'count': 60, 'id': '1', 'status': 'ok'},
            id='simple test 1',
        ),
        pytest.param(
            '2',
            200,
            {'count': 13, 'id': '2', 'status': 'ok'},
            id='simple test 2',
        ),
        pytest.param(
            '3',
            200,
            {'count': 0, 'id': '3', 'status': 'ok'},
            id='simple test 3',
        ),
        pytest.param(
            '666',
            200,
            {'count': 0, 'id': '666', 'status': 'ok'},
            id='insurer not found',
        ),
    ],
)
async def test_report_count(
        web_app_client, insurer_id, expect_code, expect_content,
):
    response = await web_app_client.get(
        '/v1/admin/report_count',
        params={
            'insurer_id': insurer_id,
            'start_at': '2020-08-03',
            'end_at': '2020-08-06',
        },
    )
    assert response.status == expect_code
    if response.status == 404:
        return

    content = await response.json()
    assert content == expect_content
