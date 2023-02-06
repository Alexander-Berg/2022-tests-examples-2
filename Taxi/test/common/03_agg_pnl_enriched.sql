/*=================================================================
 Обогащаем agg_pnl так, чтобы данных хватило для расчета статей
=================================================================*/
DROP TABLE IF EXISTS {stg_agg_pnl_enriched};
CREATE TABLE {stg_agg_pnl_enriched}
AS (
  SELECT p.lcl_event_dt                                                       AS lcl_calculation_dt
    , p.country_name
    , p.region_name
    , p.region_id
    , p.place_id                                                              AS store_id
    , p.month_dt
    , p.days_in_month
    , p.days_in_month_passed
    , p.gmv_w_vat_lcy                                                         AS gmv_value_lcy
    , SUM(p.gmv_w_vat_lcy) OVER w                                             AS gmv_full_month_value_lcy
    , rv.gmv_reserve_value_lcy
    , p.revenue_from_sales_wo_vat_lcy                                         AS revenue_from_sales_value_lcy
    , SUM(p.revenue_from_sales_wo_vat_lcy) OVER w                             AS revenue_from_sales_full_month_value_lcy
    , rv.gross_revenue_sales_reserve_value_lcy                                AS revenue_from_sales_reserve_value_lcy
    , p.delivery_fee_w_vat_lcy                                                AS delivery_fee_value_lcy
    , SUM(p.delivery_fee_w_vat_lcy) OVER w                                    AS delivery_fee_full_month_value_lcy
    , rv.gross_revenue_delivery_fee_reserve_value_lcy                         AS delivery_fee_reserve_value_lcy
    , ABS(p.incentives_discount_wo_vat_lcy)                                   AS incentives_discount_value_lcy
    , ABS(p.incentives_promocode_wo_vat_lcy)                                  AS incentives_promocode_value_lcy
    , ABS(p.incentives_cashback_added_amt)                                    AS incentives_cashback_amt
    , ABS(p.incentives_discount_wo_vat_lcy)
        + ABS(p.incentives_promocode_wo_vat_lcy)
        + ABS(p.incentives_cashback_added_amt)                                AS incentives_value_lcy
    , SUM(
        ABS(p.incentives_discount_wo_vat_lcy)
          + ABS(p.incentives_promocode_wo_vat_lcy)
          + ABS(p.incentives_cashback_added_amt)
      ) OVER w                                                                AS incentives_full_month_value_lcy
    , rv.incentives_total_reserve_value_lcy                                   AS incentives_reserve_value_lcy
    , COALESCE(gc.packaging_per_order_lcy, 0)
        * (p.order_cnt - p.market_delivery_wo_upsale_cnt)                     AS packaging_value_lcy
    , COALESCE(gc.packaging_per_order_lcy, 0)
        * SUM(p.order_cnt - p.market_delivery_wo_upsale_cnt) OVER w           AS packaging_full_month_value_lcy
    , rv.packaging_reserve_value_lcy
    , COALESCE(gc.insurance_and_sms_per_order_lcy, 0)
        * (p.order_cnt - p.internal_delivery_cnt)                             AS insurance_and_sms_value_lcy
    , COALESCE(gc.insurance_and_sms_per_order_lcy, 0)
        * SUM(p.order_cnt - p.internal_delivery_cnt) OVER w                   AS insurance_and_sms_full_month_value_lcy
    , rv.insurance_reserve_value_lcy
    , rv.sms_reserve_value_lcy
    , COALESCE(gc.last_mile_revenue_per_item_lcy, 0)
        * p.parcel_market_cnt                                                 AS last_mile_income_value_lcy
    , COALESCE(gc.last_mile_revenue_per_item_lcy, 0)
        * SUM(p.parcel_market_cnt) OVER w                                     AS last_mile_income_full_month_value_lcy
    , rv.last_mile_revenue_reserve_value_lcy                                  AS last_mile_income_reserve_value_lcy
    , gc.acquiring_per_gmv_less_incentives_shr
        * (p.transaction_for_acquiring_w_vat_lcy
             - ABS(p.incentives_discount_wo_vat_lcy)
             - ABS(p.incentives_promocode_wo_vat_lcy)
             - ABS(p.incentives_cashback_added_amt)
          )                                                                   AS acquiring_value_lcy
    , gc.acquiring_per_gmv_less_incentives_shr
        * SUM(
            p.transaction_for_acquiring_w_vat_lcy
              - ABS(p.incentives_discount_wo_vat_lcy)
              - ABS(p.incentives_promocode_wo_vat_lcy)
              - ABS(p.incentives_cashback_added_amt)
          ) OVER w                                                            AS acquiring_full_month_value_lcy
    , rv.acquiring_reserve_value_lcy
    , rv.support_reserve_value_lcy
    , rv.easy_logistics_reserve_value_lcy
    , p.vat_lcy                                                               AS vat_value_lcy
    , p.internal_delivery_cnt
    , p.market_delivery_w_upsale_cnt
    , p.market_delivery_wo_upsale_cnt
    , p.parcel_market_cnt
    , p.order_cnt
    , p.order_cnt - p.internal_delivery_cnt                                   AS clear_orders_cnt
    , SUM(p.order_cnt - p.internal_delivery_cnt) OVER w                       AS clear_orders_full_month_cnt
  FROM {stg_agg_pnl_w_regions} AS p
  LEFT JOIN {stg_general_constant} AS gc
    ON p.month_dt = gc.month_dt
    AND p.country_name = gc.country_name
  LEFT JOIN {stg_reserve} AS rv
    ON p.month_dt = rv.month_dt
    AND p.country_name = rv.country_name
  WINDOW w AS (PARTITION BY p.month_dt, p.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_agg_pnl_enriched};
GRANT ALL ON {stg_agg_pnl_enriched} TO "ed-avetisyan";
GRANT ALL ON {stg_agg_pnl_enriched} TO agabitashvili;
GRANT ALL ON {stg_agg_pnl_enriched} TO "robot-lavka-analyst";
