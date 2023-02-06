insert into eats_nomenclature.sku(uuid, alternate_name)
values
    ('11111111-1111-1111-1111-111111111111', 'alternate_name_1')
;

insert into eats_nomenclature.products(origin_id, name, public_id, brand_id, sku_id)
values
    ('origin_id_1','name_1', '00000000-0000-0000-0000-000000000001', 1, 1)
;

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, available_from)
values
    (1, 1, 'origin_id_1', 100, now())
;

insert into eats_nomenclature.stocks(place_product_id, value)
values
    (1, 50)
;
