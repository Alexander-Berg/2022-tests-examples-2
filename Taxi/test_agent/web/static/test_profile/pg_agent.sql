INSERT INTO agent.departments VALUES
('yandex',NOW(),NOW(),'Яндекс',null),
('yandex_taxi',NOW(),NOW(),'Яндекс Такси','yandex'),
('yandex_kpb',NOW(),NOW(),'Яндекс Такси',null),
('yandex_taxisupport',NOW(),NOW(),'Яндекс Поддержка Такси',null),
('yandex_eatssupport',NOW(),NOW(),'Яндекс Поддержка Еды',null),
('yandex_lavkasupport',NOW(),NOW(),'Яндекс Поддержка Лавки',null),
('yandex_deliverysupport',NOW(),NOW(),'Яндекс Поддержка Доставки',null);



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
    piece,
    country,
    phones,
    telegram
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    'Alexandr',
    'Ivanov',
    '2016-06-02',
    null,
    false,
    'ru',
    '{"26fe660e100e45c897225fc8637edfff"}',
    '{"1e55e7049fc543dc9ebbb63c8fc4d7ed"}'
),
(
  1120000000252888,
     NOW(),
    'topalyan',
    'Ольга',
    'Топалян',
    'Olya',
    'Topalyan',
    '2016-06-02',
    null,
    false,
    'ru',
    null,
    null
),
(
  1120000000252888,
     NOW(),
    'akozhevina',
    'Анна',
    'Кожевина',
    'Ann',
    'Kozhevina',
    '2016-06-02',
    null,
    false,
     'ru',
    null,
 null
),
(
  1120000000252888,
     NOW(),
    'mikh-vasily',
    'Василий',
    'Михайлов',
    'Vasily',
    'Mihaylov',
    '2016-06-02',
    null,
    false,
    'ru',
    null,
 null
),
(
  1120000000252888,
     NOW(),
    'volozh',
    'Аркадий',
    'Волож',
    'Arkady',
    'Volozh',
    '2016-06-02',
    'yandex',
    false,
     'ru',
    null,
 null
),
(
  1120000000252888,
     NOW(),
    'strashnov',
    'Александр',
    'Страшнов',
    'Alexandt',
    'Strashnov',
    '2016-06-02',
    'yandex_taxi',
    false,
     'ru',
    null,
 null
),
(
  1120000000252888,
     NOW(),
    'nikslim',
    'Никита',
    'Борисов',
    'Nikita',
    'Borisov',
    '2016-06-02',
    'yandex_kpb',
    false,
     'ru',
    null,
 null
),
(
  1120000000252888,
     NOW(),
    'test_battlepass_login',
    'test_battlepass_login',
    'test_battlepass_login',
    'test_battlepass_login',
    'test_battlepass_login',
    '2016-06-02',
    'yandex_kpb',
    false,
     'ru',
    null,
 null
),
(
  1120000000252888,
  NOW(),
  'unholy',
  'Нияз',
  'Наибулин',
  'Niyaz',
  'Naibulin',
  '2016-06-02',
  null,
  false,
     'ru',
  null,
 null
),
(
    1120000000252888,
     NOW(),
    'valentin',
    'Валентин',
    'Петухов',
    'Valentin',
    'Petuhov',
    '2016-06-02',
    null,
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'justmark0',
    'Марк',
    'Николсон',
    'Mark',
    'Nicholson',
    '2016-06-02',
    null,
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'taxisupport_support_login',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    '2016-06-02',
    'yandex_taxisupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'taxisupport_support_login_1',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    '2016-06-02',
    'yandex_taxisupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'taxisupport_support_login_2',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    'taxisupport_support_first_name',
    'taxisupport_support_last_name',
    '2016-06-02',
    'yandex_taxisupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'eats_user_1',
    'eats_user_1_first_name',
    'eats_user_1_last_name',
    'eats_user_1_first_name',
    'eats_user_1_last_name',
    '2016-06-02',
    'yandex_eatssupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'lavkasupport_user_1',
    'lavkasupport_user_1_first_name',
    'lavkasupport_user_1_last_name',
    'lavkasupport_user_1_first_name',
    'lavkasupport_user_1_last_name',
    '2016-06-02',
    'yandex_lavkasupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'deliverysupport_user_1',
    'deliverysupport_user_1_first_name',
    'deliverysupport_user_1_last_name',
    'deliverysupport_user_1_first_name',
    'deliverysupport_user_1_last_name',
    '2016-06-02',
    'yandex_deliverysupport',
    false,
     'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'piece_user_1',
    'piece_user_1',
    'piece_user_1',
    'piece_user_1',
    'piece_user_1',
    '2016-06-02',
    null,
    true,
    'ru',
    null,
    null
),
(
    1120000000252888,
     NOW(),
    'driverhiring_user_1',
    'driverhiring_user_1',
    'driverhiring_user_1',
    'driverhiring_user_1',
    'driverhiring_user_1',
    '2016-06-02',
    null,
    true,
    'ru',
    null,
    null
);

