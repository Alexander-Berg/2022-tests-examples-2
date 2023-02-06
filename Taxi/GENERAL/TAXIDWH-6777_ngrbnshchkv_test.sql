BEGIN;
CREATE TABLE analyst.ngrbnshchkv_tmp ON COMMIT DROP AS
SELECT distinct on ("order_order__id", utc_valid_from_dttm) "order_order__id", "courier_courier__id", "_deleted_flg", utc_valid_from_dttm
FROM (SELECT md5(''||cast("id" as varchar)||'.._..') :: uuid as "order_order__id", md5(''||cast("courier_id" as varchar)||'.._..') :: uuid as "courier_courier__id", coalesce(false, false) as "_deleted_flg"
        , date_trunc('second', "utc_business_dttm") AS utc_valid_from_dttm
        , "utc_business_dttm" AS utc_valid_from_dttm_src
        , _etl_processed_dttm

      FROM "eda_stg_bigfood"."order"
      WHERE _etl_processed_dttm > '2015-01-01'
        AND ((True  AND "id" IS NOT NULL))) t
ORDER BY "order_order__id", utc_valid_from_dttm, _etl_processed_dttm desc, utc_valid_from_dttm_src DESC, "order_order__id", "courier_courier__id", "_deleted_flg"
DISTRIBUTED BY ("order_order__id");
ANALYZE analyst.ngrbnshchkv_tmp;
COMMIT;

