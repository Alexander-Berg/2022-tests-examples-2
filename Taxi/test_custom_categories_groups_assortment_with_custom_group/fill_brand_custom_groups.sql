insert into eats_nomenclature.brands (id) values (1), (2);
insert into eats_nomenclature.places (id, slug) values (1, 'slug'), (2, 'slug2');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (1, 2);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- active for place 2
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, null), (2, 2, null);

insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'test_1'),
       (1, 'default_assortment');

insert into eats_nomenclature.custom_categories_groups (id, public_id, name)
values (1, '11111111111111111111111111111111', 'custom_group_1'),
       (2, '22222222222222222222222222222222', 'custom_group_2'),
       (3, '33333333333333333333333333333333', 'custom_group_3'),
       (4, '44444444444444444444444444444444', 'custom_group_4'),
       (5, '55555555555555555555555555555555', 'custom_group_5'),
       (6, '66666666666666666666666666666666', 'custom_group_6'),
       (7, '77777777777777777777777777777777', 'custom_group_7');

insert into eats_nomenclature.brands_custom_categories_groups (brand_id, custom_categories_group_id, sort_order, trait_id)
values (1, 3, 200, 1),
       (1, 4, 300, 1),
       (1, 5, 100, 1),
       (1, 6, 100, 1),
       (1, 3, 200, 2),
       (1, 4, 300, 2),
       (1, 5, 100, 2),
       (1, 6, 100, 2);