INSERT INTO agent.departments_heads VALUES
('volozh','yandex','chief');


INSERT INTO agent.permissions VALUES
(
 'permission_1',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'permission_1',
 'permission_1',
 'permission_1',
 'permission_1'

),
(
 'permission_2',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'permission_2',
 'permission_2',
 'permission_2',
 'permission_2'

),
(
 'widget_calltaxi_callsall',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_callsall',
 'widget_calltaxi_callsall',
 'widget_calltaxi_callsall',
 'widget_calltaxi_callsall'

),
(
 'widget_calltaxi_callstrip',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_callstrip',
 'widget_calltaxi_callstrip',
 'widget_calltaxi_callstrip',
 'widget_calltaxi_callstrip'

),
  (
 'widget_calltaxi_convert',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_convert',
 'widget_calltaxi_convert',
 'widget_calltaxi_convert',
 'widget_calltaxi_convert'

),
(
 'widget_calltaxi_qa',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_qa',
 'widget_calltaxi_qa',
 'widget_calltaxi_qa',
 'widget_calltaxi_qa'

),
(
 'widget_calltaxi_discipline',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_discipline',
 'widget_calltaxi_discipline',
 'widget_calltaxi_discipline',
 'widget_calltaxi_discipline'

),
(
 'widget_calltaxi_basic_score',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_basic_score',
 'widget_calltaxi_basic_score',
 'widget_calltaxi_basic_score',
 'widget_calltaxi_basic_score'
),
(
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'read_users_calltaxi',
 'read_users_calltaxi',
 'read_users_calltaxi',
 'read_users_calltaxi'
),
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'
),
(
 'widget_directsupport_csat',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'unholy',
 'widget_directsupport_csat',
 'widget_directsupport_csat',
 'widget_directsupport_csat',
 'widget_directsupport_csat'
),
(
 'widget_directsupport_wfm',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'unholy',
 'widget_directsupport_wfm',
 'widget_directsupport_wfm',
 'widget_directsupport_wfm',
 'widget_directsupport_wfm'
),
(
 'widget_directsupport_skip',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'unholy',
 'widget_directsupport_skip',
 'widget_directsupport_skip',
 'widget_directsupport_skip',
 'widget_directsupport_skip'
),
(
 'widget_calltaxi_speed',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_speed',
 'widget_calltaxi_speed',
 'widget_calltaxi_speed',
 'widget_calltaxi_speed'
),
(
 'widget_calltaxi_production',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_calltaxi_production',
 'widget_calltaxi_production',
 'widget_calltaxi_production',
 'widget_calltaxi_production'
),
(
 'widget_taxisupport_csat',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_taxisupport_csat',
 'widget_taxisupport_csat',
 'widget_taxisupport_csat',
 'widget_taxisupport_csat'
),
(
 'widget_taxisupport_qa',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_taxisupport_qa',
 'widget_taxisupport_qa',
 'widget_taxisupport_qa',
 'widget_taxisupport_qa'
),
(
 'widget_taxisupport_norm',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_taxisupport_norm',
 'widget_taxisupport_norm',
 'widget_taxisupport_norm',
 'widget_taxisupport_norm'
),
(
 'widget_comdelivery_contracts',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_contracts',
 'widget_comdelivery_contracts',
 'widget_comdelivery_contracts',
 'widget_comdelivery_contracts'
),
(
 'widget_comdelivery_listedclients',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_listedclients',
 'widget_comdelivery_listedclients',
 'widget_comdelivery_listedclients',
 'widget_comdelivery_listedclients'
),
(
 'widget_comdelivery_deliverysccs',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_deliverysccs',
 'widget_comdelivery_deliverysccs',
 'widget_comdelivery_deliverysccs',
 'widget_comdelivery_deliverysccs'
),
(
 'widget_comdelivery_health',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_health',
 'widget_comdelivery_health',
 'widget_comdelivery_health',
 'widget_comdelivery_health'
),
(
   'widget_comdelivery_donetasks',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_donetasks',
 'widget_comdelivery_donetasks',
 'widget_comdelivery_donetasks',
 'widget_comdelivery_donetasks'
),
(
   'widget_comdelivery_callssccs',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_callssccs',
 'widget_comdelivery_callssccs',
 'widget_comdelivery_callssccs',
 'widget_comdelivery_callssccs'
),
(
   'widget_comdelivery_quality',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_quality',
 'widget_comdelivery_quality',
 'widget_comdelivery_quality',
 'widget_comdelivery_quality'
),
(
   'widget_comdelivery_tov',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_tov',
 'widget_comdelivery_tov',
 'widget_comdelivery_tov',
 'widget_comdelivery_tov'
),
(
   'widget_comdelivery_hygiene',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_hygiene',
 'widget_comdelivery_hygiene',
 'widget_comdelivery_hygiene',
 'widget_comdelivery_hygiene'
),
(
   'widget_comdelivery_algorithm',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_comdelivery_algorithm',
 'widget_comdelivery_algorithm',
 'widget_comdelivery_algorithm',
 'widget_comdelivery_algorithm'
),
(
 'user_zapravki',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_zapravki',
 'user_zapravki',
 'user_zapravki',
 'user_zapravki'
),
(
 'widget_edasupport_csat',
 '2022-01-01 00:00:00',
 '2022-01-01 00:00:00',
 'webalex',
 'widget_edasupport_csat',
 'widget_edasupport_csat',
 'widget_edasupport_csat',
 'widget_edasupport_csat'
),
(
 'widget_edasupport_qa',
 '2022-01-01 00:00:00',
 '2022-01-01 00:00:00',
 'webalex',
 'widget_edasupport_qa',
 'widget_edasupport_qa',
 'widget_edasupport_qa',
 'widget_edasupport_qa'
),
(
 'widget_lavkasupport_norm',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_lavkasupport_norm',
 'widget_lavkasupport_norm',
 'widget_lavkasupport_norm',
 'widget_lavkasupport_norm'
),
(
 'widget_lavkasupport_csat',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_lavkasupport_csat',
 'widget_lavkasupport_csat',
 'widget_lavkasupport_csat',
 'widget_lavkasupport_csat'
),
(
 'widget_deliverysupport_norm',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_deliverysupport_norm',
 'widget_deliverysupport_norm',
 'widget_deliverysupport_norm',
 'widget_deliverysupport_norm'
),
(
 'widget_driverhiring_speed',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_driverhiring_speed',
 'widget_driverhiring_speed',
 'widget_driverhiring_speed',
 'widget_driverhiring_speed'
),
(
 'widget_driverhiring_conversion',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_driverhiring_conversion',
 'widget_driverhiring_conversion',
 'widget_driverhiring_conversion',
 'widget_driverhiring_conversion'
),
(
 'widget_driverhiring_calls',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_driverhiring_calls',
 'widget_driverhiring_calls',
 'widget_driverhiring_calls',
 'widget_driverhiring_calls'
),
(
 'widget_driverhiring_actives',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_driverhiring_actives',
 'widget_driverhiring_actives',
 'widget_driverhiring_actives',
 'widget_driverhiring_actives'
),
(
 'widget_driverhiring_qa',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'widget_driverhiring_qa',
 'widget_driverhiring_qa',
 'widget_driverhiring_qa',
 'widget_driverhiring_qa'
),
(
 'user_driverhiring',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_driverhiring',
 'user_driverhiring',
 'user_driverhiring',
 'user_driverhiring'
 );


