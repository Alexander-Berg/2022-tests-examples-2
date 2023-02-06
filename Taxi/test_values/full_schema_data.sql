insert into eats_nomenclature.vendors (name, country)
values
    ('vendor_1', '')
;

insert into eats_nomenclature.products(origin_id,name, public_id,shipping_type_id,vendor_id,quantum,measure_unit_id,measure_value,adult,is_catch_weight,is_choosable,brand_id)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 1,1,1.0,1,100,false,false,true,1),
    ('origin_id_2','name_2', '00000000-0000-0000-0000-000000000002', 1,1,1.0,1,100,false,false,true,1)
;

insert into eats_nomenclature.pictures(url, processed_url)
values
    ('1_raw','1_processed'),
    ('2_raw','2_processed'),
    ('3_raw','3_processed'),
    ('4_raw','4_processed')
;

insert into eats_nomenclature.tags (id, name)
values (default, 'Тег 1'),
       (default, 'Тег 2');

insert into eats_nomenclature.custom_categories(id, name, description, external_id)
values (11, 'custom category 1', 'abc', 1),
       (22, 'custom category 2', 'def', 2);

insert into eats_nomenclature.custom_category_tags(custom_category_id, tag_id)
values (11, 1),
       (22, 1),
       (22, 2);

insert into eats_nomenclature.categories_dictionary (id, name)
values
    (1, 'category_1'),
    (2, 'category_2'),
    (3, 'category_3'),
    (4, 'category_4')
;

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id, is_base, is_custom, custom_category_id)
values
    (1, 'category_1', 'category_1_origin', 1, true, false, 11),
    (1, 'category_2', 'category_2_origin', 2, true, false, 22),
    (1, 'category_3', 'category_3_origin', 3, true, false, null),
    (1, 'category_4', 'category_4_origin', 4, true, false, null)
;

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id, sort_order)
values
    (1, 1, null, 1),
    (1, 2, 1, 2),
    (1, 3, 2, 3),
    (1, 4, 2, 4)
;

insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4)
;

insert into eats_nomenclature.categories_products(assortment_id,category_id,product_id,sort_order)
values
    (1, 3, 1, 1),
    (1, 3, 2, 2),
    (1, 4, 1, 1),
    (1, 4, 2, 2)
;
