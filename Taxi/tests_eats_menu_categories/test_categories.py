import typing

import pytest

from tests_eats_menu_categories import models
from tests_eats_menu_categories import utils


TIME_NOW = '2022-01-01T12:00:00+00:00'
YANDEX_LOGIN = '@testsuite'

CATEGORIES_HANDLE_PREFIX = '/internal/eats-menu-categories/v1/categories/'

CATEGORIES_GET_HANDLE = CATEGORIES_HANDLE_PREFIX + 'get'
CATEGORIES_POST_HANDLE = CATEGORIES_HANDLE_PREFIX + 'post'
CATEGORIES_UPDATE_HANDLE = CATEGORIES_HANDLE_PREFIX + 'update'
CATEGORIES_DELETE_HANDLE = CATEGORIES_HANDLE_PREFIX + 'delete'
CATEGORIES_POST_CHECK_HANDLE = CATEGORIES_POST_HANDLE + '/check'
CATEGORIES_UPDATE_CHECK_HANDLE = CATEGORIES_UPDATE_HANDLE + '/check'
CATEGORIES_DELETE_CHECK_HANDLE = CATEGORIES_DELETE_HANDLE + '/check'


CATEGORY_BURGERS = models.Category(
    category_id='1',
    slug='burgers',
    name='Бургеры',
    status=models.CategoryStatus.PUBLISHED,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
    created_by=YANDEX_LOGIN,
    updated_by=YANDEX_LOGIN,
)
CATEGORY_PIZZA = models.Category(
    category_id='2',
    slug='pizza',
    name='Пицца',
    status=models.CategoryStatus.DRAFT,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
)
CATEGORY_SHAVERMA = models.Category(
    category_id='3',
    slug='shaverma',
    name='Шаурма',
    status=models.CategoryStatus.HIDDEN,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
)
CATEGORY_BURGERS_2 = models.Category(
    category_id='4',
    slug='new_BURGERS_v2',
    name='Новые бургеры',
    status=models.CategoryStatus.PUBLISHED,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
    created_by=YANDEX_LOGIN,
    updated_by=YANDEX_LOGIN,
)


ERROR_MISSING_REQUEST_PARAMS = {
    'code': 'MISSING_REQUEST_PARAMS',
    'message': 'Category id or slug is required',
}
ERROR_AMBIGUOUS_REQUEST = {
    'code': 'AMBIGUOUS_REQUEST',
    'message': 'Request is ambiguous. Specify id or slug',
}
ERROR_CATEGORY_NOT_FOUND = {
    'code': 'CATEGORY_NOT_FOUND',
    'message': 'Category not found',
}
ERROR_DUPLICATE_CATEGORY = {
    'code': 'DUPLICATE_CATEGORY',
    'message': 'Category with slug burgers already exists',
}


