/*=====================================================================================
 Неаллоцированные деньги для закрытых месяцев
=====================================================================================*/
-- Объединяем словари страны
CREATE TEMPORARY TABLE unallocated_united
ON COMMIT DROP
AS (
  SELECT month_dt
    , 'Россия'::VARCHAR AS country_name
    , region_name
    , EXTRACT(DAYS FROM month_dt + '1 month - 1 day'::INTERVAL)  AS days_in_month
    , gmv_unallocated_value_lcy::NUMERIC                         AS gmv_unallocated_value_rub
    , gross_revenue_sales_unallocated_value_lcy::NUMERIC         AS gross_revenue_sales_unallocated_value_rub
    , gross_revenue_delivery_fee_unallocated_value_lcy::NUMERIC  AS gross_revenue_delivery_fee_unallocated_value_rub
    , royalty_from_franchisee_unallocated_value_lcy::NUMERIC     AS royalty_from_franchisee_unallocated_value_rub
    , last_mile_revenue_unallocated_value_lcy::NUMERIC           AS last_mile_revenue_unallocated_value_rub
    , other_revenue_unallocated_value_lcy::NUMERIC               AS other_revenue_unallocated_value_rub
    , incentives_total_unallocated_value_lcy::NUMERIC            AS incentives_total_unallocated_value_rub
    , cogs_unallocated_value_lcy::NUMERIC                        AS cogs_unallocated_value_rub
    , writeoffs_unallocated_value_lcy::NUMERIC                   AS writeoffs_unallocated_value_rub
    , cwh_total_reseve_value_lcy::NUMERIC                        AS cwh_total_reseve_value_rub
    , courier_logistics_unallocated_value_lcy::NUMERIC           AS courier_logistics_unallocated_value_rub
    , easy_logistics_unallocated_value_lcy::NUMERIC              AS easy_logistics_unallocated_value_rub
    , marketing_unallocated_value_lcy::NUMERIC                   AS marketing_unallocated_value_rub
    , other_logistics_unallocated_value_lcy::NUMERIC             AS other_logistics_unallocated_value_rub
    , courier_acquisition_unallocated_value_lcy::NUMERIC         AS courier_acquisition_unallocated_value_rub
    , support_unallocated_value_lcy::NUMERIC                     AS support_unallocated_value_rub
    , acquiring_unallocated_value_lcy::NUMERIC                   AS acquiring_unallocated_value_rub
    , insurance_unallocated_value_lcy::NUMERIC                   AS insurance_unallocated_value_rub
    , sms_unallocated_value_lcy::NUMERIC                         AS sms_unallocated_value_rub
    , packaging_unallocated_value_lcy::NUMERIC                   AS packaging_unallocated_value_rub
    , rent_unallocated_value_lcy::NUMERIC                        AS rent_unallocated_value_rub
    , utilities_unallocated_value_lcy::NUMERIC                   AS utilities_unallocated_value_rub
    , people_cost_unallocated_value_lcy::NUMERIC                 AS people_cost_unallocated_value_rub
    , transport_unallocated_value_lcy::NUMERIC                   AS transport_unallocated_value_rub
    , brand_royalty_unallocated_value_lcy::NUMERIC               AS brand_royalty_unallocated_value_rub
    , service_fee_unallocated_value_lcy::NUMERIC                 AS service_fee_unallocated_value_rub
    , overheads_adj_hr_expenses_unallocated_value_lcy::NUMERIC   AS overheads_adj_hr_expenses_unallocated_value_rub
    , overheads_rent_hq_unallocated_value_lcy::NUMERIC           AS overheads_rent_hq_unallocated_value_rub
    , overheads_general_and_other_unallocated_value_lcy::NUMERIC AS overheads_general_and_other_unallocated_value_rub
  FROM {pnl_ru_unallocated}
  UNION ALL
  SELECT month_dt
    , 'Израиль'::VARCHAR AS country_name
    , region_name
    , EXTRACT(DAYS FROM month_dt + '1 month - 1 day'::INTERVAL)  AS days_in_month
    , gmv_unallocated_value_rub::NUMERIC
    , gross_revenue_sales_unallocated_value_rub::NUMERIC
    , gross_revenue_delivery_fee_unallocated_value_rub::NUMERIC
    , NULL::NUMERIC                                              AS royalty_from_franchisee_unallocated_value_rub
    , last_mile_revenue_unallocated_value_rub::NUMERIC
    , other_revenue_unallocated_value_rub::NUMERIC
    , incentives_total_unallocated_value_rub::NUMERIC
    , cogs_unallocated_value_rub::NUMERIC
    , writeoffs_unallocated_value_rub::NUMERIC
    , cwh_total_reseve_value_rub::NUMERIC
    , courier_logistics_unallocated_value_rub::NUMERIC
    , NULL::NUMERIC                                              AS easy_logistics_unallocated_value_rub
    , marketing_unallocated_value_rub::NUMERIC
    , other_logistics_unallocated_value_rub::NUMERIC
    , courier_acquisition_unallocated_value_rub::NUMERIC
    , support_unallocated_value_rub::NUMERIC
    , acquiring_unallocated_value_rub::NUMERIC
    , insurance_unallocated_value_rub::NUMERIC
    , sms_unallocated_value_rub::NUMERIC
    , packaging_unallocated_value_rub::NUMERIC
    , rent_unallocated_value_rub::NUMERIC
    , utilities_unallocated_value_rub::NUMERIC
    , people_cost_unallocated_value_rub::NUMERIC
    , transport_unallocated_value_rub::NUMERIC
    , brand_royalty_unallocated_value_rub::NUMERIC
    , NULL::NUMERIC                                              AS service_fee_unallocated_value_rub
    , overheads_adj_hr_expenses_unallocated_value_rub::NUMERIC
    , overheads_rent_hq_unallocated_value_rub::NUMERIC
    , overheads_general_and_other_unallocated_value_rub::NUMERIC
  FROM {pnl_il_unallocated}
) DISTRIBUTED BY (month_dt);
ANALYZE unallocated_united;

