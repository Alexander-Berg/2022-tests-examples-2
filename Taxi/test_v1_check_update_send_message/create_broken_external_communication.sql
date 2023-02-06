INSERT INTO crm_policy.entity_types (name) VALUES('user_id');
INSERT INTO crm_policy.entity_ids (type_id, entity_str) VALUES(1, 'test_reciever');
INSERT INTO crm_policy.channels (name) VALUES('fullscreen') ON CONFLICT(name) DO NOTHING;

INSERT INTO crm_policy.registered_external_communications (campaign_id, expire_time, expected_entity_type_id) VALUES('1', NOW() + ('12 hour')::interval, 1);
