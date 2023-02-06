HANDLER = '/v1/manage/tags/create'
NAME = 'category_tag'


async def test_create_tag(taxi_eats_nomenclature, pgsql):

    response = await taxi_eats_nomenclature.post(HANDLER + f'?name={NAME}')

    assert response.status_code == 201

    db_tags = sql_get_tags(pgsql)
    assert len(db_tags) == 1
    assert db_tags[0][0] == NAME

    response_repeat = await taxi_eats_nomenclature.post(
        HANDLER + f'?name={NAME}',
    )
    assert response_repeat.status_code == 409


def sql_get_tags(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select name
        from eats_nomenclature.tags
        """,
    )
    return cursor.fetchall()
