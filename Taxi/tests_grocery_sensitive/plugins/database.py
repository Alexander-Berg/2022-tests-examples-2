import json
from typing import List

import pytest

from .. import models

_UPSERT_DATA_SQL = """
INSERT INTO sensitive.data (
    entity_type,
    entity_id,
    request_id,
    yandex_uid,
    personal_phone_id,
    user_data,
    extra_data
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (entity_type, entity_id, request_id) DO UPDATE
    SET yandex_uid = excluded.yandex_uid,
        personal_phone_id = excluded.personal_phone_id,
        user_data = excluded.user_data,
        extra_data = excluded.extra_data
"""

_LOAD_DATA_SQL = """
SELECT
    entity_type,
    entity_id,
    request_id,
    yandex_uid,
    personal_phone_id,
    user_data,
    extra_data
FROM sensitive.data
WHERE entity_type = %s
  AND entity_id = %s
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_sensitive'].cursor()

    def upsert(self, *values):
        for value in values:
            if isinstance(value, models.SensitiveData):
                self.upsert_data(value)
            else:
                assert False, 'Unsupported type: ' + str(type(value))

    def upsert_data(self, data: models.SensitiveData):
        self.cursor().execute(
            _UPSERT_DATA_SQL,
            [
                data.entity_type,
                data.entity_id,
                data.request_id,
                data.yandex_uid,
                data.personal_phone_id,
                json.dumps(data.user_data),
                json.dumps(data.extra_data),
            ],
        )

    def load_data(
            self, entity_type: str, entity_id: str,
    ) -> List[models.SensitiveData]:
        cursor = self.cursor()
        cursor.execute(_LOAD_DATA_SQL, [entity_type, entity_id])

        return [models.SensitiveData(*it) for it in cursor]


@pytest.fixture(name='grocery_sensitive_db')
def grocery_sensitive_db(pgsql):
    return Database(pgsql)
