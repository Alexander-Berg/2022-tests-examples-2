INSERT INTO supportai.roles (
    id,
    title,
    permissions
) VALUES
(1, 'Super Admin', '{}'),
(2, 'Project Admin', '{"read","write","modify"}'),
(3, 'Project Editor', '{"read","write"}'),
(4, 'Project Reader', '{"read"}');

INSERT INTO supportai.users (id, provider_id, login, is_active) VALUES
(1, 34, 'ya_user_1', TRUE),
(2, 35, 'ya_user_2', TRUE),
(3, '000000', 'ya_user_3', FALSE),
(4, '007', 'ya_user_4', TRUE),
(5, '12321', 'ya_user_5', FALSE);

INSERT INTO supportai.projects (id, slug, title, new_config_schema) VALUES
(1, 'ya_market', 'Маркет', False),
(2, 'ya_lavka', 'Лавка', True),
(3, 'ya_useless', 'Бесполезный проект', False);

ALTER SEQUENCE supportai.projects_id_seq RESTART WITH 4;

INSERT INTO supportai.user_to_role (user_id, role_id, project_slug) VALUES
(1, 3, 'ya_market'),
(1, 3, 'ya_lavka'),
(2, 2, 'ya_lavka'),
(2, 3, 'ya_market'),
(2, 3, 'ya_useless'),
(3, 4, 'ya_useless'),
(4, 1, NULL),
(5, 4, 'ya_lavka');

-- to avoid id collisions
ALTER SEQUENCE supportai.users_id_seq RESTART WITH 1000;


INSERT INTO supportai.capabilities (id, slug) VALUES
(1, 'topics'),
(2, 'features'),
(4, 'user_based'),
(5, 'su_user_based'),
(6, 'demo');

INSERT INTO supportai.presets (slug, title) VALUES
('test_preset', 'Test Preset'),
('awesome_preset', 'Awesome Preset'),
('pretty_awesome_preset', 'Pretty Awesome Preset');

INSERT INTO supportai.capabilities_presets (capability_slug, preset_id, type) VALUES
('topics', 1, 'allowed'),
('features', 1, 'allowed'),
('features', 2, 'blocked'),
('user_based', 2, 'allowed'),
('demo', 2, 'blocked'),
('topics', 3, 'allowed'),
('user_based', 3, 'allowed'),
('demo', 3, 'blocked');

ALTER SEQUENCE supportai.capabilities_id_seq RESTART WITH 1000;


INSERT INTO supportai.capabilities_to_project (capability_slug, project_slug, type) VALUES
('topics', NULL, 'allowed'),
('features', NULL, 'allowed'),
('features', 'ya_market', 'blocked'),
('demo', 'ya_lavka', 'allowed');

INSERT INTO supportai.capabilities_to_user (capability_slug, user_id, type) VALUES
('user_based', 1, 'allowed');

INSERT INTO supportai.capabilities_to_role (capability_slug, role_id, type) VALUES
('user_based', 3, 'allowed'),
('su_user_based', 1, 'allowed');

INSERT INTO supportai.tasks (id, project_id, type, created, file_id, name, status) VALUES
(7, 3, 'test_configuration', '2021-01-01 15:00:00+03', NULL, NULL, 'completed'),
(8, 2, 'test_configuration', '2021-01-01 15:00:00+03', NULL, NULL, 'completed'),
(9, 2, 'test_configuration', '2021-01-01 15:00:00+03', NULL, NULL, 'completed'),
(10, 1, 'clustering', '2021-01-01 15:00:00+03', NULL, NULL, 'completed'),
(11, 1, 'clustering', '2021-01-01 15:00:00+03', NULL, NULL, 'created'),
(12, 1, 'outgoing_calls_init', '2021-01-01 15:00:00+03', 1, NULL, 'created');

ALTER SEQUENCE supportai.tasks_id_seq RESTART WITH 13;

INSERT INTO supportai.configuration_test (id, task_id, request_text, is_equal, chat_id, diff) VALUES
(1, 7, 'Здравствуйте!', True, 1, NULL),
(2, 7, 'Спасибо!', False, 1, NULL),
(3, 7, 'Где мой заказ?', True, 1, NULL),
(4, 7, 'Здравствуйте!', True, 1, NULL),
(5, 7, 'Спасибо!', False, 1, NULL),
(6, 7, 'Где мой заказ?', True, 1, NULL),
(7, 7, 'Здравствуйте!', True, 1, NULL),
(8, 7, 'Спасибо!', False, 1, NULL),
(9, 7, 'Где мой заказ?', True, 1, NULL),
(10, 7, 'Здравствуйте!', True, 1, NULL),
(11, 7, 'Спасибо!', False, 1, NULL),
(12, 7, 'Где мой заказ?', True, 1, NULL),
(13, 8, 'Как оставить отзыв?', True, 1, NULL),
(14, 9, 'Дифф', False, NULL, '{"release": "{\"reply\": {\"text\": \"Здравствуйте!\"}}", "draft": "{\"reply\": {\"text\": \"Досвидания!\"}}"}');

ALTER SEQUENCE supportai.configuration_test_id_seq RESTART WITH 15;

INSERT INTO supportai.testing_aggregation (id,
                                           task_id,
                                           ok_chat_count,
                                           chat_count,
                                           equal_count,
                                           topic_ok_count_v1,
                                           topic_ok_count_v2,
                                           reply_count_v1,
                                           reply_count_v2,
                                           close_count_v1,
                                           close_count_v2,
                                           reply_or_close_count_v1,
                                           reply_or_close_count_v2,
                                           topic_details

) VALUES
(1, 7, 4, 10, 4, 2, 1, 8, 9, 7, 5, 10, 9, '{"topic_1": {"v1": 5, "v2": 6, "int_count": 4}}'),
(2, 8, 4, 20, 5, 4, 3, 8, 9, 7, 5, 10, 8, '{"topic_1": {"v1": 6, "v2": 1, "int_count": 0}}');

ALTER SEQUENCE supportai.configuration_test_id_seq RESTART WITH 3;

INSERT INTO supportai.files (id, project_id, filename, content_type, data) VALUES
(4242, 1, 'template_file_name', 'some_type', '\x00')
