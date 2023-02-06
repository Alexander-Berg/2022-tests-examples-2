insert into eats_products.brand (brand_id, slug, is_enabled)
values (5, 'slug5', True),
       (6, 'slug6', True),
       (7, 'slug7', False);

insert into eats_products.place (place_id, slug, brand_id, is_enabled)
values (1, 'place1', 5, True),
       (5, 'place5', 5, True),
       (6, 'place6', 6, False),
       (7, 'place7', 7, True),
       (8, 'place_to_change_brand', 7, True);
