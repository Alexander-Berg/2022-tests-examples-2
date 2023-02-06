import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import (
    TopicModel,
)

class WmsOrderStatusUpdated(TopicModel):
    company_id = Has(types=str, required=True)
    cluster_id = Has(types=str, required=True)
    head_supervisor_id = Has(types=str, required=False)
    supervisor_id = Has(types=str, required=False)

    store_id = Has(types=str, required=True)
    type = Has(types=str, required=True)
    order_id = Has(types=str, required=True)
    timestamp = Has(
        types=datetime.datetime,
        required=False,
        coerce=coerces.date_time
    )

    status = Has(types=str, required=True)
    estatus = Has(types=str, required=True)
    eda_status = Has(types=str, required=False)

    order_external_id = Has(types=str, required=False)
    store_external_id = Has(types=str, required=False)
    lsn = Has(types=int, required=False)
    source = Has(types=str, required=False)
    user_id = Has(types=str, required=False)
    courier_id = Has(types=str, required=False)
    courier_shift_id = Has(types=str, required=False)
    courier_delivery_type = Has(types=str, required=False)
    dispatch_delivery_type = Has(types=str, required=False)
    created_timestamp = Has(
        types=datetime.datetime,
        required=True,
        coerce=coerces.date_time
    )

    total_pause = Has(types=int, required=False, default=0)
    items_count = Has(types=int, required=False, default=0)
    items_uniq = Has(types=int, required=False, default=0)
    suggests_count = Has(types=int, required=False, default=0)

    @staticmethod
    def table_alias():
        return 'wms_order_status_updated'

    @classmethod
    def create_query(cls):
        return f'''
        CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
            "timestamp"                 DateTime('UTC'),
            "company_id"                String,
            "cluster_id"                String,
            "head_supervisor_id"        Nullable(String),
            "supervisor_id"             Nullable(String),

            "store_id"                  String,
            "type"                      String,
            "order_id"                  String,

            "status"                    String,
            "estatus"                   String,
            "eda_status"                Nullable(String),

            "order_external_id"         Nullable(String),
            "store_external_id"         Nullable(String),
            "lsn"                       Nullable(Int64),
            "source"                    Nullable(String),
            "user_id"                   Nullable(String),
            "courier_id"                Nullable(String),
            "courier_shift_id"          Nullable(String),
            "courier_delivery_type"     Nullable(String),
            "dispatch_delivery_type"    Nullable(String),
            "created_timestamp"         DateTime('UTC'),

            "total_pause"               Nullable(Int32),
            "items_count"               Nullable(Int32),
            "items_uniq"                Nullable(Int32),
            "suggests_count"            Nullable(Int32),

            "_topic"                    Nullable(String),
            "_rest"                     Nullable(String),
            "_timestamp"                Nullable(DateTime),
            "_partition"                Nullable(String),
            "_offset"                   Nullable(UInt64),
            "_idx"                      Nullable(UInt32)
        ) ENGINE = MergeTree()
        ORDER BY ("store_id", "type", "order_id", "timestamp")
        PARTITION BY toYYYYMM("timestamp")
    '''
