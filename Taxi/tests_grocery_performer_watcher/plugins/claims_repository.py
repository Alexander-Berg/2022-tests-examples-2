# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from dataclasses import dataclass, field
from typing import Optional

import psycopg2
import pytest


@dataclass
class Claim:
    claim_id: str
    waybill_ref: str
    version: int


class ClaimsRepository:
    def __init__(self, pgsql):
        self._cursor = pgsql['grocery_performer_watcher'].cursor(
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def add(self, claim: Claim) -> None:
        self._cursor.execute(
            'INSERT into performer_watcher.claims(claim_id, waybill_ref, version) '
            'VALUES (%s, %s, %s) '
            'ON CONFLICT (claim_id) DO UPDATE SET '
            'waybill_ref = excluded.waybill_ref, '
            'version = excluded.version ',
            (claim.claim_id, claim.waybill_ref, claim.version),
        )

    def fetch_by_claim_id(self, claim_id: str) -> Optional[Claim]:
        self._cursor.execute(
            'SELECT claim_id, waybill_ref, version '
            'FROM performer_watcher.claims '
            'WHERE claim_id = %s',
            (claim_id,),
        )
        row = self._cursor.fetchone()
        if row is None:
            return None
        return Claim(
            claim_id=row['claim_id'],
            waybill_ref=row['waybill_ref'],
            version=row['version'],
        )


@pytest.fixture(name='claims')
def claims_(pgsql):
    return ClaimsRepository(pgsql)
