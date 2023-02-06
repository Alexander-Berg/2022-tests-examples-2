HANDLER = '/v1/manage/brand/assortment/delete'
BRAND_ID = 1
ASSORTMENT = 'new_assortment'


async def test_404_not_found(taxi_eats_nomenclature, pgsql):
    sql_insert_assortment_traits(pgsql)
    unknown_assortment = 'unknown_assortment'
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}'
        f'&assortment_name={unknown_assortment}',
    )
    assert response.status_code == 404
    assert len(sql_get_all_assortment_traits(pgsql)) == 1


async def test_204_ok(taxi_eats_nomenclature, pgsql):
    sql_insert_assortment_traits(pgsql)
    sql_insert_assortment_traits(
        pgsql, brand_id=2, assortment_name='some_assortment',
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' f'&assortment_name={ASSORTMENT}',
    )
    assert response.status_code == 204
    assert len(sql_get_all_assortment_traits(pgsql)) == 1


async def test_409_place_assortment_in_use(taxi_eats_nomenclature, pgsql):

    trait_id = sql_insert_assortment_traits(pgsql)
    sql_add_default_assortment(pgsql, 1, trait_id)

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' f'&assortment_name={ASSORTMENT}',
    )
    assert response.status_code == 409
    assert len(sql_get_all_assortment_traits(pgsql)) == 1


async def test_409_brand_assortment_in_use(taxi_eats_nomenclature, pgsql):

    trait_id = sql_insert_assortment_traits(pgsql)
    sql_add_brand_assortment(pgsql, BRAND_ID, trait_id)

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' f'&assortment_name={ASSORTMENT}',
    )
    assert response.status_code == 409
    assert len(sql_get_all_assortment_traits(pgsql)) == 1


def sql_add_default_assortment(pgsql, place_id, trait_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            insert into eats_nomenclature.places (id, slug)
            values ({place_id}, 'slug')""",
    )
    cursor.execute(
        f"""
            insert into eats_nomenclature.place_default_assortments
            (place_id, trait_id)
            values ({place_id}, {trait_id})""",
    )


def sql_add_brand_assortment(pgsql, brand_id, trait_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            insert into eats_nomenclature.brand_default_assortments
            (brand_id, trait_id)
            values ({brand_id}, {trait_id})""",
    )


def sql_insert_assortment_traits(
        pgsql, brand_id=BRAND_ID, assortment_name=ASSORTMENT,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands (id)
        values ({brand_id})""",
    )

    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_traits
        (brand_id, assortment_name)
        values ({brand_id}, '{assortment_name}')
        returning id""",
    )
    return cursor.fetchone()[0]


def sql_get_all_assortment_traits(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()

    cursor.execute(
        f"""
        select brand_id, assortment_name
        from eats_nomenclature.assortment_traits""",
    )
    return list(cursor)
