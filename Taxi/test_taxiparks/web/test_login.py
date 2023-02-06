import datetime

import freezegun


def test_login_deactivated(
        taxiparks_client, log_user_in, mongodb):
    data = {
        'login': 'deactivated_root',
        'password': 'root_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 409


def test_login_non_existent(taxiparks_client, log_user_in, mongodb):
    data = {
        'login': 'root_non_existent',
        'password': 'root_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 400


def test_login_invalid_pass(
        taxiparks_client, log_user_in, mongodb):
    data = {
        'login': 'root',
        'password': 'invalid_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 400


def test_login_invalid_csrf(
        taxiparks_client, log_user_in):
    data = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': 'ijijij'
    }
    res = log_user_in(data)
    assert res.status_code == 403


def test_login_valid(
        taxiparks_client, log_user_in,
        log_user_out):
    data = {
        'login': 'root',
        'password': 'root_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 200

    headers = res.headers
    res = log_user_out(headers)
    assert res.status_code == 200


def test_login_rate_limit_sets(
        taxiparks_client, log_user_in, log_user_out,
):
    invalid_login = {
        'login': 'root',
        'password': 'invalid_pass'
    }
    valid_login = {
        'login': 'root',
        'password': 'root_pass'
    }
    res = log_user_in(valid_login)
    assert res.status_code == 200
    log_user_out(res.headers)

    for i in range(5):
        res = log_user_in(invalid_login)
        assert res.status_code == 400

    datetimes = [
        datetime.datetime.utcnow() + datetime.timedelta(minutes=1 * i)
        for i in range(5)
    ]
    for dt in datetimes:
        with freezegun.freeze_time(dt):
            res = log_user_in(valid_login)
            assert res.status_code == 400


@freezegun.freeze_time('2018-5-4T17:55:00')
def test_login_rate_limit_unsets(
        taxiparks_client, log_user_in,
):
    valid_login = {
        'login': 'root',
        'password': 'root_pass'
    }
    res = log_user_in(valid_login)
    assert res.status_code == 200
