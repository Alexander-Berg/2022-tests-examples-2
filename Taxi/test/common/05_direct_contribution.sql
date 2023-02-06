/*========================================================================
 ЗАКЛЮЧИТЕЛЬНАЯ ЧАСТЬ:
 - Указываем методологии
 - Проставляем флаг финансового закрытия месяца
 - И, собственно, собираем источник
========================================================================*/
-- Описываем все поля
CREATE TEMPORARY TABLE result_table (
  lcl_calculation_dt DATE NULL
  , country_name VARCHAR NULL
  , region_name VARCHAR NULL
  , store_id VARCHAR NULL
  , store_name VARCHAR NULL

  -- GMV
  , gmv_value_lcy NUMERIC NULL
  , gmv_from_finance_department_value_lcy NUMERIC NULL
  , gmv_reserve_value_lcy NUMERIC NULL
  , gmv_final_w_reserve_value_lcy NUMERIC NULL
  , gmv_final_method_name VARCHAR NULL

  -- Revenue from Sales
  , revenue_from_sales_value_lcy NUMERIC NULL
  , revenue_from_sales_from_finance_department_value_lcy NUMERIC NULL
  , revenue_from_sales_reserve_value_lcy NUMERIC NULL
  , revenue_from_sales_final_w_reserve_value_lcy NUMERIC NULL
  , revenue_from_sales_final_method_name VARCHAR NULL

  -- Delivery Fee
  , delivery_fee_value_lcy NUMERIC NULL
  , delivery_fee_from_finance_department_value_lcy NUMERIC NULL
  , delivery_fee_reserve_value_lcy NUMERIC NULL
  , delivery_fee_final_w_reserve_value_lcy NUMERIC NULL
  , delivery_fee_final_method_name VARCHAR NULL

  -- Incentives
  , incentives_discount_value_lcy NUMERIC NULL
  , incentives_promocode_value_lcy NUMERIC NULL
  , incentives_cashback_amt NUMERIC NULL
  , incentives_value_lcy NUMERIC NULL
  , incentives_from_finance_department_value_lcy NUMERIC NULL
  , incentives_reserve_value_lcy NUMERIC NULL
  , incentives_final_w_reserve_value_lcy NUMERIC NULL
  , incentives_final_method_name VARCHAR NULL

  -- Packaging
  , packaging_value_lcy NUMERIC NULL
  , packaging_from_finance_department_value_lcy NUMERIC NULL
  , packaging_reserve_value_lcy NUMERIC NULL
  , packaging_final_w_reserve_value_lcy NUMERIC NULL
  , packaging_final_method_name VARCHAR NULL

  -- Insurance and SMS
  , insurance_and_sms_value_lcy NUMERIC NULL
  , insurance_and_sms_from_finance_department_value_lcy NUMERIC NULL
  , insurance_reserve_value_lcy NUMERIC NULL
  , sms_reserve_value_lcy NUMERIC NULL
  , insurance_and_sms_reserve_value_lcy NUMERIC NULL
  , insurance_and_sms_final_w_reserve_value_lcy NUMERIC NULL
  , insurance_and_sms_final_method_name VARCHAR NULL

  -- Last Mile Income
  , last_mile_income_value_lcy NUMERIC NULL
  , last_mile_income_from_finance_department_value_lcy NUMERIC NULL
  , last_mile_income_reserve_value_lcy NUMERIC NULL
  , last_mile_income_final_w_reserve_value_lcy NUMERIC NULL
  , last_mile_income_final_method_name VARCHAR NULL

  -- Acquiring
  , acquiring_value_lcy NUMERIC NULL
  , acquiring_from_finance_department_value_lcy NUMERIC NULL
  , acquiring_reserve_value_lcy NUMERIC NULL
  , acquiring_final_w_reserve_value_lcy NUMERIC NULL
  , acquiring_final_method_name VARCHAR NULL

  -- Support
  , support_value_lcy NUMERIC NULL
  , support_from_finance_department_value_lcy NUMERIC NULL
  , support_reserve_value_lcy NUMERIC NULL
  , support_final_w_reserve_value_lcy NUMERIC NULL
  , support_final_method_name VARCHAR NULL

  -- Easy Logistics
  , easy_logistics_value_lcy NUMERIC NULL
  , easy_logistics_from_finance_department_value_lcy NUMERIC NULL
  , easy_logistics_reserve_value_lcy NUMERIC NULL
  , easy_logistics_final_w_reserve_value_lcy NUMERIC NULL
  , easy_logistics_final_method_name VARCHAR NULL

  -- Other Revenue
  , other_revenue_value_lcy NUMERIC NULL
  , other_revenue_from_finance_department_value_lcy NUMERIC NULL
  , other_revenue_reserve_value_lcy NUMERIC NULL
  , other_revenue_final_w_reserve_value_lcy NUMERIC NULL
  , other_revenue_final_method_name VARCHAR NULL

  -- Central Warehouse and Transport
  , cwh_var_value_lcy NUMERIC NULL
  , cwh_fixed_value_lcy NUMERIC NULL
  , cwh_value_lcy NUMERIC NULL
  , cwh_from_finance_department_value_lcy NUMERIC NULL
  , cwh_reserve_value_lcy NUMERIC NULL
  , cwh_final_w_reserve_value_lcy NUMERIC NULL
  , cwh_final_method_name VARCHAR NULL

  -- Courier Logistics
  , courier_logistics_value_lcy NUMERIC NULL
  , courier_logistics_from_finance_department_value_lcy NUMERIC NULL
  , courier_logistics_reserve_value_lcy NUMERIC NULL
  , courier_logistics_final_w_reserve_value_lcy NUMERIC NULL
  , courier_logistics_final_method_name VARCHAR NULL

  -- COGS
  , cogs_value_lcy NUMERIC NULL
  , cogs_permanent_reserve_value_lcy NUMERIC NULL
  , cogs_from_finance_department_value_lcy NUMERIC NULL
  , cogs_reserve_value_lcy NUMERIC NULL
  , cogs_final_w_reserve_value_lcy NUMERIC NULL
  , cogs_final_method_name VARCHAR NULL

  -- Writeoffs
  , writeoffs_value_lcy NUMERIC NULL
  , writeoffs_permanent_reserve_value_lcy NUMERIC NULL
  , writeoffs_from_finance_department_value_lcy NUMERIC NULL
  , writeoffs_reserve_value_lcy NUMERIC NULL
  , writeoffs_final_w_reserve_value_lcy NUMERIC NULL
  , writeoffs_final_method_name VARCHAR NULL

  -- Courier Acquisition
  , courier_acquisition_value_lcy NUMERIC NULL
  , courier_acquisition_from_finance_department_value_lcy NUMERIC NULL
  , courier_acquisition_reserve_value_lcy NUMERIC NULL
  , courier_acquisition_final_w_reserve_value_lcy NUMERIC NULL
  , courier_acquisition_final_method_name VARCHAR NULL

  -- Other Logistics
  , other_logistics_value_lcy NUMERIC NULL
  , other_logistics_from_finance_department_value_lcy NUMERIC NULL
  , other_logistics_reserve_value_lcy NUMERIC NULL
  , other_logistics_final_w_reserve_value_lcy NUMERIC NULL
  , other_logistics_final_method_name VARCHAR NULL

  -- Transport
  , transport_value_lcy NUMERIC NULL
  , transport_from_finance_department_value_lcy NUMERIC NULL
  , transport_reserve_value_lcy NUMERIC NULL
  , transport_final_w_reserve_value_lcy NUMERIC NULL
  , transport_final_method_name VARCHAR NULL

  -- Rents
  , rents_value_lcy NUMERIC NULL
  , rents_from_finance_department_value_lcy NUMERIC NULL
  , rents_reserve_value_lcy NUMERIC NULL
  , rents_final_w_reserve_value_lcy NUMERIC NULL
  , rents_final_method_name VARCHAR NULL

  -- Utilities
  , utilities_value_lcy NUMERIC NULL
  , utilities_from_finance_department_value_lcy NUMERIC NULL
  , utilities_reserve_value_lcy NUMERIC NULL
  , utilities_final_w_reserve_value_lcy NUMERIC NULL
  , utilities_final_method_name VARCHAR NULL

  -- People Cost
  , people_cost_value_lcy NUMERIC NULL
  , people_cost_from_finance_department_value_lcy NUMERIC NULL
  , people_cost_reserve_value_lcy NUMERIC NULL
  , people_cost_final_w_reserve_value_lcy NUMERIC NULL
  , people_cost_final_method_name VARCHAR NULL

  -- VAT
  , vat_value_lcy NUMERIC NULL

  -- Натуральные показатели
  , internal_delivery_cnt BIGINT NULL
  , market_delivery_w_upsale_cnt BIGINT NULL
  , market_delivery_wo_upsale_cnt BIGINT NULL
  , parcel_market_cnt BIGINT NULL
  , order_cnt BIGINT NULL

  -- Признак закрытого месяца
  , fiscal_year_closed_period_flg BOOLEAN NULL

  -- Курсы валют для локалей
  , currency_rate_rub NUMERIC NULL
  , currency_rate_usd NUMERIC NULL
) ON COMMIT DROP
DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);

