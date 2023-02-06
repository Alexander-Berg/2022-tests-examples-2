INSERT INTO agent.chatterbox_support_settings
(
    login,
    assigned_lines,
    can_choose_from_assigned_lines,
    can_choose_except_assigned_lines,
    max_chats,
    languages,
    work_off_shift
)
VALUES
('regular_login','{line_1,line_2}',TRUE,TRUE,12,'{ru,en}',TRUE);

INSERT INTO auth_user
(id,username)
VALUES
(1,'regular_login'),
(2,'not_on_piece_login'),
(3,'disabled_login'),
(7,'login_with_minimum_info'),
(8,'absent_login'),
(9,'use_reserves_login'),
(10,'not_use_reserves_login');

INSERT INTO compendium_reserves
(user_id, "limit")
VALUES
(1,12),
(2,10),
(3,10),
(6,10),
(8,10),
(9,-10),
(10,-10);

INSERT INTO compendium_customuser
(
user_ptr_id,
max_tickets,
max_chats_chatterbox,
time_start,
time_end,
piece,
dis_tickets_off_shift,
disable_access_day,
work_department_id,
dismissed,
schedule_id,
tariff_piece_id
)
VALUES
(1,2,3,'12:00:00','13:00:00',TRUE,FALSE,'2022-06-04',1,FALSE,1,1),
(2,10,12,'11:00:00','15:00:00',FALSE,FALSE,'2022-06-04',1,FALSE,1,1),
(3,10,12,'12:00:00','13:00:00',TRUE,FALSE,'2020-06-04',1,FALSE,1,1),
(7,NULL,NULL,'12:00:00','13:00:00',TRUE,NULL,NULL,1,FALSE,1,1),
(8,10,12,'12:00:00','13:00:00',TRUE,FALSE,'2022-06-04',1,FALSE,1,1),
(9,2,3,'12:00:00','13:00:00',TRUE,FALSE,'2022-06-04',1,FALSE,1,1),
(10,2,3,'12:00:00','13:00:00',TRUE,FALSE,'2022-06-04',1,FALSE,1,1);

INSERT INTO compendium_work_department
(id, url)
VALUES
(1,'url_1');

INSERT INTO compendium_customuser_knows_languages
(customuser_id, users_languages_id)
VALUES
(1,1),
(2,1),
(2,2),
(3,1);

INSERT INTO compendium_users_languages
(id, code)
VALUES
(1,'ru'),
(2,'en');

INSERT INTO agent.absent_users
VALUES ('absent_login');

INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    en_first_name,
    en_last_name,
    join_at,
    department,
    piece
)
VALUES
(1120000000252888,NOW(),'regular_login','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'not_on_piece_login','text','text','text','text','2016-06-02',null,FALSE),
(1120000000252888,NOW(),'disabled_login','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'login_with_minimum_info','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'absent_login','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'not_compendium_user','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'returned_after_dismiss_user','text','text','text','text','2021-06-02',null,TRUE),
(1120000000252888,NOW(),'use_reserves_login','text','text','text','text','2016-06-02',null,TRUE),
(1120000000252888,NOW(),'not_use_reserves_login','text','text','text','text','2016-06-02',null,TRUE);

INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'regular_login',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'
);

INSERT INTO agent.teams (key,name,en_name,permission,use_reserves) VALUES
('use_reserves_team','team','team','user_calltaxi', TRUE),
('not_use_reserves_team','team','team','user_calltaxi', FALSE);

UPDATE agent.users SET team='use_reserves_team' WHERE login='use_reserves_login';
UPDATE agent.users SET team='not_use_reserves_team' WHERE login='not_use_reserves_login';

INSERT INTO agent.roles VALUES
(
 'calltaxi',
 '2021-01-01 00:00:00',
 null,
 'regular_login',
 'text',
 'text',
 'text',
 'text',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'regular_login'
);

INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
('2020-01-01 00:00:00','regular_login','calltaxi'),
('2020-01-01 00:00:00','not_on_piece_login','calltaxi'),
('2020-01-01 00:00:00','disabled_login','calltaxi'),
('2020-01-01 00:00:00','login_with_minimum_info','calltaxi'),
('2020-01-01 00:00:00','absent_login','calltaxi'),
('2020-01-01 00:00:00','not_compendium_user','calltaxi'),
('2020-01-01 00:00:00','returned_after_dismiss_user','calltaxi'),
('2020-01-01 00:00:00','use_reserves_login','calltaxi'),
('2020-01-01 00:00:00','not_use_reserves_login','calltaxi');

INSERT INTO agent.dismissed_users
(
login,
term_date,
created_at
)
VALUES
('regular_login','2022-06-03','2020-01-01 00:00:00'),
('not_on_piece_login','2022-06-03','2020-01-01 00:00:00'),
('disabled_login','2020-06-01','2020-01-01 00:00:00'),
('disabled_login','2020-06-03','2020-01-02 00:00:00'),
('absent_login','2022-06-04','2020-01-01 00:00:00'),
('returned_after_dismiss_user','2020-01-01','2020-01-01 00:00:00'),
('use_reserves_login','2022-05-25','2020-01-01 00:00:00'),
('not_use_reserves_login','2022-06-06', '2020-01-01 00:00:00');


INSERT INTO agent.chatterbox_available_lines (login,lines) VALUES ('regular_login','{line_1,line_2}')
