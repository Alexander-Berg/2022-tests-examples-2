-- Transform uuids to WMS-like strings with suffixes
-- This is to distinguish WMS goods/categories ids from 1C ones
CREATE OR REPLACE FUNCTION wmsify(in_id TEXT, suffix TEXT) RETURNS TEXT AS 
$BODY$
BEGIN
    RETURN REGEXP_REPLACE(in_id, '-', '', 'g') || suffix;       
END
$BODY$
    LANGUAGE PLPGSQL;

-- First populate eats mappings before modifying goods ids for 1C depots in WMS
INSERT INTO catalog.eats_goods_mappings(depot_id, product_id, category_id, eats_id)
SELECT d.external_id::BIGINT,
       gc.product_id,
       wmsify(gc.category_id, 'WMSCAT'),
       -- 10000 here is required not to conflict with 1C eats ids mappings
       10000 + row_number() OVER (ORDER BY gc.product_id, gc.category_id)
FROM catalog_wms.depots d,
     catalog_wms.goods_categories gc;

INSERT INTO catalog.eats_categories_mappings(depot_id, category_id, eats_category_id)
SELECT d.external_id::BIGINT,
       wmsify(c.category_id, 'WMSCAT'),
       row_number() OVER (ORDER BY c.category_id)
FROM catalog_wms.depots d,
     catalog_wms.categories c;

-- category_id
UPDATE catalog_wms.depots
   SET root_category_id = wmsify(root_category_id, 'WMSCAT');

UPDATE catalog_wms.categories
   SET category_id = wmsify(category_id, 'WMSCAT'),
       parent_id   = wmsify(parent_id, 'WMSCAT');

UPDATE catalog_wms.goods_categories
   SET product_id  = wmsify(product_id, 'WMSGOOD'),
       category_id = wmsify(category_id, 'WMSCAT');

-- product_id
UPDATE catalog_wms.goods
   SET product_id  = wmsify(product_id, 'WMSGOOD');

UPDATE catalog_wms.assortment_items
   SET product_id  = wmsify(product_id, 'WMSGOOD');

UPDATE catalog_wms.price_list_items
   SET product_id  = wmsify(product_id, 'WMSGOOD');

UPDATE catalog_wms.stocks
   SET product_id  = wmsify(product_id, 'WMSGOOD');

-- Populate eats mappings for WMS product ids
INSERT INTO catalog.eats_goods_mappings(depot_id, product_id, category_id, eats_id)
SELECT d.external_id::BIGINT,
       gc.product_id,
       gc.category_id,
       -- 20000 here is required not to conflict with other eats ids mappings
       20000 + row_number() OVER (ORDER BY gc.product_id, gc.category_id)
FROM catalog_wms.depots d,
     catalog_wms.goods_categories gc;

DROP FUNCTION wmsify(TEXT,TEXT);
