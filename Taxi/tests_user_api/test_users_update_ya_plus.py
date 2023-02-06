import pytest


@pytest.mark.parametrize(
    'request_user_id', ['user-with-ya-plus', 'user-without-ya-plus'],
)
@pytest.mark.parametrize('request_ya_plus', [True, False, None])
@pytest.mark.parametrize('request_cashback_plus', [True, False, None])
async def test_update_ya_plus(
        taxi_user_api,
        mongodb,
        request_user_id,
        request_ya_plus,
        request_cashback_plus,
):
    old_doc = mongodb.users.find_one({'_id': request_user_id})
    request_json = {'user_id': request_user_id}

    if request_ya_plus is not None:
        request_json['has_ya_plus'] = request_ya_plus
        expected_ya_plus = request_ya_plus
    else:
        expected_ya_plus = old_doc.get('has_ya_plus', False)

    if request_cashback_plus is not None:
        request_json['has_cashback_plus'] = request_cashback_plus
        expected_cashback_plus = request_cashback_plus
    else:
        expected_cashback_plus = old_doc.get('has_cashback_plus', False)

    response = await taxi_user_api.post(
        'users/update-ya-plus', json=request_json,
    )
    assert response.status_code == 200

    new_doc = mongodb.users.find_one({'_id': request_user_id})
    assert new_doc.get('has_ya_plus', False) == expected_ya_plus
    assert new_doc.get('has_cashback_plus', False) == expected_cashback_plus