@pytest.mark.parametrize(
    """status_filter,slug_filter,name_filter,limit,expected_categories""",
    [
        pytest.param([], None, None, None, [], id='no filters, no categories'),
        pytest.param(
            [],
            None,
            None,
            None,
            [CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='no filters, all',
        ),
        pytest.param(
            [models.CategoryStatus.PUBLISHED],
            None,
            None,
            None,
            [CATEGORY_BURGERS],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='filter published, only published',
        ),
        pytest.param(
            [],
            '',
            None,
            None,
            [CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='slug filter empty, all',
        ),
        pytest.param(
            [],
            'Burgers',
            None,
            None,
            [CATEGORY_BURGERS, CATEGORY_BURGERS_2],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_BURGERS_2, CATEGORY_PIZZA,
            ),
            id='slug filter partial, some categories',
        ),
        pytest.param(
            [],
            'burgers-pizza',
            None,
            None,
            [],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='slug filter extra chars, none',
        ),
        pytest.param(
            [],
            None,
            '',
            None,
            [CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='name filter empty, all',
        ),
        pytest.param(
            [],
            None,
            'Бургеры',
            None,
            [CATEGORY_BURGERS],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_BURGERS_2, CATEGORY_PIZZA,
            ),
            id='name filter partial, some categories',
        ),
        pytest.param(
            [],
            None,
            'бургеры пицца',
            None,
            [],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='name filter extra chars, none',
        ),
        pytest.param(
            [],
            None,
            'Бургеры_пицца%суши',
            None,
            [
                models.Category(
                    category_id='5',
                    slug='weird_category',
                    name='Бургеры_пицца%суши',
                    status=models.CategoryStatus.PUBLISHED,
                    created_at=TIME_NOW,
                    updated_at=TIME_NOW,
                    created_by=YANDEX_LOGIN,
                    updated_by=YANDEX_LOGIN,
                ),
            ],
            marks=pytest.mark.categories(
                models.Category(
                    category_id='5',
                    slug='weird_category',
                    name='Бургеры_пицца%суши',
                    status=models.CategoryStatus.PUBLISHED,
                    created_at=TIME_NOW,
                    updated_at=TIME_NOW,
                    created_by=YANDEX_LOGIN,
                    updated_by=YANDEX_LOGIN,
                ),
                # если бы плейсхолдеры не экранировались, то такая
                # категория бы тоже попала в выдачу
                models.Category(
                    category_id='6',
                    slug='burger_pizza',
                    name='Бургеры пицца воки суши',
                    status=models.CategoryStatus.PUBLISHED,
                    created_at=TIME_NOW,
                    updated_at=TIME_NOW,
                    created_by=YANDEX_LOGIN,
                    updated_by=YANDEX_LOGIN,
                ),
            ),
            id='name filter LIKE placeholder chars, filtered',
        ),
        pytest.param(
            [],
            None,
            None,
            1,
            [CATEGORY_BURGERS],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='limit=1, 1 category',
        ),
        pytest.param(
            [],
            None,
            None,
            4,
            [CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA],
            marks=pytest.mark.categories(
                CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA,
            ),
            id='limit too big, all',
        ),
    ],
)
async def test_categories_list(
        taxi_eats_menu_categories,
        categories,
        status_filter: typing.List[models.CategoryStatus],
        slug_filter: typing.Optional[str],
        name_filter: typing.Optional[str],
        limit: typing.Optional[int],
        expected_categories: typing.List[models.Category],
):
    """
    Проверяем что /categories/list возвращает все категории,
    удовлетворяющие условиям фильтрации
    """

    categories = await categories.list(
        status_filter=status_filter,
        slug_filter=slug_filter,
        name_filter=name_filter,
        limit=limit,
    )
    assert categories == expected_categories


@pytest.mark.categories(
    CATEGORY_BURGERS, CATEGORY_PIZZA, CATEGORY_SHAVERMA, CATEGORY_BURGERS_2,
)
async def test_categories_list_pagination(taxi_eats_menu_categories):
    """
    Проверяем что /categories/list поддерживает пагинацию
    """

    page_size = 2

    # page 1
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/categories/list',
        headers={'x-yandex-login': YANDEX_LOGIN},
        json={'limit': page_size},
    )
    assert response.status == 200
    response_data = response.json()
    page_1 = utils.categories_from_response(response_data)
    assert page_1 == [CATEGORY_BURGERS, CATEGORY_PIZZA]
    next_page_cursor = response_data['next_page_cursor']
    assert next_page_cursor == '2'

    # page 2
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/categories/list',
        headers={'x-yandex-login': YANDEX_LOGIN},
        json={'limit': page_size, 'cursor': next_page_cursor},
    )
    assert response.status == 200
    response_data = response.json()
    page_2 = utils.categories_from_response(response_data)
    assert page_2 == [CATEGORY_SHAVERMA, CATEGORY_BURGERS_2]
    assert 'next_page_cursor' not in response_data


