async def test_dummy(taxi_maas):
    response = await taxi_maas.post(
        '/vtb/v1/user/update',
        headers={'MessageUniqueId': '12345abcd'},
        json={'maas_user_id': 'abcd-abcd-0', 'hash_key': 'dba1-abda'},
    )
    assert response.status == 200
    assert response.json() == {}
