import typing

import pytest

from tests_eats_menu_categories import models
from tests_eats_menu_categories import utils


TIME_NOW = '2022-01-01T12:00:00+00:00'
YANDEX_LOGIN = '@testsuite'

CATEGORY_TESTING = models.Category(
    category_id='category-1',
    slug='testing',
    name='Категория',
    status=models.CategoryStatus.PUBLISHED,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
    created_by=YANDEX_LOGIN,
    updated_by=YANDEX_LOGIN,
)


RULE = models.Rule(
    rule_id='1',
    slug='rule-1',
    name='My rule 1',
    effect=models.RuleEffect.MAP,
    category_ids=['category-1'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload=utils.make_eq_predicate(arg_name='item_id', value='item-1'),
    created_at='2021-12-09T00:00:00+00:00',
    updated_at='2021-12-09T01:00:00+00:00',
)

RULE_2 = models.Rule(
    rule_id='2',
    slug='rule-2',
    name='My rule 2',
    effect=models.RuleEffect.MAP,
    category_ids=['category-1'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload=utils.make_eq_predicate(arg_name='item_id', value='item-2'),
    created_at='2021-12-09T00:02:00+00:00',
    updated_at='2021-12-09T01:02:00+00:00',
)

RULE_2_DUP = models.Rule(
    rule_id='3',
    slug='rule-2',
    name='My duplicate rule 2',
    effect=models.RuleEffect.MAP,
    category_ids=['category-1'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload=utils.make_eq_predicate(arg_name='item_id', value='item-2'),
    created_at='2021-12-09T00:02:00+00:00',
    updated_at='2021-12-09T01:02:00+00:00',
)

WRONG_CATEGORY_RULE = models.Rule(
    rule_id='4',
    slug='empty',
    name='Empty rule',
    effect=models.RuleEffect.MAP,
    category_ids=['category-200'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload=utils.make_eq_predicate(arg_name='item_id', value='item-2'),
    created_at='2021-12-09T00:02:00+00:00',
    updated_at='2021-12-09T01:02:00+00:00',
)

RULE_3_DISABLED = models.Rule(
    rule_id='5',
    slug='rule-3',
    name='My rule 3',
    effect=models.RuleEffect.MAP,
    category_ids=['category-3'],
    type=models.RuleType.PREDICATE,
    enabled=False,
    payload=utils.make_eq_predicate(arg_name='item_id', value='item-3'),
    created_at='2021-12-09T00:03:00+00:00',
    updated_at='2021-12-09T01:03:00+00:00',
)


async def get_rule(taxi_eats_menu_categories, rule_id, expected_code=200):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/get',
        headers={'x-yandex-login': 'testsuite'},
        json={'id': rule_id},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        return response.json()['rule']


@pytest.mark.rules(RULE)
async def test_rule_get(taxi_eats_menu_categories):

    rule_data = await get_rule(taxi_eats_menu_categories, rule_id=RULE.rule_id)
    assert rule_data == RULE.as_json()


async def test_rule_create(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': RULE.as_json(with_id=False, with_times=False)},
    )
    assert response.status_code == 200
    assert response.json() == {'rule': {'id': RULE.rule_id}}

    rule_data = await get_rule(taxi_eats_menu_categories, rule_id=RULE.rule_id)
    assert rule_data['created_at'] == rule_data['updated_at'] > RULE.updated_at
    del rule_data['created_at']
    del rule_data['updated_at']
    assert rule_data == RULE.as_json(with_times=False)


@pytest.mark.parametrize(
    'invalid_slug', ['', ' ', '?', '*', 'a b', 'c*', '/d', '(e)'],
)
async def test_rule_create_invalid_slug(
        taxi_eats_menu_categories, invalid_slug,
):

    rule_invalid_slug = models.Rule(
        rule_id='',  # Не используется
        slug=invalid_slug,
        name='My rule 1',
        effect=models.RuleEffect.MAP,
        category_ids=['category-1'],
        type=models.RuleType.PREDICATE,
        enabled=True,
        payload=utils.make_eq_predicate(arg_name='item_id', value='item-1'),
        created_at='',  # Не используется
        updated_at='',  # Не используется
    )

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create',
        headers={'x-yandex-login': 'testsuite'},
        json={
            'rule': rule_invalid_slug.as_json(with_id=False, with_times=False),
        },
    )
    assert response.status_code == 400


@pytest.mark.rules(RULE)
async def test_rule_create_same_slug(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': RULE.as_json(with_id=False, with_times=False)},
    )
    assert response.status_code == 409


@pytest.mark.rules(RULE)
async def test_rule_update(taxi_eats_menu_categories):

    updated_rule = models.Rule(
        rule_id=RULE.rule_id,
        slug=RULE.slug,
        name='My rule 1 updated',
        effect=models.RuleEffect.UNMAP,
        category_ids=[
            'category-1-updated',
            'category-10-updated',
            'category-100-updated',
        ],
        type=models.RuleType.PREDICATE,
        enabled=False,
        payload=utils.make_eq_predicate(
            arg_name='item_id', value='item-1-updated',
        ),
        created_at=RULE.created_at,
        updated_at='',  # Не используется
    )

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/update',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': updated_rule.as_json(with_times=False)},
    )
    assert response.status_code == 204

    updated_rule_data = await get_rule(
        taxi_eats_menu_categories, rule_id=RULE.rule_id,
    )
    assert updated_rule_data['updated_at'] > RULE.updated_at
    del updated_rule_data['updated_at']
    assert updated_rule_data == updated_rule.as_json(with_updated_at=False)


@pytest.mark.rules(RULE, RULE_2)
async def test_rule_update_requested_only(taxi_eats_menu_categories):
    """
    EDACAT-2414: тест проверяет, что обновляется только запрошенное правило.
    """

    updated_rule = models.Rule(
        rule_id=RULE.rule_id,
        slug=RULE.slug,
        name='My rule 1 updated',
        effect=models.RuleEffect.UNMAP,
        category_ids=[
            'category-1-updated',
            'category-10-updated',
            'category-100-updated',
        ],
        type=models.RuleType.PREDICATE,
        enabled=False,
        payload=utils.make_eq_predicate(
            arg_name='item_id', value='item-1-updated',
        ),
        created_at=RULE.created_at,
        updated_at='',  # Не используется
    )

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/update',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': updated_rule.as_json(with_times=False)},
    )
    assert response.status_code == 204

    updated_rule_data = await get_rule(
        taxi_eats_menu_categories, rule_id=RULE.rule_id,
    )
    del updated_rule_data['updated_at']
    assert updated_rule_data == updated_rule.as_json(with_updated_at=False)

    non_changes_rule_data = await get_rule(
        taxi_eats_menu_categories, rule_id=RULE_2.rule_id,
    )
    assert non_changes_rule_data == RULE_2.as_json()


