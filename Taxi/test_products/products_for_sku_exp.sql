insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, volume, yt_updated_at, сarbohydrates, proteins, fats, calories, expiration_info)
values ( 1,
         'Состав1',
         ('Хранить в сухом месте при температуре не более +25°С'),
         'f4e3f17d-607c-47a3-9235-3e883b048276',
         'Альтернативное имя1',
         11,
         '2019-11-16 14:20:16.653015+0000', '11.1 г', '12.2 г', '13.3 г', '111.1 ккал', '100 д');

update eats_nomenclature.products
set sku_id = 1
where id = 401