INSERT INTO agent.roles VALUES
(
 'yandex_taxi_team',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент поддержки яндекс такси',
 'support taxi',
 'Агент поддержки яндекс такси',
 'Support Yandex taxi',
 true
),
(
 'agent_call_taxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент поддержки СallTaxi',
 'Агент поддержки СallTaxi',
 'Агент поддержки СallTaxi',
 'Агент поддержки СallTaxi',
 true
),
(
 'agent_direct_support',
 '2021-01-01 00:00:00',
 null,
 'unholy',
 'Агент поддержки direct',
 'Агент поддержки direct',
 'Агент поддержки direct',
 'Агент поддержки direct',
 true
),
(
 'agent_comdelivery_team',
 '2021-01-01 00:00:00',
 null,
 'justmark0',
 'Агент поддержки Commerce delivery',
 'Агент поддержки Commerce delivery',
 'Агент поддержки Commerce delivery',
 'Агент поддержки Commerce delivery',
 true
),
(
 'agent_taxisupport_team',
 '2021-01-01 00:00:00',
 null,
 'taxisupport_support_login',
 'taxisupport',
 'taxisupport',
 'taxisupport',
 'taxisupport',
 true
),
(
 'yandex_zapravki',
 '2021-01-01 00:00:00',
 null,
 'taxisupport_support_login',
 'yandex_zapravki',
 'yandex_zapravki',
 'yandex_zapravki',
 'yandex_zapravki',
 true
),
(
 'yandex_eats_team',
 '2021-01-01 00:00:00',
 null,
 'eats_user_1',
 'eatssupport',
 'eatssupport',
 'eatssupport',
 'eatssupport',
 true
),
(
 'yandex_lavkasupport_team',
 '2021-01-01 00:00:00',
 null,
 'lavkasupport_user_1',
 'lavkasupport',
 'lavkasupport',
 'lavkasupport',
 'lavkasupport',
 true
),
(
 'yandex_deliverysupport_team',
 '2021-01-01 00:00:00',
 null,
 'deliverysupport_user_1',
 'deliverysupport',
 'deliverysupport',
 'deliverysupport',
 'deliverysupport',
 true
),
(
 'user_driverhiring',
 '2021-01-01 00:00:00',
 null,
 'driverhiring_user_1',
 'driverhiring',
 'driverhiring',
 'driverhiring',
 'driverhiring',
 true
);