async def test_rule_update_non_existing(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/update',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': RULE.as_json(with_times=False)},
    )
    assert response.status_code == 404


@pytest.mark.rules(RULE)
async def test_rule_remove(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/remove',
        headers={'x-yandex-login': 'testsuite'},
        json={'id': RULE.rule_id},
    )
    assert response.status_code == 204

    await get_rule(
        taxi_eats_menu_categories, rule_id=RULE.rule_id, expected_code=404,
    )


async def test_rule_remove_non_existing(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/remove',
        headers={'x-yandex-login': 'testsuite'},
        json={'id': '2'},
    )
    assert response.status_code == 404


@pytest.mark.rules(RULE, RULE_2, RULE_3_DISABLED)
async def test_rule_list_retrieval(taxi_eats_menu_categories):

    # 1. List enabled
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/list',
        headers={'x-yandex-login': 'testsuite'},
        json={'types': ['predicate'], 'enabled': True},
    )
    assert response.status_code == 200
    assert sorted(response.json()['rules'], key=lambda r: r['id']) == [
        RULE.as_json(),
        RULE_2.as_json(),
    ]

    # 2. List disabled
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/list',
        headers={'x-yandex-login': 'testsuite'},
        json={'types': ['predicate'], 'enabled': False},
    )
    assert response.status_code == 200
    assert response.json()['rules'] == [RULE_3_DISABLED.as_json()]

    # 3. List all
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/list',
        headers={'x-yandex-login': 'testsuite'},
        json={},
    )
    assert response.status_code == 200
    assert sorted(response.json()['rules'], key=lambda r: r['id']) == [
        RULE.as_json(),
        RULE_2.as_json(),
        RULE_3_DISABLED.as_json(),
    ]


