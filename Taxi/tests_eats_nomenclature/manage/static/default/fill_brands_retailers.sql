-- Insert brands and retailers

insert into eats_nomenclature.retailers (id, name, slug) values (1, 'Замечательный', 'zamechatelniy');

insert into eats_nomenclature.brands (id, retailer_id, is_enabled) values (777, 1, true);
insert into eats_nomenclature.brands (id, is_enabled) values (778, false);
insert into eats_nomenclature.brands (id) values (779);
