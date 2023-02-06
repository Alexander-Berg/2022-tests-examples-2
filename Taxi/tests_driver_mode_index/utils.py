import datetime
import json
from typing import Any
from typing import Dict
from typing import Optional


def execute_query(query, pgsql):
    pg_cursor = pgsql['driver_mode_index'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


def execute(query, pgsql, parameters=None):
    pg_cursor = pgsql['driver_mode_index'].cursor()
    pg_cursor.execute(query, parameters)


def databases_states(pgsql):
    index = execute_query(
        """SELECT
        park_id,
        driver_profile_id,
        external_ref,
        modes.mode as mode,
        mode_settings,
        billing_mode,
        billing_mode_rule,
        to_char (event_at, 'YYYY-MM-DD"T"HH24:MI:SS'),
        to_char (billing_synced_at, 'YYYY-MM-DD"T"HH24:MI:SS'),
        to_char (updated, 'YYYY-MM-DD"T"HH24:MI:SS'),
        is_active,
        source,
        reason,
        mode_properties.properties as properties
    FROM dmi.documents
    INNER JOIN dmi.modes
    ON modes.mode_id = documents.mode_id
    LEFT JOIN dmi.mode_properties
    ON mode_properties.properties_id = documents.properties_id""",
        pgsql,
    )

    return index if index is not None else []


def databases_states_with_id(pgsql):
    index = execute_query(
        """SELECT
        id,
        park_id,
        driver_profile_id,
        external_ref,
        modes.mode as mode,
        mode_settings,
        billing_mode,
        billing_mode_rule,
        to_char (event_at, 'YYYY-MM-DD"T"HH24:MI:SS'),
        to_char (billing_synced_at, 'YYYY-MM-DD"T"HH24:MI:SS'),
        to_char (updated, 'YYYY-MM-DD"T"HH24:MI:SS'),
        is_active
    FROM dmi.documents
    INNER JOIN dmi.modes
    ON modes.mode_id = documents.mode_id""",
        pgsql,
    )

    return index if index is not None else []


def validate_items_count_in_db(indexed_drivers, pgsql):
    index_db = databases_states(pgsql)

    assert len(index_db) == indexed_drivers

    return index_db


def get_items_count_in_db_with_id(indexed_drivers, pgsql):
    index_db = databases_states_with_id(pgsql)

    assert len(index_db) == indexed_drivers

    return index_db


def driver_exists_in_db(park_id, driver_profile_id, pgsql):
    found_in_db = execute_query(
        f"""SELECT * FROM dmi.documents
        WHERE park_id='{park_id}'
        AND driver_profile_id='{driver_profile_id}';""",
        pgsql,
    )
    return len(found_in_db) > 0


def validate_properties_table_size(count, pgsql):
    res = execute_query(
        """SELECT
        COUNT(*)
    FROM dmi.mode_properties""",
        pgsql,
    )
    assert res[0][0] == count


def insert_values(
        pgsql,
        park_id,
        driver_profile_id,
        external_ref,
        work_mode,
        mode_settings,
        billing_mode,
        billing_mode_rule,
        event_at,
        billing_synced_at,
        updated,
        replicated=False,
        source=None,
        reason=None,
        mode_properties=None,
):
    insert_query_mode = (
        """INSERT INTO dmi.modes (
            mode
        ) VALUES (\'{mode}\')
        ON CONFLICT(mode)
        DO UPDATE SET mode = EXCLUDED.mode
        RETURNING mode_id;
        """.format(
            mode=work_mode,
        )
    )

    mode_id = execute_query(insert_query_mode, pgsql)

    properties_id = None
    if mode_properties:
        insert_query_properties = f"""INSERT INTO dmi.mode_properties (
                    properties
                ) VALUES ({mode_properties})
                ON CONFLICT(properties)
                DO UPDATE SET properties = EXCLUDED.properties
                RETURNING properties_id;
                """

        properties_id = execute_query(insert_query_properties, pgsql)

    insert_query = """INSERT INTO dmi.documents (
                            park_id,
                            driver_profile_id,
                            external_ref,
                            mode_id,
                            mode_settings,
                            billing_mode,
                            billing_mode_rule,
                            event_at,
                            billing_synced_at,
                            updated,
                            is_replicated,
                            source,
                            reason,
                            properties_id
                        ) VALUES (
                            %(park_id)s,
                            %(driver_profile_id)s,
                            %(external_ref)s,
                            %(mode_id)s,
                            %(mode_settings)s,
                            %(billing_mode)s,
                            %(billing_mode_rule)s,
                            %(event_at)s,
                            %(billing_synced_at)s,
                            %(updated)s,
                            %(is_replicated)s,
                            %(source)s,
                            %(reason)s,
                            %(properties_id)s
                        );
                        """

    parameters = dict(
        park_id=park_id,
        driver_profile_id=driver_profile_id,
        external_ref=external_ref,
        mode_id=mode_id[0][0],
        mode_settings=mode_settings,
        billing_mode=billing_mode,
        billing_mode_rule=billing_mode_rule,
        event_at=event_at,
        billing_synced_at=billing_synced_at,
        updated=updated,
        is_replicated=replicated,
        source=(source if source else None),
        reason=(reason if reason else None),
        properties_id=(properties_id if properties_id else None),
    )

    execute(insert_query, pgsql, parameters)


class TestData:
    id_ = 1

    def __init__(
            self,
            park_id: str,
            driver_id: str,
            event_at: datetime.datetime,
            updated_at: datetime.datetime,
            created_at: datetime.datetime,
            billing_synced_at: Optional[datetime.datetime],
            external_ref: str,
            work_mode: str,
            settings: Dict[str, str],
            billing_mode: Optional[str] = None,
            billing_mode_rule: Optional[str] = None,
            is_active: bool = True,
            source: Optional[str] = None,
            reason: Optional[str] = None,
            mode_properties: Optional[list] = None,
    ):
        self.id_ = TestData._get_id()
        self.park_id = park_id
        self.driver_id = driver_id
        self.event_at = event_at
        self.updated_at = updated_at
        self.created_at = created_at
        self.billing_synced_at = billing_synced_at
        self.external_ref = external_ref
        self.settings = settings
        self.work_mode = work_mode
        self.is_active = is_active
        self.billing_mode = billing_mode
        self.billing_mode_rule = billing_mode_rule
        self.source = source
        self.reason = reason
        self.mode_properties = mode_properties

    @staticmethod
    def _get_id():
        id_ = TestData.id_
        TestData.id_ = TestData.id_ + 1
        return id_

    def add_to_pgsql(self, pgsql):
        insert_values(
            pgsql,
            self.park_id,
            self.driver_id,
            self.external_ref,
            self.work_mode,
            json.dumps(self.settings) if self.settings is not None else None,
            self.billing_mode,
            self.billing_mode_rule,
            self.event_at.strftime('%Y-%m-%d %H:%M:%S%z'),
            (
                '\''
                + self.billing_synced_at.strftime('%Y-%m-%d %H:%M:%S%z')
                + '\''
            )
            if self.billing_synced_at
            else None,
            self.updated_at.strftime('%Y-%m-%d %H:%M:%S%z'),
            False,
            self.source,
            self.reason,
            self.mode_properties,
        )

    def as_billing_report_entry(self, use_old_format: bool = False):
        response: Dict[str, Any] = {
            'doc_id': self.id_,
            'kind': 'driver_mode_subscription',
            'external_obj_id': 'taxi/driver_mode_subscription/park_id_0/uuid',
            'external_event_ref': self.external_ref,
            'event_at': self.event_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'process_at': self.event_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'service': 'test',
            'service_user_id': 'some_id',
            'data': {
                'driver': {
                    'park_id': self.park_id,
                    'driver_id': self.driver_id,
                },
                'mode': self.billing_mode,
                'settings': self.settings,
            },
            'created': self.created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'status': 'complete',
            'tags': ['test_tag'],
        }

        if not use_old_format:
            response['data']['subscription'] = {'driver_mode': self.work_mode}

        if self.source and self.reason:
            if use_old_format:
                response['data']['subscription'] = {}

            response['data']['subscription']['source'] = self.source
            response['data']['subscription']['source'] = self.reason

        return response

    def as_history_entry(self):
        response: Dict[str, Any] = {
            'data': {
                'driver': {
                    'driver_profile_id': self.driver_id,
                    'park_id': self.park_id,
                },
                'mode': self.work_mode,
                'settings': self.settings,
            },
            'event_at': self.event_at.isoformat(),
            'external_event_ref': self.external_ref,
        }

        if self.source and self.reason:
            response['data']['subscription_data'] = {
                'source': self.source,
                'reason': self.reason,
            }

        return response

    def as_billing_orders_response(self):
        response: Dict[str, Any] = {
            'doc_id': self.id_,
            'kind': 'driver_mode_subscription',
            'data': {
                'driver': {
                    'park_id': self.park_id,
                    'driver_id': self.driver_id,
                },
                'mode': self.billing_mode,
                'settings': self.settings,
            },
            'external_ref': self.external_ref,
            'topic': 'topic',
            'event_at': self.event_at.isoformat(),
            'created': self.event_at.isoformat(),
        }

        if self.source and self.reason:
            response['data']['subscription'] = {
                'source': self.source,
                'reason': self.reason,
            }

        return response

    def as_mode_subscribe_request(self):
        response: Dict[str, Any] = {
            'event_at': self.event_at.isoformat(),
            'external_ref': self.external_ref,
            'data': {
                'driver': {
                    'driver_profile_id': self.driver_id,
                    'park_id': self.park_id,
                },
                'work_mode': self.work_mode,
                'settings': self.settings,
                'billing_settings': {
                    'mode': self.billing_mode,
                    'mode_rule': self.billing_mode_rule,
                },
            },
        }

        if self.source and self.reason:
            response['data']['subscription_data'] = {
                'source': self.source,
                'reason': self.reason,
            }

        if self.mode_properties:
            response['data']['mode_properties'] = self.mode_properties

        return response

    def as_mode_subscribe_response(self):
        response: Dict[str, Any] = {
            'data': {
                'driver': {
                    'driver_profile_id': self.driver_id,
                    'park_id': self.park_id,
                },
                'work_mode': self.work_mode,
                'settings': self.settings,
                'billing_settings': {
                    'mode': self.billing_mode,
                    'mode_rule': self.billing_mode_rule,
                },
            },
            'event_at': self.event_at.isoformat(),
            'external_ref': self.external_ref,
        }

        if self.source and self.reason:
            response['data']['subscription_data'] = {
                'source': self.source,
                'reason': self.reason,
            }

        return response

    def as_db_row(self, not_yet_synced=False, include_billing=False):
        return (
            self.park_id,
            self.driver_id,
            self.external_ref,
            self.work_mode,
            self.settings,
            self.billing_mode if include_billing else None,
            self.billing_mode_rule if include_billing else None,
            self.event_at.strftime('%Y-%m-%dT%H:%M:%S'),
            self.billing_synced_at.strftime('%Y-%m-%dT%H:%M:%S')
            if self.billing_synced_at and not not_yet_synced
            else None,
            self.updated_at.strftime('%Y-%m-%dT%H:%M:%S'),
            self.is_active,
            self.source,
            self.reason,
            self.mode_properties,
        )


def get_config(
        billing_sync_enabled: bool = True,
        billing_sync_job: Optional[Dict[str, Any]] = None,
        cleanup_job: Optional[Dict[str, Any]] = None,
        replication_job: Optional[Dict[str, Any]] = None,
):
    return {
        'enabled': True,
        'billing_sync_enabled': billing_sync_enabled,
        'billing_sync_job': billing_sync_job or (
            {'enabled': False, 'batch_size': 100}
        ),
        'cleanup_job': cleanup_job or (
            {
                'enabled': False,
                'delete_after': 3600,
                'batch_size': 1,
                'delete_limit': 4,
            }
        ),
        'replication_job': replication_job or (
            {
                'enabled': False,
                'batch_size': 100,
                'replication_batch_size': 100,
            }
        ),
        'metrics_job': {'enabled': False},
    }