@pytest.mark.categories(CATEGORY_TESTING)
async def test_rule_create_check_simple_ok(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на создание валиден.
    """

    request = {'rule': RULE.as_json(with_id=False, with_times=False)}
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create/check',
        headers={'x-yandex-login': 'testsuite'},
        json=request,
    )

    assert response.status_code == 200
    assert response.json()['data'] == request
    assert response.json()['diff']['new'] == request['rule']

    second_request = {'rule': RULE_2.as_json(with_id=False, with_times=False)}
    second_response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create/check',
        headers={'x-yandex-login': 'testsuite'},
        json=second_request,
    )

    assert second_response.status_code == 200
    assert second_response.json()['data'] == second_request
    assert second_response.json()['diff']['new'] == second_request['rule']


@pytest.mark.rules(RULE_2)
@pytest.mark.categories(CATEGORY_TESTING)
@pytest.mark.parametrize(
    'rule, code',
    [
        pytest.param(
            models.Rule(
                rule_id='',
                slug='',
                name='Empty',
                effect=models.RuleEffect.MAP,
                category_ids=['category-1'],
                type=models.RuleType.PREDICATE,
                enabled=True,
                payload=utils.make_eq_predicate(
                    arg_name='item_id', value='item-1',
                ),
                created_at='2021-12-09T00:00:00+00:00',
                updated_at='2021-12-09T01:00:00+00:00',
            ),
            400,
            id='empty rule',
        ),
        pytest.param(RULE_2_DUP, 409, id='duplicating'),
        pytest.param(WRONG_CATEGORY_RULE, 404, id='category is not in base'),
    ],
)
async def test_rule_create_check_fail(taxi_eats_menu_categories, rule, code):
    """
    Проверяет, что драфт на создание не валиден.
    """

    request = {'rule': rule.as_json(with_id=False, with_times=False)}
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/create/check',
        headers={'x-yandex-login': 'testsuite'},
        json=request,
    )

    assert response.status_code == code


@pytest.mark.categories(
    models.Category(
        category_id='category-1-updated',
        slug='testing_category',
        name='Категория',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
        created_by=YANDEX_LOGIN,
        updated_by=YANDEX_LOGIN,
    ),
)
@pytest.mark.rules(RULE)
@pytest.mark.parametrize(
    'payload',
    [
        pytest.param(
            utils.make_gte_predicate(
                arg_name='item_id', value='item-1-updated',
            ),
            id='eq predicate',
        ),
        pytest.param(
            utils.make_and_predicate(
                utils.make_eq_predicate(
                    arg_name='item_id', value='item-1-updated',
                ),
                utils.make_gte_predicate(
                    arg_name='item_name', value='slug-updated',
                ),
            ),
            id='and predicate',
        ),
        pytest.param(
            utils.make_not_predicate(
                utils.make_eq_predicate(
                    arg_name='item_id', value='item-1-updated',
                ),
                utils.make_gte_predicate(
                    arg_name='item_name', value='slug-updated',
                ),
            ),
            id='not predicate',
        ),
    ],
)
async def test_rule_update_check_ok(taxi_eats_menu_categories, payload):
    """
    Проверяет, что драфт на обновление валиден.
    """

    updated_rule = models.Rule(
        rule_id=RULE.rule_id,
        slug=RULE.slug,
        name='My rule 1 updated',
        effect=models.RuleEffect.UNMAP,
        category_ids=['category-1-updated'],
        type=models.RuleType.PREDICATE,
        enabled=False,
        payload=payload,
        created_at=RULE.created_at,
        updated_at='',  # Не используется
    )

    request = {'rule': updated_rule.as_json(with_slug=True, with_times=False)}
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/update/check',
        headers={'x-yandex-login': 'testsuite'},
        json=request,
    )

    assert response.status_code == 200

    response = response.json()

    assert response['diff']['current'] == RULE.as_json(
        with_id=False, with_slug=True, with_times=False,
    )

    assert response['diff']['new'] == updated_rule.as_json(
        with_id=False, with_slug=True, with_times=False,
    )

    assert response['data'] == request

    # EDACAT-2512
    if payload['type'] in ['all_of', 'not']:
        new_payload = response['data']['rule']['payload']
        assert 'predicates' in new_payload['predicate']
        assert len(new_payload['predicate']['predicates']) == len(
            payload['predicates'],
        )


async def test_rule_update_check_fail(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на обновление не валиден (правило не найдено)
    """

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/update/check',
        headers={'x-yandex-login': 'testsuite'},
        json={'rule': RULE.as_json(with_slug=True, with_times=True)},
    )

    assert response.status_code == 404


