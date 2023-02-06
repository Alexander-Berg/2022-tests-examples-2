import copy
import json

from tests_eats_nomenclature_viewer import models


class SqlSetter:
    def __init__(self, pg_cursor):
        self.pg_cursor = pg_cursor

    def save(self, data):
        if isinstance(data, models.Product):
            return self._save_product(data)
        if isinstance(data, models.Brand):
            return self._save_brand(data)
        if isinstance(data, models.Place):
            return self._save_place(data)
        if isinstance(data, models.AssortmentName):
            return self._save_assortment_name(data)
        if isinstance(data, models.Assortment):
            return self._save_assortment(data)
        if isinstance(data, models.PlaceAssortment):
            return self._save_place_assortment(data)
        if isinstance(data, models.ProductUsage):
            return self._save_product_usage(data)
        if isinstance(data, models.PlaceAvailabilityFile):
            return self._save_place_availability_file(data)
        if isinstance(data, models.PlaceFallbackFile):
            return self._save_place_fallback_file(data)
        if isinstance(data, models.PlaceTaskStatus):
            return self._save_place_task_status(data)
        if isinstance(data, models.PlaceProductPrice):
            return self._save_place_product_price(data)
        if isinstance(data, models.PlaceProductVendorData):
            return self._save_place_product_vendor_data(data)
        if isinstance(data, models.PlaceProductStock):
            return self._save_place_product_stock(data)
        if isinstance(data, models.PlaceEnrichmentStatus):
            return self._save_place_enrichment_status(data)
        raise ValueError(f'Unsupported object type: {str(type(data))}')

    def _save_product(self, product: models.Product):
        product_dict = copy.deepcopy(product).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.products(
                nmn_id,
                brand_id,
                origin_id,
                sku_id,
                name,
                quantum,
                measure_unit,
                measure_value,
                updated_at
            )
            values(
                %(nmn_id)s,
                %(brand_id)s,
                %(origin_id)s,
                %(sku_id)s,
                %(name)s,
                %(quantum)s,
                %(measure_unit)s,
                %(measure_value)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(nmn_id) do nothing
        """,
            product_dict,
        )

        for product_attribute in product.product_attributes:
            self._save_product_attribute(
                product_nmn_id=product.nmn_id,
                product_attribute=product_attribute,
            )

        return product_dict['nmn_id']

    def _save_product_attribute(
            self, product_nmn_id, product_attribute: models.ProductAttribute,
    ):
        product_attribute_dict = copy.deepcopy(product_attribute).__dict__

        product_attribute_dict['attribute_id'] = self._save_attribute(
            product_attribute_dict['attribute'],
        )
        product_attribute_dict.pop('attribute')

        product_attribute_dict['attribute_value'] = json.dumps(
            product_attribute_dict['attribute_value'],
        )

        product_attribute_dict['product_nmn_id'] = product_nmn_id

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.product_attributes(
                product_nmn_id,
                attribute_id,
                attribute_value,
                updated_at
            )
            values(
                %(product_nmn_id)s,
                %(attribute_id)s,
                %(attribute_value)s::jsonb,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(product_nmn_id, attribute_id) do nothing
        """,
            product_attribute_dict,
        )

    def _save_attribute(self, attribute: models.Attribute):
        attribute_dict = copy.deepcopy(attribute).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            with ids as(
                insert into eats_nomenclature_viewer.attributes(
                    name,
                    updated_at
                )
                values(
                    %(name)s,
                    case
                        when %(updated_at)s is not null
                            then %(updated_at)s
                        else now()
                    end
                )
                on conflict(name) do nothing
                returning id
            )
            select id from ids
            union
            select id
            from eats_nomenclature_viewer.attributes
            where name=%(name)s
        """,
            attribute_dict,
        )

        return pg_cursor.fetchone()['id']

    def _save_brand(self, brand: models.Brand):
        brand_dict = copy.deepcopy(brand).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.brands(
                id,
                slug,
                name,
                is_enabled,
                updated_at
            )
            values(
                %(brand_id)s,
                %(slug)s,
                %(name)s,
                %(is_enabled)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(id) do nothing
        """,
            brand_dict,
        )

        return brand_dict['brand_id']

    def _save_place(self, place: models.Place):
        place_dict = copy.deepcopy(place).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.places(
                id,
                slug,
                brand_id,
                is_enabled,
                is_enabled_changed_at,
                stock_reset_limit,
                updated_at
            )
            values(
                %(place_id)s,
                %(slug)s,
                %(brand_id)s,
                %(is_enabled)s,
                case
                    when %(is_enabled_changed_at)s is not null
                        then %(is_enabled_changed_at)s
                    else now()
                end,
                %(stock_reset_limit)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(id) do nothing
        """,
            place_dict,
        )

        return place_dict['place_id']

    def _save_assortment_name(self, assortment_name: models.AssortmentName):
        assortment_name_dict = copy.deepcopy(assortment_name).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            with ids as(
                insert into eats_nomenclature_viewer.assortment_names(
                    name,
                    updated_at
                )
                values(
                    %(name)s,
                    case
                        when %(updated_at)s is not null
                            then %(updated_at)s
                        else now()
                    end
                )
                on conflict(name) do nothing
                returning id
            )
            select id from ids
            union
            select id
            from eats_nomenclature_viewer.assortment_names
            where name=%(name)s
        """,
            assortment_name_dict,
        )

        return pg_cursor.fetchone()['id']

    def _save_assortment(self, assortment: models.Assortment):
        assortment_dict = copy.deepcopy(assortment).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.assortments(
                id,
                updated_at,
                created_at
            )
            values(
                %(assortment_id)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end,
                case
                    when %(created_at)s is not null
                        then %(created_at)s
                    else now()
                end
            )
            on conflict(id) do nothing
            returning id
        """,
            assortment_dict,
        )

        return assortment_dict['assortment_id']

    def _save_place_assortment(self, place_assortment: models.PlaceAssortment):
        place_assortment_dict = copy.deepcopy(place_assortment).__dict__

        place_assortment_dict['assortment_name_id'] = self.save(
            place_assortment_dict['assortment_name'],
        )
        place_assortment_dict['active_assortment_id'] = (
            self.save(place_assortment_dict['active_assortment'])
            if place_assortment_dict['active_assortment']
            else None
        )
        place_assortment_dict['in_progress_assortment_id'] = (
            self.save(place_assortment_dict['in_progress_assortment'])
            if place_assortment_dict['in_progress_assortment']
            else None
        )

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_assortments(
                place_id,
                assortment_name_id,
                active_assortment_id,
                in_progress_assortment_id,
                updated_at
            )
            values(
                %(place_id)s,
                %(assortment_name_id)s,
                %(active_assortment_id)s,
                %(in_progress_assortment_id)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            place_assortment_dict,
        )

    def _save_place_enrichment_status(
            self, place_status: models.PlaceEnrichmentStatus,
    ):
        place_status_dict = copy.deepcopy(place_status).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_enrichment_statuses(
                place_id,
                are_prices_ready,
                are_stocks_ready,
                is_vendor_data_ready,
                updated_at
            )
            values(
                %(place_id)s,
                %(are_prices_ready)s,
                %(are_stocks_ready)s,
                %(is_vendor_data_ready)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            place_status_dict,
        )

    def _save_product_usage(self, product_usage: models.ProductUsage):
        product_usage_dict = copy.deepcopy(product_usage).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.product_usage(
                product_nmn_id,
                last_referenced_at,
                created_at,
                updated_at
            )
            values(
                %(product_nmn_id)s,
                case
                    when %(last_referenced_at)s is not null
                        then %(last_referenced_at)s
                    else now()
                end,
                case
                    when %(created_at)s is not null
                        then %(created_at)s
                    else now()
                end,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            product_usage_dict,
        )

    def _save_place_availability_file(
            self, availability_file: models.PlaceAvailabilityFile,
    ):
        availability_file_dict = copy.deepcopy(availability_file).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_availability_files(
                place_id,
                file_path,
                file_datetime,
                updated_at
            )
            values(
                %(place_id)s,
                %(file_path)s,
                case
                    when %(file_datetime)s is not null
                        then %(file_datetime)s
                    else now()
                end,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            availability_file_dict,
        )

    def _save_place_fallback_file(
            self, fallback_file: models.PlaceFallbackFile,
    ):
        fallback_file_dict = copy.deepcopy(fallback_file).__dict__
        fallback_file_dict['task_type'] = fallback_file_dict['task_type'].value

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_fallback_files(
                place_id,
                task_type,
                file_path,
                file_datetime,
                updated_at
            )
            values(
                %(place_id)s,
                %(task_type)s,
                %(file_path)s,
                case
                    when %(file_datetime)s is not null
                        then %(file_datetime)s
                    else now()
                end,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            fallback_file_dict,
        )

    def _save_place_task_status(self, task_status: models.PlaceTaskStatus):
        task_status_dict = copy.deepcopy(task_status).__dict__
        task_status_dict['task_type'] = task_status_dict['task_type'].value

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_task_statuses(
                place_id,
                task_type,
                task_started_at,
                task_is_in_progress,
                task_finished_at,
                updated_at
            )
            values(
                %(place_id)s,
                %(task_type)s,
                case
                    when %(task_started_at)s is not null
                        then %(task_started_at)s
                    else now()
                end,
                %(task_is_in_progress)s,
                %(task_finished_at)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            task_status_dict,
        )

    def _save_place_product_price(self, price: models.PlaceProductPrice):
        price_dict = copy.deepcopy(price).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_product_prices(
                place_id,
                product_nmn_id,
                price,
                old_price,
                full_price,
                old_full_price,
                vat,
                updated_at
            )
            values(
                %(place_id)s,
                %(product_nmn_id)s,
                %(price)s,
                %(old_price)s,
                %(full_price)s,
                %(old_full_price)s,
                %(vat)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            price_dict,
        )

    def _save_place_product_vendor_data(
            self, vendor_data: models.PlaceProductVendorData,
    ):
        vendor_data_dict = copy.deepcopy(vendor_data).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_product_vendor_data(
                place_id,
                product_nmn_id,
                vendor_code,
                position,
                updated_at
            )
            values(
                %(place_id)s,
                %(product_nmn_id)s,
                %(vendor_code)s,
                %(position)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            vendor_data_dict,
        )

    def _save_place_product_stock(self, stock: models.PlaceProductStock):
        stock_dict = copy.deepcopy(stock).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_nomenclature_viewer.place_product_stocks(
                place_id,
                product_nmn_id,
                value,
                updated_at
            )
            values(
                %(place_id)s,
                %(product_nmn_id)s,
                %(value)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
        """,
            stock_dict,
        )
