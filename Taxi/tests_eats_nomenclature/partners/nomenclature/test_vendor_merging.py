import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_vendor_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_vendors(pgsql) == [
        ('vendor_1', 'country_1'),
        ('vendor_2', 'country_2'),
        ('vendor_3', 'country_3'),
    ]

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_vendors(pgsql) == [
        ('vendor_1', 'country_1'),
        ('vendor_2', 'country_2'),
        ('vendor_3', 'country_3'),
        ('vendor_4', 'country_4'),
    ]


def get_vendors(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """SELECT name, country
        FROM eats_nomenclature.vendors
        ORDER BY name, country""",
    )
    return list(cursor)
