import pytest

TASK_PATH = 'brand-fusion'


def make_catalog_storage_obj(place_id, brand_id):
    return {
        'id': place_id,
        'revision_id': place_id,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'brand': {
            'id': brand_id,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
    }


CATALOG_STORAGE_DATA_DEFAULT = [
    make_catalog_storage_obj(1, 1),
    make_catalog_storage_obj(3, 3),
    make_catalog_storage_obj(4, 4),
    make_catalog_storage_obj(5, 5),
]


def create_result_table_line(place_id, old_brand, new_brand, dry_run=True):
    return (str(place_id), str(old_brand), str(new_brand), dry_run)


@pytest.mark.config(EATS_BRAND_FUSION_START_PERIODIC_BRAND_FUSION=True)
@pytest.mark.parametrize(
    'result_table, size_after_filter',
    [
        pytest.param(
            [
                create_result_table_line(1, 1, 2),
                create_result_table_line(3, 3, 4),
                create_result_table_line(5, 5, 6),
            ],
            3,
            marks=pytest.mark.eats_catalog_storage_cache(
                CATALOG_STORAGE_DATA_DEFAULT
                + [
                    make_catalog_storage_obj(2, 2),
                    make_catalog_storage_obj(6, 6),
                ],
            ),
        ),
        pytest.param(
            [
                create_result_table_line(1, 1, 2),
                create_result_table_line(3, 3, 4),
            ],
            2,
            marks=pytest.mark.eats_catalog_storage_cache(
                CATALOG_STORAGE_DATA_DEFAULT
                + [make_catalog_storage_obj(2, 2)],
            ),
        ),
        pytest.param(
            [
                create_result_table_line(3, 3, 4),
                create_result_table_line(5, 5, 6),
            ],
            3,
            marks=pytest.mark.eats_catalog_storage_cache(
                CATALOG_STORAGE_DATA_DEFAULT
                + [
                    make_catalog_storage_obj(2, 1),
                    make_catalog_storage_obj(6, 6),
                ],
            ),
        ),
        pytest.param(
            [
                create_result_table_line(1, 1, 2),
                create_result_table_line(3, 3, 4),
                create_result_table_line(5, 5, 6),
            ],
            4,
            marks=pytest.mark.eats_catalog_storage_cache(
                CATALOG_STORAGE_DATA_DEFAULT
                + [
                    make_catalog_storage_obj(2, 2),
                    make_catalog_storage_obj(6, 6),
                    make_catalog_storage_obj(11, 2),
                ],
            ),
        ),
    ],
)
@pytest.mark.yt(
    static_table_data=['yt_related_restaurants_data_big_table.yaml'],
)
@pytest.mark.usefixtures('yt_apply')
async def test_db(
        pgsql,
        testpoint,
        taxi_eats_brand_fusion,
        yt_apply_force,
        yt_apply,
        yt_client,
        eats_catalog_storage_cache,
        result_table,
        size_after_filter,
):
    @testpoint('before-filter-related-restaurants')
    def before_filter(data):
        pass

    @testpoint('after-filter-related-restaurants')
    def after_filter(data):
        pass

    await taxi_eats_brand_fusion.run_task(TASK_PATH)

    assert before_filter.next_call()['data'] == {'size_before_filter': 7}
    assert after_filter.next_call()['data'] == {
        'size_after_filter': size_after_filter,
    }

    cursor = pgsql['eats_brand_fusion'].cursor()
    cursor.execute(
        """
    SELECT place_id, previous_brand, new_brand, dry_run
    FROM eats_brand_fusion.place_id_transfer_history
    ORDER BY place_id
    """,
    )

    assert list(cursor) == result_table
