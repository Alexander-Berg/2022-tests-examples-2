import tests_bank_idm.db_helpers as db_helpers


async def test_disable_system(taxi_bank_idm, pgsql):
    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'idm', 'user_login': 'kalievoral'},
    )
    assert response.status_code == 200

    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        'select system_status from bank_idm.systems '
        'where system_slug = \'idm\'',
    )
    system_status = cursor.fetchall()[0][0]
    assert system_status == 'disabled'


async def test_disable_system_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'user_without_permission'
    db_helpers.add_user(pgsql, user_login, 'test@gmail.com')

    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'idm', 'user_login': user_login},
    )
    assert response.status_code == 403


async def test_disable_system_user_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'idm', 'user_login': 'not_existed_user'},
    )
    assert response.status_code == 404


async def test_disable_system_system_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'not_existed_system', 'user_login': 'kalievoral'},
    )
    assert response.status_code == 404


async def test_disable_system_few_times(taxi_bank_idm, pgsql, testpoint):
    @testpoint('system_already_disabled')
    def system_already_disabled_tp(_):
        return

    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'idm', 'user_login': 'kalievoral'},
    )
    assert response.status_code == 200

    assert system_already_disabled_tp.times_called == 0
    response = await taxi_bank_idm.post(
        'v1/disable-system',
        json={'system_slug': 'idm', 'user_login': 'kalievoral'},
    )
    assert system_already_disabled_tp.times_called == 1
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        'select system_status from bank_idm.systems '
        'where system_slug = \'idm\'',
    )
    system_status = cursor.fetchall()[0][0]
    assert system_status == 'disabled'
