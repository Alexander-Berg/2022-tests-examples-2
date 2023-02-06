INSERT INTO catalog_wms.categories(category_id, external_id, status, name, description, rank, parent_id, images, legal_restrictions, deep_link)
VALUES
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'external-id-1', 'active', 'Корень 1', 'Корневая категория', 0, null, array[]::text[], array[]::text[], null),
('73fa0267-8519-485a-9e06-5e18a9a7514c', 'external-id-2', 'active', 'Завтрак', 'Завтрак - описание', 173, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', '{"zavtrak_template.jpg"}', '{}', 'breakfast'),
('61d24b27-0e8e-4173-a861-95c87802972f', null, 'active', 'Яйца', 'Яйца - описание', 97, '73fa0267-8519-485a-9e06-5e18a9a7514c', '{"eggs_template.jpg"}', '{}', null)
;
