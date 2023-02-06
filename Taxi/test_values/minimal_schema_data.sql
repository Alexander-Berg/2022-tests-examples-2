insert into eats_nomenclature.vendors (name, country)
values
    ('vendor_1', '')
;

insert into eats_nomenclature.products(origin_id,name, public_id,shipping_type_id,vendor_id,quantum,measure_unit_id,measure_value,adult,is_catch_weight,is_choosable,brand_id)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 1,1,1.0,1,100,false,false,true,1)
;


insert into eats_nomenclature.categories_dictionary (id, name)
values
    (1, 'category_1')
;

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id)
values
    (1, 'category_1', 'category_1_origin', 1);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values
    (1, 1, null)
;

insert into eats_nomenclature.categories_products(assortment_id,category_id,product_id)
values
    (1, 1, 1)
;
