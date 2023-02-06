INSERT INTO scenarios.action (id, description, text_tanker_key, client_callback, show_message_input, conditions)
VALUES ('action_1', null,  'text1', 'text', FALSE, null),
       ('action_2', null, 'text2', 'text', TRUE, null),
       ('action_3', null, 'text3', 'call', TRUE, null),
       ('action_4', 'Описание', 'text4', 'text', TRUE, null);


INSERT INTO scenarios.actions_tree (parent_id, child_id, trigger_tanker)
VALUES ('action_1', 'action_2', 'scenarios.yes'), ('action_1', 'action_3', 'scenarios.no');
