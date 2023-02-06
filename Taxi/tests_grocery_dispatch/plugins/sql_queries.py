INSERT_EXTRA_SQL = """
INSERT INTO dispatch.dispatches_extra_info (
    dispatch_id,
    eta_timestamp,
    smoothed_eta_timestamp,
    smoothed_eta_eval_time,
    result_eta_timestamp,
    heuristic_polyline_eta_ts,
    performer_position,
    pickup_eta_seconds,
    deliver_prev_eta_seconds,
    deliver_current_eta_seconds,
    smoothed_heuristic_eval_time,
    smoothed_heuristic_eta_ts
)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT(dispatch_id) DO UPDATE SET
   eta_timestamp=EXCLUDED.eta_timestamp,
   smoothed_eta_timestamp=EXCLUDED.smoothed_eta_timestamp,
   smoothed_eta_eval_time=EXCLUDED.smoothed_eta_eval_time,
   result_eta_timestamp=EXCLUDED.result_eta_timestamp,
   heuristic_polyline_eta_ts=EXCLUDED.heuristic_polyline_eta_ts,
   performer_position=EXCLUDED.performer_position,
   pickup_eta_seconds=EXCLUDED.pickup_eta_seconds,
   deliver_prev_eta_seconds=EXCLUDED.deliver_prev_eta_seconds,
   deliver_current_eta_seconds=EXCLUDED.deliver_current_eta_seconds,
   smoothed_heuristic_eval_time=EXCLUDED.smoothed_heuristic_eval_time,
   smoothed_heuristic_eta_ts=EXCLUDED.smoothed_heuristic_eta_ts;
"""

UPDATE_EXTRA_SQL = """
UPDATE dispatch.dispatches_extra_info SET
   eta_timestamp = %(eta_timestamp)s,
   smoothed_eta_timestamp = %(smoothed_eta_timestamp)s,
   smoothed_eta_eval_time = %(smoothed_eta_eval_time)s,
   result_eta_timestamp = %(result_eta_timestamp)s,
   heuristic_polyline_eta_ts = %(heuristic_polyline_eta_ts)s,
   performer_position = %(performer_position)s,
   pickup_eta_seconds = %(pickup_eta_seconds)s,
   deliver_prev_eta_seconds = %(deliver_prev_eta_seconds)s,
   deliver_current_eta_seconds = %(deliver_current_eta_seconds)s,
   smoothed_heuristic_eval_time = %(smoothed_heuristic_eval_time)s,
   smoothed_heuristic_eta_ts = %(smoothed_heuristic_eta_ts)s
WHERE dispatch_id = %(dispatch_id)s
;
"""

INSERT_DISPATCHES_SQL = """
INSERT INTO  dispatch.dispatches (
   id,
   order_id,
   performer_id,
   dispatch_type,
   version,
   status,
   status_updated,
   order_info,
   performer_info,
   status_meta,
   wave,
   eta
)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
;
"""

UPDATE_DISPATCHES_SQL = """
UPDATE dispatch.dispatches SET
   order_id = %(order_id)s,
   performer_id = %(performer_id)s,
   dispatch_type = %(dispatch_type)s,
   status = %(status)s,
   status_updated = %(status_updated)s,
   order_info = %(order_info)s,
   performer_info = %(performer_info)s,
   status_meta = %(status_meta)s,
   wave = %(wave)s,
   eta = %(eta)s,
   version = version + 1
WHERE id = %(dispatch_id)s
;
"""

SELECT_DISPATCHES_SQL = """
SELECT
    id,
    dispatch_type,
    version,
    status,
    status_updated,
    order_info,
    performer_info,
    status_meta,
    wave,
    eta,
    failure_reason_type
FROM  dispatch.dispatches
WHERE id = %s
;
"""

SELECT_EXTRA_SQL = """
SELECT
    dispatch_id,
    eta_timestamp,
    smoothed_eta_timestamp,
    smoothed_eta_eval_time,
    result_eta_timestamp,
    heuristic_polyline_eta_ts,
    performer_position,
    pickup_eta_seconds,
    deliver_prev_eta_seconds,
    deliver_current_eta_seconds,
    smoothed_heuristic_eval_time,
    smoothed_heuristic_eta_ts
FROM dispatch.dispatches_extra_info
WHERE dispatch_id = %s
;
"""

INSERT_CARGO_CLAIM_SQL = f"""
INSERT INTO dispatch.cargo_dispatches (
   dispatch_id,
   claim_id,
   is_current_claim,
   claim_status,
   claim_version,
   auth_token_key,
   wave,
   order_location
)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
;
"""

SELECT_DISPATCHES_HISTORY_UPDATED_SQL = """
SELECT * FROM  dispatch.dispatches_history
WHERE id=%s
ORDER BY updated;
"""

DELETE_DISPATCHES_SQL = """
DELETE FROM dispatch.dispatches
WHERE id = %s
;
"""

GET_CARGO_CLAIM_BY_CLAIM_ID_SQL = """
SELECT
    dispatch_id,
    claim_id,
    is_current_claim,
    claim_status,
    claim_version,
    auth_token_key,
    wave,
    order_location
FROM dispatch.cargo_dispatches
WHERE claim_id = %s
;
"""

GET_RESCHEDULE_STATE = """
SELECT
    dispatch_id,
    idempotency_token,
    wave,
    options,
    status
FROM dispatch.reschedule_state
WHERE dispatch_id = %s
;
"""
