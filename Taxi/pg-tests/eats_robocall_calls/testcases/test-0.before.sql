INSERT INTO eats_robocall.calls
(id, call_external_id, ivr_flow_id, personal_phone_id, context, status, ivr_dispatcher_record_id, scenario, answers, updated_at)
VALUES
(1, 'call-1', 'eats_flow', 'id-1', '{}', 'waiting_for_call', 'record-1', '{}', array[]::varchar[], '2021-05-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
(2, 'call-2', 'eats_flow', 'id-2', '{}', 'waiting_for_call', 'record-2', '{}', array[]::varchar[], '2021-06-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
(3, 'call-3', 'eats_flow', 'id-3', '{}', 'waiting_for_call', 'record-3', '{}', array[]::varchar[], '2021-07-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
(4, 'call-4', 'eats_flow', 'id-4', '{}', 'waiting_for_call', 'record-4', '{}', array[]::varchar[], '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
