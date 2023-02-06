from typing import List

from tests_eats_menu_categories import models


def categories_from_response(response: dict) -> List[models.Category]:
    result = []
    for item in response['categories']:
        result.append(category_from_response(item))
    return result


def category_from_response(response: dict) -> models.Category:
    return models.Category(
        category_id=response['id'],
        slug=response['slug'],
        name=response['name'],
        status=models.CategoryStatus(response['status']),
        created_at=response['created_at'],
        updated_at=response['updated_at'],
        created_by=(
            response['created_by'] if 'created_by' in response else None
        ),
        updated_by=(
            response['updated_by'] if 'updated_by' in response else None
        ),
    )


def make_eq_predicate(arg_name, value):
    return {
        'type': 'eq',
        'init': {'arg_name': arg_name, 'arg_type': 'string', 'value': value},
    }


def make_gte_predicate(arg_name, value):
    return {
        'type': 'gte',
        'init': {'arg_name': arg_name, 'arg_type': 'string', 'value': value},
    }


def make_and_predicate(predicate_1, predicate_2):
    return {
        'type': 'all_of',
        'init': {},
        'predicates': [predicate_1, predicate_2],
    }


def make_not_predicate(predicate_1, predicate_2):
    return {
        'type': 'not',
        'init': {},
        'predicates': [predicate_1, predicate_2],
    }


def make_item_mapping(
        item_id: str, category_ids: List[str],
) -> models.ItemWithCategories:
    return models.ItemWithCategories(
        item_id=item_id,
        categories=[
            models.ScoredCategory(category_id=id) for id in category_ids
        ],
    )


def item_mappings_from_response(
        response: dict,
) -> List[models.ItemWithCategories]:
    result: List[models.ItemWithCategories] = []
    for mapping in response['items']:
        result.append(
            models.ItemWithCategories(
                item_id=mapping['item_id'],
                categories=[
                    models.ScoredCategory(
                        category_id=cat['category_id'], score=cat['score'],
                    )
                    for cat in mapping['categories']
                ],
            ),
        )
    return result
