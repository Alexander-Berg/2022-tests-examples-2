INSERT INTO callcenter_qa.calls
(id, stq_started_at, stq_finished_at, call_id, call_guid, duration,
 in_operation_id, out_operation_id, in_text, in_words, out_text, out_words)
VALUES (
  'internalid2', '2021-07-16T10:00:00+03:00', null, 'call-id-01',
  '0000000001-0000000001-1625233862-0000000002', '00:01:00',
  'operation_1_in_not_found', 'operation_2_out', null, null, null, null
);
