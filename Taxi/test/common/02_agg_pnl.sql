/*==================================================
 Собираем agg_lavka_pnl с регионами
==================================================*/
-- Сначала берем agg_lavka_order
CREATE TEMPORARY TABLE agg_order
ON COMMIT DROP
AS (
  SELECT lcl_order_created_dt
    , region_id
    , place_id
    , order_cnt
    , internal_delivery_cnt
    , market_delivery_w_upsale_cnt
    , market_delivery_wo_upsale_cnt
    , parcel_market_cnt
  FROM {agg_lavka_order_daily}
) DISTRIBUTED BY (lcl_order_created_dt, region_id, place_id);
ANALYZE agg_order;

-- Затем agg_lavka_finance
CREATE TEMPORARY TABLE agg_finance
ON COMMIT DROP
AS (
  SELECT lcl_event_dt
    , region_id
    , place_id
    , gmv_w_vat_lcy
    , vat_lcy
    , revenue_from_sales_wo_vat_lcy
    , delivery_fee_w_vat_lcy
    , incentives_discount_wo_vat_lcy
    , incentives_promocode_wo_vat_lcy
    , incentives_cashback_added_amt
    , transaction_for_acquiring_w_vat_lcy
  FROM {agg_lavka_finance_daily}
) DISTRIBUTED BY (lcl_event_dt, region_id, place_id);
ANALYZE agg_finance;

-- Джоиним dmlo и тлог
CREATE TEMPORARY TABLE agg_pnl
ON COMMIT DROP
AS (
  SELECT COALESCE(o.lcl_order_created_dt, f.lcl_event_dt) AS lcl_event_dt
    , COALESCE(o.region_id, f.region_id)                  AS region_id
    , COALESCE(o.place_id, f.place_id)                    AS place_id
    , COALESCE(o.order_cnt, 0)                            AS order_cnt
    , COALESCE(o.internal_delivery_cnt, 0)                AS internal_delivery_cnt
    , COALESCE(o.market_delivery_w_upsale_cnt, 0)         AS market_delivery_w_upsale_cnt
    , COALESCE(o.market_delivery_wo_upsale_cnt, 0)        AS market_delivery_wo_upsale_cnt
    , COALESCE(o.parcel_market_cnt, 0)                    AS parcel_market_cnt
    , COALESCE(f.gmv_w_vat_lcy, 0)                        AS gmv_w_vat_lcy
    , COALESCE(f.vat_lcy, 0)                              AS vat_lcy
    , COALESCE(f.revenue_from_sales_wo_vat_lcy, 0)        AS revenue_from_sales_wo_vat_lcy
    , COALESCE(f.delivery_fee_w_vat_lcy, 0)               AS delivery_fee_w_vat_lcy
    , COALESCE(f.incentives_discount_wo_vat_lcy, 0)       AS incentives_discount_wo_vat_lcy
    , COALESCE(f.incentives_promocode_wo_vat_lcy, 0)      AS incentives_promocode_wo_vat_lcy
    , COALESCE(f.incentives_cashback_added_amt, 0)        AS incentives_cashback_added_amt
    , COALESCE(f.transaction_for_acquiring_w_vat_lcy, 0)  AS transaction_for_acquiring_w_vat_lcy
  FROM agg_order AS o
  FULL JOIN agg_finance AS f
       ON o.lcl_order_created_dt = f.lcl_event_dt
         AND o.region_id = f.region_id
         AND o.place_id = f.place_id
) DISTRIBUTED BY (lcl_event_dt, region_id, place_id);
ANALYZE agg_pnl;

-- Получаем итоговую табличку
DROP TABLE IF EXISTS {stg_agg_pnl_w_regions};
CREATE TABLE {stg_agg_pnl_w_regions}
AS (
  SELECT p.lcl_event_dt
    , s.country_name
    , s.region_name
    , s.region_id
    , p.place_id
    , date_trunc('month', p.lcl_event_dt)::DATE                                                 AS month_dt
    , EXTRACT(
        DAYS FROM date_trunc('month', p.lcl_event_dt) + '1 month - 1 day'::INTERVAL
      )                                                                                         AS days_in_month
    , EXTRACT(
        DAYS FROM
          CASE WHEN date_trunc('month', p.lcl_event_dt) = date_trunc('month', CURRENT_DATE - 1)
            THEN CURRENT_DATE - 1
            ELSE (date_trunc('month', p.lcl_event_dt) + '1 month - 1 day'::INTERVAL)::DATE
          END
      )                                                                                         AS days_in_month_passed
    , p.order_cnt
    , p.internal_delivery_cnt
    , p.market_delivery_w_upsale_cnt
    , p.market_delivery_wo_upsale_cnt
    , p.parcel_market_cnt
    , p.gmv_w_vat_lcy
    , p.vat_lcy
    , p.revenue_from_sales_wo_vat_lcy
    , p.delivery_fee_w_vat_lcy
    , p.incentives_discount_wo_vat_lcy
    , p.incentives_promocode_wo_vat_lcy
    , p.incentives_cashback_added_amt
    , p.transaction_for_acquiring_w_vat_lcy
  FROM agg_pnl AS p
  JOIN {stg_store} AS s
    ON p.place_id = s.store_id
  WHERE p.lcl_event_dt <= CURRENT_DATE - 1
) DISTRIBUTED BY (lcl_event_dt, region_name, place_id);
ANALYZE {stg_agg_pnl_w_regions};
GRANT ALL ON {stg_agg_pnl_w_regions} TO "ed-avetisyan";
GRANT ALL ON {stg_agg_pnl_w_regions} TO agabitashvili;
GRANT ALL ON {stg_agg_pnl_w_regions} TO "robot-lavka-analyst";
