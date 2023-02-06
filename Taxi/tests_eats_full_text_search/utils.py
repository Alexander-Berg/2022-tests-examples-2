import contextlib
import json

import pytest

from . import catalog
from . import rest_menu_storage


def serialize_parent_categories(categories):
    if isinstance(categories, str):
        return categories
    return json.dumps(categories)


def category_to_gta(category):
    attrs = [
        {'Key': 'i_pid', 'Value': str(category['place_id'])},
        {'Key': 's_place_slug', 'Value': str(category['place_slug'])},
        {'Key': 'i_category_id', 'Value': str(category['category_id'])},
        {'Key': 'title', 'Value': str(category['title'])},
        {'Key': 'i_type', 'Value': '2'},
        {
            'Key': 's_parent_categories_v2',
            'Value': serialize_parent_categories(
                category['parent_categories'],
            ),
        },
    ]

    if 'gallery' in category:
        attrs.append(
            {'Key': 's_gallery', 'Value': json.dumps(category['gallery'])},
        )

    if 'factors' in category:
        attrs.append({'Key': '_JsonFactors', 'Value': category['factors']})

    return attrs


def item_to_gta(item, with_price=False, doc_type=1):
    attrs = [
        {'Key': 'i_pid', 'Value': str(item['place_id'])},
        {'Key': 's_place_slug', 'Value': str(item['place_slug'])},
        {'Key': 'title', 'Value': str(item['title'])},
        {'Key': 's_description', 'Value': str(item['description'])},
        {'Key': 's_nom_item_id', 'Value': str(item['nomenclature_item_id'])},
        {'Key': 'i_type', 'Value': str(doc_type)},
        {
            'Key': 's_parent_categories_v2',
            'Value': serialize_parent_categories(item['parent_categories']),
        },
        {'Key': 'i_adult', 'Value': str(int(item['adult']))},
        {'Key': 'i_shipping_type', 'Value': str(int(item['shipping_type']))},
        {'Key': 's_categories', 'Value': str(json.dumps(item['categories']))},
        {'Key': 's_origin_id', 'Value': str(item['origin_id'])},
    ]
    if with_price:
        attrs.append({'Key': 'price', 'Value': str(item['price'])})
    if 'weight' in item:
        attrs.append({'Key': 's_weight', 'Value': str(item['weight'])})
    if 'gallery' in item:
        attrs.append(
            {'Key': 's_gallery', 'Value': json.dumps(item['gallery'])},
        )
    if 'factors' in item:
        attrs.append({'Key': '_JsonFactors', 'Value': item['factors']})
    if 'core_item_id' in item:
        attrs.append(
            {'Key': 'i_core_item_id', 'Value': str(item['core_item_id'])},
        )

    return attrs


def retail_item_to_gta(item):
    attrs = [
        {'Key': 'i_pid', 'Value': str(item['place_id'])},
        {'Key': 's_place_slug', 'Value': str(item['place_slug'])},
        {'Key': 'z_title', 'Value': item['title']},
        {'Key': 'p_public_id', 'Value': item['nomenclature_item_id']},
        {'Key': 'p_origin_id', 'Value': item['origin_id']},
    ]
    if 'brand' in item:
        attrs.append({'Key': 'z_brand', 'Value': item['brand']})
    if 'parent_categories' in item:
        categories_str = ''
        for category in item['parent_categories']:
            title = category['title']
            if not categories_str:
                categories_str = f'{title}.'
            else:
                categories_str += f' {title}.'
        attrs.append({'Key': 'z_categories', 'Value': categories_str})
    if 'type' in item:
        attrs.append({'Key': 'z_type', 'Value': item['type']})
    if 'is_catch_weight' in item:
        attrs.append(
            {
                'Key': 'p_is_catch_weight',
                'Value': str(int(item['is_catch_weight'])),
            },
        )
    if 'buy_score' in item:
        attrs.append({'Key': 'f_buy_score', 'Value': str(item['buy_score'])})
    if 'measure' in item:
        attrs.append({'Key': 'z_measure_value', 'Value': item['measure']})

    return attrs


