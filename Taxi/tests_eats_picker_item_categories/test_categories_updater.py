import datetime

import pytest

from . import utils


async def test_categories_updater(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
        mockserver,
        get_categories_for_all_items,
):
    place_id = 1
    eats_item_id1 = 'item_id1'
    eats_item_id2 = 'item_id2'
    item_id1 = create_item(
        place_id, eats_item_id1, '2021-04-25T12:00:00.000000+03:00',
    )
    item_id2 = create_item(place_id, eats_item_id2)

    category_public_id1 = 'public_id1'
    category_name1 = 'name1'
    category_public_id2 = 'public_id2'
    category_name2 = 'name2'
    category_id1 = create_category(category_public_id1, category_name1)
    category_id2 = create_category(category_public_id2, category_name2)

    create_item_category(item_id1, category_id1, 0)
    create_item_category(item_id2, category_id2, 0)

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id1}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id1,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    records = get_categories_for_all_items()
    assert len(records) == 3
    item1, item2, item3 = records
    assert item1['eats_item_id'] == eats_item_id1
    assert item1['name'] == highlevel_category_name
    assert item1['public_id'] == highlevel_category_id
    assert item2['eats_item_id'] == eats_item_id1
    assert item2['name'] == lowest_category_name
    assert item2['public_id'] == lowest_category_id
    assert item3['eats_item_id'] == eats_item_id2
    assert item3['name'] == category_name2
    assert item3['public_id'] == category_public_id2


async def test_categories_updater_multiple_categories_per_item(
        taxi_eats_picker_item_categories,
        create_item,
        mockserver,
        get_item_categories,
):
    place_id = 1
    eats_item_id = 'item_id'
    create_item(place_id, eats_item_id, '2021-04-25T12:00:00.000000+03:00')

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [
                    {'public_id': '0', 'name': '0', 'public_parent_id': '1'},
                    {'public_id': '1', 'name': '1', 'public_parent_id': '2'},
                    {'public_id': '2', 'name': '2'},
                    {'public_id': '3', 'name': '3', 'public_parent_id': '4'},
                    {'public_id': '4', 'name': '4'},
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['0', '3'],
                    },
                ],
            },
            status=200,
        )

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    item_categories = get_item_categories(eats_item_id)
    assert len(item_categories) == 5
    for i, (hierarchy_number, level, public_id, public_parent_id) in enumerate(
            zip(
                [0, 0, 0, 1, 1],
                [0, 1, 2, 0, 1],
                ['2', '1', '0', '4', '3'],
                [None, '2', '1', None, '4'],
            ),
    ):
        assert item_categories[i]['eats_item_id'] == eats_item_id
        assert item_categories[i]['hierarchy_number'] == hierarchy_number
        assert item_categories[i]['level'] == level
        assert item_categories[i]['public_id'] == public_id
        assert item_categories[i]['public_parent_id'] == public_parent_id


@pytest.mark.parametrize('had_categories', [False, True])
async def test_categories_updater_no_categories(
        taxi_eats_picker_item_categories,
        had_categories,
        create_item,
        create_category,
        create_item_category,
        mockserver,
        get_item_categories,
):
    place_id = 1
    eats_item_id = 'item_id'
    item_id = create_item(
        place_id, eats_item_id, '2021-04-25T12:00:00.000000+03:00',
    )

    if had_categories:
        category_id1 = create_category('0', '0')
        category_id2 = create_category('1', '1', '0')
        create_item_category(item_id, category_id1, 0)
        create_item_category(item_id, category_id2, 1)

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [],
                'products': [
                    {'origin_id': 'item_id', 'category_public_ids': []},
                ],
            },
            status=200,
        )

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    item_categories = get_item_categories(eats_item_id)
    assert not item_categories


@utils.item_refresh_delay_config(batch_size=1)
async def test_categories_updater_select_the_oldest(
        taxi_eats_picker_item_categories,
        create_item,
        mockserver,
        get_categories_for_all_items,
):
    now = datetime.datetime.utcnow()
    place_id = 1
    eats_item_id1 = 'item_id1'
    eats_item_id2 = 'item_id2'
    create_item(place_id, eats_item_id1, now - datetime.timedelta(minutes=30))
    create_item(place_id, eats_item_id2, now - datetime.timedelta(minutes=40))

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id2}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id2,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    records = get_categories_for_all_items()
    assert len(records) == 2
    for record in records:
        assert record[0] == eats_item_id2


@pytest.mark.parametrize('expected_status_code', [200, 404])
async def test_categories_clean_legacy_place(
        taxi_eats_picker_item_categories,
        expected_status_code,
        create_item,
        create_category,
        create_item_category,
        mockserver,
        get_categories_for_all_items,
):
    place_id = 1
    eats_item_id1 = 'item_id1'
    eats_item_id2 = 'item_id2'
    item_id1 = create_item(
        place_id, eats_item_id1, '2021-04-25T12:00:00.000000+03:00',
    )
    item_id2 = create_item(place_id, eats_item_id2)

    category_public_id1 = 'public_id1'
    category_name1 = 'name1'
    category_public_id2 = 'public_id2'
    category_name2 = 'name2'
    category_id1 = create_category(category_public_id1, category_name1)
    category_id2 = create_category(category_public_id2, category_name2)

    create_item_category(item_id1, category_id1, 0)
    create_item_category(item_id2, category_id2, 0)

    records = get_categories_for_all_items()
    assert len(records) == 2

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        return mockserver.make_response(status=expected_status_code)

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    records = get_categories_for_all_items()
    if expected_status_code == 404:
        assert not records
    else:
        assert len(records) == 2


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_update_outdating_items(
        taxi_eats_picker_item_categories,
        create_item,
        mockserver,
        get_categories_for_all_items,
):
    now = datetime.datetime.now()
    actual_period = now
    outdating_period = now - datetime.timedelta(minutes=120)
    place_id = 1
    eats_item_id1 = 'item_id1'
    eats_item_id2 = 'item_id2'
    create_item(place_id, eats_item_id1, actual_period)
    create_item(place_id, eats_item_id2, outdating_period)

    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.json['products'] == [{'origin_id': eats_item_id2}]
        assert request.query['include_custom_categories'] == 'false'
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id2,
                        'category_public_ids': [lowest_category_id],
                    },
                ],
            },
            status=200,
        )

    await taxi_eats_picker_item_categories.run_task(
        'distlock/categories-updater',
    )

    assert _mock_eats_nomenclature.times_called == 1

    records = get_categories_for_all_items()
    assert len(records) == 1
    assert records[0][0] == eats_item_id2
    assert records[0][1] == lowest_category_name
