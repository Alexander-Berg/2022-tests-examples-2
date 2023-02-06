insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.products (id, origin_id, name, public_id, quantum, brand_id)
values (1, 'origin_1', 'Place-1_Префикс-1_1', '11111111-1111-1111-1111-111111111111', 0.1, 1),
       (2, 'origin_2', 'Place-1_Префикс-1_2', '22222222-2222-2222-2222-222222222222', 0.1, 1),
       (3, 'origin_3', 'Place-1_Префикс-2_1', '33333333-3333-3333-3333-333333333333', 0.1, 1);

insert into eats_nomenclature.sku (id, uuid, alternate_name)
values (1, '11111111-1111-1111-1111-111111111111', 'name1'),
    (2, '22222222-2222-2222-2222-222222222222', 'name2'),
    (3, '33333333-3333-3333-3333-333333333333', 'name3');
