from taxiparks_app import app
from infranaim.conftest import *


@pytest.fixture
@pytest.mark.filldb
def taxiparks_client(mongodb):
    app.config['SECRET_KEY'] = 'i9i9ii'
    app.db = mongodb
    return app.test_client()


@pytest.fixture
@pytest.mark.fill_db
def taxiparks_client_factory():
    def _run(dbmongo, **kwargs):
        app.config['SECRET_KEY'] = 'i9i9ii'
        for key, value in kwargs.get('configs', {}).items():
            app.config[key] = value
        app.db = dbmongo
        return app.test_client()
    return _run


@pytest.fixture
def csrf_token(taxiparks_client):
    res = taxiparks_client.get('/get_token')
    assert res.status_code == 200
    return res.json['token']


@pytest.fixture
def csrf_token_session(taxiparks_client):
    def _run():
        res = taxiparks_client.get('/get_token')
        assert res.status_code == 200
        return res.json['token']
    return _run


@pytest.fixture
def log_user_in(taxiparks_client, csrf_token):
    def do_it(doc):
        if 'csrf_token' not in doc:
            doc['csrf_token'] = csrf_token
        res = taxiparks_client.post('/login', json=doc)
        return res
    return do_it


@pytest.fixture
def log_in(taxiparks_client, csrf_token):
    return taxiparks_client.post(
        '/login',
        json={
            'login': 'root',
            'password': 'root_pass',
            'csrf_token': csrf_token
        }
    )


@pytest.fixture
def log_user_out(taxiparks_client, csrf_token):
    def do_it(headers):
        res = taxiparks_client.post(
            '/logout',
            headers=headers,
            json={
                'csrf_token': taxiparks_client.get('/get_token').json['token'],
            },
        )
        return res
    return do_it


@pytest.fixture
def taxipark_show(taxiparks_client):
    def do_it(park_id, headers=None):
        res = taxiparks_client.get(
            '/v2/taxiparks/show?_id={}'.format(park_id),
            headers=headers,
        )
        return res.json
    return do_it


@pytest.fixture
def user_edit(taxiparks_client, csrf_token_session):
    def do_it(data, headers=None):
        if 'csrf_token' not in data:
            data['csrf_token'] = csrf_token_session()
        res = taxiparks_client.post(
            '/user_edit',
            json=data,
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture
def users_create(taxiparks_client, csrf_token_session):
    def do_it(data, headers=None):
        if 'csrf_token' not in data:
            data['csrf_token'] = csrf_token_session()
        res = taxiparks_client.post(
            '/users/create',
            json=data,
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture
def user_get(taxiparks_client):
    def do_it(_id, headers=None):
        res = taxiparks_client.get(
            '/user_get',
            query_string={'_id': _id},
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture
def find_documents_in_users():
    def _run(dbmongo):
        return list(dbmongo.users.find())
    return _run
