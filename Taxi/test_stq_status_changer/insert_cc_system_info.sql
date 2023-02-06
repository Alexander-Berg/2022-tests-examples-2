INSERT INTO callcenter_queues.callcenter_system_info
(
    metaqueue,
    subcluster,
    enabled_for_call_balancing,
    enabled_for_sip_user_autobalancing,
    enabled
)
VALUES
    ('disp', 's1', true, true, true),
    ('disp', 's2', true, true, true),
    ('corp', 's3', true, true, true);

INSERT INTO callcenter_queues.routed_calls
(id, asterisk_call_id, created_at, call_guid, metaqueue, subcluster)
VALUES
    ('commutation_id_1', 'call_id_1', '2020-11-01T10:35:00.00Z', 'call_guid_1', 'disp', 's1');
-- to prefer second sub always
