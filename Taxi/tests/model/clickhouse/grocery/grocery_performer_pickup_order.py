import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)


class GroceryOrderPickup(TopicModel):
    timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    order_id = Has(types=str, required=True)
    performer_id = Has(types=str, required=True)

    @staticmethod
    def table_alias():
        return 'grocery_performer_pickup_order'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"     DateTime('UTC') NOT NULL,
            "depot_id"      TEXT NOT NULL,
            "order_id"      TEXT NOT NULL,
            "performer_id"  TEXT NOT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''