INSERT INTO agent.roles_permissions VALUES
(
 'yandex_taxi_team',
 'widget_calltaxi_callsall',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_callstrip',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_convert',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_qa',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_discipline',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_basic_score',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_contracts',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_listedclients',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_deliverysccs',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_health',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_donetasks',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
  'agent_comdelivery_team',
 'widget_comdelivery_callssccs',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_quality',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_tov',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_hygiene',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'agent_comdelivery_team',
 'widget_comdelivery_algorithm',
 '2021-01-01 00:00:00',
 'justmark0'
),
(
 'yandex_taxi_team',
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'agent_call_taxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'agent_direct_support',
 'widget_directsupport_skip',
 '2021-01-01 00:00:00',
 'unholy'
),
(
 'agent_direct_support',
 'widget_directsupport_wfm',
 '2021-01-01 00:00:00',
 'unholy'
),
(
 'agent_direct_support',
 'widget_directsupport_csat',
 '2021-01-01 00:00:00',
 'unholy'
),
(
 'agent_direct_support',
 'widget_calltaxi_basic_score',
 '2021-01-01 00:00:00',
 'unholy'
),
(
 'yandex_taxi_team',
 'widget_calltaxi_speed',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'yandex_taxi_team',
 'widget_calltaxi_production',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'agent_taxisupport_team',
 'widget_taxisupport_csat',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'agent_taxisupport_team',
 'widget_taxisupport_qa',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'agent_taxisupport_team',
 'widget_taxisupport_norm',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_zapravki',
 'user_zapravki',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_eats_team',
 'widget_edasupport_csat',
 '2022-01-01 00:00:00',
 'webalex'
),
(
 'yandex_eats_team',
 'widget_edasupport_qa',
 '2022-01-01 00:00:00',
 'webalex'
),
(
 'yandex_lavkasupport_team',
 'widget_lavkasupport_norm',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_lavkasupport_team',
 'widget_lavkasupport_csat',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_deliverysupport_team',
 'widget_deliverysupport_norm',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'widget_driverhiring_speed',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'widget_driverhiring_conversion',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'widget_driverhiring_calls',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'widget_driverhiring_actives',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'widget_driverhiring_qa',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_driverhiring',
 'user_driverhiring',
 '2021-01-01 00:00:00',
 'webalex'
 );


INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
(
'2020-01-01 00:00:00',
'webalex',
'yandex_taxi_team'
),
(
'2020-01-01 00:00:00',
'valentin',
'yandex_taxi_team'
),
(
 '2020-01-01 00:00:00',
 'akozhevina',
 'agent_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'mikh-vasily',
 'yandex_taxi_team'
),
(
 '2020-01-01 00:00:00',
 'test_battlepass_login',
 'agent_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'unholy',
 'agent_direct_support'
),
(
 '2020-01-01 00:00:00',
 'justmark0',
 'agent_comdelivery_team'
),
(
 '2020-01-01 00:00:00',
 'taxisupport_support_login',
 'agent_taxisupport_team'
),
(
 '2020-01-01 00:00:00',
 'taxisupport_support_login_1',
 'agent_taxisupport_team'
),
(
 '2020-01-01 00:00:00',
 'taxisupport_support_login_2',
 'agent_taxisupport_team'
),
(
 '2020-01-01 00:00:00',
 'piece_user_1',
 'yandex_zapravki'
),
(
 '2022-01-01 00:00:00',
 'eats_user_1',
 'yandex_eats_team'
),
(
 '2022-01-01 00:00:00',
 'lavkasupport_user_1',
 'yandex_lavkasupport_team'
),
(
 '2022-01-01 00:00:00',
 'deliverysupport_user_1',
 'yandex_deliverysupport_team'
),
(
 '2022-01-01 00:00:00',
 'driverhiring_user_1',
 'user_driverhiring'
);


