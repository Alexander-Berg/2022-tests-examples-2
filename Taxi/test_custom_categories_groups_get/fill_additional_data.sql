insert into eats_nomenclature.pictures (url, processed_url)
values ('url_4', 'url_4'),
       ('url_5', null),
       ('url_6', 'url_6'),
       ('url_7', 'url_7');

insert into eats_nomenclature.product_pictures (product_id, picture_id, updated_at)
values (1, 4, '2021-04-20 10:00:00'),
       (1, 5, '2021-04-21 12:00:00'), -- won't be taken because of null processed_url
       (2, 6, '2021-04-23 15:00:00'),
       (2, 7, '2021-04-24 16:00:00');
