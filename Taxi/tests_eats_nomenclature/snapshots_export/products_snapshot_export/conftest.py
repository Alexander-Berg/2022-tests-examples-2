import pytest

BRAND_ID = 777


@pytest.fixture
def put_products_snapshot_task_into_stq(stq_runner):  # pylint: disable=C0103
    async def do_work(
            brand_id, task_id='1', expect_fail=False, exec_tries=None,
    ):
        await stq_runner.eats_nomenclature_export_products_snapshot.call(
            task_id=task_id,
            args=[],
            kwargs={'brand_id': brand_id},
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return do_work


@pytest.fixture
def generate_product_snapshot_from_row():  # pylint: disable=C0103
    def do_work(row):
        snapshot = {
            'brand_id': row['brand_id'],
            'id': row['id'],
            'origin_id': row['origin_id'],
            'name': row['name'],
            'is_adult': row['is_adult'],
        }
        for field_name in [
                'is_choosable',
                'is_catch_weight',
                'sku_id',
                'description',
                'composition',
                'carbohydrates_in_grams',
                'proteins_in_grams',
                'fats_in_grams',
                'calories',
                'storage_requirements',
                'expiration_info',
                'package_info',
                'product_type',
                'product_brand',
                'vendor_name',
                'vendor_country',
                'measure_in_grams',
                'measure_in_milliliters',
                'volume',
                'is_delivery_available',
                'is_pickup_available',
                'is_alcohol',
                'is_fresh',
                'marking_type',
                'fat_content',
                'milk_type',
                'flavour',
                'cultivar',
                'meat_type',
                'carcass_part',
                'egg_category',
                'alco_grape_cultivar',
                'alco_flavour',
                'alco_aroma',
                'alco_pairing',
        ]:
            if field_name in row:
                snapshot[field_name] = row[field_name]
        for field_name in ['barcodes', 'image_urls']:
            if field_name in row:
                snapshot[field_name] = sorted(row[field_name])
        return snapshot

    return do_work


@pytest.fixture
def sorted_logged_data():
    def do_work(logged_data):
        return sorted(logged_data, key=lambda item: item['origin_id'])

    return do_work


@pytest.fixture
def verify_logged_part():
    def do_work(logged_data, expected_partial_data):
        for key, expected_value in expected_partial_data.items():
            val = logged_data[0][key]
            if isinstance(expected_value, list):
                assert sorted(val) == sorted(expected_value)
            else:
                assert val == expected_value

    return do_work
