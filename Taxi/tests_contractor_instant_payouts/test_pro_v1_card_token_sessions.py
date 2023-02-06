async def test_create_card_token_session_modulbank(pro_v1, mock_api):
    response = await pro_v1.create_card_token_session(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        json={'id': '30000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 200, response.text

    json = response.json()
    assert json['id'] == '30000000-0000-0000-0000-000000000001'
    assert json['form_url'].startswith('https://')
    assert json['form_url'].endswith('/forms/cards/tokenize?session=xxx')


async def test_create_card_token_session_qiwi(pro_v1, mock_api):
    response = await pro_v1.create_card_token_session(
        park_id='PARK-02',
        contractor_id='CONTRACTOR-01',
        json={'id': '30000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 200, response.text

    json = response.json()
    assert json['id'] == '30000000-0000-0000-0000-000000000001'
    assert json['form_url'] == 'https://oplata.qiwi.com/form/?invoice_uid=xxx'


async def test_create_card_token_session_interpay(pro_v1, mock_api):
    response = await pro_v1.create_card_token_session(
        park_id='PARK-Interpay',
        contractor_id='CONTRACTOR-01',
        json={'id': '30000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 200, response.text

    json = response.json()
    assert json['id'] == '30000000-0000-0000-0000-000000000001'
    assert (
        json['form_url']
        == 'https://cp.sandbox.interpaysys.com/v1/disbmt/cards/1/nonce1'
    )
