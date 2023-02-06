import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_images_post(taxi_eats_nomenclature, pgsql):

    place_id = 1
    product_origin_id = 'item_origin_1'
    urls = ['url_1']

    ids, old_pictures = sql_get_pictures(pgsql, urls)
    assert len(ids) == len(urls)
    sql_ids = sql_get_product_picture_ids(pgsql, place_id, product_origin_id)
    assert ids.issubset(sql_ids)

    pictures_to_upload = [
        {'url': urls[0], 'hash': None},
        {'url': 'url_NEW', 'hash': 'New hash: NEW'},
    ]

    request = {'images': pictures_to_upload}

    response = await taxi_eats_nomenclature.post(
        '/v1/partners/item/images?'
        f'place_id={place_id}&item_origin_id={product_origin_id}',
        request,
    )
    assert response.status == 204

    ids, pictures = sql_get_pictures(pgsql, urls + ['url_NEW'])
    assert len(ids) == len(pictures)
    # Nothing should be changed.
    assert list_of_dicts_to_set_of_tuples(
        pictures,
    ) == list_of_dicts_to_set_of_tuples(old_pictures)

    sql_ids = sql_get_product_picture_ids(pgsql, place_id, product_origin_id)
    assert ids.issubset(sql_ids)


def sql_get_pictures(pgsql, urls):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id, url, processed_url, hash
        from eats_nomenclature.pictures
          join unnest(array{list(urls)}) as src_url on src_url = url
        """,
    )
    data = set(cursor)
    return (
        {i[0] for i in data},
        [{'url': i[1], 'processed_url': i[2], 'hash': i[3]} for i in data],
    )


def sql_get_product_picture_ids(pgsql, place_id, product_origin_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select ppic.picture_id
        from eats_nomenclature.product_pictures ppic
          join eats_nomenclature.products p
            on ppic.product_id = p.id
          join eats_nomenclature.places_products pp
            on pp.product_id = p.id
        where pp.place_id = '{place_id}'
            and p.origin_id = '{product_origin_id}'
        """,
    )
    return {i[0] for i in set(cursor)}


def list_of_dicts_to_set_of_tuples(list_of_dicts):
    return {tuple(sorted(d.items())) for d in list_of_dicts}
