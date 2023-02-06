INSERT INTO crm_policy.entity_types (name) VALUES('user_id');
INSERT INTO crm_policy.entity_ids (type_id, entity_str) VALUES(1, 'test_reciever');

INSERT INTO crm_policy.channels (name) VALUES('fullscreen') ON CONFLICT(name) DO NOTHING;

INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('1', '', NOW() + ('12 hour')::interval, 1);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
  VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = '1'), '', '2160 hour'::interval, ('2019-02-01 14:00:09')::timestamp,1);

CREATE TABLE crm_policy.messages_history_12_27 ( CHECK (valid_till >= '2020-12-27 00:00:00' AND valid_till < '2020-12-28 00:00:00') ) inherits (crm_policy.messages_history);
INSERT INTO crm_policy.messages_history_12_27 (big_key, entity_id, communication_id, send_at, channel_id, valid_till) VALUES (4294967297, 1, 1, ('2020-09-28 02:09:13')::timestamp, 1, '2020-12-27 02:09:13');


INSERT INTO crm_policy.round_tables (head) VALUES(0);
