insert into eats_rest_menu_storage.brands (id) values (1);
insert into eats_rest_menu_storage.places(
    id, brand_id, slug
) values (1, 1, 'slug1');

--pictures
insert into eats_rest_menu_storage.pictures (
    url, ratio
) values
    ('url1', 1.0),
    ('url2', 0.5),
    ('url3', 1.0),
    ('url30', null);
