---------------------------------
-- VAT и натуральные показатели
---------------------------------
DROP TABLE IF EXISTS {stg_vat_n_cnt};
CREATE TABLE {stg_vat_n_cnt}
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id
    , (e.vat_value_lcy / cr.lcl_to_rub)::NUMERIC AS vat_value_lcy
    , e.internal_delivery_cnt::BIGINT
    , e.market_delivery_w_upsale_cnt::BIGINT
    , e.market_delivery_wo_upsale_cnt::BIGINT
    , e.parcel_market_cnt::BIGINT
    , e.order_cnt::BIGINT
  FROM {stg_agg_pnl_enriched} AS e
  LEFT JOIN {stg_currency_rate} AS cr
    ON cr.lcl_currency_rate_dt = e.lcl_calculation_dt AND cr.country_name = e.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_vat_n_cnt};
GRANT ALL ON {stg_vat_n_cnt} TO "ed-avetisyan";
GRANT ALL ON {stg_vat_n_cnt} TO agabitashvili;
GRANT ALL ON {stg_vat_n_cnt} TO "robot-lavka-analyst";
