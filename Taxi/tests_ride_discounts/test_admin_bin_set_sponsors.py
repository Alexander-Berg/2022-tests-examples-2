async def test_bin_set_sponsors(client, headers):
    response = await client.get('/v1/admin/bin-set-sponsors', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        'sponsors': ['RuPay', 'Maestro', 'Mastercard', 'MIR', 'Visa'],
    }
