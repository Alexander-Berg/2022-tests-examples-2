import pytest


async def test_update_last_tariff_no_user(taxi_user_api):
    response = await taxi_user_api.post(
        'users/update-last-tariff-info',
        json={'user_id': 'user-not-found', 'category_name': 'econom'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_user_id',
    [
        'user-without-last-tariff',
        'user-with-last-tariff-full',
        'user-with-last-tariff-category',
    ],
)
@pytest.mark.parametrize(
    'request_service, request_category', [(50, 'econom'), (None, 'econom')],
)
@pytest.mark.now('2020-12-01T12:00:00+00:00')
async def test_update_last_tariff(
        taxi_user_api,
        mongodb,
        request_user_id,
        request_service,
        request_category,
):
    old_doc = mongodb.users.find_one({'_id': request_user_id})

    request_json = {
        'user_id': request_user_id,
        'category_name': request_category,
    }
    if request_service is not None:
        request_json['service_level'] = request_service

    response = await taxi_user_api.post(
        'users/update-last-tariff-info', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == {}

    new_doc = mongodb.users.find_one({'_id': request_user_id})
    assert new_doc['last_tariff_imprint']['service_level'] == request_service
    assert new_doc['last_tariff_imprint']['category_name'] == request_category
    assert new_doc['updated'] > old_doc['updated']
