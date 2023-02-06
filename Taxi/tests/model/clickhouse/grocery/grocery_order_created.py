import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)


DELIVERY_TYPE = [
    'pickup',         # Забор клиентом из лавки
    'dispatch',       # Стандартный grocery-dispatch
    'rover',          # Доставка ровером
]


class GroceryOrderCreated(TopicModel):
    timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    order_id = Has(types=str, required=True)
    max_eta = Has(types=int, required=True)
    delivery_type = Has(types=str, required=True, enum=DELIVERY_TYPE)

    @staticmethod
    def table_alias():
        return 'grocery_order_created'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"     DateTime('UTC') NOT NULL,
            "depot_id"      TEXT NOT NULL,
            "order_id"      TEXT NOT NULL,
            "max_eta"       INT NOT NULL,
            "delivery_type" TEXT NOT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''
