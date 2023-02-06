insert into eats_nomenclature.vendors (name, country)
values
    ('vendor_1', 'country_1')
;

insert into eats_nomenclature.sku (uuid, alternate_name, is_alcohol, is_fresh, is_adult)
values
    ('00000000-0000-0000-0000-000000000001', 'alternate_name', true, true, true)
;

insert into eats_nomenclature.products(
    origin_id,
    name,
    public_id,
    sku_id,
    description,
    shipping_type_id,
    vendor_id,
    quantum,
    measure_unit_id,
    measure_value,
    volume_unit_id,
    volume_value,
    adult,
    is_catch_weight,
    is_choosable,
    brand_id,
    marking_type_id,
    package_info
)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 1, 'desc',1,1,1.0,1,100,1,100,false,true,true,1, 1,'package'),
    ('origin_id_2','name_2', '00000000-0000-0000-0000-000000000002', 1, 'desc',1,1,1.0,1,100,1,100,false,true,true,1, 1,'package')
;

insert into eats_nomenclature.pictures(url, processed_url)
values
    ('1_1_raw','1_1_processed'),
    ('1_2_raw','1_2_processed'),
    ('2_1_raw','2_1_processed'),
    ('2_2_raw','2_2_processed')
;

insert into eats_nomenclature.product_pictures(product_id, picture_id)
values
    (1,1),
    (1,2),
    (2,3),
    (2,4)
;

insert into eats_nomenclature.barcodes(value, unique_key, barcode_type_id, barcode_weight_encoding_id)
values
    ('1_1','1_1',1,1),
    ('1_2','1_2',1,1),
    ('2_1','2_1',1,1),
    ('2_2','2_2',1,1)
;

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values
    (1,1),
    (1,2),
    (2,3),
    (2,4)
;

insert into eats_nomenclature.product_brands(value, value_uuid)
values
    ('product_brand','00000000-0000-0000-0000-000000000001')
;

insert into eats_nomenclature.product_types(value, value_uuid)
values
    ('product_type','00000000-0000-0000-0000-000000000001')
;

insert into eats_nomenclature.overriden_product_attributes(product_id, product_brand_id, product_type_id)
values
    (1, 1, 1),
    (2, 1, 1)
;

insert into eats_nomenclature.categories_products(assortment_id,category_id,product_id,sort_order)
values
    (1, 1, 1, 1),
    (1, 1, 2, 1)
;
