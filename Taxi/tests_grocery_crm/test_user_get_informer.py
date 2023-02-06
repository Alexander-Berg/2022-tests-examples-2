from tests_grocery_crm import models


async def test_get_user_informer(taxi_grocery_crm, pgsql):
    informer_id = 'test_id'
    informer = models.Informer(pgsql, informer_id=informer_id)

    await taxi_grocery_crm.invalidate_caches(
        clean_update=False, cache_names=['informers-pg-cache'],
    )

    request_json = {'informer_id': informer_id}
    response = await taxi_grocery_crm.post(
        '/internal/user/v1/get-informer', json=request_json,
    )
    assert response.status_code == 200
    assert response.json()['informer'] == informer.json()


async def test_404(taxi_grocery_crm):
    request_json = {'informer_id': 'test_id'}
    response = await taxi_grocery_crm.post(
        '/internal/user/v1/get-informer', json=request_json,
    )
    assert response.status_code == 404
    assert 'informer' not in response.json()
