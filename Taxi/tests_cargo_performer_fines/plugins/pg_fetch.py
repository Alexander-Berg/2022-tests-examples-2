import dataclasses
from typing import List

import pytest


def recursive_dict(x):
    result_dict = {}
    for key, value in x.__dict__.items():
        if isinstance(value, List):
            result_dict[key] = [recursive_dict(i) for i in sorted(value)]
        elif '__dict__' in dir(value):
            result_dict[key] = recursive_dict(value)
        else:
            result_dict[key] = value
    return result_dict


@dataclasses.dataclass
class Cancellation:
    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    id_: int
    cancel_id: int
    cargo_order_id: str
    taxi_order_id: str
    park_id: str
    driver_id: str
    cargo_cancel_reason: str
    guilty: bool
    completed: bool
    free_cancellations_limit_exceeded: bool
    payload: dict


@pytest.fixture
def fetch_cancellation(pgsql):
    def fetch(where_condition):
        cursor = pgsql['cargo_performer_fines'].cursor()
        cursor.execute(
            f"""
            SELECT
                id,
                cancel_id,
                cargo_order_id,
                taxi_order_id,
                park_id,
                driver_id,
                cargo_cancel_reason,
                guilty,
                completed,
                free_cancellations_limit_exceeded,
                payload
            FROM cargo_performer_fines.cancellations WHERE {where_condition}
            """,
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(
                f'No cancellation found by condition {where_condition}',
            )
        return Cancellation(
            id_=row[0],
            cancel_id=row[1],
            cargo_order_id=row[2],
            taxi_order_id=row[3],
            park_id=row[4],
            driver_id=row[5],
            cargo_cancel_reason=row[6],
            guilty=row[7],
            completed=row[8],
            free_cancellations_limit_exceeded=row[9],
            payload=row[10],
        )

    return fetch


@dataclasses.dataclass
class PerformerStatistics:
    driver_id: str
    park_id: str
    completed_orders: int
    cancel_count: int


@pytest.fixture
def fetch_performer_statistics(pgsql):
    def fetch(where_condition):
        cursor = pgsql['cargo_performer_fines'].cursor()
        cursor.execute(
            f"""
            SELECT
                driver_id,
                park_id,
                completed_orders_count_after_last_cancellation,
                cancellation_count_after_last_reset
            FROM cargo_performer_fines.performer_statistics
            WHERE {where_condition}
            """,
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(
                f'No performer statistics found by condition '
                f'{where_condition}',
            )
        return PerformerStatistics(
            driver_id=row[0],
            park_id=row[1],
            completed_orders=row[2],
            cancel_count=row[3],
        )

    return fetch
