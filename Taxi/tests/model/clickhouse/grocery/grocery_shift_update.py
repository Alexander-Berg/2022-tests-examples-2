import datetime
from mouse import Has
from libstall.model import coerces
from tests.model.clickhouse.base_model import TopicModel


STATUS_TYPE = [
    'open',       # курьер на смене
    'pause',      # курьер ушел на паузу
    'unpause',    # курьер вышел с паузы
    'close',      # курьер ушел со смены
]

class GroceryShiftUpdate(TopicModel):
    _timestamp = Has(
        types=datetime.datetime,
        required=False,
        coerce=coerces.date_time
    )
    timestamp = Has(
        types=datetime.datetime,
        required=False,
        coerce=coerces.date_time
    )
    depot_id = Has(types=str, required=True)
    shift_id = Has(types=str, required=True)
    performer_id = Has(types=str, required=True)
    status = Has(types=str, required=True, enum=STATUS_TYPE)

    @staticmethod
    def table_alias():
        return 'grocery_performer_shift_update'

    @classmethod
    def create_query(cls):
        return f'''
            CREATE TABLE IF NOT EXISTS `{cls.table_alias()}` (
                "_timestamp"    DateTime('UTC') NOT NULL,
                "timestamp"     DateTime('UTC'),
                "depot_id"      TEXT NOT NULL,
                "shift_id"      TEXT NOT NULL,
                "performer_id"  TEXT NOT NULL,
                "status"  TEXT NOT NULL
            ) ENGINE = MergeTree()
            ORDER BY ("depot_id")
        '''