INSERT INTO agent.gp_dsp_operator_activity_daily
VALUES
(
 'webalex',
 '2021-01-01',
 '2021-01-02 12:00:00',
 0,
 0,
 0,
 0,
 1,
 1,
 1,
 200,
 100,
 0,
 0
),
(
 'mikh-vasily',
 '2021-01-01',
 '2021-01-02 12:00:00',
 80,
 80,
 1,
 1,
 0,
 0,
 0,
 200,
 100,
 40,
 27);



INSERT INTO agent.teams VALUES
('team_1','Команда 1','permission_1',false,'team_1'),
('team_2','Команда 2','permission_2',false,'team_2'),
('yandex_taxi_econom','yandex_taxi_econom','permission_1',true,'yandex_taxi_econom');

UPDATE agent.users SET team='team_1' WHERE login IN ('mikh-vasily','webalex','valentin');
UPDATE agent.users SET team='yandex_taxi_econom' WHERE login IN ('piece_user_1');




INSERT INTO agent.battle_pass_events
(
 start,
 stop,
 project
)
VALUES
(
 '2021-01-01 00:00:00+0300',
 '2100-01-01 00:00:00+0300',
 'calltaxi'
);

INSERT INTO agent.taxi_support_metrics
(
	last_update,
    login,
    csat_avg,
    csat_cnt,
    csat_not_excepted_cnt,
    csat_not_excepted_sum,
    quality_cnt,
    quality_avg,
    csat_low_cnt,
    quality_sum,
    date
)
VALUES
('2021-12-15','taxisupport_support_login_1',100,1,100,1,1,100,100,100,'2021-11-30'),
('2021-12-15','taxisupport_support_login_2',1000,1000,1000,1000,1000,1000,1000,1000,'2021-11-30'),
('2021-12-15','taxisupport_support_login_2',4.55,122,4.55,122,2,50,50,50,'2021-12-01'),
('2021-12-15','taxisupport_support_login_2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2021-12-02'),
('2021-12-15','taxisupport_support_login_2',1.55,22,1.55,22,3,80,80,80,'2021-12-03'),
('2021-12-15','taxisupport_support_login_2',1000,1000,1000,1000,1000,1000,1000,1000,'2022-01-01'),
('2021-12-15','lavkasupport_user_1',100,900,1000,1,1,100,13,13,'2021-12-01'),
('2021-12-15','lavkasupport_user_1',100,900,1000,1,1,100,400,400,'2021-12-02'),
('2021-12-15','driverhiring_user_1',NULL,NULL,NULL,NULL,100,NULL,NULL,100,'2022-01-18'),
('2021-12-15','driverhiring_user_1',NULL,NULL,NULL,NULL,12,NULL,NULL,144,'2022-01-19');


INSERT INTO agent.gp_rep_drc_conversion
(
    dt,
    login,
    call_cnt,
    lead_cnt,
    activated_lead_cnt
)
VALUES
('2022-01-18','driverhiring_user_1',100,50,144),
('2022-01-19','driverhiring_user_1',100,50,144);


INSERT INTO agent.users_payday (login,created,payday_uuid,card_mask,phone_pd_id,status)
VALUES ('webalex',NOW(),'71cc9f25-f737-4fdb-9228-e1a1e3b9b3e7','427684******3250','5b06fdaed4d25b346b65c59d42d9e4df','active'),
       ('topalyan',NOW(),'fe8c00ab-e753-4216-8d4e-351541c6212f','427684******1234','b6763c4cc75e565b376883f85c0186de','active');



INSERT INTO agent.taxi_delivery
(login, date, cnt_corp_contract_id, cnt_corp_contract_id_this_month, sum_deliveries_sccs, active_days_percent, avg_quality_rate, avg_tov_rate, avg_hygiene_rate, avg_algorithm_rate, sum_calls_sccs_60, overall_done_tasks)
VALUES
('justmark0', '2021-01-01', 123, 321, 15, 95.4, 4.5, 5.7, 40, 30, 61, 20);
