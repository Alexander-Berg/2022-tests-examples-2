async def test_get_nomenclature_no_assortment(taxi_eats_nomenclature, pgsql):

    set_sql_place_info(pgsql)

    response = await taxi_eats_nomenclature.get('/v1/nomenclature?slug=slug')

    assert response.status == 200
    assert response.json() == {'categories': []}


def set_sql_place_info(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands (id) values (1);
        insert into eats_nomenclature.places (id, slug) values (1, 'slug');
        insert into eats_nomenclature.brand_places (brand_id, place_id)
        values (1, 1);
        """,
    )
