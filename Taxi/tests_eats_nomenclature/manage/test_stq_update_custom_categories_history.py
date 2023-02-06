import dataclasses
import datetime as dt

import pytest
import pytz

NOW = dt.datetime(2021, 1, 1, 0, tzinfo=pytz.UTC)
PLACE_ID = 1
PLACE_SLUG = '1'
BRAND_ID = 1


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_partner_no_changes(
        pgsql,
        stq_call_forward,
        stq,
        fill_custom_assortment,
        load_json,
        sql_fill_products_and_pictures,
):
    sql_fill_products_and_pictures()
    await fill_custom_assortment(
        request_json=load_json('custom_categories.json'), trait_id=None,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    assert [] == sql_read_categories_history(pgsql)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('is_base', [True, False])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_all_new_categories(
        pgsql,
        stq_call_forward,
        stq,
        fill_custom_assortment,
        load_json,
        sql_fill_products_and_pictures,
        sql_get_assortment_trait_id,
        is_base,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID, None, insert_if_missing=True,
    )

    sql_fill_products_and_pictures()
    await fill_custom_assortment(
        request_json=load_json('custom_categories.json'),
        trait_id=trait_id,
        is_base=is_base,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    expected = [
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_2',
            is_base,
            NOW,
            None,
            NOW,
        ),
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_4',
            is_base,
            NOW,
            None,
            NOW,
        ),
        CategoryHistory(
            PLACE_ID, PLACE_SLUG, None, 'category_5', is_base, NOW, None, NOW,
        ),
        CategoryHistory(
            PLACE_ID, PLACE_SLUG, None, 'category_6', is_base, NOW, None, NOW,
        ),
    ]
    assert expected == sql_read_categories_history(pgsql)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('old_is_base', [True, False])
@pytest.mark.parametrize('new_is_base', [True, False])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_merge(
        pgsql,
        stq_call_forward,
        stq,
        fill_custom_assortment,
        load_json,
        mocked_time,
        sql_fill_products_and_pictures,
        sql_get_assortment_trait_id,
        old_is_base,
        new_is_base,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID, None, insert_if_missing=True,
    )

    sql_fill_products_and_pictures()
    # Insert some categories history.
    await fill_custom_assortment(
        request_json=load_json('custom_categories.json'),
        trait_id=trait_id,
        is_base=old_is_base,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    # Update categories history.
    new_now = NOW + dt.timedelta(hours=1)
    mocked_time.set(new_now)
    await fill_custom_assortment(
        request_json=load_json('custom_categories_2.json'),
        trait_id=trait_id,
        is_base=new_is_base,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    expected = [
        # should be inserted: becomes a leaf category
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_1',
            new_is_base,
            new_now,
            None,
            new_now,
        ),
        # should be deactivated: disappears from categories tree
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_2',
            old_is_base,
            NOW,
            new_now,
            new_now,
        ),
        # should be deactivated: new root parent
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_4',
            old_is_base,
            NOW,
            new_now,
            new_now,
        ),
        # should be inserted: new root parent
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_5',
            'category_4',
            new_is_base,
            new_now,
            None,
            new_now,
        ),
        # should be deactivated: not a leaf category anymore
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_5',
            old_is_base,
            NOW,
            new_now,
            new_now,
        ),
        # should be deactivated: disappears from categories tree
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_6',
            old_is_base,
            NOW,
            new_now,
            new_now,
        ),
    ]
    assert expected == sql_read_categories_history(pgsql)

    # Update categories history again.
    new_now_2 = new_now + dt.timedelta(hours=1)
    mocked_time.set(new_now_2)
    await fill_custom_assortment(
        request_json=load_json('custom_categories_3.json'),
        trait_id=trait_id,
        is_base=new_is_base,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)
    # If category is again in a tree, deactivated row
    # shouldn't be updated, it should be inserted as a new row.
    expected += [
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_6',
            new_is_base,
            new_now_2,
            None,
            new_now_2,
        ),
    ]
    assert expected == sql_read_categories_history(pgsql)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_place_slug_has_changed(
        pgsql,
        stq_call_forward,
        stq,
        fill_custom_assortment,
        load_json,
        mocked_time,
        sql_fill_products_and_pictures,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID, None, insert_if_missing=True,
    )

    sql_fill_products_and_pictures()
    # Insert some categories history.
    await fill_custom_assortment(
        request_json=load_json('custom_categories.json'), trait_id=trait_id,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    new_place_slug = 'new_place_slug'
    sql_update_place_slug(pgsql, new_place_slug)

    # Update categories history with the same categories.
    new_now = NOW + dt.timedelta(hours=1)
    mocked_time.set(new_now)
    await fill_custom_assortment(
        request_json=load_json('custom_categories.json'), trait_id=trait_id,
    )
    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(task_info)
    task_info = (
        stq.eats_nomenclature_update_custom_categories_history.next_call()
    )
    await stq_call_forward(task_info)

    expected = [
        # all old categories should be deactivated
        # because of new place_slug
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_2',
            False,
            NOW,
            new_now,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            'category_1',
            'category_4',
            False,
            NOW,
            new_now,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_5',
            False,
            NOW,
            new_now,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            PLACE_SLUG,
            None,
            'category_6',
            False,
            NOW,
            new_now,
            new_now,
        ),
        # the same categories with new place_slug
        # should be inserted
        CategoryHistory(
            PLACE_ID,
            new_place_slug,
            'category_1',
            'category_2',
            False,
            new_now,
            None,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            new_place_slug,
            'category_1',
            'category_4',
            False,
            new_now,
            None,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            new_place_slug,
            None,
            'category_5',
            False,
            new_now,
            None,
            new_now,
        ),
        CategoryHistory(
            PLACE_ID,
            new_place_slug,
            None,
            'category_6',
            False,
            new_now,
            None,
            new_now,
        ),
    ]
    assert expected == sql_read_categories_history(pgsql)


