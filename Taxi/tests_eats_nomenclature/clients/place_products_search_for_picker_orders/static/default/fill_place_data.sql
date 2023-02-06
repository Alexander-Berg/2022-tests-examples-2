insert into eats_nomenclature.brands (id, slug) values (1, '1');
insert into eats_nomenclature.places (id, slug) values (1, '1'), (2, '2');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1),(1,2);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, null), (2, 1, null, null);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.categories_dictionary (id, name)
values (1, 'category_1');

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id)
values (1, 'category_1', 'category_1_origin', 1);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values (1, 1, null);