def gta_to_document(url, gta, mtime=100):
    return {
        'Relevance': 1,
        'Priority': 1,
        'InternalPriority': 1,
        'DocId': 'doc_1',
        'SRelevance': 1,
        'SPriority': 1,
        'SInternalPriority': 1,
        'ArchiveInfo': {
            'Title': 'My Search Item',
            'Headline': '...',
            'IndexGeneration': 1,
            'Passage': ['...'],
            'Url': url,
            'Size': 1,
            'Charset': 'utf-8',
            'Mtime': mtime,
            'GtaRelatedAttribute': gta,
        },
    }


def catalog_to_saas_business(business: str) -> str:
    result = 0
    if business == catalog.Business.Restaurant:
        result = 0
    elif business == catalog.Business.Shop:
        result = 1
    elif business == catalog.Business.Store:
        result = 2
    elif business == catalog.Business.Pharmacy:
        result = 3
    return str(result)


def catalog_place_to_saas_doc(place: catalog.Place) -> dict:
    gta = [
        {'Key': 'i_region_id', 'Value': '1'},
        {'Key': 'i_rating', 'Value': '10'},
        {'Key': 'title', 'Value': place.name},
        {'Key': 's_launched_at', 'Value': '2017-11-23T00:00:00+03:00'},
        {
            'Key': 'i_business',
            'Value': catalog_to_saas_business(place.business),
        },
        {'Key': 's_place_slug', 'Value': place.slug},
        {'Key': 'i_pid', 'Value': str(place.id)},
        {'Key': 'i_type', 'Value': '0'},
    ]
    return gta_to_document(f'/{place.slug}', gta)


def item_preview_to_saas_doc(
        place_id: str,
        place_slug: str,
        item_preview: rest_menu_storage.ItemPreview,
) -> dict:
    gta = [
        {'Key': 'title', 'Value': item_preview.name},
        {'Key': 's_place_slug', 'Value': place_slug},
        {'Key': 'i_pid', 'Value': place_id},
        {'Key': 's_rest_menu_storage_id', 'Value': item_preview.id},
        {'Key': 'i_type', 'Value': '4'},
    ]
    return gta_to_document(f'/{place_slug}/items/{item_preview.id}', gta)


def rest_menu_item_to_saas_doc(
        place_id: str, place_slug: str, item: rest_menu_storage.Item,
) -> dict:
    gta = [
        {'Key': 'title', 'Value': item.name},
        {'Key': 's_place_slug', 'Value': place_slug},
        {'Key': 'i_pid', 'Value': place_id},
        {'Key': 's_rest_menu_storage_id', 'Value': item.id},
        {'Key': 'i_type', 'Value': '4'},
    ]
    return gta_to_document(f'/{place_slug}/items/{item.id}', gta)


def get_saas_response(docs):
    group = []
    for doc in docs:
        group.append({'CategoryName': '', 'Document': [doc]})

    return {
        'Head': {'Version': 1, 'SegmentId': '', 'IndexGeneration': 1},
        'DebugInfo': {
            'BaseSearchCount': 1,
            'BaseSearchNotRespondCount': 0,
            'AnswerIsComplete': True,
        },
        'BalancingInfo': {'Elapsed': 1, 'WaitInQueue': 1, 'ExecutionTime': 1},
        'SearcherProp': [],
        'ErrorInfo': {'GotError': 0},
        'TotalDocCount': [1, 0, 0],
        'Grouping': [
            {
                'Attr': '',
                'Mode': 1,
                'NumGroups': [1, 0, 0],
                'NumDocs': [2, 0, 0],
                'Group': group,
            },
        ],
    }


def get_headers():
    return {
        'x-device-id': 'kgjaa0hq-gie23bvedw8-tct4h082hg-1h6ubaw17yf',
        'x-platform': 'desktop_web',
        'x-app-version': '1.1.1',
        'X-YaTaxi-User': 'eats_user_id=456',  # auth_context header
    }


