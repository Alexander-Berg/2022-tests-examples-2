INSERT INTO agent.departments (name,updated,created,key,parent) VALUES
('Яндекс',NOW(),NOW(),'yandex',null );


INSERT INTO agent.users (
    uid, created, login, first_name, last_name, en_first_name, en_last_name, join_at, quit_at, department, piece, country
)
VALUES
    (1120000000252888, NOW(), 'chief', 'chief', 'chief','chief','chief', '2016-06-02', NULL, 'yandex', NULL, 'ru'),
    (1120000000252889, NOW(), 'calltaxi_support', 'chief', 'chief','chief','chief', '2016-06-02', NULL, 'yandex', NULL, 'by');

INSERT INTO agent.departments_heads  (key,login,role) VALUES
('yandex','chief','chief');


INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('user_calltaxi',NOW(),'chief','user_calltaxi','user_calltaxi','user_calltaxi','user_calltaxi');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('calltaxi',NOW(),'chief','calltaxi','calltaxi','calltaxi','calltaxi',true);


INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('calltaxi','user_calltaxi',NOW(),'chief');


INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'chief','calltaxi'),
(NOW(),'calltaxi_support','calltaxi');


INSERT INTO agent.teams (key,name,en_name,permission) VALUES
('a_team','A-команда','A team','user_calltaxi');


UPDATE agent.users SET team='a_team' WHERE login='chief';
UPDATE agent.users SET team='a_team' WHERE login='calltaxi_support';


INSERT INTO agent.chatterbox_support_settings
(
    login,
    assigned_lines,
    languages
)
VALUES
('chief', '{line_1}', '{ru, en}'),
('calltaxi_support', '{}', '{en}');


INSERT INTO agent.chatterbox_lines_info
(
    line,
    line_tanker_key
)
VALUES
('line_1', 'line_1_name'),
('line_2', 'line_2_name'),
('null_tanker_key_line', NULL),
('line_4', 'line_4_name');


INSERT INTO agent.chatterbox_available_lines
(
    login,
    lines
)
VALUES
('chief', '{line_1, line_2}'),
('calltaxi_support', '{null_tanker_key_line, line_4}');
