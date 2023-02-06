import datetime as dt

import pytest
import pytz

from tests_eats_products import utils


NOW = dt.datetime(1979, 1, 1, 0, tzinfo=pytz.UTC)


def select_discount_products(pgsql, place_id):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""select nomenclature_id, updated_at
            from eats_products.discount_product
            where place_id = {place_id}
        """,
    )
    return {r[0]: r[1] for r in cursor}


def insert_discount_products(pgsql, place_id, updated_at):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""
        insert into eats_products.discount_product (
            place_id, nomenclature_id, updated_at
        )
        values
            (1, 'old-product-1', '{updated_at}')
           ,(1, 'old-product-2', '{updated_at}')
           ,(1, 'old-product-3', '{updated_at}')
        ;""",
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_products', files=['place_data.sql'])
async def test_update_discount_products(
        pgsql, load_json, stq_runner, mocked_time, mockserver,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        response = load_json('nomenclature-response.json')
        if 'category_id' in request.query:
            return response
        for category in response['categories']:
            category['items'] = []
        return response

    place_id = 1
    insert_discount_products(pgsql, place_id, NOW)

    updated_now = NOW + dt.timedelta(days=1)
    mocked_time.set(updated_now)

    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(place_id),
        kwargs={'place_id': str(place_id)},
        expect_fail=False,
    )

    expected = {
        'old-product-1': NOW,
        'old-product-2': NOW,
        'new-product-1': updated_now,
        'new-product-3': updated_now,
    }

    actual = select_discount_products(pgsql, place_id)
    assert expected == actual
