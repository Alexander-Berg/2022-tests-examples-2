insert into eats_nomenclature.products(origin_id,name, public_id,description,shipping_type_id,vendor_id,quantum,measure_unit_id,measure_value,volume_unit_id,adult,is_catch_weight,is_choosable,brand_id)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 'desc',1,1,1.0,1,100,null,false,false,true,1),
    ('origin_id_2','name_2', '00000000-0000-0000-0000-000000000002', 'desc',1,1,1.0,1,100,null,false,false,true,1)
;

insert into eats_nomenclature.barcodes(unique_key,value, barcode_weight_encoding_id)
values
    ('1_1', '1_1', null),
    ('2_1', '2_1', null)
;

insert into eats_nomenclature.product_barcodes(product_id,barcode_id)
values
    (1, 1),
    (2, 2)
;

insert into eats_nomenclature.categories_products(assortment_id,category_id,product_id,sort_order)
values
    (1, 1, 1, 1),
    (1, 1, 2, 1)
;

insert into eats_nomenclature.places_products(place_id,product_id,origin_id,price,old_price,vendor_code,available_from)
values
    (1,1,'origin_id_1',100,null,'1',now()),
    (1,2,'origin_id_2',100,null,'2',now())
;
