INSERT INTO eats_proactive_support.idempotency_tokens
(destination, token_sensitive, token_uuid)
VALUES
    ('eats_core_notification',
     'order_nr:111111-111111_action_id:100',
     'test_token_uuid_1');