def to_nomenclature_product(item):
    """
    Возаращает представление продукта
    как в ручке assortiment/details
    """
    result = {
        'product_id': item['nomenclature_item_id'],
        'name': item['title'],
        'description': item['description'],
        'adult': item['adult'],
        'images': [],
    }
    if item['shipping_type'] == 0:
        result['shipping_type'] = 'all'
    elif item['shipping_type'] == 1:
        result['shipping_type'] = 'delivery'
    else:
        result['shipping_type'] = 'pickup'

    images = item.get('images')
    if images:
        result['images'] = item['images']

    promo_price = item.get('promo_price')
    if promo_price:
        result['price'] = promo_price
        result['old_price'] = item['price']
    else:
        result['price'] = item['price']
    in_stock = item.get('in_stock')
    if in_stock:
        result['in_stock'] = in_stock
    weight = item.get('weight')
    if weight:
        measure_as_array = weight.split()
        if measure_as_array[1] == 'g':
            unit = 'GRM'
        else:
            unit = 'KGRM'
        measure = {'value': int(measure_as_array[0]), 'unit': unit}
        result['measure'] = measure
    return result


def to_nomenclature_category(category):
    """
    Возвращает представление категории
    как в ручке assortiment/details
    """
    return {'category_id': str(category['category_id'])}


def assert_place_match(place: dict, catalog_place: catalog.Place):
    """
    Сравнивает модель плейса из ответа поиска
    с моделью плейса из каталога
    """
    assert place['available'] == catalog_place.availability.is_available
    assert place['available_from'] == catalog_place.availability.available_from
    assert place['available_to'] == catalog_place.availability.available_to

    assert place['business'] == catalog_place.business
    assert place['delivery']['text'] == catalog_place.delivery.text
    assert place['picture']['url'] == catalog_place.picture.uri
    assert place['picture']['ratio'] == catalog_place.picture.ratio
    assert (
        place['price_category']['title'] == catalog_place.price_category.name
    )

    assert place['slug'] == catalog_place.slug
    for place_tag, catalog_place_tag in zip(place['tags'], catalog_place.tags):
        assert place_tag['title'] == catalog_place_tag.name

    assert place['title'] == catalog_place.name


def assert_has_catalog_place(
        block_payload: dict, catalog_place: catalog.Place,
):
    """
    Пытается найти плейс в ответе сервиса и
    сравнить модель плейса из ответа сервиса
    с моделью из каталога
    """

    found = False
    for place in block_payload:
        if place['slug'] == catalog_place.slug:
            assert_place_match(place, catalog_place)
            found = True
            break

    assert found, f'CatalogPlace with slug {catalog_place.slug} was not found'


@contextlib.contextmanager
def drop_table(cursor, schema, table):
    """
    :param cursor: курсов из фикстуры pgsql для доступа к postgresql
    :param schema: имя схемы в базе
    :param table: имя таблицы, которую нужно дропнуть

    Контекст менеждер, который переименовывает
    таблицу в рамках скоего скоупа

    Нужен, так как testsuite на самом деле не выполняет все скрипты
    из schemas/postgresql перед каждым тестом
    и если просто дропнуть в коде таблицу, то все следующие тесты это
    увидят.
    """

    cursor.execute(
        f"""
        ALTER TABLE {schema}.{table}
        RENAME TO {table}_renamed;
        """,
    )

    try:
        yield
    finally:
        cursor.execute(
            f"""
            ALTER TABLE {schema}.{table}_renamed
            RENAME TO {table};
            """,
        )


def dynamic_prices(default_percent: int, items_percents: dict = None):
    items = {'__default__': default_percent}
    if items_percents:
        items.update(items_percents)
    return pytest.mark.experiments3(
        name='eats_dynamic_price_by_user',
        consumers=['eats_smart_prices/user'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': True,
                    'calculate_method': 'by_place_percent',
                    'modification_percent': items,
                },
            },
        ],
    )
