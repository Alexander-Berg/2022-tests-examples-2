insert into crm_admin.geo_hierarchy_countries (node_id, name_ru) values
('br_azerbaijan', 'Азербайджан'),
('br_belarus', 'Белоруссия'),
('br_russia', 'Россия');

insert into crm_admin.geo_hierarchy_zones (node_id, name_ru, tz_country_node_id, node_type) values
('br_bobruisk', 'Бобруйск', 'br_belarus', 'agglomeration'),
('br_brest', 'Брест', 'br_belarus', 'agglomeration'),
('br_cherepovets', 'Череповец', 'br_russia', 'agglomeration'),
('br_blagoveshchensk', 'Благовещенск', 'br_russia', 'agglomeration'),
('br_brjanskaja_obl', 'Брянская область', 'br_belarus', 'node'),
('br_baku', 'Баку', 'br_azerbaijan', 'agglomeration');
