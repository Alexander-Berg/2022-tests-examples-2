insert into eats_nomenclature.places (id, slug, is_enabled) values (2, '2', true);

insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 2);

insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (2, 1, 2);

insert into eats_nomenclature.places_products(id, place_id, product_id, origin_id, price, vat, available_from)
values (101, 2, 4, 'item_origin_4', 999, 50, '2020-12-12 14:27:48.607413');

insert into eats_nomenclature.stocks (place_product_id, value)
values (101, 15);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 2, 1, 0),
       (1, 2, 2, 0),
       (1, 2, 3, 0),
       (1, 2, 4, 0),
       (1, 2, 5, 0);
