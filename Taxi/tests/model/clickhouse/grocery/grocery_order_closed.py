import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)


class GroceryOrderClosed(TopicModel):
    timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    order_id = Has(types=str, required=True)
    is_canceled = Has(types=int, required=True)
    cancel_reason_type = Has(types=str, required=False)
    cancel_reason_message = Has(types=str, required=False)

    @staticmethod
    def table_alias():
        return 'grocery_order_closed'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"             DateTime('UTC') NOT NULL,
            "depot_id"              TEXT NOT NULL,
            "order_id"              TEXT NOT NULL,
            "is_canceled"           BOOL NOT NULL,
            "cancel_reason_type"    TEXT NULL,
            "cancel_reason_message" TEXT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''
