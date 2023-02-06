INSERT INTO eats_moderation.contexts ( 
value 
) VALUES ('{"place_id": "1234567", "partner_id": "7654321"}');

INSERT INTO eats_moderation.moderation_queue ( 
task_id,
context_id,
payload_id,
tag
) VALUES ('123', 1, 1, '456');

INSERT INTO eats_moderation.payloads (
    scope,
    queue,
    external_id,
    value
) VALUES ('eda', 'restapp_moderation_hero', NULL, '{"data":"qwerty"}');
