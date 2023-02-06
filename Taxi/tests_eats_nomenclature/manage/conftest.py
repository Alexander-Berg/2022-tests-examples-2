import datetime as dt

import pytest


@pytest.fixture(name='fill_brand_custom_categories')
async def _fill_brand_custom_categories(
        taxi_eats_nomenclature, load_json, pgsql,
):
    async def do_fill_brand_custom_categories(
            assortment_name,
            is_base=False,
            is_restaurant=False,
            request_json=None,
    ):
        if not request_json:
            request_json = load_json('custom_categories_request.json')
        request_json['is_base'] = is_base
        request_json['is_restaurant'] = is_restaurant
        # Fill custom categories groups.
        response = await taxi_eats_nomenclature.post(
            '/v1/manage/custom_categories_groups', json=request_json,
        )
        group_id = response.json()['group_id']

        # Fill brand custom categories groups.
        request = {
            'categories_groups': [{'id': f'{group_id}'}],
            'use_only_custom_categories': False,
        }

        assortment_query = (
            f'&assortment_name={assortment_name}' if assortment_name else ''
        )
        await taxi_eats_nomenclature.post(
            '/v1/manage/brand/custom_categories_groups?brand_id=1'
            + assortment_query,
            json=request,
        )

    return do_fill_brand_custom_categories


@pytest.fixture(name='sql_read_data')
def _sql_read_data(pgsql):
    def do_sql_read_data(query):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(query)
        return {tuple(row) for row in cursor}

    return do_sql_read_data


@pytest.fixture(name='sql_fill_enrichment_status')
def _sql_fill_enrichment_status(pgsql):
    def do_sql_fill_enrichment_status(
            place_id,
            is_active,
            are_custom_categories_ready,
            enrichment_started_at=dt.datetime.now(),
    ):
        field = 'assortment_id'
        if not is_active:
            field = 'in_progress_assortment_id'

        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select pa.{field}
            from eats_nomenclature.place_assortments pa
            join eats_nomenclature.assortments a
              on pa.{field} = a.id
            where pa.place_id = {place_id}
            """,
        )
        result = list(cursor)
        if result:
            assortment_id = result[0][0]
        else:
            cursor.execute(
                f"""
                insert into eats_nomenclature.assortments
                default values
                returning id;
                """,
            )
            assortment_id = list(cursor)[0][0]
            cursor.execute(
                f"""
                insert into eats_nomenclature.place_assortments(
                    place_id, {field}
                )
                values ({place_id}, {assortment_id})
                on conflict (place_id, coalesce(trait_id, -1)) do update
                set
                    {field} = excluded.{field},
                    updated_at = now();
                """,
            )

        cursor.execute(
            f"""
            insert into eats_nomenclature.assortment_enrichment_statuses (
                assortment_id,
                are_custom_categories_ready,
                enrichment_started_at
            )
            values (
                '{assortment_id}',
                '{are_custom_categories_ready}',
                '{enrichment_started_at}'
            )
            on conflict (assortment_id)
            do update set
            are_custom_categories_ready = excluded.are_custom_categories_ready;
            """,
        )
        return assortment_id

    return do_sql_fill_enrichment_status


@pytest.fixture(name='sql_fill_products_and_pictures')
def _sql_fill_products_and_pictures(pgsql):
    def do_fill_products_and_pictures():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.pictures (url, hash)
            values ('url_1', '1'),
                   ('url_2', '2'),
                   ('url_3', '3')
            on conflict do nothing;

            insert into eats_nomenclature.products
            (origin_id, name, brand_id, public_id)
            values ('item_origin_1', 'item_1', 1,
                    '11111111111111111111111111111111'),
                   ('item_origin_2', 'item_2', 1,
                    '22222222222222222222222222222222'),
                   ('item_origin_3', 'item_3', 1,
                    '33333333333333333333333333333333');

            insert into eats_nomenclature.product_pictures
            (product_id, picture_id, updated_at)
            values (1, 1, '2021-04-20 10:00:00');

            insert into eats_nomenclature.places_products
            (place_id, product_id, origin_id, price, available_from)
            values (1, 1, 'item_origin_1', '100', '2017-01-08 04:05:06'),
                   (1, 2, 'item_origin_2', '100', '2017-01-08 04:05:06'),
                   (1, 3, 'item_origin_3', '100', '2017-01-08 04:05:06');
            """,
        )

    return do_fill_products_and_pictures


