import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)


DELIVERY_TYPE = [
    'courier',         # Лавочный курьер
    'yandex_taxi',     # Доставка через такси
]


class GroceryOrderMatched(TopicModel):
    timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    performer_id = Has(types=str, required=True)
    order_id = Has(types=str, required=True)
    claim_id = Has(types=str, required=True)
    delivery_type = Has(types=str, required=False, enum=DELIVERY_TYPE)

    @staticmethod
    def table_alias():
        return 'grocery_order_matched'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"     DateTime('UTC') NOT NULL,
            "depot_id"      TEXT NOT NULL,
            "performer_id"  TEXT NOT NULL,
            "order_id"      TEXT NOT NULL,
            "claim_id"      TEXT NOT NULL,
            "delivery_type" TEXT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''
