import json
import uuid

import psycopg2.extras


import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.models as models


def ids_to_pg_list(ids):
    if ids is None:
        return None
    psycopg2.extras.register_uuid()
    result = list()
    for id in ids:
        result.append(uuid.UUID(id))
    return result


def insert_send_events_requests(pgsql, req):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
            INSERT INTO bank_notifications.send_events_requests (
            req_id, consumer, idempotency_token, bank_uid,
            events, status_code, code, message, event_ids)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING req_id, consumer, idempotency_token, bank_uid,
            events, status_code, code, message, event_ids, created_at
        """
    cursor.execute(
        sql,
        (
            req.req_id,
            req.consumer,
            req.idempotency_token,
            req.bank_uid,
            json.dumps([ev.to_json() for ev in req.events]),
            req.status_code,
            req.code,
            req.message,
            ids_to_pg_list(req.event_ids),
        ),
    )
    return [models.SendEventsRequest(*it) for it in cursor]


def select_send_events_requests(pgsql):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
        SELECT req_id, consumer, idempotency_token, bank_uid,
        events, status_code, code, message, event_ids, created_at
        FROM bank_notifications.send_events_requests
        """
    cursor.execute(sql)
    return [models.SendEventsRequest(*it) for it in cursor]


def insert_event(pgsql, event):
    cursor = pgsql['bank_notifications'].cursor()
    title_tanker_args = (
        json.dumps(event.title_tanker_args)
        if event.title_tanker_args is not None
        else None
    )
    description_tanker_args = (
        json.dumps(event.description_tanker_args)
        if event.description_tanker_args is not None
        else None
    )
    payload = json.dumps(event.payload) if event.payload is not None else None

    sql = """
            INSERT INTO bank_notifications.events (
            event_id, bank_uid, req_id, event_type, defaults_group,
            priority, title, description, action, merge_key, merge_status,
            experiment, title_tanker_args,
            description_tanker_args, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s)
            RETURNING event_id, bank_uid, req_id, event_type,
            defaults_group,  priority, title, description, action,
            merge_key, created_at, payload
            """
    cursor.execute(
        sql,
        (
            event.event_id,
            event.bank_uid,
            event.req_id,
            event.event_type,
            event.defaults_group,
            event.priority,
            event.title,
            event.description,
            event.action,
            event.merge_key,
            event.merge_status,
            event.experiment,
            title_tanker_args,
            description_tanker_args,
            payload,
        ),
    )
    return [models.Event(*it) for it in cursor]


def select_events(pgsql, buid):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
            SELECT event_id, bank_uid, req_id, created_at, event_type,
            defaults_group, priority, title, description, action,
            merge_key, merge_status, experiment, title_tanker_args,
            description_tanker_args, payload
            FROM bank_notifications.events
            WHERE bank_uid = %s
            ORDER BY cursor_key
        """
    cursor.execute(sql, [buid])
    return [models.Event(*it) for it in cursor]


def insert_mark_events_requests(pgsql, req):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
            INSERT INTO bank_notifications.mark_events_requests (
            req_id, initiator_type, initiator_id, idempotency_token,
            bank_uid, event_type, event_ids, mark_type,
            status_code, code, message, merge_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING req_id, initiator_type, initiator_id,
            idempotency_token, bank_uid, event_type, event_ids,
            mark_type, status_code, code, message, created_at, merge_key
        """
    cursor.execute(
        sql,
        (
            req.req_id,
            req.initiator_type,
            req.initiator_id,
            req.idempotency_token,
            req.bank_uid,
            req.event_type,
            ids_to_pg_list(req.event_ids),
            req.mark_type,
            req.status_code,
            req.code,
            req.message,
            req.merge_key,
        ),
    )
    return [models.MarkEventsRequest(*it) for it in cursor]


def select_mark_events_requests(pgsql):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
            SELECT req_id, initiator_type, initiator_id, idempotency_token,
            bank_uid, event_type, event_ids, mark_type, status_code, code,
            message, created_at, merge_key
            FROM bank_notifications.mark_events_requests
            """
    cursor.execute(sql)
    return [models.MarkEventsRequest(*it) for it in cursor]


def select_marks(pgsql, buid):
    cursor = pgsql['bank_notifications'].cursor()
    sql = """
            SELECT mark_id, bank_uid, req_id, created_at,
            mark_type, event_id
            FROM bank_notifications.marks
            WHERE bank_uid = %s
        """
    cursor.execute(sql, [buid])
    return [models.Mark(*it) for it in cursor]


def insert_mark(pgsql, buid, event_id, mark_type='READ'):
    cursor = pgsql['bank_notifications'].cursor()
    req_id = defaults.gen_uuid()
    sql = """
                INSERT INTO bank_notifications.marks (
                bank_uid, req_id, event_id, mark_type)
                VALUES(%s, %s, %s, %s)
                RETURNING mark_id
           """
    cursor.execute(sql, (buid, req_id, event_id, mark_type))
    return list(cursor)
