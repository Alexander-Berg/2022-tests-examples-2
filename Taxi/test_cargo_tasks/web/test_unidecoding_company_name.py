async def test_preparing_company_name(web_app_client):
    response = await web_app_client.post(
        '/functions/get-company-name-unidecoded',
        json={'company_name': 'OOO Ретроградный Меркурий'},
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'unidecoded_company_name': 'retrogradnyimerkurii'}
