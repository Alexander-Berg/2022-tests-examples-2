import json
from typing import List
from typing import Optional

import psycopg2.extras
import pytest

from .. import models

_UPSERT_JOB_SQL = """
INSERT INTO takeout.jobs (job_id,
                          job_type,
                          till_dt,
                          graph,
                          status,
                          anonym_id)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (job_id) DO UPDATE
    SET job_type = excluded.job_type,
        till_dt = excluded.till_dt,
        graph = excluded.graph,
        status = excluded.status,
        anonym_id = excluded.anonym_id
"""

_LOAD_JOB_SQL = """
SELECT job_id,
       job_type,
       till_dt,
       graph,
       status,
       anonym_id
FROM takeout.jobs
WHERE job_id = %s
"""

_UPSERT_JOB_ENTITY_TASK_SQL = """
INSERT INTO takeout.job_entity_tasks (job_id,
                                      entity_type,
                                      status,
                                      entity_ids,
                                      entity_ids_version)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (job_id, entity_type) DO UPDATE
    SET status = excluded.status,
        entity_ids = excluded.entity_ids,
        entity_ids_version = excluded.entity_ids_version
"""

_LOAD_JOB_ENTITY_TASK_SQL = """
SELECT job_id,
       entity_type,
       status,
       entity_ids,
       entity_ids_version
FROM takeout.job_entity_tasks
WHERE job_id = %s
  AND entity_type = %s
"""

_UPSERT_JOB_ENTITY_SQL = """
INSERT INTO takeout.job_entities (job_id,
                                  entity_type,
                                  entity_id,
                                  entity_data)
VALUES (%s, %s, %s, %s)
ON CONFLICT (job_id, entity_type, entity_id) DO UPDATE
    SET entity_data = excluded.entity_data
"""

_LOAD_JOB_ENTITY_SQL = """
SELECT job_id,
       entity_type,
       entity_id,
       entity_data
FROM takeout.job_entities
WHERE job_id = %s
  AND entity_type = %s
  AND entity_id = %s
"""

_LOAD_JOB_ENTITIES_SQL = """
SELECT job_id,
       entity_type,
       entity_id,
       entity_data
FROM takeout.job_entities
WHERE job_id = %s
  AND entity_type = %s
"""

_UPSERT_DELETE_REQUEST_SQL = """
INSERT INTO takeout.delete_requests (job_id,
                                     yandex_uids,
                                     user_ids,
                                     phone_ids,
                                     personal_phone_ids,
                                     personal_email_ids,
                                     status,
                                     created)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (job_id) DO UPDATE
    SET yandex_uids = excluded.yandex_uids,
        user_ids = excluded.user_ids,
        phone_ids = excluded.phone_ids,
        personal_phone_ids = excluded.personal_phone_ids,
        personal_email_ids = excluded.personal_email_ids,
        status = excluded.status,
        created = excluded.created
"""

_LOAD_DELETE_REQUEST_SQL = """
SELECT job_id,
       yandex_uids,
       user_ids,
       phone_ids,
       personal_phone_ids,
       personal_email_ids,
       status,
       created
FROM takeout.delete_requests
WHERE job_id = %s
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self, **kwargs):
        return self._pgsql['grocery_takeout'].cursor(**kwargs)

    def cursor_dict(self):
        return self.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def upsert(self, *values):
        for value in values:
            if isinstance(value, models.Job):
                self.upsert_job(value)
            elif isinstance(value, models.JobEntityTask):
                self.upsert_job_entity_task(value)
            elif isinstance(value, models.JobEntity):
                self.upsert_job_entity(value)
            elif isinstance(value, models.DeleteRequest):
                self.upsert_delete_request(value)
            else:
                assert False, 'Unsupported type: ' + str(type(value))

    def upsert_job(self, value: models.Job):
        self.cursor().execute(
            _UPSERT_JOB_SQL,
            [
                value.job_id,
                value.job_type,
                value.till_dt,
                json.dumps(value.graph.serialize()),
                value.status,
                value.anonym_id,
            ],
        )

    def load_job(self, job_id: str) -> Optional[models.Job]:
        cursor = self.cursor_dict()
        cursor.execute(_LOAD_JOB_SQL, [job_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.Job(
            job_id=result['job_id'],
            job_type=result['job_type'],
            till_dt=result['till_dt'],
            graph=models.EntityGraph.parse(result['graph']),
            status=result['status'],
            anonym_id=result['anonym_id'],
        )

    def upsert_job_entity_task(self, value: models.JobEntityTask):
        self.cursor().execute(
            _UPSERT_JOB_ENTITY_TASK_SQL,
            [
                value.job_id,
                value.entity_type,
                value.status,
                value.entity_ids,
                value.entity_ids_version,
            ],
        )

    def load_job_entity_task(
            self, job_id: str, entity_type: str,
    ) -> Optional[models.JobEntityTask]:
        cursor = self.cursor_dict()
        cursor.execute(_LOAD_JOB_ENTITY_TASK_SQL, [job_id, entity_type])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.JobEntityTask(**result)

    def upsert_job_entity(self, value: models.JobEntity):
        self.cursor().execute(
            _UPSERT_JOB_ENTITY_SQL,
            [
                value.job_id,
                value.entity_type,
                value.entity_id,
                json.dumps(value.entity_data),
            ],
        )

    def load_job_entity(
            self, job_id: str, entity_type: str, entity_id: str,
    ) -> Optional[models.JobEntity]:
        cursor = self.cursor_dict()
        cursor.execute(_LOAD_JOB_ENTITY_SQL, [job_id, entity_type, entity_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.JobEntity(**result)

    def load_job_entities(
            self, job_id: str, entity_type: str,
    ) -> List[models.JobEntity]:
        cursor = self.cursor_dict()
        cursor.execute(_LOAD_JOB_ENTITIES_SQL, [job_id, entity_type])

        return [models.JobEntity(**result) for result in cursor]

    def upsert_delete_request(self, value: models.DeleteRequest):
        self.cursor().execute(
            _UPSERT_DELETE_REQUEST_SQL,
            [
                value.job_id,
                value.yandex_uids,
                value.user_ids,
                value.phone_ids,
                value.personal_phone_ids,
                value.personal_email_ids,
                value.status,
                value.created,
            ],
        )

    def load_delete_request(
            self, job_id: str,
    ) -> Optional[models.DeleteRequest]:
        cursor = self.cursor_dict()
        cursor.execute(_LOAD_DELETE_REQUEST_SQL, [job_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.DeleteRequest(**result)


@pytest.fixture(name='grocery_takeout_db')
def grocery_takeout_db(pgsql):
    return Database(pgsql)
