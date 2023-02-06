import datetime
import typing

DB_NAME_TOLL_ROADS = 'toll_roads'


class DbTollRoads:
    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def _query_columns(self):
        return [desc[0] for desc in self.db_cursor.description]

    def save_order(
            self,
            order_id: str,
            created_at: datetime.datetime,
            can_switch_road: bool,
            offer_id: str,
            auto_payment: bool,
            price: typing.Optional[str],
            point_a: typing.Optional[str],
            point_b: typing.Optional[str],
    ) -> None:
        self.db_cursor.execute(
            f"""
            INSERT INTO toll_roads.orders
            (order_id, created_at, can_switch_road, offer_id,
            auto_payment)
            VALUES (
                '{order_id}', '{created_at}', {can_switch_road},
                '{offer_id}', '{auto_payment}'
            ) ON CONFLICT DO NOTHING
            """,
        )
        if price:
            self.db_cursor.execute(
                f"""
            INSERT INTO toll_roads.orders_prices (order_id, price)
            VALUES ('{order_id}', '{price}')
            ON CONFLICT DO NOTHING
            """,
            )
        if point_a:
            self.db_cursor.execute(
                f"""
            UPDATE toll_roads.orders SET point_a = '{point_a}'
            WHERE order_id = '{order_id}';
            """,
            )
        if point_b:
            self.db_cursor.execute(
                f"""
            UPDATE toll_roads.orders SET point_b = '{point_b}'
            WHERE order_id = '{order_id}';
            """,
            )

    def update_order(
            self,
            order_id: str,
            can_switch_road: bool,
            offer_id: str,
            price_limits: list,
    ) -> None:
        self.db_cursor.execute(
            f"""
            UPDATE toll_roads.orders
            SET can_switch_road = {can_switch_road}, offer_id = '{offer_id}',
            price_min_limit = '{price_limits[0]}',
            price_max_limit = '{price_limits[1]}'
            WHERE order_id = '{order_id}'
            """,
        )

    def get_order(self, order_id: str) -> dict:
        self.db_cursor.execute(
            f"""
            SELECT *
            FROM toll_roads.orders
            WHERE order_id = '{order_id}'
            """,
        )
        columns = [desc[0] for desc in self.db_cursor.description]
        rows = list(self.db_cursor)
        return [dict(zip(columns, row)) for row in rows][0]

    def get_order_price(self, order_id: str) -> dict:
        self.db_cursor.execute(
            f"""
            SELECT *
            FROM toll_roads.orders_prices
            WHERE order_id = '{order_id}'
            """,
        )
        columns = [desc[0] for desc in self.db_cursor.description]
        rows = list(self.db_cursor)
        return [dict(zip(columns, row)) for row in rows][0]

    def save_log(
            self,
            order_id: str,
            created_at: datetime.datetime,
            has_toll_road: bool,
    ) -> None:
        self.db_cursor.execute(
            f"""
            INSERT INTO toll_roads.log_has_toll_road
            (order_id, created_at, has_toll_road)
            VALUES ('{order_id}', '{created_at}', {has_toll_road})
            ON CONFLICT DO NOTHING
        """,
        )
