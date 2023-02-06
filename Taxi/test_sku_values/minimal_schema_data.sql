insert into eats_nomenclature.vendors (name, country)
values
    ('vendor_1', '')
;

insert into eats_nomenclature.sku (uuid, alternate_name)
values
    ('00000000-0000-0000-0000-000000000001', 'alternate_name')
;

insert into eats_nomenclature.products (origin_id,name, public_id,sku_id,shipping_type_id,vendor_id,quantum,measure_unit_id,measure_value,adult,is_catch_weight,is_choosable,brand_id)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 1,1,1,1.0,1,100,false,false,true,1)
;

insert into eats_nomenclature.categories_products (assortment_id,category_id,product_id,sort_order)
values
    (1, 1, 1, 1)
;