@pytest.mark.rules(RULE)
async def test_rule_remove_check_ok(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на удаление валиден.
    """

    request = {'id': RULE.rule_id}
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/remove/check',
        headers={'x-yandex-login': 'testsuite'},
        json=request,
    )
    assert response.status_code == 200
    assert response.json()['data'] == request


async def test_rule_remove_check_fail(taxi_eats_menu_categories):
    """
    Проверяет, что драфт на удаление валиден.
    """

    request = {'id': RULE.rule_id}
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/remove/check',
        headers={'x-yandex-login': 'testsuite'},
        json=request,
    )
    assert response.status_code == 404


@pytest.mark.rules(RULE, RULE_2, RULE_3_DISABLED)
@pytest.mark.parametrize(
    'types, enabled, name, slug, cursor, limit, expected',
    [
        pytest.param(
            [],
            None,
            None,
            None,
            None,
            None,
            [RULE.as_json(), RULE_2.as_json(), RULE_3_DISABLED.as_json()],
            id='no filters return all',
        ),
        pytest.param(
            [],
            True,
            None,
            None,
            None,
            None,
            [RULE.as_json(), RULE_2.as_json()],
            id='only enabled',
        ),
        pytest.param(
            [],
            False,
            None,
            None,
            None,
            None,
            [RULE_3_DISABLED.as_json()],
            id='only disabled',
        ),
        pytest.param(
            [],
            None,
            None,
            None,
            None,
            1,
            [RULE.as_json()],
            id='limit response',
        ),
        pytest.param(
            [],
            None,
            None,
            None,
            '1',
            1,
            [RULE_2.as_json()],
            id='paginate single rule',
        ),
        pytest.param(
            [],
            None,
            '2',
            None,
            None,
            None,
            [RULE_2.as_json()],
            id='search by name',
        ),
        pytest.param(
            [],
            None,
            None,
            '-2',
            None,
            None,
            [RULE_2.as_json()],
            id='search by slug',
        ),
        pytest.param(
            ['predicate'],
            True,
            None,
            None,
            '1',
            None,
            [RULE_2.as_json()],
            id='paginate and search by types and status',
        ),
    ],
)
async def test_rule_list(
        taxi_eats_menu_categories,
        types: typing.List[str],
        enabled: typing.Optional[bool],
        name: typing.Optional[str],
        slug: typing.Optional[str],
        cursor: typing.Optional[str],
        limit: typing.Optional[int],
        expected: list,
):
    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/rules/list',
        headers={'x-yandex-login': 'testsuite'},
        json={
            'types': types,
            'enabled': enabled,
            'name': name,
            'slug': slug,
            'cursor': cursor,
            'limit': limit,
        },
    )
    assert response.status_code == 200

    rules = response.json()['rules']
    if rules:
        assert 'next_page_cursor' in response.json()

    if limit is not None:
        assert len(rules) <= limit

    assert len(expected) == len(rules)
    for want, got in zip(expected, rules):
        assert want == got
