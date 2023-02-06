import pytest


@pytest.mark.parametrize(
    'quantity_picked, quantity_requested, test_id',
    [
        (4, 5, 'quantity_picked_is_less'),
        (5, 4, 'quantity_picked_is_greater'),
        (4.5, 5.5, 'non_integer_quantity'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_autodisable_items(
        pg_cursor,
        testpoint,
        stq_runner,
        # parametrize params
        quantity_requested,
        quantity_picked,
        test_id,
):
    @testpoint('not-picked-items_requested-not-more-than-picked')
    def quantity_picked_is_not_less(data):
        pass

    await _put_task_into_stq(
        stq_runner,
        [
            {
                'place_id': '1',
                'not_picked_items': [
                    {
                        'eats_item_id': 'item_origin_1',
                        'quantity': quantity_requested,
                        'quantity_picked': quantity_picked,
                    },
                    {
                        'eats_item_id': 'item_origin_3',
                        'quantity': quantity_requested,
                        'quantity_picked': quantity_picked,
                    },
                ],
            },
            {
                'place_id': '1',
                'not_picked_items': [
                    {
                        'eats_item_id': 'item_origin_2',
                        'quantity': quantity_requested,
                        'quantity_picked': quantity_picked,
                    },
                ],
            },
        ],
    )

    data_from_db = _sql_get_not_picked_items(pg_cursor)
    if test_id in ('quantity_picked_is_less', 'non_integer_quantity'):
        expected_data = [
            {
                'id': 1,
                'place_id': 1,
                'product_id': 401,
                'origin_id': 'item_origin_1',
                'quantity': quantity_requested,
                'quantity_picked': quantity_picked,
            },
            {
                'id': 2,
                'place_id': 1,
                'product_id': 403,
                'origin_id': 'item_origin_3',
                'quantity': quantity_requested,
                'quantity_picked': quantity_picked,
            },
            {
                'id': 3,
                'place_id': 1,
                'product_id': 402,
                'origin_id': 'item_origin_2',
                'quantity': quantity_requested,
                'quantity_picked': quantity_picked,
            },
        ]
        expected_data = sorted(expected_data, key=lambda k: k['product_id'])
        data_from_db = sorted(data_from_db, key=lambda k: k['product_id'])

        assert expected_data == data_from_db
    elif test_id == 'quantity_picked_is_greater':
        assert quantity_picked_is_not_less.has_calls is True
        assert [] == data_from_db


@pytest.mark.parametrize(
    'should_map_origin_to_product_by_brand, expected_product_id',
    [
        pytest.param(True, 409, id='correct_product_id'),
        pytest.param(False, 408, id='wrong_product_id'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_product_with_wrong_brand.sql',
    ],
)
async def test_autodisable_item_with_correct_brand(
        pg_cursor,
        stq_runner,
        taxi_config,
        # parametrize params
        should_map_origin_to_product_by_brand,
        expected_product_id,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_map_origin_to_product_by_brand': (
                    should_map_origin_to_product_by_brand
                ),
            },
        },
    )

    quantity_requested = 10
    quantity_picked = 5
    await _put_task_into_stq(
        stq_runner,
        [
            {
                'place_id': '2',
                'not_picked_items': [
                    {
                        'eats_item_id': 'item_origin_8',
                        'quantity': quantity_requested,
                        'quantity_picked': quantity_picked,
                    },
                ],
            },
        ],
    )
    assert _sql_get_not_picked_items(pg_cursor) == [
        {
            'id': 1,
            'place_id': 2,
            'product_id': expected_product_id,
            'origin_id': 'item_origin_8',
            'quantity': quantity_requested,
            'quantity_picked': quantity_picked,
        },
    ]


async def _put_task_into_stq(
        stq_runner, data_for_stq, task_id='1', expect_fail=False,
):
    for data_piece in data_for_stq:
        await stq_runner.eats_picker_not_picked_items.call(
            task_id=task_id,
            args=[],
            kwargs=data_piece,
            expect_fail=expect_fail,
        )


def _sql_get_not_picked_items(pg_cursor):
    pg_cursor.execute(
        """
        select
            npi.id,
            npi.place_id,
            npi.product_id,
            npi.origin_id,
            npi.quantity_requested,
            npi.quantity_picked
        from eats_nomenclature.not_picked_items npi
        """,
    )
    return [
        {
            'id': i[0],
            'place_id': i[1],
            'product_id': i[2],
            'origin_id': i[3],
            'quantity': i[4],
            'quantity_picked': i[5],
        }
        for i in pg_cursor
    ]