-- Собираем источник [
CREATE TEMPORARY TABLE superjoin
ON COMMIT DROP
AS (
  -- 1. Делаем суперджоин всех статей
  SELECT sd.lcl_calculation_dt
    , sd.country_name
    , sd.region_name
    , sd.store_id
    , sd.store_name
    , sd.month_dt
    , gmv.gmv_value_lcy
    , gmv.gmv_from_finance_department_value_lcy
    , gmv.gmv_reserve_value_lcy
    , gmv.gmv_final_w_reserve_value_lcy
    , res.revenue_from_sales_value_lcy
    , res.revenue_from_sales_from_finance_department_value_lcy
    , res.revenue_from_sales_reserve_value_lcy
    , res.revenue_from_sales_final_w_reserve_value_lcy
    , del.delivery_fee_value_lcy
    , del.delivery_fee_from_finance_department_value_lcy
    , del.delivery_fee_reserve_value_lcy
    , del.delivery_fee_final_w_reserve_value_lcy
    , inc.incentives_discount_value_lcy
    , inc.incentives_promocode_value_lcy
    , inc.incentives_cashback_amt
    , inc.incentives_value_lcy
    , inc.incentives_from_finance_department_value_lcy
    , inc.incentives_reserve_value_lcy
    , inc.incentives_final_w_reserve_value_lcy
    , pack.packaging_value_lcy
    , pack.packaging_from_finance_department_value_lcy
    , pack.packaging_reserve_value_lcy
    , pack.packaging_final_w_reserve_value_lcy
    , ins.insurance_and_sms_value_lcy
    , ins.insurance_and_sms_from_finance_department_value_lcy
    , ins.insurance_reserve_value_lcy
    , ins.sms_reserve_value_lcy
    , ins.insurance_and_sms_reserve_value_lcy
    , ins.insurance_and_sms_final_w_reserve_value_lcy
    , mil.last_mile_income_value_lcy
    , mil.last_mile_income_from_finance_department_value_lcy
    , mil.last_mile_income_reserve_value_lcy
    , mil.last_mile_income_final_w_reserve_value_lcy
    , acq.acquiring_value_lcy
    , acq.acquiring_from_finance_department_value_lcy
    , acq.acquiring_reserve_value_lcy
    , acq.acquiring_final_w_reserve_value_lcy
    , sup.support_value_lcy
    , sup.support_from_finance_department_value_lcy
    , sup.support_reserve_value_lcy
    , sup.support_final_w_reserve_value_lcy
    , eas.easy_logistics_value_lcy
    , eas.easy_logistics_from_finance_department_value_lcy
    , eas.easy_logistics_reserve_value_lcy
    , eas.easy_logistics_final_w_reserve_value_lcy
    , ore.other_revenue_value_lcy
    , ore.other_revenue_from_finance_department_value_lcy
    , ore.other_revenue_reserve_value_lcy
    , ore.other_revenue_final_w_reserve_value_lcy
    , cwh.cwh_var_value_lcy
    , cwh.cwh_fixed_value_lcy
    , cwh.cwh_value_lcy
    , cwh.cwh_from_finance_department_value_lcy
    , cwh.cwh_reserve_value_lcy
    , cwh.cwh_final_w_reserve_value_lcy
    , cou.courier_logistics_value_lcy
    , cou.courier_logistics_from_finance_department_value_lcy
    , cou.courier_logistics_reserve_value_lcy
    , cou.courier_logistics_final_w_reserve_value_lcy
    , cog.cogs_value_lcy
    , cog.cogs_permanent_reserve_value_lcy
    , cog.cogs_from_finance_department_value_lcy
    , cog.cogs_reserve_value_lcy
    , cog.cogs_final_w_reserve_value_lcy
    , wri.writeoffs_value_lcy
    , wri.writeoffs_permanent_reserve_value_lcy
    , wri.writeoffs_from_finance_department_value_lcy
    , wri.writeoffs_reserve_value_lcy
    , wri.writeoffs_final_w_reserve_value_lcy
    , tra.transport_value_lcy
    , tra.transport_reserve_value_lcy
    , tra.transport_from_finance_department_value_lcy
    , tra.transport_final_w_reserve_value_lcy
    , coa.courier_acquisition_value_lcy
    , coa.courier_acquisition_from_finance_department_value_lcy
    , coa.courier_acquisition_reserve_value_lcy
    , coa.courier_acquisition_final_w_reserve_value_lcy
    , olo.other_logistics_value_lcy
    , olo.other_logistics_from_finance_department_value_lcy
    , olo.other_logistics_reserve_value_lcy
    , olo.other_logistics_final_w_reserve_value_lcy
    , rnt.rents_value_lcy
    , rnt.rents_from_finance_department_value_lcy
    , rnt.rents_reserve_value_lcy
    , rnt.rents_final_w_reserve_value_lcy
    , rnt.rents_final_method_name
    , utl.utilities_value_lcy
    , utl.utilities_from_finance_department_value_lcy
    , utl.utilities_reserve_value_lcy
    , utl.utilities_final_w_reserve_value_lcy
    , utl.utilities_final_method_name
    , pec.people_cost_value_lcy
    , pec.people_cost_from_finance_department_value_lcy
    , pec.people_cost_reserve_value_lcy
    , pec.people_cost_final_w_reserve_value_lcy
    , pec.people_cost_final_method_name
    , oth.vat_value_lcy
    , oth.internal_delivery_cnt
    , oth.market_delivery_w_upsale_cnt
    , oth.market_delivery_wo_upsale_cnt
    , oth.parcel_market_cnt
    , oth.order_cnt
  FROM {stg_stores_n_dates} AS sd
  LEFT JOIN {stg_gmv} AS gmv
    ON sd.lcl_calculation_dt = gmv.lcl_calculation_dt
    AND sd.store_id = gmv.store_id
    AND sd.region_name = gmv.region_name
  LEFT JOIN {stg_revenue_from_sales} AS res
    ON sd.lcl_calculation_dt = res.lcl_calculation_dt
    AND sd.store_id = res.store_id
    AND sd.region_name = res.region_name
  LEFT JOIN {stg_delivery_fee} AS del
    ON sd.lcl_calculation_dt = del.lcl_calculation_dt
    AND sd.store_id = del.store_id
    AND sd.region_name = del.region_name
  LEFT JOIN {stg_incentives} AS inc
    ON sd.lcl_calculation_dt = inc.lcl_calculation_dt
    AND sd.store_id = inc.store_id
    AND sd.region_name = inc.region_name
  LEFT JOIN {stg_packaging} AS pack
    ON sd.lcl_calculation_dt = pack.lcl_calculation_dt
    AND sd.store_id = pack.store_id
    AND sd.region_name = pack.region_name
  LEFT JOIN {stg_insurance_and_sms} AS ins
    ON sd.lcl_calculation_dt = ins.lcl_calculation_dt
    AND sd.store_id = ins.store_id
    AND sd.region_name = ins.region_name
  LEFT JOIN {stg_last_mile_income} AS mil
    ON sd.lcl_calculation_dt = mil.lcl_calculation_dt
    AND sd.store_id = mil.store_id
    AND sd.region_name = mil.region_name
  LEFT JOIN {stg_acquiring} AS acq
    ON sd.lcl_calculation_dt = acq.lcl_calculation_dt
    AND sd.store_id = acq.store_id
    AND sd.region_name = acq.region_name
  LEFT JOIN {stg_support} AS sup
    ON sd.lcl_calculation_dt = sup.lcl_calculation_dt
    AND sd.store_id = sup.store_id
    AND sd.region_name = sup.region_name
  LEFT JOIN {stg_easy_logistics} AS eas
    ON sd.lcl_calculation_dt = eas.lcl_calculation_dt
    AND sd.store_id = eas.store_id
    AND sd.region_name = eas.region_name
  LEFT JOIN {stg_other_revenue} AS ore
    ON sd.lcl_calculation_dt = ore.lcl_calculation_dt
    AND sd.store_id = ore.store_id
    AND sd.region_name = ore.region_name
  LEFT JOIN {stg_cwh} AS cwh
    ON sd.lcl_calculation_dt = cwh.lcl_calculation_dt
    AND sd.store_id = cwh.store_id
    AND sd.region_name = cwh.region_name
  LEFT JOIN {stg_courier_logistics} AS cou
    ON sd.lcl_calculation_dt = cou.lcl_calculation_dt
    AND sd.store_id = cou.store_id
    AND sd.region_name = cou.region_name
  LEFT JOIN {stg_cogs} AS cog
    ON sd.lcl_calculation_dt = cog.lcl_calculation_dt
    AND sd.store_id = cog.store_id
    AND sd.region_name = cog.region_name
  LEFT JOIN {stg_writeoffs} AS wri
    ON sd.lcl_calculation_dt = wri.lcl_calculation_dt
    AND sd.store_id = wri.store_id
    AND sd.region_name = wri.region_name
  LEFT JOIN {stg_courier_acquisition} AS coa
    ON sd.lcl_calculation_dt = coa.lcl_calculation_dt
    AND sd.store_id = coa.store_id
    AND sd.region_name = coa.region_name
  LEFT JOIN {stg_other_logistics} AS olo
    ON sd.lcl_calculation_dt = olo.lcl_calculation_dt
    AND sd.store_id = olo.store_id
    AND sd.region_name = olo.region_name
  LEFT JOIN {stg_vat_n_cnt} AS oth
    ON sd.lcl_calculation_dt = oth.lcl_calculation_dt
    AND sd.store_id = oth.store_id
    AND sd.region_name = oth.region_name
  LEFT JOIN {stg_transport} AS tra
    ON sd.lcl_calculation_dt = tra.lcl_calculation_dt
    AND sd.store_id = tra.store_id
    AND sd.region_name = tra.region_name
  LEFT JOIN {stg_rents} AS rnt
    ON sd.lcl_calculation_dt = rnt.lcl_calculation_dt
    AND sd.store_id = rnt.store_id
    AND sd.region_name = rnt.region_name
  LEFT JOIN {stg_utilities} AS utl
    ON sd.lcl_calculation_dt = utl.lcl_calculation_dt
    AND sd.store_id = utl.store_id
    AND sd.region_name = utl.region_name
  LEFT JOIN {stg_people_cost} AS pec
    ON sd.lcl_calculation_dt = pec.lcl_calculation_dt
    AND sd.store_id = pec.store_id
    AND sd.region_name = pec.region_name
) DISTRIBUTED BY (lcl_calculation_dt, country_name);
ANALYZE superjoin;

-- 2. Оставляем только те записи, у которых есть хотя бы одна ненулевая статья
INSERT INTO result_table
SELECT dc.lcl_calculation_dt
  , dc.country_name
  , dc.region_name
  , dc.store_id
  , dc.store_name
  , COALESCE(dc.gmv_value_lcy, 0)                                         AS gmv_value_lcy
  , COALESCE(dc.gmv_from_finance_department_value_lcy, 0)                 AS gmv_from_finance_department_value_lcy
  , COALESCE(dc.gmv_reserve_value_lcy, 0)                                 AS gmv_reserve_value_lcy
  , COALESCE(dc.gmv_final_w_reserve_value_lcy, 0)                         AS gmv_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS gmv_final_method_name
  , COALESCE(dc.revenue_from_sales_value_lcy, 0)                          AS revenue_from_sales_value_lcy
  , COALESCE(dc.revenue_from_sales_from_finance_department_value_lcy, 0)  AS revenue_from_sales_from_finance_department_value_lcy
  , COALESCE(dc.revenue_from_sales_reserve_value_lcy, 0)                  AS revenue_from_sales_reserve_value_lcy
  , COALESCE(dc.revenue_from_sales_final_w_reserve_value_lcy, 0)          AS revenue_from_sales_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS revenue_from_sales_final_method_name
  , COALESCE(dc.delivery_fee_value_lcy, 0)                                AS delivery_fee_value_lcy
  , COALESCE(dc.delivery_fee_from_finance_department_value_lcy, 0)        AS delivery_fee_from_finance_department_value_lcy
  , COALESCE(dc.delivery_fee_reserve_value_lcy, 0)                        AS delivery_fee_reserve_value_lcy
  , COALESCE(dc.delivery_fee_final_w_reserve_value_lcy, 0)                AS delivery_fee_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS delivery_fee_final_method_name
  , COALESCE(dc.incentives_discount_value_lcy, 0)                         AS incentives_discount_value_lcy
  , COALESCE(dc.incentives_promocode_value_lcy, 0)                        AS incentives_promocode_value_lcy
  , COALESCE(dc.incentives_cashback_amt, 0)                               AS incentives_cashback_amt
  , COALESCE(dc.incentives_value_lcy, 0)                                  AS incentives_value_lcy
  , COALESCE(dc.incentives_from_finance_department_value_lcy, 0)          AS incentives_from_finance_department_value_lcy
  , COALESCE(dc.incentives_reserve_value_lcy, 0)                          AS incentives_reserve_value_lcy
  , COALESCE(dc.incentives_final_w_reserve_value_lcy, 0)                  AS incentives_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS incentives_final_method_name
  , COALESCE(dc.packaging_value_lcy, 0)                                   AS packaging_value_lcy
  , COALESCE(dc.packaging_from_finance_department_value_lcy, 0)           AS packaging_from_finance_department_value_lcy
  , COALESCE(dc.packaging_reserve_value_lcy, 0)                           AS packaging_reserve_value_lcy
  , COALESCE(dc.packaging_final_w_reserve_value_lcy, 0)                   AS packaging_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_forecast_curr_month}'
             END
      ELSE '{txt_forecast_prev_month}'
    END::VARCHAR                                                          AS packaging_final_method_name
  , COALESCE(dc.insurance_and_sms_value_lcy, 0)                           AS insurance_and_sms_value_lcy
  , COALESCE(dc.insurance_and_sms_from_finance_department_value_lcy, 0)   AS insurance_and_sms_from_finance_department_value_lcy
  , COALESCE(dc.insurance_reserve_value_lcy, 0)                           AS insurance_reserve_value_lcy
  , COALESCE(dc.sms_reserve_value_lcy, 0)                                 AS sms_reserve_value_lcy
  , COALESCE(dc.insurance_and_sms_reserve_value_lcy, 0)                   AS insurance_and_sms_reserve_value_lcy
  , COALESCE(dc.insurance_and_sms_final_w_reserve_value_lcy, 0)           AS insurance_and_sms_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_forecast_curr_month}'
             END
      ELSE '{txt_forecast_prev_month}'
    END::VARCHAR                                                          AS insurance_and_sms_final_method_name
  , COALESCE(dc.last_mile_income_value_lcy, 0)                            AS last_mile_income_value_lcy
  , COALESCE(dc.last_mile_income_from_finance_department_value_lcy, 0)    AS last_mile_income_from_finance_department_value_lcy
  , COALESCE(dc.last_mile_income_reserve_value_lcy, 0)                    AS last_mile_income_reserve_value_lcy
  , COALESCE(dc.last_mile_income_final_w_reserve_value_lcy, 0)            AS last_mile_income_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_forecast_curr_month}'
             END
      ELSE '{txt_forecast_prev_month}'
    END::VARCHAR                                                          AS last_mile_income_final_method_name
  , COALESCE(dc.acquiring_value_lcy, 0)                                   AS acquiring_value_lcy
  , COALESCE(dc.acquiring_from_finance_department_value_lcy, 0)           AS acquiring_from_finance_department_value_lcy
  , COALESCE(dc.acquiring_reserve_value_lcy, 0)                           AS acquiring_reserve_value_lcy
  , COALESCE(dc.acquiring_final_w_reserve_value_lcy, 0)                   AS acquiring_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_forecast_curr_month}'
             END
      ELSE '{txt_forecast_prev_month}'
    END::VARCHAR                                                          AS acquiring_final_method_name
  , COALESCE(dc.support_value_lcy, 0)                                     AS support_value_lcy
  , COALESCE(dc.support_from_finance_department_value_lcy, 0)             AS support_from_finance_department_value_lcy
  , COALESCE(dc.support_reserve_value_lcy, 0)                             AS support_reserve_value_lcy
  , COALESCE(dc.support_final_w_reserve_value_lcy, 0)                     AS support_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS support_final_method_name
  , COALESCE(dc.easy_logistics_value_lcy, 0)                              AS easy_logistics_value_lcy
  , COALESCE(dc.easy_logistics_from_finance_department_value_lcy, 0)      AS easy_logistics_from_finance_department_value_lcy
  , COALESCE(dc.easy_logistics_reserve_value_lcy, 0)                      AS easy_logistics_reserve_value_lcy
  , COALESCE(dc.easy_logistics_final_w_reserve_value_lcy, 0)              AS easy_logistics_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS easy_logistics_final_method_name
  , COALESCE(dc.other_revenue_value_lcy, 0)                               AS other_revenue_value_lcy
  , COALESCE(dc.other_revenue_from_finance_department_value_lcy, 0)       AS other_revenue_from_finance_department_value_lcy
  , COALESCE(dc.other_revenue_reserve_value_lcy, 0)                       AS other_revenue_reserve_value_lcy
  , COALESCE(dc.other_revenue_final_w_reserve_value_lcy, 0)               AS other_revenue_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS other_revenue_final_method_name
  , COALESCE(dc.cwh_var_value_lcy, 0)                                     AS cwh_var_value_lcy
  , COALESCE(dc.cwh_fixed_value_lcy, 0)                                   AS cwh_fixed_value_lcy
  , COALESCE(dc.cwh_value_lcy, 0)                                         AS cwh_value_lcy
  , COALESCE(dc.cwh_from_finance_department_value_lcy, 0)                 AS cwh_from_finance_department_value_lcy
  , COALESCE(dc.cwh_reserve_value_lcy, 0)                                 AS cwh_reserve_value_lcy
  , COALESCE(dc.cwh_final_w_reserve_value_lcy, 0)                         AS cwh_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_forecast_curr_month}'
             END
      ELSE '{txt_forecast_prev_month}'
    END::VARCHAR                                                          AS cwh_final_method_name
  , COALESCE(dc.courier_logistics_value_lcy, 0)                           AS courier_logistics_value_lcy
  , COALESCE(dc.courier_logistics_from_finance_department_value_lcy, 0)   AS courier_logistics_from_finance_department_value_lcy
  , COALESCE(dc.courier_logistics_reserve_value_lcy, 0)                   AS courier_logistics_reserve_value_lcy
  , COALESCE(dc.courier_logistics_final_w_reserve_value_lcy, 0)           AS courier_logistics_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS courier_logistics_final_method_name
  , COALESCE(dc.cogs_value_lcy, 0)                                        AS cogs_value_lcy
  , COALESCE(dc.cogs_permanent_reserve_value_lcy, 0)                      AS cogs_permanent_reserve_value_lcy
  , COALESCE(dc.cogs_from_finance_department_value_lcy, 0)                AS cogs_from_finance_department_value_lcy
  , COALESCE(dc.cogs_reserve_value_lcy, 0)                                AS cogs_reserve_value_lcy
  , COALESCE(dc.cogs_final_w_reserve_value_lcy, 0)                        AS cogs_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS cogs_final_method_name
  , COALESCE(dc.writeoffs_value_lcy, 0)                                   AS writeoffs_value_lcy
  , COALESCE(dc.writeoffs_permanent_reserve_value_lcy, 0)                 AS writeoffs_permanent_reserve_value_lcy
  , COALESCE(dc.writeoffs_from_finance_department_value_lcy, 0)           AS writeoffs_from_finance_department_value_lcy
  , COALESCE(dc.writeoffs_reserve_value_lcy, 0)                           AS writeoffs_reserve_value_lcy
  , COALESCE(dc.writeoffs_final_w_reserve_value_lcy, 0)                   AS writeoffs_final_w_reserve_value_lcy
  , CASE
      WHEN mc.fiscal_year_closed_period_flg
        THEN '{txt_financial_total_sp}'
      ELSE '{txt_source_fact}'
    END::VARCHAR                                                          AS writeoffs_final_method_name
  , COALESCE(dc.courier_acquisition_value_lcy, 0)                         AS courier_acquisition_value_lcy
  , COALESCE(dc.courier_acquisition_from_finance_department_value_lcy, 0) AS courier_acquisition_from_finance_department_value_lcy
  , COALESCE(dc.courier_acquisition_reserve_value_lcy, 0)                 AS courier_acquisition_reserve_value_lcy
  , COALESCE(dc.courier_acquisition_final_w_reserve_value_lcy, 0)         AS courier_acquisition_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS courier_acquisition_final_method_name
  , COALESCE(dc.other_logistics_value_lcy, 0)                             AS other_logistics_value_lcy
  , COALESCE(dc.other_logistics_from_finance_department_value_lcy, 0)     AS other_logistics_from_finance_department_value_lcy
  , COALESCE(dc.other_logistics_reserve_value_lcy, 0)                     AS other_logistics_reserve_value_lcy
  , COALESCE(dc.other_logistics_final_w_reserve_value_lcy, 0)             AS other_logistics_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS other_logistics_final_method_name
  , COALESCE(dc.transport_value_lcy, 0)                                   AS transport_value_lcy
  , COALESCE(dc.transport_from_finance_department_value_lcy, 0)           AS transport_from_finance_department_value_lcy
  , COALESCE(dc.transport_reserve_value_lcy, 0)                           AS transport_reserve_value_lcy
  , COALESCE(dc.transport_final_w_reserve_value_lcy, 0)                   AS transport_final_w_reserve_value_lcy
  , CASE
      WHEN NOT mc.got_from_previous_month_flg
        THEN CASE
               WHEN mc.fiscal_year_closed_period_flg
                 THEN '{txt_financial_total_sp}'
               ELSE '{txt_plan_curr_month}'
             END
      ELSE '{txt_plan_prev_month}'
    END::VARCHAR                                                          AS transport_final_method_name
  , COALESCE(dc.rents_value_lcy, 0)                                       AS rents_value_lcy
  , COALESCE(dc.rents_from_finance_department_value_lcy, 0)               AS rents_from_finance_department_value_lcy
  , COALESCE(dc.rents_reserve_value_lcy, 0)                               AS rents_reserve_value_lcy
  , COALESCE(dc.rents_final_w_reserve_value_lcy, 0)                       AS rents_final_w_reserve_value_lcy
  , COALESCE(
      dc.rents_final_method_name, '{txt_incalculable}'
    )::VARCHAR                                                            AS rents_final_method_name
  , COALESCE(dc.utilities_value_lcy, 0)                                   AS utilities_value_lcy
  , COALESCE(dc.utilities_from_finance_department_value_lcy, 0)           AS utilities_from_finance_department_value_lcy
  , COALESCE(dc.utilities_reserve_value_lcy, 0)                           AS utilities_reserve_value_lcy
  , COALESCE(dc.utilities_final_w_reserve_value_lcy, 0)                   AS utilities_final_w_reserve_value_lcy
  , COALESCE(
      dc.utilities_final_method_name, '{txt_incalculable}'
    )::VARCHAR                                                            AS utilities_final_method_name
  , COALESCE(dc.people_cost_value_lcy, 0)                                 AS people_cost_value_lcy
  , COALESCE(dc.people_cost_from_finance_department_value_lcy, 0)         AS people_cost_from_finance_department_value_lcy
  , COALESCE(dc.people_cost_reserve_value_lcy, 0)                         AS people_cost_reserve_value_lcy
  , COALESCE(dc.people_cost_final_w_reserve_value_lcy, 0)                 AS people_cost_final_w_reserve_value_lcy
  , COALESCE(
      dc.people_cost_final_method_name, '{txt_incalculable}'
    )::VARCHAR                                                            AS people_cost_final_method_name
  , COALESCE(dc.vat_value_lcy, 0)                                         AS vat_value_lcy
  , COALESCE(dc.internal_delivery_cnt, 0)                                 AS internal_delivery_cnt
  , COALESCE(dc.market_delivery_w_upsale_cnt, 0)                          AS market_delivery_w_upsale_cnt
  , COALESCE(dc.market_delivery_wo_upsale_cnt, 0)                         AS market_delivery_wo_upsale_cnt
  , COALESCE(dc.parcel_market_cnt, 0)                                     AS parcel_market_cnt
  , COALESCE(dc.order_cnt, 0)                                             AS order_cnt
  , mc.fiscal_year_closed_period_flg
  , cr.lcl_to_rub                                                         AS currency_rate_rub
  , cr.lcl_to_usd                                                         AS currency_rate_usd
