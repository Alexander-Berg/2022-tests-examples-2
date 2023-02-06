import pytest

ROUTE = '/users/history'


@pytest.fixture
def user_history(taxiparks_client):
    def do_it(login):
        params = dict(login=login)
        response = taxiparks_client.get(
            ROUTE,
            query_string=params,
        )
        return response
    return do_it


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'login',
    [
        'root'
    ]
)
def test_user_history_dummy(user_history, login):
    response = user_history(login)
    assert response.status_code == 200
    assert len(response.json) == 0


@pytest.mark.usefixtures('log_in')
def test_user_create_edit_history(
        users_create,
        user_edit,
        user_get,
        user_history,
        load_json
):
    create_data = load_json('create_user_template.json')
    edit_data = load_json('edit_user_template.json')

    login = create_data['login']

    response = users_create(create_data)
    assert response.status_code == 200
    history_len = 1
    assert len(user_history(login).json) == history_len

    for i in range(10):
        edit_data['user_name'] = f'Макиавелли Никколо {i+1}'
        history_len += 1
        response = user_edit(edit_data)
        assert response.status_code == 200
        assert len(user_history(login).json) == history_len

    response = user_edit(edit_data)
    assert response.status_code == 208
    assert response.json['code'] == 'NO_RESULT_GENERATED'
    assert len(user_history(login).json) == history_len

    response = user_get(login)
    assert response.status_code == 200
    assert response.json['user_name'] == edit_data['user_name']
