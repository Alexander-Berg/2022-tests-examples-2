import copy

from tests_eats_retail_business_alerts import models


class SqlSetter:
    def __init__(self, pg_cursor):
        self.pg_cursor = pg_cursor

    def save(self, data):
        if isinstance(data, models.Brand):
            return self._save_brand(data)
        if isinstance(data, models.Place):
            return self._save_place(data)
        if isinstance(data, models.PlaceCancelledOrdersStats):
            return self._save_place_cancelled_orders_stats(data)
        if isinstance(data, models.PlaceCancelledOrdersStatsHistory):
            return self._save_place_cancelled_orders_stats_history(data)
        if isinstance(data, models.PlaceCreatedOrdersStats):
            return self._save_place_created_orders_stats(data)
        if isinstance(data, models.PlaceCreatedOrdersStatsHistory):
            return self._save_place_created_orders_stats_history(data)
        if isinstance(data, models.PlaceOrder):
            return self._save_place_order(data)
        if isinstance(data, models.Region):
            return self._save_region(data)
        raise ValueError(f'Unsupported object type: {str(type(data))}')

    def _save_brand(self, brand: models.Brand):
        brand_dict = copy.deepcopy(brand).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_retail_business_alerts.brands(
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
            insert into eats_retail_business_alerts.places(
                id,
                slug,
                name,
                brand_id,
                region_id,
                is_enabled,
                is_enabled_changed_at,
                updated_at
            )
            values(
                %(place_id)s,
                %(slug)s,
                %(name)s,
                %(brand_id)s,
                %(region_id)s,
                %(is_enabled)s,
                case
                    when %(is_enabled_changed_at)s is not null
                        then %(is_enabled_changed_at)s
                    else now()
                end,
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

    def _save_place_cancelled_orders_stats(
            self, place_stats: models.PlaceCancelledOrdersStats,
    ):
        place_stats_dict = copy.deepcopy(place_stats).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into
            eats_retail_business_alerts.places_cancelled_orders_stats(
                place_id,
                cancelled_by,
                orders_count,
                last_date_in_msc,
                updated_at
            )
            values(
                %(place_id)s,
                %(cancelled_by)s,
                %(orders_count)s,
                %(last_date_in_msc)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(place_id, cancelled_by) do nothing
            """,
            place_stats_dict,
        )

    def _save_place_cancelled_orders_stats_history(
            self, place_stats_history: models.PlaceCancelledOrdersStatsHistory,
    ):
        place_stats_history_dict = copy.deepcopy(place_stats_history).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into
            eats_retail_business_alerts.places_cancelled_orders_stats_history(
                place_id,
                cancelled_by,
                orders_count,
                last_date_in_msc,
                id,
                updated_at
            )
            values(
                %(place_id)s,
                %(cancelled_by)s,
                %(orders_count)s,
                %(last_date_in_msc)s,
                %(record_id)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(id) do nothing
            """,
            place_stats_history_dict,
        )
        pg_cursor.execute(
            f"""
            alter sequence
            eats_retail_business_alerts.places_cancelled_orders_stats_history_id_seq
            restart with {place_stats_history.record_id + 1}
            """,
        )

    def _save_place_created_orders_stats(
            self, place_stats: models.PlaceCreatedOrdersStats,
    ):
        place_stats_dict = copy.deepcopy(place_stats).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into
            eats_retail_business_alerts.places_created_orders_stats(
                place_id,
                orders_count,
                last_date_in_msc,
                updated_at
            )
            values(
                %(place_id)s,
                %(orders_count)s,
                %(last_date_in_msc)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(place_id) do nothing
            """,
            place_stats_dict,
        )

    def _save_place_created_orders_stats_history(
            self, place_stats_history: models.PlaceCreatedOrdersStatsHistory,
    ):
        place_stats_history_dict = copy.deepcopy(place_stats_history).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into
            eats_retail_business_alerts.places_created_orders_stats_history(
                place_id,
                orders_count,
                last_date_in_msc,
                id,
                updated_at
            )
            values(
                %(place_id)s,
                %(orders_count)s,
                %(last_date_in_msc)s,
                %(record_id)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(id) do nothing
            """,
            place_stats_history_dict,
        )
        pg_cursor.execute(
            f"""
            alter sequence
            eats_retail_business_alerts.places_created_orders_stats_history_id_seq
            restart with {place_stats_history.record_id + 1}
            """,
        )

    def _save_place_order(self, place_order: models.PlaceOrder):
        place_order_dict = copy.deepcopy(place_order).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_retail_business_alerts.places_orders(
                place_id,
                order_nr,
                updated_at
            )
            values(
                %(place_id)s,
                %(order_nr)s,
                case
                    when %(updated_at)s is not null
                        then %(updated_at)s
                    else now()
                end
            )
            on conflict(order_nr) do nothing
            """,
            place_order_dict,
        )

    def _save_region(self, region: models.Region):
        region_dict = copy.deepcopy(region).__dict__

        pg_cursor = self.pg_cursor
        pg_cursor.execute(
            """
            insert into eats_retail_business_alerts.regions(
                id,
                slug,
                name,
                is_enabled,
                updated_at
            )
            values(
                %(region_id)s,
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
            region_dict,
        )

        return region_dict['region_id']
