from tests_grocery_crm import headers
from tests_grocery_crm import models


async def test_basic(taxi_grocery_crm, pgsql):
    informer_ids = ['test_id_0', 'test_id_1', 'test_id_2']
    informers = [
        models.Informer(
            pgsql,
            informer_id=informer_ids[0],
            show_in_root=True,
            category_ids=['cat-1', 'cat-2'],
            category_group_ids=['cat-gr-1', 'cat-gr-1'],
            product_ids=['pr-1', 'pr-2'],
            hide_if_product_is_missing=['pr-3', 'pr-4'],
        ),
        models.Informer(
            pgsql, informer_id=informer_ids[1], show_in_root=False,
        ),
        models.Informer(pgsql, informer_id=informer_ids[2]),
    ]
    models.UserInformer(
        pgsql=pgsql,
        informer_id=informer_ids[0],
        yandex_uid=headers.YANDEX_UID,
        shown_count=1,
    )
    models.UserInformer(
        pgsql=pgsql,
        informer_id=informer_ids[1],
        yandex_uid=headers.YANDEX_UID,
        shown_count=1,
    )
    models.UserInformer(
        pgsql=pgsql,
        informer_id=informer_ids[2],
        yandex_uid=headers.YANDEX_UID,
        shown_count=1,
    )

    await taxi_grocery_crm.invalidate_caches(
        clean_update=False, cache_names=['informers-pg-cache'],
    )

    request_json = {'yandex_uid': headers.YANDEX_UID}
    response = await taxi_grocery_crm.post(
        '/internal/user/v1/get-catalog-informers', json=request_json,
    )
    assert response.status_code == 200
    assert response.json()['informers'] == [
        informers[1].json(),
        informers[0].json(),
    ]
