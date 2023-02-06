async def test_204(taxi_eats_nomenclature):

    response = await taxi_eats_nomenclature.post(
        '/v1/partners/nomenclature?brand_id=777'
        '&place_ids=123&place_slug=lavka_krasina',
        json={'categories': [], 'items': []},
    )

    assert response.status == 204
