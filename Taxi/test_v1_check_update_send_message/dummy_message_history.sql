INSERT INTO crm_policy.entity_types (name) VALUES('user_id');
INSERT INTO crm_policy.entity_ids (type_id, entity_str) VALUES(1, 'test_reciever');

INSERT INTO crm_policy.registered_external_communications (id, campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES(1, '1', '', NOW() + ('12 hour')::interval, 1);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = '1'), '', '10 sec'::interval, ('2019-02-01 14:00:09')::timestamp,1);


INSERT INTO crm_policy.messages_history (big_key, entity_id, communication_id, send_at, channel_id) VALUES (4294967297, 1, 1, ('2019-02-01 13:59:59')::timestamp, 1);
INSERT INTO crm_policy.messages_history (big_key, entity_id, communication_id, send_at, channel_id) VALUES (4294967297, 1, 1, ('2019-02-01 13:59:59')::timestamp, 1);
INSERT INTO crm_policy.messages_history (big_key, entity_id, communication_id, send_at, channel_id) VALUES (4294967297, 1, 1, ('2019-02-01 13:50:59')::timestamp, 1);
