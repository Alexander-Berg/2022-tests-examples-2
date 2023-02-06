import datetime as dt

import pytest
import pytz


MOCK_NOW = dt.datetime(2021, 8, 13, 12, tzinfo=pytz.UTC)
BRAND_ID = 777
S3_AVAILABILITY_PATH = 'availability/availability_1.json'
S3_PRICES_PATH = 'prices/prices_1.json'
S3_STOCKS_PATH = 'stocks/stocks_1.json'
TEST_DATETIME = '2021-03-01T10:45:00+03:00'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_activation(
        activate_assortment,
        get_sql_assortments_status,
        get_in_progress_assortment,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        brand_task_enqueue,
        update_taxi_config,
        pgsql,
        stq,
):
    delay = 999
    update_taxi_config(
        'EATS_NOMENCLATURE_ASSORTMENT_ACTIVATION_NOTIFICATION_SETTINGS',
        {
            'common_delay_in_seconds': delay,
            'is_enabled': True,
            'per_component_additional_settings': {
                '__default__': {
                    'is_enabled': True,
                    'additional_delay_in_seconds': 0,
                },
            },
        },
    )

    place_id = 1
    place_assortments = get_sql_assortments_status(place_id)
    previous_active_assortment_id = place_assortments['assortment_id']
    assert previous_active_assortment_id
    assert place_assortments['in_progress_assortment_id']

    prev_ass_last_referenced_at_1 = _get_assortment_last_referenced_at(
        pgsql, previous_active_assortment_id,
    )

    await brand_task_enqueue()

    in_progress_assortment_id = get_in_progress_assortment(place_id)
    assert (
        in_progress_assortment_id
        != place_assortments['in_progress_assortment_id']
    )

    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    new_place_assortments = get_sql_assortments_status(place_id)
    assert new_place_assortments['assortment_id'] == in_progress_assortment_id
    assert not new_place_assortments['in_progress_assortment_id']

    prev_ass_last_referenced_at_2 = _get_assortment_last_referenced_at(
        pgsql, previous_active_assortment_id,
    )
    assert prev_ass_last_referenced_at_2 > prev_ass_last_referenced_at_1

    last_status = {
        'assortment_id': in_progress_assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert sql_get_place_assortment_last_status_history(place_id) == [
        last_status,
    ]

    assert (
        stq.eats_nomenclature_assortment_activation_notifier.times_called == 1
    )

    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    assert task_info['kwargs']['place_ids'] == [place_id]
    now = dt.datetime.fromisoformat(MOCK_NOW.isoformat()).replace(tzinfo=None)
    assert (task_info['eta'] - now).total_seconds() == delay


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_second_place_data.sql',
    ],
)
async def test_assortment_activation_many_places(
        get_sql_assortments_status,
        get_in_progress_assortment,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        brand_task_enqueue,
        stq,
        pgsql,
        stq_call_forward,
        put_availability_data_to_s3,
        availability_enqueue,
        put_prices_data_to_s3,
        prices_enqueue,
        put_stock_data_to_s3,
        stocks_enqueue,
        sql_are_availabilities_ready,
        sql_are_custom_categories_ready,
        sql_are_prices_ready,
        sql_are_stocks_ready,
):
    place_id_1 = 1
    place_id_2 = 2
    place_ids = [place_id_1, place_id_2]
    place_assortments = get_sql_assortments_status(place_id_1)
    previous_active_assortment_id = place_assortments['assortment_id']
    assert previous_active_assortment_id
    assert place_assortments['in_progress_assortment_id']
    place_assortments_2 = get_sql_assortments_status(place_id_2)
    previous_active_assortment_id_2 = place_assortments_2['assortment_id']
    assert previous_active_assortment_id_2 == previous_active_assortment_id

    assert (
        place_assortments_2['in_progress_assortment_id']
        == place_assortments['in_progress_assortment_id']
    )

    prev_ass_last_referenced_at_1 = _get_assortment_last_referenced_at(
        pgsql, previous_active_assortment_id,
    )

    await brand_task_enqueue(place_ids=[str(place_id_1), str(place_id_2)])

    in_progress_assortment_id = get_in_progress_assortment(place_id_1)
    assert (
        in_progress_assortment_id
        != place_assortments['in_progress_assortment_id']
    )
    assert get_in_progress_assortment(place_id_2) == in_progress_assortment_id

    async def enrich_place(place_id):
        new_availabilities = [
            {'origin_id': 'item_origin_4', 'available': True},
            {'origin_id': 'item_origin_5', 'available': True},
            {'origin_id': 'item_origin_6', 'available': True},
        ]
        await put_availability_data_to_s3(
            new_availabilities, S3_AVAILABILITY_PATH, str(place_id),
        )
        await availability_enqueue(
            place_id, S3_AVAILABILITY_PATH, TEST_DATETIME,
        )

        new_prices = [
            {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
            {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
            {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
        ]
        await put_prices_data_to_s3(new_prices, S3_PRICES_PATH, str(place_id))
        await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME)

        new_stocks = [
            {
                'origin_id': item['origin_id'],
                'stocks': '500' if item['available'] else '0',
            }
            for item in new_availabilities
        ]
        await put_stock_data_to_s3(new_stocks, S3_STOCKS_PATH, str(place_id))
        await stocks_enqueue(place_id, S3_STOCKS_PATH, TEST_DATETIME)

    # enrich places
    await enrich_place(place_id_1)
    await enrich_place(place_id_2)

    # places are not marked as enriched
    # because assortment is not enriched
    for place_id in place_ids:
        assert not sql_are_availabilities_ready(place_id)
        assert not sql_are_prices_ready(place_id)
        assert not sql_are_stocks_ready(place_id)

    assert stq.eats_nomenclature_add_custom_assortment.has_calls is True
    times_called = stq.eats_nomenclature_add_custom_assortment.times_called
    for _ in range(times_called):
        task_info = stq.eats_nomenclature_add_custom_assortment.next_call()
        await stq_call_forward(task_info)

    # assortment is enriched
    assert sql_are_custom_categories_ready(in_progress_assortment_id)

    # place assortments are not activated
    # because places are not enriched yet
    for place_id in place_ids:
        new_place_assortments = get_sql_assortments_status(place_id)
        assert new_place_assortments['in_progress_assortment_id']

    # enrich only place_id_1
    await enrich_place(place_id_1)

    assert sql_are_availabilities_ready(place_id_1) is True
    assert sql_are_prices_ready(place_id_1) is True
    assert sql_are_stocks_ready(place_id_1) is True

    # place_id_1 assortment is activated
    # after place and assortment enrichment
    new_place_assortments = get_sql_assortments_status(place_id_1)
    assert new_place_assortments['assortment_id'] == in_progress_assortment_id
    assert not new_place_assortments['in_progress_assortment_id']

    prev_ass_last_referenced_at_2 = _get_assortment_last_referenced_at(
        pgsql, previous_active_assortment_id,
    )
    assert prev_ass_last_referenced_at_2 > prev_ass_last_referenced_at_1

    # place_id_2 assortment is not activated
    # because place is not enriched yet
    new_place_assortments_2 = get_sql_assortments_status(place_id_2)
    assert (
        new_place_assortments_2['in_progress_assortment_id']
        == in_progress_assortment_id
    )

    last_status_1 = {
        'assortment_id': in_progress_assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert (
        sql_get_place_assortment_proc_last_status(place_id_1) == last_status_1
    )
    assert sql_get_place_assortment_last_status_history(place_id_1) == [
        last_status_1,
    ]

    assert sql_get_place_assortment_proc_last_status(place_id_2) is None
    assert sql_get_place_assortment_last_status_history(place_id_2) == []

    # enrich only place_id_2
    await enrich_place(place_id_2)

    assert sql_are_availabilities_ready(place_id_2) is True
    assert sql_are_prices_ready(place_id_2) is True
    assert sql_are_stocks_ready(place_id_2) is True

    # place_id_2 assortment is now activated
    # after place and assortment enrichment
    new_place_assortments = get_sql_assortments_status(place_id_2)
    assert new_place_assortments['assortment_id'] == in_progress_assortment_id
    assert not new_place_assortments['in_progress_assortment_id']

    prev_ass_last_referenced_at_3 = _get_assortment_last_referenced_at(
        pgsql, previous_active_assortment_id,
    )
    assert prev_ass_last_referenced_at_3 > prev_ass_last_referenced_at_2

    last_status_2 = {
        'assortment_id': in_progress_assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert (
        sql_get_place_assortment_proc_last_status(place_id_2) == last_status_2
    )
    assert sql_get_place_assortment_last_status_history(place_id_2) == [
        last_status_2,
    ]


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_second_place_data.sql',
    ],
)
async def test_many_places_notified(
        activate_assortment, brand_task_enqueue, stq,
):
    place_id_1 = 1
    place_id_2 = 2
    place_ids = [place_id_1, place_id_2]

    new_availabilities = [{'origin_id': 'item_id_1', 'available': True}]
    new_stocks = [{'origin_id': 'item_id_1', 'stocks': None}]
    new_prices = [
        {'origin_id': 'item_id_1', 'price': '1000', 'currency': 'RUB'},
    ]

    for place_id in place_ids:
        await brand_task_enqueue(place_ids=[str(place_id)])
        await activate_assortment(
            new_availabilities,
            new_stocks,
            new_prices,
            place_id,
            str(place_id),
        )

    notifier_stq = stq.eats_nomenclature_assortment_activation_notifier
    times_called = notifier_stq.times_called
    assert times_called == len(place_ids)

    task_ids = set()
    notified_place_ids = []
    for _ in range(times_called):
        task_info = notifier_stq.next_call()
        assert len(task_info['kwargs']['place_ids']) == 1
        notified_place_ids.append(task_info['kwargs']['place_ids'][0])
        task_ids.add(task_info['id'])

    assert len(task_ids) == len(place_ids)
    assert set(notified_place_ids) == set(place_ids)


def _get_assortment_last_referenced_at(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select last_referenced_at
        from eats_nomenclature.assortments
        where id = %s
        """,
        (assortment_id,),
    )
    return cursor.fetchone()
