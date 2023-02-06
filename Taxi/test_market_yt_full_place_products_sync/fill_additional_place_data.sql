insert into eats_nomenclature.places (id, slug, is_enabled)
values (5, '5', true), 
       (6, '6', true);
insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 5), 
       (778, 6);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id)
values (777, 5, 10, 100, 120), 
       (778, 6, 70, 130, 150);
insert into eats_nomenclature.assortments default values; -- active for place 5 with trait_id = 1 (default assorment)
insert into eats_nomenclature.assortments default values; -- active for place 5 with trait_id = null (not default assorment)
insert into eats_nomenclature.assortments default values; -- active for place 6 with trait_id = null (default assorment)
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_2');

insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (5, 4, null, 2),
       (5, 5, null, null),
       (6, 6, null, null);

insert into eats_nomenclature.place_default_assortments(place_id, trait_id)
values (5, 2);

-- Items

-- uq: place_id, product_id
insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat)
values (5, 1, 'item_origin_1', null, null, null, null, null, null),
       (5, 2, 'item_origin_2', 999, 10, null, null, null, 10),
       (5, 3, 'item_origin_3', 100, 50, 200, 150, '2017-01-08 04:05:06', 12),
       (6, 2, 'item_origin_2', 999, 10, null, null, null, 10);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (11, 0), 
       (12, 20),
       (13, 0),
       (14, 20);

insert into eats_nomenclature.categories (assortment_id, name, public_id, is_base)
values (4, 'category_1', 1, true),
       (4, 'category_2', 2, true),
       (4, 'category_3', 3, true),
       (4, 'category_4', 4, true),
       (4, 'category_8', 8, false),
       (6, 'category_2', 2, true);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (4, 12, 1),
       (4, 12, 2),
       (4, 15, 2),
       (4, 15, 3),
       (4, 16, 1),
       (4, 16, 2),
       (6, 17, 2);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values (4, 12, null),
       (4, 13, null),
       (4, 14, 13),
       (4, 15, 14),
       (4, 16, null),
       (6, 17, null);