@pytest.mark.parametrize(
    'category_id, category_slug, expected_code, expected_response',
    [
        pytest.param(
            None,
            None,
            400,
            ERROR_MISSING_REQUEST_PARAMS,
            id='missing id and slug 400',
        ),
        pytest.param(
            '1',
            'burgers',
            400,
            ERROR_AMBIGUOUS_REQUEST,
            id='ambiguous request 400',
        ),
        pytest.param(
            '1', None, 404, ERROR_CATEGORY_NOT_FOUND, id='not found 404',
        ),
        pytest.param(
            '1',
            None,
            200,
            {
                'id': '1',
                'slug': 'burgers',
                'name': 'Бургеры',
                'status': 'published',
                'created_at': TIME_NOW,
                'updated_at': TIME_NOW,
                'created_by': YANDEX_LOGIN,
                'updated_by': YANDEX_LOGIN,
            },
            marks=pytest.mark.categories(
                CATEGORY_PIZZA, CATEGORY_SHAVERMA, CATEGORY_BURGERS,
            ),
            id='found category by id 200',
        ),
        pytest.param(
            None,
            'burgers',
            200,
            {
                'id': '1',
                'slug': 'burgers',
                'name': 'Бургеры',
                'status': 'published',
                'created_at': TIME_NOW,
                'updated_at': TIME_NOW,
                'created_by': YANDEX_LOGIN,
                'updated_by': YANDEX_LOGIN,
            },
            marks=pytest.mark.categories(
                CATEGORY_PIZZA, CATEGORY_SHAVERMA, CATEGORY_BURGERS,
            ),
            id='found category by slug 200',
        ),
    ],
)
@pytest.mark.now(TIME_NOW)
async def test_categories_get(
        taxi_eats_menu_categories,
        categories,
        category_id: str,
        category_slug: str,
        expected_code: int,
        expected_response: dict,
):
    """
    Проверяем что /categories/get возвращает нужную категорию по id
    """

    request = dict()
    if category_id:
        request['id'] = category_id
    if category_slug:
        request['slug'] = category_slug

    response = await taxi_eats_menu_categories.post(
        CATEGORIES_GET_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=request,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'expected_code, expected_response',
    [
        pytest.param(
            200,
            {
                'id': '1',
                'slug': 'burgers',
                'name': 'Бургеры',
                'status': 'published',
                'created_at': TIME_NOW,
                'updated_at': TIME_NOW,
                'created_by': YANDEX_LOGIN,
                'updated_by': YANDEX_LOGIN,
            },
            id='post category 200',
        ),
        pytest.param(
            400,
            ERROR_DUPLICATE_CATEGORY,
            marks=pytest.mark.categories(CATEGORY_BURGERS),
            id='duplicate slug 400',
        ),
    ],
)
@pytest.mark.now(TIME_NOW)
async def test_categories_post(
        taxi_eats_menu_categories,
        categories,
        expected_code: int,
        expected_response: dict,
):
    """
    Проверяем что /categories/post добавляет категорию в сервис
    """

    category_slug = 'burgers'
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_POST_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json={'slug': category_slug, 'name': 'Бургеры', 'status': 'published'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response

    category = await categories.get_by_slug(category_slug)
    assert category == CATEGORY_BURGERS


@pytest.mark.parametrize(
    'expected_code, expected_response, expected_category',
    [
        pytest.param(
            200,
            {
                'id': '1',
                'slug': 'burgers',
                'name': 'Новые бургеры',
                'status': 'hidden',
                'created_at': TIME_NOW,
                'updated_at': '2022-01-01T14:00:00+00:00',
                'created_by': YANDEX_LOGIN,
                'updated_by': '@mad-manager',
            },
            models.Category(
                category_id='1',
                slug='burgers',
                name='Новые бургеры',
                status=models.CategoryStatus.HIDDEN,
                created_at=TIME_NOW,
                updated_at='2022-01-01T14:00:00+00:00',
                created_by=YANDEX_LOGIN,
                updated_by='@mad-manager',
            ),
            marks=pytest.mark.categories(CATEGORY_BURGERS),
            id='update category 200',
        ),
        pytest.param(
            404, ERROR_CATEGORY_NOT_FOUND, None, id='id not found 404',
        ),
        pytest.param(
            404,
            ERROR_CATEGORY_NOT_FOUND,
            models.Category(
                category_id='1',
                slug='burgers_old',
                name='Бургеры',
                status=models.CategoryStatus.DRAFT,
                created_at=TIME_NOW,
                updated_at=TIME_NOW,
            ),
            marks=pytest.mark.categories(
                models.Category(
                    category_id='1',
                    slug='burgers_old',
                    name='Бургеры',
                    status=models.CategoryStatus.DRAFT,
                    created_at=TIME_NOW,
                    updated_at=TIME_NOW,
                ),
                models.Category(
                    category_id='2',
                    slug='burgers',
                    name='Бургеры',
                    status=models.CategoryStatus.DRAFT,
                    created_at=TIME_NOW,
                    updated_at=TIME_NOW,
                ),
            ),
            id='slug not found 404',
        ),
    ],
)
@pytest.mark.now('2022-01-01T14:00:00+00:00')
async def test_categories_update(
        taxi_eats_menu_categories,
        categories,
        expected_code: int,
        expected_response: dict,
        expected_category: models.Category,
):
    """
    Проверяем что /categories/update изменяет категорию
    """

    category_id = '1'
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_UPDATE_HANDLE,
        headers={'x-yandex-login': '@mad-manager'},
        json={
            'id': category_id,
            'slug': 'burgers',
            'name': 'Новые бургеры',
            'status': 'hidden',
        },
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response

    category = await categories.get_by_id(category_id)
    assert category == expected_category


@pytest.mark.parametrize(
    'expected_code, expected_response',
    [
        pytest.param(
            200,
            {
                'id': '1',
                'slug': 'burgers',
                'name': 'Бургеры',
                'status': 'published',
                'created_at': TIME_NOW,
                'updated_at': TIME_NOW,
                'created_by': YANDEX_LOGIN,
                'updated_by': YANDEX_LOGIN,
            },
            marks=pytest.mark.categories(CATEGORY_BURGERS),
            id='delete category 200',
        ),
        pytest.param(404, ERROR_CATEGORY_NOT_FOUND, id='not found 404'),
    ],
)
@pytest.mark.now(TIME_NOW)
async def test_categories_delete(
        taxi_eats_menu_categories,
        categories,
        expected_code: int,
        expected_response: dict,
):
    """
    Проверяем что /categories/delete удаляет категорию
    """

    category_id = '1'
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_DELETE_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json={'id': category_id},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response

    category = await categories.get_by_id(category_id)
    assert not category


async def test_categories_post_check_ok(taxi_eats_menu_categories):
    category = {'name': 'test_category', 'slug': 'testing'}
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_POST_CHECK_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=category,
    )

    assert response.status_code == 200
    assert response.json()['data'] == category


