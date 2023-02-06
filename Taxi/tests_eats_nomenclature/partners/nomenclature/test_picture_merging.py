import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_brand_processing_picture_merging(pgsql, brand_task_enqueue):
    # check current data
    assert get_pictures(pgsql) == {
        (1, 'url_1', 'processed_url_1', True),
        (2, 'url_2', None, True),
        (3, 'url_3', 'processed_url_3', False),
        (4, 'url_4', 'processed_url_4', False),
        (5, 'url_5', 'processed_url_5', True),
    }

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    assert get_pictures(pgsql) == {
        (1, 'url_1', 'processed_url_1', True),
        (
            2,
            'url_2',
            None,
            True,
        ),  # processed url is not updated for existing pictures
        (3, 'url_3', 'processed_url_3', False),
        (4, 'url_4', 'processed_url_4', False),
        (5, 'url_5', 'processed_url_5', True),
        # set new pictures as not processed and as needing a subscription
        (6, 'url_6', None, True),
    }


def get_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select id, url, processed_url, needs_subscription
        from eats_nomenclature.pictures
        """,
    )
    return set(cursor)
