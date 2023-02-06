import pytest


class Credentials:
    def __init__(self, partner_id, login, password_hash):
        self.partner_id = partner_id
        self.login = login
        self.password_hash = password_hash


class Data:
    def __init__(self, creds, count, response_code):
        self.creds = creds
        self.count = count
        self.code = response_code


@pytest.mark.parametrize(
    'datas',
    [
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(1, 'NaNaNuNa', 'password_hash'), 1, 204),
            ],
            id='check_add_with_diff_login',
        ),
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(10, 'NaNaNuNa_10', 'password_hash'), 1, 204),
                Data(Credentials(12, 'NaNaNuNa_12', 'password_hash'), 2, 204),
                Data(Credentials(14, 'NaNaNuNa_14', 'password_hash'), 3, 204),
                Data(Credentials(16, 'NaNaNuNa_16', 'password_hash'), 4, 204),
                Data(Credentials(18, 'NaNaNuNa18', 'password_hash'), 5, 204),
                Data(Credentials(19, 'NaNaNuNa_19', 'password_hash'), 6, 204),
                Data(Credentials(200, 'NaNaNuNa200', 'password_hash'), 7, 204),
            ],
            id='set credentionals for diff login and partner_id',
        ),
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(1, 'NANANUNA', 'password_hash'), 1, 204),
                Data(Credentials(1, 'NaNaNUNA', 'password_hash_1'), 1, 204),
                Data(Credentials(1, 'NanaNunA', 'password_hash_2'), 1, 204),
            ],
            id='set creds for one login with diff case',
        ),
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(1, 'nananuna_1', 'password_hash'), 1, 204),
                Data(Credentials(1, 'nanunana_2', 'password_hash'), 1, 204),
                Data(Credentials(1, 'nananuna', 'password_hash_2'), 1, 204),
                Data(Credentials(1, 'nananuna_3', 'password_hash_3'), 1, 204),
            ],
            id='set creds for diff login with one partner_id',
        ),
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(2, 'nananuna', 'password_hash'), 1, 400),
                Data(Credentials(20, 'NANAnuna', 'password_hash_2'), 1, 400),
                Data(Credentials(30, 'NanaNuna_2', 'password_hash'), 1, 204),
            ],
            id='set creds with conflict login',
        ),
        pytest.param(
            [
                Data(Credentials(1, 'nananuna', None), 0, 400),
                Data(Credentials(1, 'nananuna', 'password_hash'), 0, 204),
                Data(Credentials(1, 'NanaNuna_2', None), 1, 204),
            ],
            id='set creds without password',
        ),
    ],
)
async def test_internal_set_credentials_partner(
        taxi_eats_restapp_authorizer, pgsql, datas,
):
    cursor = pgsql['eats_restapp_authorizer'].cursor()

    for data in datas:
        creds = data.creds
        cursor.execute(
            'SELECT COUNT(*) ' 'FROM eats_restapp_authorizer.partners_creds',
        )
        assert list(cursor)[0] == (data.count,)

        headers = {'login': creds.login}
        if creds.password_hash:
            headers['password'] = creds.password_hash

        response = await taxi_eats_restapp_authorizer.post(
            '/internal/partner/set_credentials',
            headers=headers,
            json={'partner_id': creds.partner_id},
        )
        assert response.status_code == data.code

        if data.code == 204:
            cursor.execute(
                'SELECT login, password FROM '
                'eats_restapp_authorizer.partners_creds '
                'WHERE partner_id = {}'.format(creds.partner_id),
            )
            row = list(cursor)[0]
            assert row[0] == str(creds.login).lower()
            if creds.password_hash:
                assert row[1] == creds.password_hash
            else:
                assert len(row[1]) > 5


@pytest.mark.redis_store(
    ['set', 'partner_id:5', '{"email":"nananuna","version":"22"}'],
    ['expire', 'partner_id:5', 3000],
    ['set', 'token:111', '{"partner_id":5,"version":"22"}'],
    ['expire', 'token:111', 3000],
)
@pytest.mark.parametrize(
    'default_login,default_password,default_id',
    [pytest.param('nananuna', 'password_1', 5)],
)
@pytest.mark.parametrize(
    'partner_id, login, password, token, is_unset',
    [
        pytest.param(5, 'nananuna', 'password_1', '111', False),
        pytest.param(5, 'nananuna_2', 'password_1', '111', True),
        pytest.param(5, 'nananuna', 'password_2', '111', True),
        pytest.param(5, 'NanaNuna_3', 'password_3', '111', True),
        pytest.param(5, 'NaNaNUNA', 'password_1', '111', False),
    ],
)
async def test_iternal_set_credentials_partner_with_unset(
        taxi_eats_restapp_authorizer,
        default_login,
        default_password,
        default_id,
        partner_id,
        login,
        password,
        token,
        is_unset,
):
    # set default data
    response = await taxi_eats_restapp_authorizer.post(
        '/internal/partner/set_credentials',
        headers={'login': default_login, 'password': default_password},
        json={'partner_id': default_id},
    )
    assert response.status_code == 204

    # set new data
    response = await taxi_eats_restapp_authorizer.post(
        '/internal/partner/set_credentials',
        headers={'login': login, 'password': password},
        json={'partner_id': partner_id},
    )
    assert response.status_code == 204

    # check session
    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        '/v1/session/current', json=data,
    )
    if not is_unset:
        assert response.status_code == 200
        assert response.json()['partner_id'] == partner_id
        assert response.json()['email'] == default_login
    else:
        assert response.status_code == 404


@pytest.mark.parametrize(
    'request_data',
    [
        [],
        [{'id': 1, 'login': 'nananuna', 'hash': 'password_hash'}],
        [
            {'id': 1, 'login': 'nananuna', 'hash': 'password_hash'},
            {'id': 2, 'login': 'nananuna_2', 'hash': 'password_hash_2222'},
            {'id': 3, 'login': 'NANANUNA_3', 'hash': 'password_hash_3'},
        ],
    ],
)
async def test_internal_credentials_bulk(
        taxi_eats_restapp_authorizer, pgsql, request_data,
):
    cursor = pgsql['eats_restapp_authorizer'].cursor()

    response = await taxi_eats_restapp_authorizer.post(
        '/internal/partner/bulk_add_credentials',
        json={'payload': request_data},
    )
    assert response.status_code == 204

    cursor.execute(
        'SELECT partner_id, login, password '
        'FROM eats_restapp_authorizer.partners_creds '
        'ORDER BY partner_id',
    )
    data = list(cursor)
    assert len(data) == len(request_data)
    inc = 0
    for item in request_data:
        assert data[inc] == (item['id'], item['login'].lower(), item['hash'])
        inc += 1