@pytest.mark.categories(CATEGORY_BURGERS)
@pytest.mark.parametrize(
    'category',
    [
        pytest.param(
            {'name': 'fake burgers', 'slug': 'burgers'}, id='slug conflict',
        ),
        pytest.param({'name': 'empty', 'slug': ''}, id='empty slug'),
    ],
)
async def test_categories_post_check_fail(taxi_eats_menu_categories, category):
    category = category
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_POST_CHECK_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=category,
    )

    assert response.status_code == 400


@pytest.mark.categories(CATEGORY_BURGERS)
async def test_categories_update_check_ok(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на обновление категории валиден.
    """

    category = {
        'id': '1',
        'slug': 'not_right_slug',
        'name': 'Бургеры',
        'status': 'published',
    }
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_UPDATE_CHECK_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=category,
    )

    assert response.status_code == 200
    assert response.json()['data'] == category


async def test_categories_update_check_fail(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на обновление категории не валиден.
    """

    category = {
        'id': '10',
        'slug': 'falafel',
        'name': 'Testing',
        'status': 'published',
    }
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_UPDATE_CHECK_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=category,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'code',
    [
        pytest.param(
            200, marks=(pytest.mark.categories(CATEGORY_BURGERS)), id='ok',
        ),
        pytest.param(
            200,
            marks=(
                pytest.mark.categories(CATEGORY_BURGERS),
                pytest.mark.rules(
                    models.Rule(
                        rule_id='1',
                        slug='rule-1',
                        name='My rule 1',
                        effect=models.RuleEffect.MAP,
                        category_ids=['1'],
                        type=models.RuleType.PREDICATE,
                        enabled=True,
                        payload=utils.make_eq_predicate(
                            arg_name='item_id', value='item-1',
                        ),
                        created_at='2021-12-09T00:00:00+00:00',
                        updated_at='2021-12-09T01:00:00+00:00',
                    ),
                ),
            ),
            id='ok with rule',
        ),
        pytest.param(404, id='failed'),
    ],
)
async def test_categories_remove_check(taxi_eats_menu_categories, code):
    """
    Проверяет драфт на удаление категории
    """

    request = {'id': '1'}
    response = await taxi_eats_menu_categories.post(
        CATEGORIES_DELETE_CHECK_HANDLE,
        headers={'x-yandex-login': YANDEX_LOGIN},
        json=request,
    )

    assert response.status_code == code

    if code == 200:
        assert response.json()['data'] == request
