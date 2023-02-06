from connection.postgresql import _make_safe_params, _hide_pass


def test_dsn_password_hider():
    assert (
        _hide_pass('host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=TheSecret sslmode=require')
        ==
        'host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=********* sslmode=require'
    )
    assert (
            _hide_pass('host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=TheSecret')
            ==
            'host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=*********'
    )


def test_password_hider():
    # Проверим утилитку, которая скрывает пароль в
    # параметрах для соединения с базой.
    # Пароль может быть как в отдельном ключе password,
    # так и в DSN строке:
    params = {
        'database': 'some-test-db',
        'password': 'the secret',
        'dsn': 'host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=TheSecret sslmode=require'

    }
    safe_params = _make_safe_params(params)
    assert safe_params['password'] == '**********'
    assert safe_params['dsn'] == 'host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=********* sslmode=require'

    # при этом оригинальный словарь функция менять не должна:
    assert params['password'] == 'the secret'
    assert params['dsn'] == 'host=db.yandex.net port=6432 dbname=taxi_dwh user=taxi password=TheSecret sslmode=require'
