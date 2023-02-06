insert into eats_nomenclature.retailers (id, name, slug)
values (1, 'retailer_name_1', 'retailer_slug_1'),
       (2, 'retailer_name_2', 'retailer_slug_2');

insert into eats_nomenclature.brands (id, slug, retailer_id)
values (1, 'brand_slug_1', 1), (2, 'brand_slug_2', 2);

insert into eats_nomenclature.sku (id, uuid, alternate_name, weight, volume)
values (1, 'sku_uuid_1', 'sku_name_1', '100 г', '100 мл'),
       (2, 'sku_uuid_2', 'sku_name_2', '200 г', null),
       (3, 'sku_uuid_3', 'sku_name_3', null, null);

insert into eats_nomenclature.pictures (id, url, processed_url)
values (1, 'picture_url_1', 'picture_url_1'),
       (2, 'picture_url_2', 'picture_url_2'),
       (3, 'picture_url_3', 'picture_url_3'),
       (4, 'picture_url_4', 'picture_url_4'),
       (5, 'picture_url_5', 'picture_url_5');

insert into eats_nomenclature.sku_pictures (sku_id, picture_id, retailer_name)
values (1, 1, 'retailer_slug_1'),
       (2, 2, 'retailer_slug_1'),
       (1, 3, 'retailer_slug_2'),
       (2, 4, 'retailer_slug_2'),
       (3, 5, 'retailer_slug_2');
