import eats_adverts_goods  # pylint: disable=import-error
import pytest

from tests_eats_upsell import eats_catalog_storage
from tests_eats_upsell import experiments
from . import types


async def test_endpoint_liveness(
        retail_recommendations,
        eats_catalog_storage_service,
        umlaas_eats_retail_suggest,
):
    """
    Проверяет, что ендпоинт вообще жив и отвечает 200.
    """

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=1, place=eats_catalog_storage.Place(slug=place_slug),
    )

    eats_catalog_storage_service.add_place(place)

    item = types.RequestItem(public_id='1')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_eats_retail_suggest.times_called == 1

    response_body: dict = response.json()
    assert not response_body['recommendations']


async def test_endpoint_ok(
        retail_recommendations,
        eats_catalog_storage_service,
        umlaas_eats_retail_suggest,
):
    """
    Проверяет, что ендпоинт возвращает рекомендации
    """

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )

    recommendations: list = ['2', '3', '4']

    eats_catalog_storage_service.add_place(place)
    umlaas_eats_retail_suggest.set_recommendations(recommendations)

    item = types.RequestItem(public_id='1')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_eats_retail_suggest.times_called == 1

    response_body: dict = response.json()
    actual_recommendations: list = response_body['recommendations']
    assert len(recommendations) == len(actual_recommendations)
    for expected, actual in zip(recommendations, actual_recommendations):
        assert expected == actual['public_id']


@experiments.disable_adverts()
@experiments.create_promotion('testsuite')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion='testsuite',
            products=[
                eats_adverts_goods.types.Product(product_id='6', core_id=6),
                eats_adverts_goods.types.Product(product_id='7', core_id=7),
            ],
        ),
    ],
)
async def test_upsell_advertisement_disabled_v1_recommendations(
        retail_recommendations,
        eats_catalog_storage_service,
        umlaas_eats_retail_suggest,
):
    umlaas_recommendations = ['1', '2', '3']
    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_status_code(200)
    umlaas_eats_retail_suggest.set_recommendations(umlaas_recommendations)

    item = types.RequestItem(public_id='42')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )

    assert response.status_code == 200

    expected_ids = umlaas_recommendations

    response_data = response.json()
    assert len(response_data['recommendations']) == len(expected_ids)

    for item, expected in zip(response_data['recommendations'], expected_ids):
        assert item['public_id'] in expected
