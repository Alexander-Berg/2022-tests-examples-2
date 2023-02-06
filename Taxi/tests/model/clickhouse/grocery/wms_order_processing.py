import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)


class WmsOrderProcessing(TopicModel):
    timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    store_id = Has(types=str, required=True)
    order_id = Has(types=str, required=True)

    @staticmethod
    def table_alias():
        return 'wms_order_processing'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"     DateTime('UTC') NOT NULL,
            "depot_id"      TEXT NOT NULL,
            "store_id"      TEXT NOT NULL,
            "order_id"      TEXT NOT NULL
        ) ENGINE = MergeTree()
        ORDER BY ("timestamp")
    '''
