insert into eats_nomenclature.brands (id) values (1);

insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'test_1'),
       (1, 'test_2');

insert into eats_nomenclature.custom_categories_groups (id, public_id, name, description)
values (1, '11111111111111111111111111111111', 'custom_group_1', 'description_1'),
       (2, '22222222222222222222222222222222', 'custom_group_2', 'description_2'),
       (3, '33333333333333333333333333333333', 'custom_group_3', 'description_3');
