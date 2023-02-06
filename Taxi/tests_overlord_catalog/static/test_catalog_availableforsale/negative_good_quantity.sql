DELETE FROM catalog_wms.stocks
WHERE depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'
        AND product_id = '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3';

INSERT INTO catalog_wms.stocks (depot_id, product_id, updated, depleted, in_stock)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '62a03ba5-c417-11e9-b7ff-ac1f6b8569b3',
        '2019-12-01 01:01:02.000000+00',
        '2019-12-01 01:01:03.000000+00',
        -1.0);

