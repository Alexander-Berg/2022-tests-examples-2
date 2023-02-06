insert into taxi_db_postgres_atlas_backend.full_geo_hierarchy (
    node_id,
    root_node_id,
    node_type,
    parent_node_id,
    population_group,
    name_ru,
    name_en,
    tariff_zone,
    direct_flg
)
values
('br_leningradskaja_obl','br_root','node','br_severo_zapadnyj_fo','RU_SPB','Ленинградская область','Leningrad Region','spb',False),
('br_leningradskaja_obl','br_root','node','br_severo_zapadnyj_fo','RU_SPB','Ленинградская область','Leningrad Region','kolpino',False),
('br_root','br_root','root',null,null,'Базовая иерархия','Basic Hierarchy','spb',False),
('br_root','br_root','root',null,null,'Базовая иерархия','Basic Hierarchy','kolpino',False),
('br_severo_zapadnyj_fo','br_root','node','br_russia',null,'Северо-Западный ФО','Northwestern Federal District','kolpino',False),
('br_severo_zapadnyj_fo','br_root','node','br_russia',null,'Северо-Западный ФО','Northwestern Federal District','spb',False),
('br_russia','br_root','country','br_root',null,'Россия','Russia','spb',False),
('br_russia','br_root','country','br_root',null,'Россия','Russia','kolpino',False),
('br_kolpino','br_root','agglomeration','br_leningradskaja_obl','RU_SPB','Колпино','Kolpino','kolpino',True),
('br_saintpetersburg_adm','br_root','node','br_saintpetersburg','RU_SPB','Санкт-Петербург (адм)','Saint-Petersburg (adm)','spb',True),
('br_saintpetersburg','br_root','agglomeration','br_leningradskaja_obl','RU_SPB','Санкт-Петербург','Saint-Petersburg','spb',False),
('br_moscow','br_root','agglomeration','br_root','RU_MSC','Москва','Moscow','moscow',True),
('br_kazan','br_root','agglomeration','br_root','RU_KZN','Казань','Kazan','kazan',True),
('br_nizhny_novgorod','br_root','agglomeration','br_root','RU_1M+','Нижний Новгород','Nizhny Novgorod','nizhnynovgorod',True),
('fi_root','fi_root','root',null,null,'Финансовые регионы','Financial Regions','spb',False),
('fi_root','fi_root','root',null,null,'Финансовые регионы','Financial Regions','kolpino',False),
('fi_russia','fi_root','country','fi_russia_macro',null,'Россия','Russia','kolpino',False),
('fi_russia','fi_root','country','fi_russia_macro',null,'Россия','Russia','spb',False),
('fi_russia_macro','fi_root','node','fi_root',null,'Россия (Макро)','Russia (Macro)','spb',False),
('fi_russia_macro','fi_root','node','fi_root',null,'Россия (Макро)','Russia (Macro)','kolpino',False),
('fi_spb_and_spbr','fi_root','node','fi_russia','RU_SPB','Санкт-Петербург и ЛО','SPb and SPb region','kolpino',False);



insert into taxi_db_postgres_atlas_backend.tariff_zone_permission (
    yandex_passport_login,
    tariff_geo_zone_name
)
values
('test_user1', 'kolpino'),
('test_user1', 'spb'),
('test_user2', 'kolpino'),
('omnipotent_user', 'moscow'),
('omnipotent_user', 'spb'),
('omnipotent_user', 'kolpino'),
('omnipotent_user', 'kazan'),
('omnipotent_user', 'nizhnynovgorod');

insert into taxi_db_postgres_atlas_backend.geo_node_info (
    node_id,
    root_node_id,
    node_type,
    parent_node_id,
    population_group,
    name_ru,
    name_en,
    tariff_zones,
    bounding_box,
    timezone)
values
('br_kolpino', 'br_root', 'agglomeration', 'br_leningradskaja_obl', 'RU_SPB', 'Колпино', 'Kolpino', '{"kolpino"}', '{"br": [59.729511887815285, 30.624719384271142], "tl": [59.79941521539069, 30.507139314488686]}', 'Europe/Moscow'),
('kolpino', 'br_root', 'tariff_zone', 'br_kolpino', null, 'kolpino', 'kolpino', '{"kolpino"}', '{"br": [59.729511887815285, 30.624719384271142], "tl": [59.79941521539069, 30.507139314488686]}', 'Europe/Moscow'),
('br_moscow', 'br_root', 'agglomeration', 'br_root', 'RU_MSC', 'Москва', 'Moscow', '{"moscow"}', '{"br": [55.4849415645463, 38.01828293668847], "tl": [55.977431625110285, 37.1946401739712]}', 'Europe/Moscow'),
('moscow', 'br_root', 'tariff_zone', 'br_moscow', null, 'moscow', 'moscow', '{"moscow"}', '{"br": [55.4849415645463, 38.01828293668847], "tl": [55.977431625110285, 37.1946401739712]}', 'Europe/Moscow'),
('br_russia', 'br_root', 'country', 'br_root', null, 'Россия', 'Russia', '{"spb", "kolpino"}', '{"br": [59.54492029685772, 30.624719384271142], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('br_saintpetersburg', 'br_root', 'agglomeration', 'br_leningradskaja_obl', 'RU_SPB', 'Санкт-Петербург', 'Saint-Petersburg', '{"spb"}', '{"br": [59.54492029685772, 30.083255025504595], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('br_leningradskaja_obl', 'br_root', 'node', 'br_severo_zapadnyj_fo', 'RU_SPB', 'Ленинградская область', 'Leningrad Region', '{"spb", "kolpino"}', '{"br": [59.54492029685772, 30.624719384271142], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('br_root', 'br_root', 'root', null, null, 'Базовая иерархия', 'Basic Hierarchy', '{"spb", "kolpino"}', '{"br": [59.54492029685772, 30.624719384271142], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('br_saintpetersburg_adm', 'br_root', 'node', 'br_saintpetersburg', 'RU_SPB', 'Санкт-Петербург (адм)', 'Saint-Petersburg (adm)', '{"spb"}', '{"br": [59.54492029685772, 30.083255025504595], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('spb', 'br_root', 'tariff_zone', 'br_saintpetersburg_adm', null, 'spb', 'spb', '{"spb"}', '{"br": [59.54492029685772, 30.083255025504595], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow'),
('br_severo_zapadnyj_fo', 'br_root', 'node', 'br_russia', null, 'Северо-Западный ФО', 'Northwestern Federal District', '{"kolpino", "spb"}', '{"br": [59.54492029685772, 30.624719384271142], "tl": [59.98661270814935, 29.760368809658015]}', 'Europe/Moscow');

insert into taxi_db_postgres_atlas_backend.geo_node_permission(
    root_node_id,
    node_id,
    yandex_passport_login
)
values
('br_root', 'br_kolpino', 'omnipotent_user'),
('br_root', 'br_moscow', 'omnipotent_user'),
('br_root', 'br_russia', 'omnipotent_user'),
('br_root', 'br_saintpetersburg', 'omnipotent_user'),
('br_root', 'br_leningradskaja_obl', 'omnipotent_user'),
('br_root', 'br_root', 'omnipotent_user'),
('br_root', 'br_saintpetersburg_adm', 'omnipotent_user'),
('br_root', 'br_severo_zapadnyj_fo', 'omnipotent_user'),
('br_root', 'br_leningradskaja_obl', 'test_user1'),
('br_root', 'br_kolpino', 'test_user1'),
('br_root', 'br_saintpetersburg', 'test_user1'),
('br_root', 'br_kolpino', 'test_user2');
