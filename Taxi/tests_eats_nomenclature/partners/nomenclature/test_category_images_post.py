import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_category_images_post(taxi_eats_nomenclature, pgsql):

    place_id = 1
    category_origin_id = 'category_1_origin'
    urls = ['url_1', 'url_2']

    ids, old_pictures = sql_get_pictures(pgsql, urls)
    assert len(ids) == len(urls)
    sql_ids = sql_get_category_picture_ids(pgsql, category_origin_id)
    assert ids.issubset(sql_ids)

    pictures_to_upload = [
        {'url': urls[0], 'hash': None},
        {'url': 'url_NEW', 'hash': 'New hash: NEW'},
    ]

    request = {'images': pictures_to_upload}

    response = await taxi_eats_nomenclature.post(
        '/v1/partners/category/images?'
        f'place_id={place_id}&category_origin_id={category_origin_id}',
        request,
    )
    assert response.status == 204

    ids, pictures = sql_get_pictures(pgsql, urls + ['url_NEW'])
    assert len(ids) == len(pictures)
    # Nothing should be changed.
    assert list_of_dicts_to_set_of_tuples(
        pictures,
    ) == list_of_dicts_to_set_of_tuples(old_pictures)

    sql_ids = sql_get_category_picture_ids(pgsql, f'{category_origin_id}')
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


def sql_get_category_picture_ids(pgsql, category_origin_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cp.picture_id
        from eats_nomenclature.category_pictures cp
          join eats_nomenclature.categories c
            on cp.category_id = c.id
        where c.origin_id = '{category_origin_id}'
        """,
    )
    return {i[0] for i in set(cursor)}


def list_of_dicts_to_set_of_tuples(list_of_dicts):
    return {tuple(sorted(d.items())) for d in list_of_dicts}
