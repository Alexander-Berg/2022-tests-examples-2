INSERT INTO eats_moderation.moderation_queue (
    task_id, context_id, payload_id, created_at, tag
) VALUES (1, 1, 1, '2021-07-13 00:00+00'::TIMESTAMP, 'abc'),
         (2, 2, 2, '2021-07-07 00:00+00'::TIMESTAMP, 'abc'),
         (3, 1, 3, '2021-07-12 12:00+00'::TIMESTAMP, 'zxc'),
         (4, 2, 4, '2021-07-11 00:00+00'::TIMESTAMP, 'abc'),
         (5, 1, 5, '2021-07-01 00:00+00'::TIMESTAMP, 'zxc');

INSERT INTO eats_moderation.moderation (
    id, task_id, payload_id, status, moderator_id, created_at, tag, reasons
) VALUES (1, 1, 1, 'new', 13, '2021-07-13 00:00+00'::TIMESTAMP, 'abc', '{}'),
         (2, 2, 2, 'approved', 1, '2021-07-07 00:03+00'::TIMESTAMP, 'abc', '{}'),
         (3, 3, 3, 'rejected', 2, '2021-07-12 12:01+00'::TIMESTAMP, 'zxc', '{}'),
         (4, 4, 4, 'deleted', 2, '2021-07-13 00:00+00'::TIMESTAMP, 'abc', '{}'),
         (5, 5, 5, 'approved', 1, '2021-07-01 00:02+00'::TIMESTAMP, 'zxc', '{}');

INSERT INTO eats_moderation.payloads (
    payload_id, scope, queue, external_id, value
) VALUES (1, 'eda', 'restapp_moderation_category', 1, '{"scope": "eda", "queue": "restapp_moderation_category", "data": "qwerty"}'),
         (2, 'eda', 'restapp_moderation_category', 2, '{"scope": "eda", "queue": "restapp_moderation_category", "data": "qwerty"}'),
         (3, 'eda', 'restapp_moderation_menu', 3, '{"scope": "eda", "queue": "restapp_moderation_menu", "data": "qwerty"}'),
         (4, 'eda', 'restapp_moderation_menu', 4, '{"scope": "eda", "queue": "restapp_moderation_menu", "data": "qwerty"}'),
         (5, 'eda', 'restapp_moderation_hero', 5, '{"scope": "eda", "queue": "restapp_moderation_hero", "data": "qwerty"}');

INSERT INTO eats_moderation.contexts (
    context_id, value
) VALUES (1, '{}'),
         (2, '{}');

INSERT INTO eats_moderation.moderators (
    moderator_id, moderator_context
) VALUES (1, '{}'),
         (2, '{}'),
         (13, '{"moderator_id":"unknown"}');

