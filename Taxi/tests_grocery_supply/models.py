import dataclasses
from typing import List
from typing import Optional

UPSERT_COURIER_SQL = """
INSERT INTO supply.couriers (courier_id,
                             full_name,
                             courier_transport_type,
                             courier_service_id,
                             phone_id,
                             inn_id,
                             billing_client_id,
                             billing_type,
                             eats_region_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (courier_id)  DO UPDATE
SET full_name = EXCLUDED.full_name,
    courier_transport_type = EXCLUDED.courier_transport_type,
    courier_service_id = EXCLUDED.courier_service_id,
    phone_id = EXCLUDED.phone_id,
    inn_id = EXCLUDED.inn_id,
    billing_client_id = EXCLUDED.billing_client_id,
    billing_type = EXCLUDED.billing_type,
    eats_region_id = EXCLUDED.eats_region_id
"""

UPSERT_COURIER_SERVICE_SQL = """
INSERT INTO supply.courier_services (
    courier_service_id,
    name,
    address,
    ogrn,
    work_schedule,
    inn,
    vat)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (courier_service_id)  DO UPDATE
    SET name = EXCLUDED.name,
        address = EXCLUDED.address,
        ogrn = EXCLUDED.ogrn,
        work_schedule = EXCLUDED.work_schedule,
        inn = EXCLUDED.inn,
        vat = EXCLUDED.vat
"""

LOG_LOGISTIC_GROUP_SQL = """
INSERT INTO supply.logistic_groups (depot_id, logistic_group_id)
VALUES
(%s, %s)
;
"""

DEFAULT_DEPOT_ID = '101010'
LOGISTIC_GROUP = 'test_lg_id'


@dataclasses.dataclass
class CourierService:
    courier_service_id: int
    name: str
    address: Optional[str]
    ogrn: Optional[str]
    work_schedule: Optional[str]
    inn: Optional[str]
    vat: Optional[int]
    pg_db: Optional[str]

    def __post_init__(self):
        self.save()

    def save(self):
        if self.pg_db is None:
            return
        cursor = self.pg_db.cursor()
        cursor.execute(
            UPSERT_COURIER_SERVICE_SQL,
            (
                self.courier_service_id,
                self.name,
                self.address,
                self.ogrn,
                self.work_schedule,
                self.inn,
                self.vat,
            ),
        )


@dataclasses.dataclass
class Courier:
    courier_id: str
    courier_transport_type: str
    full_name: Optional[str]
    courier_service: Optional[CourierService]
    phone_id: Optional[str]
    inn_id: Optional[str]
    billing_client_id: Optional[str]
    billing_type: Optional[str]
    eats_region_id: Optional[str]
    pg_db: str

    def __post_init__(self):
        self.save()

    def save(self):
        if self.pg_db is None:
            return
        cursor = self.pg_db.cursor()
        cursor.execute(
            UPSERT_COURIER_SQL,
            (
                self.courier_id,
                self.full_name,
                self.courier_transport_type,
                self.courier_service.courier_service_id
                if self.courier_service
                else None,
                self.phone_id,
                self.inn_id,
                self.billing_client_id,
                self.billing_type,
                self.eats_region_id,
            ),
        )


@dataclasses.dataclass
class LogisticGroup:
    def __init__(
            self,
            pgsql,
            logistic_group=LOGISTIC_GROUP,
            depot_id=DEFAULT_DEPOT_ID,
    ):
        self.pg_db = pgsql['grocery_supply']
        cursor = self.pg_db.cursor()
        cursor.execute(LOG_LOGISTIC_GROUP_SQL, [depot_id, logistic_group])
        self.depot_id = depot_id
        self.logistic_group = logistic_group


@dataclasses.dataclass
class LogisticGroupResponse:
    group_id: int
    places: List[int]
    meta_group_id: str


class LogisticGroupsErrorResponse:
    pass
