async def test_get_nomenclature_bad_place_slug(taxi_eats_nomenclature):

    response = await taxi_eats_nomenclature.get('/v1/nomenclature?slug=slug')

    assert response.status == 404
