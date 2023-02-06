import passlib.hash
import pytest


@pytest.fixture
def set_config(mock_external_config, load_json):
    mock_external_config(
        load_json('external_config.json')['default']
    )


@pytest.mark.usefixtures('set_config')
@pytest.mark.parametrize(
    'data_type, name, status_code',
    [
        ('valid', 'agent_legal_entity', 200),
        ('invalid', 'empty', 400),
        ('invalid', 'existing_login_users', 409),
        ('invalid', 'existing_login_custom_fields', 409),
        ('invalid', 'existing_tag', 409),
        ('invalid', 'missing_login', 400),
        ('invalid', 'missing_password', 400),
        ('invalid', 'missing_name', 400),
        ('invalid', 'missing_second_name', 400),
        ('invalid', 'missing_role', 400),
    ]
)
def test_users_create(
        taxiparks_client_factory, find_documents_in_users,
        log_user_in, users_create, load_json, get_mongo,
        data_type, name, status_code,
):
    mongo = get_mongo
    existing_users = len(find_documents_in_users(mongo))
    client = taxiparks_client_factory(mongo)
    client.post(
        '/login', json={
            "login": "root",
            "password": "root_pass",
            "csrf_token": client.get('/get_token').json['token'],
        }
    )
    data = load_json('requests_create.json')[data_type][name]
    cities = []
    if 'cities' in data:
        cities = client.get('/get_cities').json
        data['cities'] = [
            item['id']
            for item in cities
        ]
    data['csrf_token'] = client.get('/get_token').json['token']
    res = client.post('/users/create', json=data)
    assert res.status_code == status_code
    if status_code == 200:
        docs = find_documents_in_users(mongo)
        assert len(docs) == existing_users + 1
        new_user = next(
            (
                doc
                for doc in docs
                if doc['login'] == data['login']
            ),
            None
        )
        assert new_user
        assert passlib.hash.pbkdf2_sha256.verify(
            data['password'],
            new_user['password'],
        )
        assert new_user['role'] == data['role']
        assert new_user['created_by'] == 'root'
        assert new_user['updated_by'] == 'root'
        assert new_user['user_name'] == '{} {}'.format(
            data['second_name'], data['name'],
        )
        if data['role'].startswith('eda_'):
            assert 'cities' in new_user
            if data['role'] != 'eda_admin':
                assert new_user['cities'] == cities


@pytest.mark.parametrize(
    'data_type, name, status_code',
    [
        ('valid', 'root', 200),
        ('valid', 'passport_user', 200),
        ('invalid', 'empty', 400),
        ('invalid', 'missing_login', 400),
    ]
)
def test_users_edit(
        taxiparks_client_factory, find_documents_in_users,
        log_user_in, users_create, load_json, get_mongo,
        data_type, name, status_code,
):
    mongo = get_mongo
    existing_users = len(find_documents_in_users(mongo))
    client = taxiparks_client_factory(mongo)
    client.post(
        '/login', json={
            "login": "root",
            "password": "root_pass",
            "csrf_token": client.get('/get_token').json['token'],
        }
    )
    data = load_json('requests_edit.json')[data_type][name]
    data['csrf_token'] = client.get('/get_token').json['token']
    res = client.post('/user_edit', json=data)
    assert res.status_code == status_code
    if status_code == 200:
        docs = find_documents_in_users(mongo)
        assert len(docs) == existing_users
        new_user = next(
            (
                doc
                for doc in docs
                if doc['_id'] == data['_id']
            ),
            None
        )
        assert new_user
        if name == 'root':
            assert passlib.hash.pbkdf2_sha256.verify(
                data['password'],
                new_user['password'],
            )
            assert new_user['role'] == data['role']
            assert new_user['created_by'] == 'creator'
            assert new_user['updated_by'] == 'root'
        elif name == 'passport_user':
            assert new_user['personal_yandex_login_id']
            assert 'yandex_login' not in new_user