FROM superjoin AS dc
LEFT JOIN {stg_manual_correction} AS mc
  ON dc.month_dt = mc.month_dt
  AND dc.country_name = mc.country_name
LEFT JOIN {stg_currency_rate} AS cr
  ON cr.lcl_currency_rate_dt = dc.lcl_calculation_dt
  AND cr.country_name = dc.country_name
WHERE dc.gmv_value_lcy IS NOT NULL
  OR dc.revenue_from_sales_value_lcy IS NOT NULL
  OR dc.delivery_fee_value_lcy IS NOT NULL
  OR dc.incentives_discount_value_lcy IS NOT NULL
  OR dc.incentives_promocode_value_lcy IS NOT NULL
  OR dc.incentives_cashback_amt IS NOT NULL
  OR dc.packaging_value_lcy IS NOT NULL
  OR dc.insurance_and_sms_value_lcy IS NOT NULL
  OR dc.last_mile_income_value_lcy IS NOT NULL
  OR dc.acquiring_value_lcy IS NOT NULL
  OR dc.support_value_lcy IS NOT NULL
  OR dc.easy_logistics_value_lcy IS NOT NULL
  OR dc.other_revenue_value_lcy IS NOT NULL
  OR dc.cwh_var_value_lcy IS NOT NULL
  OR dc.cwh_fixed_value_lcy IS NOT NULL
  OR dc.courier_logistics_value_lcy IS NOT NULL
  OR dc.cogs_value_lcy IS NOT NULL
  OR dc.writeoffs_value_lcy IS NOT NULL
  OR dc.courier_acquisition_value_lcy IS NOT NULL
  OR dc.other_logistics_value_lcy IS NOT NULL
  OR dc.vat_value_lcy IS NOT NULL
  OR dc.internal_delivery_cnt IS NOT NULL
  OR dc.market_delivery_w_upsale_cnt IS NOT NULL
  OR dc.market_delivery_wo_upsale_cnt IS NOT NULL
  OR dc.parcel_market_cnt IS NOT NULL
  OR dc.order_cnt IS NOT NULL
  OR dc.transport_value_lcy IS NOT NULL
  OR dc.rents_value_lcy IS NOT NULL
  OR dc.rents_from_finance_department_value_lcy IS NOT NULL
  OR dc.utilities_value_lcy IS NOT NULL
  OR dc.utilities_from_finance_department_value_lcy IS NOT NULL
  OR dc.people_cost_value_lcy IS NOT NULL
  OR dc.people_cost_from_finance_department_value_lcy IS NOT NULL;
