# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-brands
pytest_plugins = ['eats_brands_plugins.pytest_plugins']

TEST_DEFAULT_LIMIT = 50
DEFAULT_CLIENT_TYPE = 'common'


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_brands'].dict_cursor()

    return create_cursor


@pytest.fixture()
def get_brand(get_cursor):
    def do_get_brand(brand_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_brands.brands WHERE id = %s', [brand_id],
        )
        return cursor.fetchone()

    return do_get_brand


@pytest.fixture()
def check_brand_data():
    def do_check_brand_data(brand, expected_data):

        nullable_fields = [
            'fast_food_notify_time_shift',
            'editorial_verdict',
            'editorial_description',
            'notify_email_personal_ids',
            'bit_settings',
        ]

        for field in nullable_fields:
            if field not in expected_data:
                assert brand[field] is None

        for field in expected_data:
            if field == 'slug':
                assert (
                    brand[field]
                    .lower()
                    .startswith(expected_data[field].lower())
                )
            else:
                assert brand[field] == expected_data[field]

    return do_check_brand_data


@pytest.fixture()
def get_merge_history(get_cursor):
    def do_get_merge_history(actual_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_brands.merge_history WHERE actual_id = %s',
            [actual_id],
        )
        return cursor.fetchone()

    return do_get_merge_history
