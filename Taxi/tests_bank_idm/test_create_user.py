async def test_create_user(taxi_bank_idm, pgsql):
    request = {'login': 'test_user', 'email': 'test@gmail.com'}

    response = await taxi_bank_idm.post('v1/create-user', json=request)
    assert response.status_code == 200

    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        'select login, email from bank_idm.users '
        f'where user_id = {response.json()["user_id"]}',
    )
    result = cursor.fetchall()[0]
    assert result[0] == request['login']
    assert result[1] == request['email']
