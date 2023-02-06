BEGIN TRANSACTION;

INSERT INTO catalog_wms.categories(category_id, external_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('master-RU', 'master', 'active', 'Корень 1', 'Корневая категория RU', 0, null, '{}', '{}'),
('master-RU-child', 'master:child', 'active', 'Корень 1', 'дочерняя категория RU', 0, 'master-RU', '{}', '{}'),
('master-IL', 'master:IL', 'active', 'Корень 2', 'Корневая категория IL', 97, null, '{}', '{}'),
('master-IL-child', 'master:child-il', 'active', 'Корень 1', 'дочерняя категория IL', 0, 'master-IL', '{}', '{}')
;

COMMIT TRANSACTION;
