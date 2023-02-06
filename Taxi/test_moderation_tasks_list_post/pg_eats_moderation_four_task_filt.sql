INSERT INTO eats_moderation.contexts ( 
value 
) VALUES ('{"place_id": 1234567}'),
         ('{"place_id": 7654321}');



INSERT INTO eats_moderation.moderation_queue ( 
task_id,
context_id,
payload_id,
tag,
created_at
) VALUES ('123', 1, 1, NULL,NOW() - interval '3 hour'),
         ('456', 2, 2, NULL,NOW() - interval '2 hour'),
         ('789', 1, 3, NULL,NOW() - interval '1 hour'),
         ('098', 2, 4, NULL,NOW());


INSERT INTO eats_moderation.payloads ( 
scope, 
queue, 
external_id, 
value 
) VALUES ('eda', 'restapp_moderation_hero', NULL, '{"data":"qwerty"}'),
         ('eda', 'restapp_moderation_hero', NULL, '{"data":"ytrewq"}'),
         ('eda', 'restapp_moderation_menu', NULL, '{"data":"asdfgh"}'),
         ('eda', 'restapp_moderation_menu', NULL, '{"data":"hgfdsa"}');


INSERT INTO eats_moderation.moderators (
moderator_context
) VALUES ('Petrov'),
         ('Ivanov');


INSERT INTO eats_moderation.moderation (
id,
task_id,
payload_id,
status,
reasons,
moderator_id,
tag
) VALUES ('456', '123', 1, 'process', '{}', 1, NULL),
         ('789', '456', 2, 'process', '{}', 2, NULL),
         ('012', '789', 3, 'process', '{}', 2, NULL),
         ('345', '098', 4, 'process', '{}', 1, NULL);
