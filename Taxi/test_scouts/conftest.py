import datetime

import flask.testing

from app import app
from infranaim.conftest import *


SERVICE_TICKET_HEADER = 'X-Ya-Service-Ticket'
YANDEX_LOGIN_HEADER = 'X-Yandex-Login'


@pytest.fixture
@pytest.mark.filldb
def flask_client(mongodb):
    app.config['SECRET_KEY'] = 'i9i9ii'
    app.config['MAX_DAYS_SINCE_TICKET_CREATION'] = 10
    app.config['MAX_DAYS_SINCE_DFT'] = 5
    app.config['DATE_ACTIVE_FIELD'] = 'date_active_25'
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=31)
    app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(days=365)
    app.db = mongodb
    return app.test_client()


@pytest.fixture
@pytest.mark.fill_db
def flask_client_factory():
    def _run(db_mongo, **kwargs) -> flask.testing.FlaskClient:
        app.config['SECRET_KEY'] = 'i9i9ii'
        for key, value in kwargs.get('configs', {}).items():
            app.config[key] = value
        app.db = db_mongo
        return app.test_client()
    return _run


@pytest.fixture
def csrf_token(flask_client):
    res = flask_client.get('/get_token')
    assert res.status_code == 200
    return res.json['token']


@pytest.fixture
def csrf_token_session(flask_client):
    def _run():
        res = flask_client.get('/get_token')
        assert res.status_code == 200
        return res.json['token']
    return _run


@pytest.fixture
def log_user_in(flask_client):
    def do_it(doc):
        if 'csrf_token' not in doc:
            doc['csrf_token'] = flask_client.get('/get_token').json['token']
        res = flask_client.post('/login', json=doc)
        return res
    return do_it


@pytest.fixture
def log_in(flask_client, csrf_token):
    return flask_client.post(
        '/login',
        json={
            'login': 'scout',
            'password': 'scout_pass',
            'csrf_token': csrf_token
        }
    )


@pytest.fixture
def log_user_out(flask_client):
    def do_it(headers):
        res = flask_client.get('/logout', headers=headers)
        return res
    return do_it


@pytest.fixture
def find_ticket(flask_client):
    def do_it(ticket_id, headers=None):
        res = flask_client.get(
            '/get_ticket?ticket_id={}'.format(ticket_id),
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture
def tickets(flask_client):
    def do_it(params=None, headers=None):
        res = flask_client.get(
            '/tickets',
            query_string=params,
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture
def download(flask_client):
    def do_it(params=None, headers=None):
        res = flask_client.post(
            '/download',
            json=params,
            headers=headers,
        )
        return res
    return do_it


@pytest.fixture(scope='session')
def find_pd_fields():
    return ['phone', 'driver_license']


@pytest.fixture
def find_documents_in_scouts_agents():
    def do_it(db_mongo):
        return list(
            db_mongo.scouts_agents_surveys.find()
        )
    return do_it


@pytest.fixture
def log_user_role(log_user_in, load_json):
    def func(login):
        user = load_json('login_dicts.json')[login]
        res = log_user_in(user)
        assert res.status_code == 200
    return func


@pytest.fixture
def generate_passport_headers():
    return {
        SERVICE_TICKET_HEADER: 'SERVICE_TICKET',
        YANDEX_LOGIN_HEADER: 'yandex_user'
    }
