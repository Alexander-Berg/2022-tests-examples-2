INSERT INTO agent.departments (name,updated,created,key,parent) VALUES
('calltaxi',NOW(),NOW(),'calltaxi',null);

INSERT INTO agent.users (
    uid, created, login, first_name, last_name, en_first_name, en_last_name, join_at, quit_at, department, piece, country, piecework_half_time
)
VALUES
    (1120000000252890, NOW(), 'calltaxi_chief', 'first_name_1', 'last_name_1','en_first_name_1','en_last_name_1', '2016-06-02', NULL,'calltaxi', False, 'ru', NULL),
    (1120000000252890, NOW(), 'calltaxi_support', 'first_name_2', 'last_name_2','en_first_name_2', 'en_last_name_2', '2016-06-02', NULL,'calltaxi', True, NULL, NULL),
    (1120000000252890, NOW(), 'calltaxi_support_without_data', 'first_name_6', 'last_name_6','en_first_name_6', 'en_last_name_6', '2016-06-02', NULL,'calltaxi', False, NULL, NULL),
    (1120000000252890, NOW(), 'calltaxi_support_with_null_data', 'first_name_7', 'last_name_7','en_first_name_7', 'en_last_name_7', '2016-06-02', NULL,'calltaxi', False, NULL, NULL);


INSERT INTO agent.departments_heads  (key,login,role) VALUES
('calltaxi','calltaxi_chief','chief');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('calltaxi',NOW(),'calltaxi_chief','calltaxi','calltaxi','calltaxi','calltaxi',true);

INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'calltaxi_chief','calltaxi');
