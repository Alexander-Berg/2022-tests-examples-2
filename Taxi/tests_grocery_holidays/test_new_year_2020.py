import pytest

STEPS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_holidays_user_split',
    consumers=['grocery-holidays'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always',
            'predicate': {'type': 'true'},
            'value': {
                # First step bigger to skip it
                'order_count_first_step': 5,
                'order_count_second_step': 4,
            },
        },
    ],
    default_value={},
    is_config=True,
)

PROMOCODE_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_holidays_promocode',
    consumers=['grocery-holidays'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always',
            'predicate': {'type': 'true'},
            'value': {'value': 228, 'name': 'HappyNewYear'},
        },
    ],
    default_value={},
    is_config=True,
)

LOCALIZATION_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_holidays_localizations',
    consumers=['grocery-holidays'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always',
            'predicate': {'type': 'true'},
            'value': {
                'l10n': [
                    {
                        'key': 'statistics_title',
                        'tanker': {
                            'key': 'statistics_title',
                            'keyset': 'grocery_holidays',
                        },
                        'default': '',
                    },
                    {
                        'key': 'orders_count',
                        'tanker': {
                            'key': 'orders_count',
                            'keyset': 'grocery_holidays',
                        },
                        'default': '',
                    },
                    {
                        'key': 'time_saved_full',
                        'tanker': {
                            'key': 'time_saved_full',
                            'keyset': 'grocery_holidays',
                        },
                        'default': '',
                    },
                    {
                        'key': 'time_saved_minutes',
                        'tanker': {
                            'key': 'time_saved_minutes',
                            'keyset': 'grocery_holidays',
                        },
                        'default': '',
                    },
                ],
            },
        },
    ],
    default_value={},
    is_config=True,
)

INSERT_DATA = """
INSERT INTO holidays.new_year_2020
(
    eats_user_id,
    puid,
    order_count,
    favorite_good,
    favorite_good_name,
    favorite_good_count,
    time_saved,
    total_goods
)
VALUES (
  %s, %s, %s, %s,
  %s, %s, %s, %s
);
"""


@STEPS_EXPERIMENT
@LOCALIZATION_EXPERIMENT
@PROMOCODE_EXPERIMENT
@pytest.mark.parametrize(
    'was_found,uid,eats_id',
    [
        (True, 'ok_uid', ''),
        (False, 'bad_uid', ''),
        (None, 'no_uid', ''),
        (True, '', 'ok_eats_id'),
    ],
)
async def test_basic(
        taxi_grocery_holidays, pgsql, mockserver, was_found, uid, eats_id,
):
    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/selected-products-data',
    )
    def mock_selected_products_data(request):
        found = 'found' if was_found else 'not_found'
        return {
            'products': [
                {
                    'state': found,
                    'product_info': {
                        'product_id': 'some_id',
                        'title': 'title',
                        'long_title': 'long_title',
                        'description': 'description',
                        'image_url_template': 'some_image',
                    },
                },
            ],
        }

    cursor = pgsql['grocery_holidays'].cursor()

    cursor.execute(
        INSERT_DATA,
        [
            'kind_of_eats_id',
            'ok_uid',
            16,
            '7a2b043fe3c84f2da9858611a9d8dd91000200010000',
            'good_name',
            6,
            528,
            95,
        ],
    )
    cursor.execute(
        INSERT_DATA,
        ['some_eats_id', 'bad_uid', 16, None, None, None, None, None],
    )
    cursor.execute(
        INSERT_DATA,
        [
            'ok_eats_id',
            'other_uid',
            16,
            '7a2b043fe3c84f2da9858611a9d8dd91000200010000',
            'good_name',
            6,
            528,
            95,
        ],
    )

    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/new-year-statistics',
        json={'location': [35, 35]},
        headers={
            'X-Yandex-UID': uid,
            'X-YaTaxi-Session': 'taxi:session',
            'X-YaTaxi-User': 'eats_user_id=' + eats_id,
        },
    )

    statistics = response.json()['statistics']
    if statistics['order_count'] > 4 and was_found:
        assert statistics['user_type'] == 'full_data'
        assert statistics['most_popular_good']['id'] == 'some_id'
        assert mock_selected_products_data.times_called == 1
    else:
        assert statistics['user_type'] != 'full_data'

    if uid != 'bad_uid':
        assert len(response.json()['l10n']) == 4
    else:
        assert len(response.json()['l10n']) == 2


@STEPS_EXPERIMENT
@LOCALIZATION_EXPERIMENT
@PROMOCODE_EXPERIMENT
@pytest.mark.parametrize(
    'locale,expected_title,expected_long_title',
    [
        pytest.param('en', 'title', 'long title'),
        pytest.param('he', 'כותרת', 'כותרת ארוכה'),
    ],
)
async def test_product_titles_translate(
        taxi_grocery_holidays,
        pgsql,
        mockserver,
        locale,
        expected_title,
        expected_long_title,
):
    uid = 'ok_uid'

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/selected-products-data',
    )
    def mock_selected_products_data(request):
        return {
            'products': [
                {
                    'state': 'found',
                    'product_info': {
                        'product_id': 'some_id',
                        'title': 'title',
                        'long_title': 'long_title',
                        'description': 'description',
                        'image_url_template': 'some_image',
                    },
                },
            ],
        }

    cursor = pgsql['grocery_holidays'].cursor()

    cursor.execute(
        INSERT_DATA,
        [
            'kind_of_eats_id',
            'ok_uid',
            16,
            '7a2b043fe3c84f2da9858611a9d8dd91000200010000',
            'good_name',
            6,
            528,
            95,
        ],
    )

    response = await taxi_grocery_holidays.post(
        'lavka/v1/holidays/v1/new-year-statistics',
        json={'location': [35, 35]},
        headers={
            'X-Yandex-UID': uid,
            'X-YaTaxi-Session': 'taxi:session',
            'X-Request-Language': locale,
        },
    )

    statistics = response.json()['statistics']
    assert statistics['most_popular_good']['id'] == 'some_id'
    assert mock_selected_products_data.times_called == 1

    assert statistics['most_popular_good']['title'] == expected_title
    assert statistics['most_popular_good']['subtitle'] == expected_long_title
