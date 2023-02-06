INSERT INTO catalog_wms.cursors (name, cursor, updated)
VALUES ('/api/external/assortments/v1/list',
        'wms_assortment_cursor',
        '2020-08-11T08:14:04.714975+00:00');

INSERT INTO catalog_wms.cursors (name, cursor, updated)
VALUES ('/api/external/assortments/v1/products',
        'wms_assortment_items_cursor',
        '2020-08-11T08:14:04.714975+00:00');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/stores/v1/list', 'wms_depots_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/products/v1/groups', 'wms_groups_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/products/v1/products', 'wms_products_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/price_lists/v1/list', 'wms_price_list_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/price_lists/v1/products', 'wms_price_list_item_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/products/v1/stocks', 'wms_stock_cursor');

INSERT INTO catalog_wms.cursors (name, cursor)
VALUES ('/api/external/companies/v1/list', 'wms_companies_cursor');

INSERT INTO catalog_wms.cursors AS c (name, cursor)
VALUES ('/api/external/assortments/v1/products', 'wms_assortment_items_cursor_2')
ON CONFLICT(name)
DO UPDATE SET
    cursor = EXCLUDED.cursor
WHERE c.name = EXCLUDED.name
