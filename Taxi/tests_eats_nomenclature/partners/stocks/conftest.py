import pytest


@pytest.fixture
def sql_get_stocks(pgsql):
    def impl(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
        select pp.origin_id, s.value, p.brand_id
        from eats_nomenclature.places_products pp
          join eats_nomenclature.stocks s
            on s.place_product_id = pp.id
            join eats_nomenclature.products p
              on pp.product_id = p.id
        where pp.place_id = {place_id}
        """,
        )
        return sorted(list(cursor), key=lambda row: (row[0], row[2]))

    return impl


@pytest.fixture
def sql_save_availability_file(pgsql):
    async def impl(place_id, file_path, file_datetime):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
        insert into eats_nomenclature.availability_files(
          place_id,
          file_path,
          file_datetime
        )
        values (
          {place_id},
          '{file_path}',
          '{file_datetime}'
        )
        on conflict(place_id)
        do nothing
        """,
        )

    return impl
