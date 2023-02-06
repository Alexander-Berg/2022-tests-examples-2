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
('br_arsk','br_root','agglomeration','br_root','RU_50K-','Арск','Arsk','arsk',True),
  ('br_vladivostok','br_root','agglomeration','br_root','RU_500K+','Владивосток','Vladivostok','vladivostok',true);
