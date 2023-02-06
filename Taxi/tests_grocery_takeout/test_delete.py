import pytest


@pytest.fixture(name='grocery_cart')
def _mock_grocery_cart(mockserver):
    class Context:
        def __init__(self):
            self.deleted_users = set()

        def check_deleted(self, yandex_uid):
            return yandex_uid in self.deleted_users

        def delete_times_called(self):
            return _mock_cart_delete.times_called

        def mark_deleted(self, yandex_uid):
            self.deleted_users.add(yandex_uid)

    context = Context()

    @mockserver.json_handler('/grocery-cart/internal/v1/takeout/delete')
    def _mock_cart_delete(request):
        context.mark_deleted(request.json['yandex_uid'])

    return context


async def do_delete(taxi_grocery_takeout, uids):
    json = {
        'request_id': 'request_id',
        'yandex_uids': [{'uid': x, 'is_portal': True} for x in uids],
    }

    return await taxi_grocery_takeout.post('/v1/takeout/delete', json=json)


async def test_delete_inserts_into_db(taxi_grocery_takeout, grocery_cart):
    yandex_uid = 'uid'
    bound_uid = 'bound_uid'
    third_uid = 'some_other_uid'

    response = await do_delete(taxi_grocery_takeout, [yandex_uid, bound_uid])
    assert response.status_code == 200

    response = await do_delete(taxi_grocery_takeout, [bound_uid, third_uid])
    assert response.status_code == 200

    await taxi_grocery_takeout.invalidate_caches()
    response = await taxi_grocery_takeout.post(
        '/internal/v1/erased-users/list', json={},
    )
    assert response.status_code == 200

    uids = response.json()['uids']
    for uid in [yandex_uid, bound_uid, third_uid]:
        assert uid in uids


async def test_status(taxi_grocery_takeout, grocery_cart):
    yandex_uid = 'yandex_uid'
    bound_uid = 'bound_uid'

    response = await do_delete(taxi_grocery_takeout, [yandex_uid, bound_uid])
    assert response.status_code == 200

    await taxi_grocery_takeout.invalidate_caches()

    response = await taxi_grocery_takeout.post(
        '/v1/takeout/status',
        json={'yandex_uids': [{'uid': bound_uid, 'is_portal': True}]},
    )
    assert response.status_code == 200

    assert response.json() == {'data_state': 'empty'}


@pytest.mark.parametrize('marketing_has_data', [True, False])
async def test_status_data_from_marketing(
        taxi_grocery_takeout, mockserver, marketing_has_data,
):
    yandex_uid = 'yandex_uid'

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _mock_marketing(request):
        return {'usage_count': 1 if marketing_has_data else 0}

    response = await taxi_grocery_takeout.post(
        '/v1/takeout/status',
        json={'yandex_uids': [{'uid': yandex_uid, 'is_portal': True}]},
    )
    assert response.status_code == 200

    expected_status = 'ready_to_delete' if marketing_has_data else 'empty'
    assert response.json() == {'data_state': expected_status}


async def test_delete_calls_cart(taxi_grocery_takeout, grocery_cart):
    yandex_uid = 'yandex_uid'
    bound_uid = 'bound_uid'

    response = await do_delete(taxi_grocery_takeout, [yandex_uid, bound_uid])
    assert response.status_code == 200

    assert grocery_cart.delete_times_called() == 2
    for uid in [yandex_uid, bound_uid]:
        assert grocery_cart.check_deleted(uid)
