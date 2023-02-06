INSERT INTO eats_robocall.calls
(id, call_external_id, ivr_flow_id, personal_phone_id, context, status, ivr_dispatcher_record_id, scenario, answers, updated_at)
VALUES
(3, 'call-3', 'eats_flow', 'id-3', '{}', 'waiting_for_call', 'record-3', '{}', array[]::varchar[], '2021-07-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
(4, 'call-4', 'eats_flow', 'id-4', '{}', 'waiting_for_call', 'record-4', '{}', array[]::varchar[], '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);

