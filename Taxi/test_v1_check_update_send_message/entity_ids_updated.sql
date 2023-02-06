INSERT INTO crm_policy.messages_history (big_key, entity_id, communication_id, send_at, channel_id, valid_till) VALUES (4294967297, 1, 1, (
    '2019-02-01 13:59:59')::timestamp, 1, ('2019-02-01 14:00:09')::timestamp);
update crm_policy.entity_ids set fullscreen_last_message_id = 3;