@pytest.fixture(name='sql_fill_category_products')
def _sql_fill_category_products(pg_realdict_cursor):
    def do_smth(assortment_id):
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            insert into eats_nomenclature.categories
            (name, assortment_id, is_custom, custom_category_id)
            values (
                       'category_1', {assortment_id}, false, null
                   ),
                   (
                       'category_2', {assortment_id}, false, null
                   ),
                   (
                       'category_3', {assortment_id}, false, null
                   )
            returning id;
            """,
        )
        categories = cursor.fetchall()

        cursor.execute(
            f"""
            insert into eats_nomenclature.categories_products
            (assortment_id, category_id, product_id, sort_order)
            values ({assortment_id}, {categories[0]['id']}, 1, 1),
                   ({assortment_id}, {categories[1]['id']}, 2, 2),
                   ({assortment_id}, {categories[2]['id']}, 3, 3);
            """,
        )

    return do_smth


@pytest.fixture(name='sql_fill_custom_assortment')
def _sql_fill_custom_assortment(pgsql):
    def do_sql_fill_custom_assortment(assortment_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.custom_categories
            (name, picture_id, external_id)
            values ('category_1', 1, 1),
                   ('category_2', 1, 2),
                   ('category_3', 1, 3)
            on conflict do nothing
            returning name, id;""",
        )
        custom_category_name_to_id = {
            category[0]: category[1] for category in list(cursor)
        }

        cursor.execute(
            f"""
            insert into eats_nomenclature.categories
            (name, assortment_id, is_custom, custom_category_id)
            values (
                       'category_1', {assortment_id}, true,
                       {custom_category_name_to_id['category_1']}
                   ),
                   (
                       'category_2', {assortment_id}, true,
                       {custom_category_name_to_id['category_2']}
                   ),
                   (
                       'category_3', {assortment_id}, true,
                       {custom_category_name_to_id['category_3']}
                   );

            insert into eats_nomenclature.category_pictures
            (assortment_id, category_id, picture_id)
            values ({assortment_id}, 1, 1),
                   ({assortment_id}, 2, 1),
                   ({assortment_id}, 3, 1);

            insert into eats_nomenclature.categories_relations
            (assortment_id, category_id, parent_category_id, sort_order)
            values ({assortment_id}, 1, null, 200),
                   ({assortment_id}, 2, 1, 250),
                   ({assortment_id}, 3, 1, 300);

            insert into eats_nomenclature.categories_products
            (assortment_id, category_id, product_id, sort_order)
            values ({assortment_id}, 2, 1, 1),
                   ({assortment_id}, 2, 2, 2),
                   ({assortment_id}, 3, 3, 3);

            insert into eats_nomenclature.places_categories
            (assortment_id, place_id, category_id, active_items_count)
            values ({assortment_id}, 1, 1, 0),
                   ({assortment_id}, 1, 2, 2),
                   ({assortment_id}, 1, 3, 1);
            """,
        )

    return do_sql_fill_custom_assortment


@pytest.fixture(name='sql_fill_not_custom_categories')
def _sql_fill_not_custom_categories(pgsql):
    def do_fill(assortment_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.categories
            (name, assortment_id, is_custom, is_base, is_restaurant)
            values ('category_4', {assortment_id}, false, true, false),
                   ('category_5', {assortment_id}, false, true, false);

            insert into eats_nomenclature.categories_relations
            (assortment_id, category_id, parent_category_id, sort_order)
            values ({assortment_id}, 4, null, 100),
                   ({assortment_id}, 5, null, 150);

            insert into eats_nomenclature.categories_products
            (assortment_id, category_id, product_id, sort_order)
            values ({assortment_id}, 4, 1, 3),
                   ({assortment_id}, 4, 2, 3),
                   ({assortment_id}, 4, 3, 3);

            insert into eats_nomenclature.category_pictures
            (assortment_id, category_id, picture_id)
            values ({assortment_id}, 4, 1),
                   ({assortment_id}, 5, 1);

            insert into eats_nomenclature.places_categories
            (assortment_id, place_id, category_id, active_items_count)
            values ({assortment_id}, 1, 4, 10),
                   ({assortment_id}, 1, 5, 20);
            """,
        )

    return do_fill


@pytest.fixture(name='sql_get_group_public_id')
def _sql_get_group_public_id(pgsql):
    def do_sql_get_group_public_id():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select public_id
            from eats_nomenclature.custom_categories_groups
            """,
        )
        return list(cursor)[0][0]

    return do_sql_get_group_public_id


