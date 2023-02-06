import copy

from . import models


class SqlSetter:
    def __init__(self, pg_cursor):
        self.pg_cursor = pg_cursor

    def save(self, data):  # pylint: disable=R1710
        if isinstance(data, models.Product):
            return self._save_product(data)
        if isinstance(data, models.Sku):
            return self._save_sku(data)
        if isinstance(data, models.Image):
            return self._save_image(data)
        if isinstance(data, models.Vendor):
            return self._save_vendor(data)
        if isinstance(data, models.ProductAttributes):
            return self._save_product_attributes(data)
        if isinstance(data, models.Category):
            return self._save_category(data)
        assert False, 'Unsupported object'

    def save_category_product(
            self, category_product: models.CategoryProduct, category_id: int,
    ):
        category_product_dict = copy.deepcopy(category_product).__dict__

        category_product_dict['product_id'] = self.save(
            category_product.product,
        )
        category_product_dict['category_id'] = category_id

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature.categories_products(
                assortment_id,
                product_id,
                category_id,
                sort_order
            )
            values(
                %(assortment_id)s,
                %(product_id)s,
                %(category_id)s,
                %(sort_order)s
            )
        """,
            category_product_dict,
        )

    def _save_category(self, category: models.Category):
        category_dict = copy.deepcopy(category).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            select id
            from eats_nomenclature.categories
            where public_id = %(public_id)s
              and assortment_id = %(assortment_id)s
        """,
            category_dict,
        )
        result = pg_cursor.fetchone()
        if result:
            # means that we've already traversed this category
            return result[0]

        pg_cursor.execute(
            """
            insert into eats_nomenclature.categories_dictionary(
                id,
                name
            )
            values(
                %(public_id)s,
                %(name)s
            )
        """,
            category_dict,
        )

        pg_cursor.execute(
            """
            insert into eats_nomenclature.categories(
                name,
                origin_id,
                assortment_id,
                public_id,
                is_custom,
                is_base
            )
            values(
                %(name)s,
                %(origin_id)s,
                %(assortment_id)s,
                %(public_id)s,
                %(is_custom)s,
                %(is_base)s
            )
            returning id
        """,
            category_dict,
        )
        category_dict['id'] = pg_cursor.fetchone()[0]

        if category.parent_category:
            category_dict['parent_id'] = self.save(category.parent_category)
        else:
            category_dict['parent_id'] = None

        pg_cursor.execute(
            """
            insert into eats_nomenclature.categories_relations(
                assortment_id,
                category_id,
                parent_category_id,
                sort_order
            )
            values(
                %(assortment_id)s,
                %(id)s,
                %(parent_id)s,
                %(sort_order)s
            )
        """,
            category_dict,
        )

        for picture_id in [self.save(i) for i in category_dict['images']]:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.category_pictures(
                    assortment_id,
                    category_id,
                    picture_id
                )
                values
                    (%s,%s,%s)
            """,
                (
                    category_dict['assortment_id'],
                    category_dict['id'],
                    picture_id,
                ),
            )

        for i in category.get_category_products():
            self.save_category_product(i, category_id=category_dict['id'])

        return category_dict['id']

    def _save_product(self, product: models.Product):
        product_dict = copy.deepcopy(product).__dict__

        measure_unit_to_id = {'GRM': 1, 'KGRM': 2, 'MLT': 4, 'LT': 3}
        product_dict['measure_unit_id'] = measure_unit_to_id[
            product.measure_unit
        ]

        if product_dict['sku']:
            product_dict['sku_id'] = self.save(product_dict['sku'])
        else:
            product_dict['sku_id'] = None

        if product_dict['use_sku_override'] and product_dict['sku_override']:
            product_dict['sku_override_id'] = self.save(
                product_dict['sku_override'],
            )
        else:
            product_dict['sku_override_id'] = None

        product_dict['vendor_id'] = self.save(product_dict['vendor'])

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature.products(
                origin_id,
                name,
                public_id,
                sku_id,
                description,
                shipping_type_id,
                vendor_id,
                quantum,
                measure_unit_id,
                measure_value,
                adult,
                is_catch_weight,
                is_choosable,
                brand_id
            )
            values(
                %(origin_id)s,
                %(name)s,
                %(public_id)s,
                %(sku_id)s,
                %(description)s,
                1,
                %(vendor_id)s,
                %(quantum)s,
                %(measure_unit_id)s,
                %(measure_value)s,
                %(is_adult)s,
                %(is_catch_weight)s,
                true,
                %(brand_id)s
            )
            returning id
        """,
            product_dict,
        )
        product_dict['id'] = pg_cursor.fetchone()[0]

        for picture_id in [self.save(i) for i in product_dict['images']]:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.product_pictures(
                    product_id,
                    picture_id
                )
                values
                    (%s,%s)
            """,
                (product_dict['id'], picture_id),
            )

        if product_dict['use_sku_override']:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.overriden_product_sku(
                    product_id,
                    sku_id
                )
                values
                    (%s,%s)
            """,
                (product_dict['id'], product_dict['sku_override_id']),
            )

        if product_dict['overriden_attributes']:
            product_dict.update(
                self.save(product_dict['overriden_attributes']),
            )
            pg_cursor.execute(
                """
                insert into eats_nomenclature.overriden_product_attributes(
                    product_id,
                    product_brand_id,
                    product_type_id
                )
                values (
                    %(id)s,
                    %(product_brand_id)s,
                    %(product_type_id)s
                )
            """,
                product_dict,
            )

        return product_dict['id']

    def _save_vendor(self, vendor: models.Vendor):
        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature.vendors (
                name,
                country
            )
            values
                (%(name)s, %(country)s)
            on conflict(name, country)
            do update set created_at=now()
            returning id
        """,
            vendor.__dict__,
        )

        return pg_cursor.fetchone()[0]

    def _save_sku(self, sku: models.Sku):
        sku_dict = copy.deepcopy(sku).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature.sku (
                uuid,
                alternate_name,
                composition,
                storage_requirements,
                weight,
                сarbohydrates,
                proteins,
                fats,
                calories,
                country,
                package_type,
                expiration_info,
                volume,
                is_alcohol,
                is_fresh,
                is_adult,
                fat_content,
                milk_type,
                cultivar,
                flavour,
                meat_type,
                carcass_part,
                egg_category
            )
            values (
                %(uuid)s,
                %(name)s,
                %(composition)s,
                %(storage_requirements)s,
                %(weight)s,
                %(сarbohydrates)s,
                %(proteins)s,
                %(fats)s,
                %(calories)s,
                %(country)s,
                %(package_type)s,
                %(expiration_info)s,
                %(volume)s,
                %(is_alcohol)s,
                %(is_fresh)s,
                %(is_adult)s,
                %(fat_content)s,
                %(milk_type)s,
                %(cultivar)s,
                %(flavour)s,
                %(meat_type)s,
                %(carcass_part)s,
                %(egg_category)s
            )
            on conflict(uuid) do update
            set updated_at=now()
            returning id
        """,
            sku_dict,
        )
        sku_dict['id'] = pg_cursor.fetchone()[0]

        for picture_id in [self.save(i) for i in sku_dict['images']]:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.sku_pictures(
                    sku_id,
                    picture_id
                )
                values
                    (%s,%s)
            """,
                (sku_dict['id'], picture_id),
            )

        if sku_dict['attributes']:
            sku_dict.update(self.save(sku_dict['attributes']))
            pg_cursor.execute(
                """
                insert into eats_nomenclature.sku_attributes(
                    sku_id,
                    product_brand_id,
                    product_type_id
                )
                values
                    (%(id)s,%(product_brand_id)s,%(product_type_id)s)
            """,
                sku_dict,
            )

        return sku_dict['id']

    def _save_image(self, image: models.Image):
        image_dict = copy.deepcopy(image).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature.pictures(
                url,
                processed_url
            )
            values
                (%(raw_url)s,%(processed_url)s)
            on conflict(url) do update
            set updated_at=now()
            returning id
        """,
            image_dict,
        )
        return pg_cursor.fetchone()[0]

    def _save_product_attributes(
            self, product_attributes: models.ProductAttributes,
    ):
        product_attributes_dict = copy.deepcopy(product_attributes).__dict__

        pg_cursor = self.pg_cursor

        if product_attributes_dict['brand']:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.product_brands(
                    value_uuid,
                    value
                )
                values
                    (%(brand)s,%(brand)s)
                on conflict(value_uuid) do update
                set updated_at=now()
                returning id
            """,
                product_attributes_dict,
            )
            product_brand_id = pg_cursor.fetchone()[0]
        else:
            product_brand_id = None

        if product_attributes_dict['type']:
            pg_cursor.execute(
                """
                insert into eats_nomenclature.product_types(
                    value_uuid,
                    value
                )
                values
                    (%(type)s,%(type)s)
                on conflict(value_uuid) do update
                set updated_at=now()
                returning id
            """,
                product_attributes_dict,
            )
            product_type_id = pg_cursor.fetchone()[0]
        else:
            product_type_id['type_id'] = None

        return {
            'product_brand_id': product_brand_id,
            'product_type_id': product_type_id,
        }
