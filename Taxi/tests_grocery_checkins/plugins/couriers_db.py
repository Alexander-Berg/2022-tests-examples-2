import dataclasses
import typing

import pytest

SELECT_ALL_SQL = """
SELECT
    courier_id,
    logistic_group,
    checkin_timestamp,
    excluded_from_queue,
    depot_id,
    excluded_shift_from_queue,
    last_pause_timestamp,
    paused_shift_id
FROM grocery_checkins.couriers
"""

INSERT_SQL = """
INSERT INTO grocery_checkins.couriers (
    courier_id,
    logistic_group,
    checkin_timestamp,
    excluded_from_queue,
    depot_id,
    excluded_shift_from_queue,
    last_pause_timestamp,
    paused_shift_id
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


@dataclasses.dataclass
class CourierInfo:
    courier_id: str
    logistic_group: str
    checkin_timestamp: str
    excluded_from_queue: bool
    depot_id: typing.Optional[str]
    excluded_shift_from_queue: typing.Optional[str]
    last_pause_timestamp: typing.Optional[str]
    paused_shift_id: typing.Optional[str]


@pytest.fixture(name='couriers_db')
def couriers_db(pgsql):
    class Context:
        def __init__(self, pg):
            self.pg_db = pg['grocery_checkins']

        def add_entry(
                self,
                courier_id,
                logistic_group,
                checkin_timestamp,
                excluded_from_queue=False,
                depot_id=None,
                excluded_shift_from_queue=None,
                last_pause_timestamp=None,
                paused_shift_id=None,
        ):
            cursor = self.pg_db.cursor()
            cursor.execute(
                INSERT_SQL,
                [
                    courier_id,
                    logistic_group,
                    checkin_timestamp,
                    excluded_from_queue,
                    depot_id,
                    excluded_shift_from_queue,
                    last_pause_timestamp,
                    paused_shift_id,
                ],
            )

        def load_all_couriers(self):
            cursor = self.pg_db.cursor()
            cursor.execute(SELECT_ALL_SQL)

            return list(
                map(
                    lambda pg_tuple: CourierInfo(*pg_tuple), cursor.fetchall(),
                ),
            )

    return Context(pgsql)