@pytest.fixture(name='sql_get_pictures')
def _sql_get_pictures(pgsql):
    def do_sql_get_pictures():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select url, processed_url, needs_subscription
            from eats_nomenclature.pictures
            """,
        )
        return set(cursor)

    return do_sql_get_pictures


@pytest.fixture(name='sql_get_categories')
def _sql_get_categories(pgsql):
    def do_sql_get_categories():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select c.name, p.url, p.processed_url, c.sort_order, c.description
            from eats_nomenclature.custom_categories c
            left join eats_nomenclature.pictures p
            on c.picture_id = p.id
            """,
        )
        categories = [
            {
                'name': row[0],
                'picture_url': row[1],
                'picture_processed_url': row[2],
                'sort_order': row[3],
                'description': row[4],
            }
            for row in cursor
        ]
        return sorted(
            categories,
            key=lambda item: (
                item['name'],
                item['picture_url'],
                item['sort_order'],
                item['description'],
            ),
        )

    return do_sql_get_categories


@pytest.fixture(name='sql_get_cat_prod_types')
def _sql_get_cat_prod_types(pgsql):
    def do_sql_get_cat_prod_types():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select c.name, cpt.product_type_id
            from eats_nomenclature.custom_categories_product_types cpt
            join eats_nomenclature.custom_categories c
            on cpt.custom_category_id = c.id
            """,
        )
        return {(row[0], row[1]) for row in cursor}

    return do_sql_get_cat_prod_types


@pytest.fixture(name='sql_get_category_tags')
def _sql_get_category_tags(pgsql):
    def do_sql_get_category_tags():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select cc.name, tags.name
            from eats_nomenclature.custom_category_tags cct
            join eats_nomenclature.custom_categories cc
            on cct.custom_category_id = cc.id
            join eats_nomenclature.tags tags
            on tags.id = cct.tag_id
            """,
        )
        return {(row[0], row[1]) for row in cursor}

    return do_sql_get_category_tags


@pytest.fixture(name='sql_get_categories_products')
def _sql_get_categories_products(pgsql):
    def do_sql_get_categories_products():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select c.name, cp.product_id
            from eats_nomenclature.custom_categories_products cp
            join eats_nomenclature.custom_categories c
            on cp.custom_category_id = c.id
            """,
        )
        return {(row[0], row[1]) for row in cursor}

    return do_sql_get_categories_products


@pytest.fixture(name='sql_get_categories_relations')
def _sql_get_categories_relations(pgsql):
    def do_sql_get_categories_relations():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select id, name
            from eats_nomenclature.custom_categories
            """,
        )
        id_to_name = {row[0]: row[1] for row in cursor}

        cursor.execute(
            f"""
            select custom_category_group_id,
                   custom_category_id,
                   parent_custom_category_id
            from eats_nomenclature.custom_categories_relations
            """,
        )
        return {
            (
                row[0],
                id_to_name[row[1]],
                id_to_name[row[2]] if row[2] else None,
            )
            for row in cursor
        }

    return do_sql_get_categories_relations


@pytest.fixture(name='sql_get_group')
def _sql_get_group(pgsql):
    def do_sql_get_group():
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select id, name, description, is_base, is_restaurant
            from eats_nomenclature.custom_categories_groups
            """,
        )
        return list(cursor)[0]

    return do_sql_get_group


class ProductSearchTestUtils:
    def __init__(self, load_json, update_taxi_config):
        self._load_json = load_json
        self._update_taxi_config = update_taxi_config

    def generate_expected_json(
            self, start_idx, end_idx, expected_limit, current_cursor,
    ):
        expected_data = self._load_json('full_response.json')

        expected_data['products'] = expected_data['products'][
            start_idx:end_idx
        ]
        if expected_data['products']:
            expected_data['cursor'] = expected_data['products'][-1]['cursor']
        else:
            expected_data['cursor'] = current_cursor
        for i in expected_data['products']:
            i.pop('cursor')
        expected_data['limit'] = expected_limit

        return expected_data

    def extract_categories_paths_from_response(
            self, response,
    ):  # pylint: disable=C0103
        categories_paths = []
        for product in response['products']:
            if 'categories_path' in product:
                categories_paths.append(product['categories_path'])
            else:
                categories_paths.append([])

        return categories_paths

    def set_brands_to_show_categories_in_admin(
            self, brands,
    ):  # pylint: disable=C0103
        self._update_taxi_config(
            'EATS_NOMENCLATURE_CATEGORIES_IN_ADMIN_SETTINGS',
            {'brands_to_show_categories_in_admin': brands},
        )

    def sorted_response(self, response):
        response['products'].sort(key=lambda k: k['id'])
        return response


@pytest.fixture
def product_search_test_utils(load_json, update_taxi_config):
    return ProductSearchTestUtils(load_json, update_taxi_config)
