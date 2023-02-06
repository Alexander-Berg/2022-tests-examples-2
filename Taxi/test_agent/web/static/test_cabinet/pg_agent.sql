INSERT INTO agent.departments (name,updated,created,key,parent) VALUES
('outstaff',NOW(),NOW(),'outstaff',null ),
('Яндекс',NOW(),NOW(),'yandex',null ),
('Яндекс.Такси',NOW(),NOW(),'yandex_taxi','yandex'),
('calltaxi',NOW(),NOW(),'calltaxi',null),
('directsupport',NOW(),NOW(),'directsupport',null),
('comdelivery',NOW(),NOW(),'comdelivery',null),
('lavkasupport',NOW(),NOW(),'lavkasupport',null),
('internationaltaxi',NOW(),NOW(),'internationaltaxi',null),
('taxisupport_cc',NOW(),NOW(),'taxisupport_cc',null),
('bo_reserve',NOW(),NOW(),'bo_reserve',null);


INSERT INTO agent.users (
    uid, created, login, first_name, last_name, en_first_name, en_last_name, join_at, quit_at, department, piece, country, piecework_half_time
)
VALUES
    (1120000000252888, NOW(), 'slon', 'Василий', 'Слон','Vasily','Slon', '2016-06-02', NULL, null, NULL, NULL, NULL),
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов','Vasily','Mihaylov', '2016-06-02', NULL, 'yandex_taxi', NULL, NULL, NULL),
    (1120000000252888, NOW(), 'justmark0', 'Марк', 'Николсон','Mark','Nicholson', '2016-06-02', NULL, 'bo_reserve', True, NULL, NULL),
    (1120000000252888, NOW(), 'support_taxi_user', 'first_name_12', 'last_name_12','first_name_12_en','last_name_12_en', '2016-06-02', NULL, 'bo_reserve', True, NULL, NULL),
    (1120000000252888, NOW(), 'cargo_callcenter_user', 'first_name_13', 'last_name_13','first_name_13_en','last_name_13_en', '2016-06-02', NULL, 'bo_reserve', True, NULL, NULL),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов','Alexandr','Ivanov', '2016-06-02', NULL, 'yandex_taxi', NULL, NULL, NULL),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина','Ann','Kozhevina', '2016-06-02', NULL, 'yandex', NULL, NULL, NULL),
    (1120000000252889, NOW(), 'unholy', 'Нияз', 'Наибулин','Niyaz','Naibulin', '2016-06-02', '2020-06-02', 'yandex', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'orangevl', 'Семён', 'Решетняк','Simon','Reshetnyak', '2016-06-02', NULL,'yandex', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'vasin', 'Илья', 'Васин','Ilya','Vasin', '2016-06-02', NULL,'outstaff', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'pirozhochek', 'Дмитрий', 'Бобров','Dmitry','Bobrov', '2016-06-02', NULL,'outstaff', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'nlo', 'Владимир', 'Владимиров','Vladimir','Vladimirov', '2016-06-02', NULL,'outstaff', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'katya', 'Катя', 'Белкина','Kate','Belkina', '2016-06-02', NULL,'outstaff', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'valera', 'Валера', 'Левин','Valery','Levin', '2016-06-02', NULL,'outstaff', NULL, 'en', FALSE),
    (1120000000252890, NOW(), 'vavan', 'Владимир', 'Николаев','Vladimir','Nikolaev', '2016-06-02', NULL,'outstaff', NULL, NULL, NULL),
    (1120000000252890, NOW(), 'calltaxi_chief', 'first_name_1', 'last_name_1','en_first_name_1','en_last_name_1', '2016-06-02', NULL,'calltaxi', False, 'ru', NULL),
    (1120000000252890, NOW(), 'calltaxi_support', 'first_name_2', 'last_name_2','en_first_name_2', 'en_last_name_2', '2016-06-02', NULL,'calltaxi', True, NULL, NULL),
    (1120000000252890, NOW(), 'directsupport_chief', 'first_name_3', 'last_name_3','first_name_3','last_name_3', '2016-06-02', NULL,'directsupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'directsupport_support', 'first_name_4', 'last_name_4','first_name_4', 'last_name_4', '2016-06-02', NULL,'directsupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'directsupport_support_without_data', 'first_name_5', 'last_name_5','first_name_5', 'last_name_5', '2016-06-02', NULL,'directsupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'comdelivery_chief', 'first_name_9', 'last_name_9','first_name_9','last_name_9', '2016-06-02', NULL,'comdelivery', False, 'ru', NULL),
    (1120000000252890, NOW(), 'comdelivery_support1', 'first_name_11', 'last_name_11','first_name_11','last_name_11', '2016-06-02', NULL,'comdelivery', False, 'ru', NULL),
    (1120000000252890, NOW(), 'calltaxi_support_without_data', 'first_name_6', 'last_name_6','en_first_name_6', 'en_last_name_6', '2016-06-02', NULL,'calltaxi', False, NULL, NULL),
    (1120000000252890, NOW(), 'calltaxi_support_with_null_data', 'first_name_7', 'last_name_7','en_first_name_7', 'en_last_name_7', '2016-06-02', NULL,'calltaxi', False, NULL, NULL),
    (1120000000252890, NOW(), 'directsupport_support_with_null_data', 'first_name_8', 'last_name_8','first_name_8', 'last_name_8', '2016-06-02', NULL,'directsupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'comdelivery_support_with_null_data', 'first_name_10', 'last_name_10','first_name_10', 'last_name_10', '2016-06-02', NULL,'comdelivery', False, NULL, NULL),
    (1120000000252890, NOW(), 'lavkasupport_chief', 'lavkasupport_chief', 'lavkasupport_chief','lavkasupport_chief', 'lavkasupport_chief', '2016-06-02', NULL,'lavkasupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'taxisupport_cc_user', 'taxisupport_cc_user', 'taxisupport_cc_user','taxisupport_cc_user', 'taxisupport_cc_user', '2016-06-02', NULL,'taxisupport_cc', False, NULL, NULL),
    (1120000000252890, NOW(), 'taxisupport_cc_chief', 'taxisupport_cc_chief', 'taxisupport_cc_chief','taxisupport_cc_chief', 'taxisupport_cc_chief', '2016-06-02', NULL,'taxisupport_cc', False, NULL, NULL),
    (1120000000252890, NOW(), 'lavkasupport_user', 'lavkasupport_user', 'lavkasupport_user','lavkasupport_user', 'lavkasupport_user', '2016-06-02', NULL,'lavkasupport', False, NULL, NULL),
    (1120000000252890, NOW(), 'internationaltaxi_chief', 'internationaltaxi_chief', 'internationaltaxi_chief','internationaltaxi_chief', 'internationaltaxi_chief', '2016-06-02', NULL,'internationaltaxi', False, NULL, NULL),
    (1120000000252890, NOW(), 'internationaltaxi_user', 'internationaltaxi_user', 'internationaltaxi_user','internationaltaxi_user', 'internationaltaxi_user', '2016-06-02', NULL,'internationaltaxi', False, NULL, NULL),
    (1120000000252890,NOW(),'superuser','superuser','superuser','superuser','superuser','2020-01-01',null,null,false,'ru',false);


INSERT INTO agent.departments_heads  (key,login,role) VALUES
('yandex','orangevl','chief'),
('outstaff','vasin','chief'),
('calltaxi','calltaxi_chief','chief'),
('directsupport','directsupport_chief','chief'),
('comdelivery','comdelivery_chief','chief'),
('lavkasupport','lavkasupport_chief','chief'),
('taxisupport_cc','taxisupport_cc_chief','chief'),
('internationaltaxi','internationaltaxi_chief','chief');


INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('perm_1',NOW(),'webalex','perm_1','perm_1','perm_1','perm_1'),
('user_calltaxi',NOW(),'webalex','user_calltaxi','user_calltaxi','user_calltaxi','user_calltaxi'),
('user_directsupport',NOW(),'webalex','user_directsupport','user_directsupport','user_directsupport','user_directsupport'),
('widget_calltaxi_callsall',NOW(),'webalex','widget_calltaxi_callsall','widget_calltaxi_callsall','widget_calltaxi_callsall','widget_calltaxi_callsall'),
('widget_calltaxi_callstrip',NOW(),'webalex','widget_calltaxi_callstrip','widget_calltaxi_callstrip','widget_calltaxi_callstrip','widget_calltaxi_callstrip'),
('widget_calltaxi_convert',NOW(),'webalex','widget_calltaxi_convert','widget_calltaxi_convert','widget_calltaxi_convert','widget_calltaxi_convert'),
('widget_calltaxi_qa',NOW(),'webalex','widget_calltaxi_qa','widget_calltaxi_qa','widget_calltaxi_qa','widget_calltaxi_qa'),
('widget_calltaxi_discipline',NOW(),'webalex','widget_calltaxi_discipline','widget_calltaxi_discipline','widget_calltaxi_discipline','widget_calltaxi_discipline'),
('widget_calltaxi_basic_score',NOW(),'webalex','widget_calltaxi_basic_score','widget_calltaxi_basic_score','widget_calltaxi_basic_score','widget_calltaxi_basic_score'),
('widget_directsupport_wfm',NOW(),'webalex','widget_directsupport_wfm','widget_directsupport_wfm','widget_directsupport_wfm','widget_directsupport_wfm'),
('widget_directsupport_skip',NOW(),'webalex','widget_directsupport_skip','widget_directsupport_skip','widget_directsupport_skip','widget_directsupport_skip'),
('widget_directsupport_goal1',NOW(),'webalex','widget_directsupport_goal1','widget_directsupport_goal1','widget_directsupport_goal1','widget_directsupport_goal1'),
('widget_directsupport_goal2',NOW(),'webalex','widget_directsupport_goal2','widget_directsupport_goal2','widget_directsupport_goal2','widget_directsupport_goal2'),
('widget_directsupport_fcalls',NOW(),'webalex','widget_directsupport_fcalls','widget_directsupport_fcalls','widget_directsupport_fcalls','widget_directsupport_fcalls'),
('widget_directsupport_nofcalls',NOW(),'webalex','widget_directsupport_nofcalls','widget_directsupport_nofcalls','widget_directsupport_nofcalls','widget_directsupport_nofcalls'),
('widget_directsupport_upsale',NOW(),'webalex','widget_directsupport_upsale','widget_directsupport_upsale','widget_directsupport_upsale','widget_directsupport_upsale'),
('widget_directsupport_iscore',NOW(),'webalex','widget_directsupport_iscore','widget_directsupport_iscore','widget_directsupport_iscore','widget_directsupport_iscore'),
('widget_directsupport_pos_oscore',NOW(),'webalex','widget_directsupport_pos_oscore','widget_directsupport_pos_oscore','widget_directsupport_pos_oscore','widget_directsupport_pos_oscore'),
('widget_comdelivery_contracts',NOW(),'webalex','widget_comdelivery_contracts','widget_comdelivery_contracts','widget_comdelivery_contracts','widget_comdelivery_contracts'),
('widget_comdelivery_listedclients',NOW(),'webalex','widget_comdelivery_listedclients','widget_comdelivery_listedclients','widget_comdelivery_listedclients','widget_comdelivery_listedclients'),
('widget_comdelivery_deliverysccs',NOW(),'webalex','widget_comdelivery_deliverysccs','widget_comdelivery_deliverysccs','widget_comdelivery_deliverysccs','widget_comdelivery_deliverysccs'),
('widget_comdelivery_health',NOW(),'webalex','widget_comdelivery_health','widget_comdelivery_health','widget_comdelivery_health','widget_comdelivery_health'),
('widget_comdelivery_donetasks',NOW(),'webalex','widget_comdelivery_donetasks','widget_comdelivery_donetasks','widget_comdelivery_donetasks','widget_comdelivery_donetasks'),
('widget_comdelivery_callssccs',NOW(),'webalex','widget_comdelivery_callssccs','widget_comdelivery_callssccs','widget_comdelivery_callssccs','widget_comdelivery_callssccs'),
('widget_comdelivery_quality',NOW(),'webalex','widget_comdelivery_quality','widget_comdelivery_quality','widget_comdelivery_quality','widget_comdelivery_quality'),
('widget_comdelivery_tov',NOW(),'webalex','widget_comdelivery_tov','widget_comdelivery_tov','widget_comdelivery_tov','widget_comdelivery_tov'),
('widget_comdelivery_hygiene',NOW(),'webalex','widget_comdelivery_hygiene','widget_comdelivery_hygiene','widget_comdelivery_hygiene','widget_comdelivery_hygiene'),
('widget_comdelivery_algorithm',NOW(),'webalex','widget_comdelivery_algorithm','widget_comdelivery_algorithm','widget_comdelivery_algorithm','widget_comdelivery_algorithm'),
('read_users_calltaxi',NOW(),'webalex','read_users_calltaxi','read_users_calltaxi','read_users_calltaxi','read_users_calltaxi'),
('read_users_support_taxi',NOW(),'support_taxi_user','read_users_support_taxi','read_users_support_taxi','read_users_support_taxi','read_users_support_taxi'),
('user_support_taxi',NOW(),'support_taxi_user','user_support_taxi','user_support_taxi','user_support_taxi','user_support_taxi'),
('read_users_cargo_callcenter',NOW(),'justmark0','read_users_cargo_callcenter','read_users_cargo_callcenter','read_users_cargo_callcenter','read_users_cargo_callcenter'),
('user_cargo_callcenter',NOW(),'justmark0','user_cargo_callcenter','user_cargo_callcenter','user_cargo_callcenter','user_cargo_callcenter'),
('widget_lavkasupport_norm',NOW(),'webalex','widget_lavkasupport_norm','widget_lavkasupport_norm','widget_lavkasupport_norm','widget_lavkasupport_norm'),
('user_lavkasupport',NOW(),'webalex','user_lavkasupport','user_lavkasupport','user_lavkasupport','user_lavkasupport'),
('widget_taxisupport_cc_norm',NOW(),'taxisupport_cc_chief','widget_taxisupport_cc_norm','widget_taxisupport_cc_norm','widget_taxisupport_cc_norm','widget_taxisupport_cc_norm'),
('user_taxisupport_cc',NOW(),'taxisupport_cc_chief','user_taxisupport_cc','user_taxisupport_cc','user_taxisupport_cc','user_taxisupport_cc'),
('widget_internationaltaxi_tph',NOW(),'webalex','widget_internationaltaxi_tph','widget_internationaltaxi_tph','widget_internationaltaxi_tph','widget_internationaltaxi_tph'),
('widget_internationaltaxi_sumactions',NOW(),'webalex','widget_internationaltaxi_sumactions','widget_internationaltaxi_sumactions','widget_internationaltaxi_sumactions','widget_internationaltaxi_sumactions'),
('widget_internationaltaxi_avgtph',NOW(),'webalex','widget_internationaltaxi_avgtph','widget_internationaltaxi_avgtph','widget_internationaltaxi_avgtph','widget_internationaltaxi_avgtph'),
('widget_internationaltaxi_workhours',NOW(),'webalex','widget_internationaltaxi_workhours','widget_internationaltaxi_workhours','widget_internationaltaxi_workhours','widget_internationaltaxi_workhours');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('calltaxi',NOW(),'webalex','calltaxi','calltaxi','calltaxi','calltaxi',true),
('comdelivery',NOW(),'webalex','comdelivery','comdelivery','comdelivery','comdelivery',true),
('directsupport',NOW(),'webalex','directsupport','directsupport','directsupport','directsupport',true),
('beta',NOW(),'webalex','beta','beta','beta','beta',true),
('support_taxi_role',NOW(),'support_taxi_user','support_taxi_role','support_taxi_role','support_taxi_role','support_taxi_role',true),
('cargo_callcenter_role',NOW(),'justmark0','cargo_callcenter_role','cargo_callcenter_role','cargo_callcenter_role','cargo_callcenter_role',true),
('lavkasupport_role',NOW(),'lavkasupport_chief','lavkasupport_role','lavkasupport_role','lavkasupport_role','lavkasupport_role',true),
('taxisupport_cc_role',NOW(),'taxisupport_cc_chief','taxisupport_cc_role','taxisupport_cc_role','taxisupport_cc_role','taxisupport_cc_role',true),
('internationaltaxi_role',NOW(),'internationaltaxi_chief','internationaltaxi_role','internationaltaxi_role','internationaltaxi_role','internationaltaxi_role',true),
('view_all_users',NOW(),'superuser','view_all_users','view_all_users','view_all_users','webalex',false);


INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('calltaxi','user_calltaxi',NOW(),'webalex'),
('directsupport','user_directsupport',NOW(),'webalex'),
('calltaxi','widget_calltaxi_callsall',NOW(),'calltaxi_chief'),
('calltaxi','widget_calltaxi_callstrip',NOW(),'calltaxi_chief'),
('calltaxi','widget_calltaxi_convert',NOW(),'calltaxi_chief'),
('calltaxi','widget_calltaxi_qa',NOW(),'calltaxi_chief'),
('calltaxi','widget_calltaxi_discipline',NOW(),'calltaxi_chief'),
('calltaxi','widget_calltaxi_basic_score',NOW(),'calltaxi_chief'),
('directsupport','widget_directsupport_wfm',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_skip',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_goal1',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_goal2',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_fcalls',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_nofcalls',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_upsale',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_iscore',NOW(),'directsupport_chief'),
('directsupport','widget_directsupport_pos_oscore',NOW(),'directsupport_chief'),
('comdelivery','widget_comdelivery_contracts',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_listedclients',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_deliverysccs',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_health',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_donetasks',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_callssccs',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_quality',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_tov',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_hygiene',NOW(),'comdelivery_chief'),
('comdelivery','widget_comdelivery_algorithm',NOW(),'comdelivery_chief'),
('beta','read_users_calltaxi',NOW(),'webalex'),
('support_taxi_role','read_users_support_taxi',NOW(),'support_taxi_user'),
('support_taxi_role','user_support_taxi',NOW(),'support_taxi_user'),
('cargo_callcenter_role','read_users_cargo_callcenter',NOW(),'justmark0'),
('cargo_callcenter_role','user_cargo_callcenter',NOW(),'justmark0'),
('lavkasupport_role','widget_lavkasupport_norm',NOW(),'lavkasupport_chief'),
('lavkasupport_role','user_lavkasupport',NOW(),'lavkasupport_chief'),
('taxisupport_cc_role','widget_taxisupport_cc_norm',NOW(),'taxisupport_cc_chief'),
('taxisupport_cc_role','user_taxisupport_cc',NOW(),'taxisupport_cc_chief'),
('internationaltaxi_role','widget_internationaltaxi_tph',NOW(),'internationaltaxi_chief'),
('internationaltaxi_role','widget_internationaltaxi_avgtph',NOW(),'internationaltaxi_chief'),
('internationaltaxi_role','widget_internationaltaxi_sumactions',NOW(),'internationaltaxi_chief'),
('internationaltaxi_role','widget_internationaltaxi_workhours',NOW(),'internationaltaxi_chief'),
('view_all_users','read_users_calltaxi',NOW(),'webalex'),
('view_all_users','read_users_support_taxi',NOW(),'webalex');



INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'slon','beta'),
(NOW(),'valera','calltaxi'),
(NOW(),'vavan','calltaxi'),
(NOW(),'calltaxi_chief','calltaxi'),
(NOW(), 'justmark0', 'cargo_callcenter_role'),
(NOW(), 'justmark0', 'support_taxi_role'),
(NOW(), 'support_taxi_user', 'support_taxi_role'),
(NOW(), 'cargo_callcenter_user', 'cargo_callcenter_role'),
(NOW(),'comdelivery_chief','comdelivery'),
(NOW(),'directsupport_chief','directsupport'),
(NOW(),'lavkasupport_chief','lavkasupport_role'),
(NOW(),'lavkasupport_user','lavkasupport_role'),
(NOW(),'taxisupport_cc_user','taxisupport_cc_role'),
(NOW(),'taxisupport_cc_chief','taxisupport_cc_role'),
(NOW(),'internationaltaxi_chief','internationaltaxi_role'),
(NOW(),'internationaltaxi_user','internationaltaxi_role'),
(NOW(),'superuser','view_all_users');


INSERT INTO agent.teams (key,name,en_name,permission) VALUES
('a_team','A-команда','A team','perm_1'),
('b_team','B-команда','B team','perm_1'),
('c_team','C-команда','C team','perm_1'),
('d_team','D-команда','D team','perm_1'),
('e_team','E-команда','E team','perm_1'),
('f_team','F-команда','F team','perm_1');

INSERT INTO agent.teams (key,name,en_name,permission, piece, use_reserves) VALUES
('support_taxi', 'Саппорт Такси', 'Support taxi', 'read_users_support_taxi', true, false),
('cargo_callcenter', 'cargo-callcenter', 'cargo-callcenter', 'read_users_cargo_callcenter', true, true);

UPDATE agent.users SET team='a_team' WHERE login='vasin';
UPDATE agent.users SET team='b_team' WHERE login='pirozhochek';
UPDATE agent.users SET team='c_team' WHERE login='vavan';
UPDATE agent.users SET team='d_team' WHERE login='valera';
UPDATE agent.users SET team='e_team' WHERE login='katya';
UPDATE agent.users SET team='f_team' WHERE login='nlo';
UPDATE agent.users SET team='cargo_callcenter' WHERE login='justmark0';
UPDATE agent.users SET team='cargo_callcenter' WHERE login='cargo_callcenter_user';
UPDATE agent.users SET team='support_taxi' WHERE login='support_taxi_user';


INSERT INTO agent.dismissed_users
(
 id,
 login,
 term_date,
 chief_login,
 organization,
 status,
 created_at
)
VALUES
(
 'ba36777b3d4d4d40944c43fe008117e1',
 'vasin',
 '2021-11-01',
 'orangevl',
 'Яндекс',
 'new',
 '2021-10-01 00:00:00'
),
(
 '078bdc7fae2c4a8b86ab2d64cb39bfe9',
 'pirozhochek',
 '2021-11-02',
 'orangevl',
 'Яндекс',
 'new',
 '2021-10-01 00:00:00'
),
(
 '9745cda67ee84a9d9fcf1f20f0c68105',
 'vavan',
 '2021-11-03',
 'orangevl',
 'Яндекс',
 'completed',
 '2021-10-01 00:00:00'
);


INSERT INTO agent.gp_dsp_operator_activity_daily
(
 login,
 date,
 call_cnt,
 success_order_cnt,
 quality_coeff_order_placing_sum,
 quality_coeff_consultation_sum,
 quality_coeff_order_placing_cnt,
 quality_coeff_consultation_cnt,
 claim_cnt,
 abcense_cnt,
 delay_cnt
)
VALUES
('calltaxi_chief','2020-12-30',10,11,12,13,14,15,16,17,18),
('calltaxi_chief','2020-12-31',10,11,12,13,14,15,16,17,18),
('calltaxi_support','2020-12-30',10,11,12,13,14,15,16,17,18),
('calltaxi_support_with_null_data','2020-12-31',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);


INSERT INTO agent.direct
(
 login,
 dt,
 wfm_perc,
 skip_perc,
 goal_1,
 avg_dur_fcalls,
 avg_dur_no_fcalls,
 goal_2,
 pos_oscore,
 iscore,
 upsale_exec
)
VALUES
('directsupport_chief','2020-12-01',10,11,12,13,14,15,16,17,18),
('directsupport_chief','2020-12-16',10,11,12,13,14,15,16,17,18),
('directsupport_support','2020-11-30',100,110,120,130,140,150,160,170,180),
('directsupport_support','2020-12-01',10,11,12,13,14,15,16,17,18),
('directsupport_support','2020-12-16',10,11,12,13,14,15,16,17,18),
('directsupport_support','2020-12-17',14,15,16,17,18,19,20,21,22),
('directsupport_support','2021-01-01',14,15,16,17,18,19,20,21,22),
('directsupport_support_with_null_data','2020-12-16',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);


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
('valera', '{line_1, line_2}', FALSE, FALSE, 12, '{ru, en}', FALSE),
('calltaxi_chief', '{}', TRUE, TRUE, 12, '{ru}', TRUE);



INSERT INTO agent.chatterbox_available_lines
(
    login,
    lines
)
VALUES
('valera', '{line_1, line_3}'),
('calltaxi_chief', '{line_2}');

INSERT INTO agent.taxi_delivery
(login, date, cnt_corp_contract_id, cnt_corp_contract_id_this_month, sum_deliveries_sccs, active_days_percent, avg_quality_rate, avg_tov_rate, avg_hygiene_rate, avg_algorithm_rate, sum_calls_sccs_60, overall_done_tasks)
VALUES
('comdelivery_chief', '2020-12-01', 123, 321, 15, 95.4, 4.5, 5.7, 40, 30, 61, 20),
('comdelivery_support1', '2020-12-01', 120, 322, 16, 95.4, 4.6, 5.8, 40, 30, 40, 21),
('comdelivery_support_with_null_data', '2020-12-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
('comdelivery_support_with_null_data', '2020-11-01',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);


INSERT INTO agent.international_taxi_support_metrics
(
    date,
    login,
    action_cnt,
    sum_time_sec,
    work_action_cnt,
    work_hours,
    last_update
)
VALUES
('2022-06-01', 'internationaltaxi_user', 15,90, 5, 0.5,'2022-06-01 12:00:00'),
('2022-06-02', 'internationaltaxi_user', 10, 60,10, 2,'2022-06-01 12:00:00'),
('2022-06-03', 'internationaltaxi_user', 10, 60,0, 0,'2022-06-01 13:30:00'),
('2022-05-03', 'internationaltaxi_user', 10, 60,0, 1,'2022-06-01 13:30:00'),
('2022-06-01', 'internationaltaxi_chief', 100, 600, 15,4,'2022-06-01 12:30:00'),
('2022-06-02', 'internationaltaxi_chief', 100, 600, 0,0.5,'2022-06-01 12:30:00'),
('2022-06-03', 'internationaltaxi_chief', 100, 600, 70, 3,'2022-06-01 13:00:00');