@pytest.fixture(name='fill_custom_assortment')
def _fill_custom_assortment(
        stq_runner,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        complete_enrichment_status,
        sql_fill_category_products,
        sql_get_assortment_trait,
        put_stock_data_to_s3,
        stocks_enqueue,
):
    async def fill(trait_id, request_json=None, is_base=False):
        if trait_id:
            trait = sql_get_assortment_trait(trait_id)
            assortment_name = trait['assortment_name']
        else:
            assortment_name = None

        await fill_brand_custom_categories(
            assortment_name, request_json=request_json, is_base=is_base,
        )
        place_id = 1
        assortment_id = sql_fill_enrichment_status(place_id, False, False)
        sql_fill_category_products(assortment_id)
        complete_enrichment_status(place_id, {'custom_assortment': False})

        await stq_runner.eats_nomenclature_add_custom_assortment.call(
            task_id='1',
            kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
            expect_fail=False,
        )

        # insert dummy stocks to run assortment activation
        await put_stock_data_to_s3([], place_id=place_id)
        await stocks_enqueue(place_id)

    return fill


@dataclasses.dataclass
class CategoryHistory:
    place_id: int
    place_slug: str
    root_category_name: str
    category_name: str
    is_base: bool
    created_at: dt.datetime
    deactivated_at: dt.datetime
    updated_at: dt.datetime


def to_utc(timestamp):
    if timestamp is None:
        return None
    return timestamp.astimezone(pytz.UTC)


def build_category_history(row):
    category_history = CategoryHistory(*row)
    category_history.created_at = to_utc(category_history.created_at)
    category_history.deactivated_at = to_utc(category_history.deactivated_at)
    category_history.updated_at = to_utc(category_history.updated_at)
    return category_history


def sql_read_categories_history(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select place_id, place_slug,
               root_category_name, category_name, is_base,
               created_at, deactivated_at, updated_at
        from eats_nomenclature.places_custom_categories_history
        order by place_id, place_slug, category_name, created_at
        """,
    )
    return [build_category_history(row) for row in list(cursor)]


def sql_update_place_slug(pgsql, slug, place_id=1):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.places
        set slug = '{slug}'
        where id = {place_id}
        """,
    )
