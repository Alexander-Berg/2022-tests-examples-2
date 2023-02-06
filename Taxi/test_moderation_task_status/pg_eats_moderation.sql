INSERT INTO eats_moderation.contexts ( 
value 
) VALUES ('{"place_id":"1","partner_id":"23"}');



INSERT INTO eats_moderation.moderation_queue ( 
task_id,
context_id,
payload_id,
tag
) VALUES ('123', 1, 1, '1');


INSERT INTO eats_moderation.payloads ( 
scope, 
queue, 
external_id, 
value 
) VALUES ('eda', 'restapp_moderation_hero', NULL, '{"data":"qwerty"}');


INSERT INTO eats_moderation.moderators (
moderator_context
) VALUES ('Petrov');


INSERT INTO eats_moderation.moderation (
id,
task_id,
payload_id,
status,
reasons,
moderator_id,
tag
) VALUES ('456', '123', 1, 'process', '{}', 1, '1');
