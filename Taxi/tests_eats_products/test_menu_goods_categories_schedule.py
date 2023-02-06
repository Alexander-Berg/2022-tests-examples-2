import pytest

from tests_eats_products import conftest
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

MONDAY_12_01 = '2022-02-28T12:01:00+03:00'
TUESDAY_12_01 = '2022-03-01T12:01:00+03:00'
TUESDAY_12_31 = '2022-03-01T12:31:00+03:00'
TUESDAY_14_00 = '2022-03-01T14:00:00+03:00'

BRAND_ID = '1'
CATEGORY_ID = '1'

SCHEDULE = {
    BRAND_ID: {
        CATEGORY_ID: {
            'intervals': [
                {'exclude': False, 'day': [2]},  # Tuesday
                {
                    'exclude': False,
                    'daytime': [{'from': '12:00:00', 'to': '13:00:00'}],
                },
                {
                    'exclude': True,
                    'daytime': [{'from': '12:30:00', 'to': '12:32:00'}],
                },
            ],
        },
    },
}


@pytest.mark.parametrize(
    ['expected_categories'],
    [
        pytest.param(set(), marks=[pytest.mark.now(MONDAY_12_01)]),
        pytest.param({1}, marks=[pytest.mark.now(TUESDAY_12_01)]),
        pytest.param(set(), marks=[pytest.mark.now(TUESDAY_12_31)]),
        pytest.param(set(), marks=[pytest.mark.now(TUESDAY_14_00)]),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_CATEGORIES_SCHEDULE=SCHEDULE)
async def test_categories_schedule(
        taxi_eats_products, mock_v1_nomenclature_context, expected_categories,
):
    """
    Тест проверяет, что категории отфильтровываются по расписанию (
    happy path)
    """
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = {c['id'] for c in resp_json['categories']}
    assert categories == expected_categories


SCHEDULE_DATETIME = {
    BRAND_ID: {
        CATEGORY_ID: {
            'intervals': [
                {
                    'exclude': True,
                    'datetime': [
                        {
                            'from': '2022-03-01 12:15:00',
                            'to': '2022-03-01 12:17:00',
                        },
                    ],
                },
            ],
        },
    },
}

TIME_IN_THE_INTERVAL = '2022-03-01T12:16:00+03:00'
TIME_OUT_OF_THE_INTERVAL_1 = '2022-03-01T12:18:00+03:00'
TIME_OUT_OF_THE_INTERVAL_2 = '2022-03-01T12:14:00+03:00'


@pytest.mark.parametrize(
    ['expected_categories'],
    [
        pytest.param(set(), marks=[pytest.mark.now(TIME_IN_THE_INTERVAL)]),
        pytest.param({1}, marks=[pytest.mark.now(TIME_OUT_OF_THE_INTERVAL_1)]),
        pytest.param({1}, marks=[pytest.mark.now(TIME_OUT_OF_THE_INTERVAL_2)]),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_CATEGORIES_SCHEDULE=SCHEDULE_DATETIME)
async def test_categories_schedule_datetime(
        taxi_eats_products, mock_v1_nomenclature_context, expected_categories,
):
    """
    Тест проверяет, что категории отфильтровываются по расписанию (
    интервалы типа datetime)
    """
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = {c['id'] for c in resp_json['categories']}
    assert categories == expected_categories


PARAMETRIZE_SOME_CASES = pytest.mark.parametrize(
    [],
    [
        pytest.param(marks=[pytest.mark.now(MONDAY_12_01)]),
        pytest.param(marks=[pytest.mark.now(TUESDAY_12_01)]),
        pytest.param(marks=[pytest.mark.now(TUESDAY_12_31)]),
        pytest.param(marks=[pytest.mark.now(TUESDAY_14_00)]),
    ],
)


@PARAMETRIZE_SOME_CASES
@pytest.mark.config(EATS_PRODUCTS_CATEGORIES_SCHEDULE={})
async def test_categories_schedule_no_brand_in_config(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    """
    Тест проверяет, что категории не отфильтровываются, если
    текущий бренд не указан в конфиге.
    """
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = {c['id'] for c in resp_json['categories']}
    assert categories == {1}


@PARAMETRIZE_SOME_CASES
@pytest.mark.config(EATS_PRODUCTS_CATEGORIES_SCHEDULE={BRAND_ID: {}})
async def test_categories_schedule_no_categories_in_config(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    """
    Тест проверяет, что категории не отфильтровываются, если
    не указаны категории в конфиге.
    """
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = {c['id'] for c in resp_json['categories']}
    assert categories == {1}


@PARAMETRIZE_SOME_CASES
@pytest.mark.config(
    EATS_PRODUCTS_CATEGORIES_SCHEDULE={
        BRAND_ID: {
            CATEGORY_ID: {
                'intervals': [
                    {
                        'exclude': True,
                        'daytime': [{'from': '99:00:00', 'to': '99:00:00'}],
                    },
                ],
            },
        },
    },
)
async def test_categories_schedule_invalid_format(
        taxi_eats_products, mock_v1_nomenclature_context,
):
    """
    Тест проверяет, что категории не отфильтровываются, если
    формат конфига неправильный.
    """
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = {c['id'] for c in resp_json['categories']}
    assert categories == {1}
