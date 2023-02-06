insert into eats_nomenclature.custom_categories_groups (id, public_id, name)
values (1, '11111111111111111111111111111111', 'custom_group_1'),
       (2, '22222222222222222222222222222222', 'custom_group_2'),
       (3, '33333333333333333333333333333333', 'custom_group_3'),
       (4, '44444444444444444444444444444444', 'custom_group_4'),
       (5, '55555555555555555555555555555555', 'custom_group_5'),
       (6, '66666666666666666666666666666666', 'custom_group_6');

insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1');

insert into eats_nomenclature.brands_custom_categories_groups (brand_id, custom_categories_group_id, trait_id)
values (777, 1, 1),
       (777, 2, 1),
       (777, 3, 1),
       (777, 4, 1);
