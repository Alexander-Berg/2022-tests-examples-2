INSERT INTO callcenter_queues.calls
(asterisk_call_id, routing_id, metaqueue, subcluster, status, last_event_at, call_guid, called_number, abonent_phone_id,
    queued_at, answered_at, completed_at, endreason, transfered_to_number, asterisk_agent_id, created_at)
VALUES
('1', '1', '1', '1', 'completed', now(), '1', '88005553535', '900', now(), now(), now(), 'abonent died', '14114', '1', now()),
('2', '2', '2', '2', 'completed', now(), '2', '666666', '900', now(), now(), now(), 'abonent resurrected', '010010', '2', now()),
('3', '3', '3', '3', 'completed', now(), '3', '3', '3', now(), now(), now(), '3', '3', '3', now()),
('4', '4', '4', '4', 'talking', now(), '4', '4', '4', now(), now(), NULL, NULL, '4', '4', now()),
('5', '5', '5', '5', 'talking', now(), '5', '5', '5', now(), now(), NULL, NULL, '5', '5', now()),
('6', '6', '6', '6', 'completed', now(), '6', '6', '6', now(), now(), now(), '6', '6', '6', now());

