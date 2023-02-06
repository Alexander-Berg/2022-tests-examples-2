from tests_grocery_marketing import common
from tests_grocery_marketing import models

ANY = 'Any'


async def add_matching_rule(
        taxi_grocery_marketing,
        pgsql,
        kind='promocode',
        min_cart_cost=None,
        city=ANY,
        country=ANY,
        depot=ANY,
        group=ANY,
        product=ANY,
        suffix=None,
):
    tag = 'tag'
    if city != ANY:
        for item in city:
            tag += f'_{item}'
    if country != ANY:
        for item in country:
            tag += f'_{item}'
    if depot != ANY:
        for item in depot:
            tag += f'_{item}'
    if group != ANY:
        for item in group:
            tag += f'_{item}'
    if product != ANY:
        for item in product:
            tag += f'_{item}'

    if tag == 'tag':
        tag = 'tag_all'

    if min_cart_cost is not None:
        tag += f'_{min_cart_cost}'

    if suffix is not None:
        tag += suffix

    await add_tag_rule(
        taxi_grocery_marketing,
        pgsql,
        tag=tag,
        kind=kind,
        min_cart_cost=min_cart_cost,
        rules=[
            models.MatchCondition(condition_name='city', values=city),
            models.MatchCondition(condition_name='country', values=country),
            models.MatchCondition(condition_name='depot', values=depot),
            models.MatchCondition(condition_name='group', values=group),
            models.MatchCondition(condition_name='product', values=product),
            models.MatchCondition(condition_name='rule_id', values=[tag]),
        ],
    )


async def add_tag_rule(
        taxi_grocery_marketing,
        pgsql,
        tag='some_tag',
        kind='promocode',
        min_cart_cost=None,
        rules=None,
):
    hierarchy_name = 'menu_tags'

    start_tags_count = common.tags_count(pgsql, hierarchy_name)

    if rules is None:
        rules = [common.VALID_ACTIVE_PERIOD]
    else:
        rules = [rule.as_object() for rule in rules]
        rules.append(common.VALID_ACTIVE_PERIOD)

    request = {
        'rules': rules,
        'data': {
            'hierarchy_name': 'menu_tags',
            'tag': {
                'description': 'some_description',
                'values_with_schedules': [
                    {
                        'value': {
                            'tag': tag,
                            'kind': kind,
                            'min_cart_cost': min_cart_cost,
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
        },
        'update_existing_tags': False,
        'revisions': [],
    }

    response = await taxi_grocery_marketing.post(
        common.ADD_RULES_URL,
        request,
        headers=common.get_draft_headers(
            'draft_id_check_add_rules_validation',
        ),
    )

    assert response.status_code == 200
    end_tags_count = common.tags_count(pgsql, hierarchy_name)

    assert start_tags_count != end_tags_count
