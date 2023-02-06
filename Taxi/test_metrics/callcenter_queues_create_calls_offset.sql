INSERT INTO callcenter_queues.calls
(asterisk_call_id,
 routing_id  ,
 metaqueue   ,
 subcluster ,
 status ,
 last_event_at  ,
 call_guid ,
 called_number,
 abonent_phone_id ,
 queued_at,
 answered_at,
 completed_at ,
 endreason ,
 transfered_to_number ,
 asterisk_agent_id)
VALUES
    ('51', '51', 'queue', '3', 'completed', '2020-06-22T08:04:57.00Z', NULL, NULL, NULL, '2020-06-22T08:04:55.00Z', '2020-06-22T08:04:56.00Z', '2020-06-22T08:04:57.00Z', 'completed_by_caller','2020-06-22T08:04:59.00Z', NULL), -- included w/o offset
    ('52', '52', 'queue', '3', 'completed', '2020-06-22T08:04:57.00Z', NULL, NULL, NULL, '2020-06-22T08:04:43.00Z', '2020-06-22T08:04:45.00Z', '2020-06-22T08:04:47.00Z', 'completed_by_caller', '2020-06-22T08:04:49.00Z', NULL), -- included
    ('53', '53', 'queue', '3', 'completed', '2020-06-22T08:04:57.00Z', NULL, NULL, NULL, '2020-06-22T08:03:51.00Z', '2020-06-22T08:03:54.00Z', '2020-06-22T08:03:57.00Z', 'completed_by_caller', '2020-06-22T08:03:59.00Z', NULL)  -- included w offset

