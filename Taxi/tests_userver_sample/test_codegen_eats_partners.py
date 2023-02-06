async def test_eats_partners_authproxy(taxi_userver_sample):
    headers = {
        'X-YaEda-PartnerId': '123',
        'X-YaEda-Partner-Uid': '99fe9999',
        'X-YaEda-Partner-Places': '11,22,33',
        'X-YaEda-Partner-Country-Code': 'RU',
        'X-YaEda-Partner-Personal-Email-Id': '123_id',
    }

    response = await taxi_userver_sample.post(
        '/eats-partners/v1/test',
        headers=headers,
        json={'places_to_check': [11]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'partner_id': 123,
        'partner_uid': '99fe9999',
        'places': [11, 22, 33],
        'country_code': 'RU',
        'personal_email_id': '123_id',
        'partner_has_access_to_places': True,
    }