-- Оставляем только закрытые месяцы + разбиваем константы, заведенные на месяц, по дням
CREATE TEMPORARY TABLE pre_stg_unallocated_by_days
ON COMMIT DROP
AS (
  SELECT generate_series(
           u.month_dt::TIMESTAMP,
           u.month_dt + '1 month - 1 day'::INTERVAL,
           '1 day'::INTERVAL
         )::DATE                                               AS lcl_calculation_dt
    , u.country_name
    , u.region_name
    , '0'::VARCHAR                                             AS store_id
    , COALESCE(u.gmv_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS gmv_unallocated_value_rub
    , COALESCE(u.gross_revenue_sales_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS gross_revenue_sales_unallocated_value_rub
    , COALESCE(u.gross_revenue_delivery_fee_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS gross_revenue_delivery_fee_unallocated_value_rub
    , COALESCE(u.royalty_from_franchisee_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS royalty_from_franchisee_unallocated_value_rub
    , COALESCE(u.last_mile_revenue_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS last_mile_revenue_unallocated_value_rub
    , COALESCE(u.other_revenue_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS other_revenue_unallocated_value_rub
    , COALESCE(u.incentives_total_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS incentives_total_unallocated_value_rub
    , COALESCE(u.cogs_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS cogs_unallocated_value_rub
    , COALESCE(u.writeoffs_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS writeoffs_unallocated_value_rub
    , COALESCE(u.cwh_total_reseve_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS cwh_total_unallocated_value_rub
    , COALESCE(u.courier_logistics_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS courier_logistics_unallocated_value_rub
    , COALESCE(u.easy_logistics_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS easy_logistics_unallocated_value_rub
    , COALESCE(u.marketing_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS marketing_unallocated_value_rub
    , COALESCE(u.other_logistics_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS other_logistics_unallocated_value_rub
    , COALESCE(u.courier_acquisition_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS courier_acquisition_unallocated_value_rub
    , COALESCE(u.support_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS support_unallocated_value_rub
    , COALESCE(u.acquiring_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS acquiring_unallocated_value_rub
    , COALESCE(u.insurance_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS insurance_unallocated_value_rub
    , COALESCE(u.sms_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS sms_unallocated_value_rub
    , COALESCE(u.packaging_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS packaging_unallocated_value_rub
    , COALESCE(u.rent_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS rent_unallocated_value_rub
    , COALESCE(u.utilities_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS utilities_unallocated_value_rub
    , COALESCE(u.people_cost_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS people_cost_unallocated_value_rub
    , COALESCE(u.transport_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS transport_unallocated_value_rub
    , COALESCE(u.brand_royalty_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS brand_royalty_unallocated_value_rub
    , COALESCE(u.service_fee_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS service_fee_unallocated_value_rub
    , COALESCE(u.overheads_adj_hr_expenses_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS overheads_adj_hr_expenses_unallocated_value_rub
    , COALESCE(u.overheads_rent_hq_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS overheads_rent_hq_unallocated_value_rub
    , COALESCE(u.overheads_general_and_other_unallocated_value_rub, 0)::NUMERIC
        / u.days_in_month                                      AS overheads_general_and_other_unallocated_value_rub
  FROM unallocated_united AS u
  JOIN {stg_manual_correction} AS mc
    ON u.month_dt = mc.month_dt
    AND u.country_name = mc.country_name
  WHERE mc.fiscal_year_closed_period_flg
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_unallocated_by_days;

-- Переводим подневные рубли в локальную валюту
DROP TABLE IF EXISTS {stg_unallocated_by_days};
CREATE TABLE {stg_unallocated_by_days}
AS (
  SELECT u.lcl_calculation_dt
    , u.country_name
    , u.region_name
    , u.store_id
    , u.gmv_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS gmv_unallocated_value_rub
    , u.gross_revenue_sales_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS gross_revenue_sales_unallocated_value_rub
    , u.gross_revenue_delivery_fee_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS gross_revenue_delivery_fee_unallocated_value_rub
    , u.royalty_from_franchisee_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS royalty_from_franchisee_unallocated_value_rub
    , u.last_mile_revenue_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS last_mile_revenue_unallocated_value_rub
    , u.other_revenue_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS other_revenue_unallocated_value_rub
    , u.incentives_total_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS incentives_total_unallocated_value_rub
    , u.cogs_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS cogs_unallocated_value_rub
    , u.writeoffs_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS writeoffs_unallocated_value_rub
    , u.cwh_total_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS cwh_total_unallocated_value_rub
    , u.courier_logistics_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS courier_logistics_unallocated_value_rub
    , u.easy_logistics_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS easy_logistics_unallocated_value_rub
    , u.marketing_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS marketing_unallocated_value_rub
    , u.other_logistics_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS other_logistics_unallocated_value_rub
    , u.courier_acquisition_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS courier_acquisition_unallocated_value_rub
    , u.support_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS support_unallocated_value_rub
    , u.acquiring_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS acquiring_unallocated_value_rub
    , u.insurance_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS insurance_unallocated_value_rub
    , u.sms_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS sms_unallocated_value_rub
    , u.packaging_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS packaging_unallocated_value_rub
    , u.rent_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS rent_unallocated_value_rub
    , u.utilities_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS utilities_unallocated_value_rub
    , u.people_cost_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS people_cost_unallocated_value_rub
    , u.transport_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS transport_unallocated_value_rub
    , u.brand_royalty_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS brand_royalty_unallocated_value_rub
    , u.service_fee_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS service_fee_unallocated_value_rub
    , u.overheads_adj_hr_expenses_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS overheads_adj_hr_expenses_unallocated_value_rub
    , u.overheads_rent_hq_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS overheads_rent_hq_unallocated_value_rub
    , u.overheads_general_and_other_unallocated_value_rub
        / cr.lcl_to_rub::NUMERIC          AS overheads_general_and_other_unallocated_value_rub
  FROM pre_stg_unallocated_by_days AS u
  LEFT JOIN {stg_currency_rate} AS cr
    ON u.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND u.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_unallocated_by_days};
GRANT ALL ON {stg_unallocated_by_days} TO "ed-avetisyan";
GRANT ALL ON {stg_unallocated_by_days} TO agabitashvili;
GRANT ALL ON {stg_unallocated_by_days} TO "robot-lavka-analyst";
