INSERT INTO scenarios.action (id, description, text_tanker_key, client_callback, show_message_input, client_callback_params, conditions, is_enabled, always_merge)
VALUES ('action_1', null,  'text1', 'text', FALSE, '{}'::jsonb, null, TRUE, FALSE),
       ('action_2', null, 'text2', 'text', TRUE, '{"style": "italic"}'::jsonb, null, TRUE, FALSE),
       ('action_3', null, 'text3', 'call', TRUE, '{"style": "italic"}'::jsonb, null, TRUE, FALSE),
       ('action_4', 'Описание', 'text4', 'text', TRUE, '{}'::jsonb, null, TRUE, FALSE),
       ('disabled_action_5', 'Описание', 'text4', 'text', TRUE, '{}'::jsonb, null, TRUE, FALSE),
       ('always_merge_action_6', 'Описание', 'text2', 'text', FALSE, '{}'::jsonb, null, TRUE, TRUE);


INSERT INTO scenarios.actions_tree (parent_id, child_id, trigger_tanker)
VALUES
       ('action_1', 'action_2', 'scenarios.yes'),
       ('action_1', 'action_3', 'scenarios.no'),
       ('action_2', 'action_3', 'scenarios.yes'),
       ('action_2', 'action_4', 'scenarios.no');