ANALYZE result_table;
-- ] Собираем источник


TRUNCATE TABLE {cdm_diary_contribution};

INSERT INTO {cdm_diary_contribution}
  SELECT * FROM result_table;

ANALYZE {cdm_diary_contribution};


GRANT ALL ON {cdm_diary_contribution} TO "ed-avetisyan" WITH GRANT OPTION;
GRANT ALL ON {cdm_diary_contribution} TO agabitashvili WITH GRANT OPTION;
GRANT ALL ON {cdm_diary_contribution} TO "robot-lavka-analyst";
GRANT ALL ON {cdm_diary_contribution} TO "robot-taxi-stat";
GRANT SELECT ON {cdm_diary_contribution} TO daryagrishko;
GRANT SELECT ON {cdm_diary_contribution} TO sparshukov;
GRANT SELECT ON {cdm_diary_contribution} TO nikitabashkir;
GRANT SELECT ON {cdm_diary_contribution} TO andreynaumov;
GRANT SELECT ON {cdm_diary_contribution} TO "robot-lavka-bi";
GRANT SELECT ON {cdm_diary_contribution} TO akudr;
GRANT SELECT ON {cdm_diary_contribution} TO victoriaga;
GRANT SELECT ON {cdm_diary_contribution} TO "i-krainova";
GRANT SELECT ON {cdm_diary_contribution} TO voytova;
GRANT SELECT ON {cdm_diary_contribution} TO "gla3ova";
GRANT SELECT ON {cdm_diary_contribution} TO elsikacheva;
