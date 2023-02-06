/*=====================================================================================
 В справочнике обязательно должен быть текущий месяц. Если его вдруг не оказывается,
 то запись для текущего месяца искусственно создается из предыдущего
=====================================================================================*/
CREATE TEMPORARY TABLE ru_manual_correction
  ON COMMIT DROP AS (
-- 5. Для каждого месяца схлопываем две записи (план + факт) в одну
  SELECT month_dt
    , CASE WHEN MAX(fiscal_year_closed_period_flg::INT) = 1
        THEN TRUE
        ELSE FALSE
      END                                                AS fiscal_year_closed_period_flg
    , CASE WHEN MAX(is_fake::INT) = 1
        THEN TRUE
        ELSE FALSE
      END                                                AS got_from_previous_month_flg
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN courier_acquisition_lcy
      END)                                               AS courier_acquisition_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN courier_acquisition_lcy
      END)                                               AS courier_acquisition_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN franchising_royalty_lcy
      END)                                               AS franchising_royalty_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN franchising_royalty_lcy
      END)                                               AS franchising_royalty_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN marketing_lcy
      END)                                               AS marketing_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN marketing_lcy
      END)                                               AS marketing_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN other_logistics_lcy
      END)                                               AS other_logistics_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN other_logistics_lcy
      END)                                               AS other_logistics_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN other_revenue_lcy
      END)                                               AS other_revenue_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN other_revenue_lcy
      END)                                               AS other_revenue_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_adj_hr_expenses_lcy
      END)                                               AS overheads_adj_hr_expenses_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_adj_hr_expenses_lcy
      END)                                               AS overheads_adj_hr_expenses_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_general_and_other_lcy
      END)                                               AS overheads_general_and_other_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_general_and_other_lcy
      END)                                               AS overheads_general_and_other_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_rent_hq_lcy
      END)                                               AS overheads_rent_hq_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_rent_hq_lcy
      END)                                               AS overheads_rent_hq_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN support_lcy
      END)                                               AS support_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN support_lcy
      END)                                               AS support_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN easy_logistics_lcy
      END)                                               AS easy_logistics_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN easy_logistics_lcy
      END)                                               AS easy_logistics_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN acquiring_value_lcy
      END)                                               AS acquiring_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN acquiring_value_lcy
      END)                                               AS acquiring_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN brand_royalty_value_lcy
      END)                                               AS brand_royalty_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN brand_royalty_value_lcy
      END)                                               AS brand_royalty_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN cogs_value_lcy
      END)                                               AS cogs_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN cogs_value_lcy
      END)                                               AS cogs_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN courier_logistics_w_easy_logistics_value_lcy
      END)                                               AS courier_logistics_w_easy_logistics_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN courier_logistics_w_easy_logistics_value_lcy
      END)                                               AS courier_logistics_w_easy_logistics_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN cwh_total_value_lcy
      END)                                               AS cwh_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN cwh_total_value_lcy
      END)                                               AS cwh_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gmv_w_vat_lcy
      END)                                               AS gmv_w_vat_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gmv_w_vat_lcy
      END)                                               AS gmv_w_vat_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gross_revenue_delivery_fee_value_lcy
      END)                                               AS gross_revenue_delivery_fee_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gross_revenue_delivery_fee_value_lcy
      END)                                               AS gross_revenue_delivery_fee_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gross_revenue_sales_wo_vat_lcy
      END)                                               AS gross_revenue_sales_wo_vat_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gross_revenue_sales_wo_vat_lcy
      END)                                               AS gross_revenue_sales_wo_vat_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN incentives_total_value_lcy
      END)                                               AS incentives_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN incentives_total_value_lcy
      END)                                               AS incentives_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN insurance_and_sms_value_lcy
      END)                                               AS insurance_and_sms_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN insurance_and_sms_value_lcy
      END)                                               AS insurance_and_sms_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN last_mile_revenue_value_lcy
      END)                                               AS last_mile_revenue_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN last_mile_revenue_value_lcy
      END)                                               AS last_mile_revenue_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN packaging_value_lcy
      END)                                               AS packaging_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN packaging_value_lcy
      END)                                               AS packaging_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN people_cost_value_lcy
      END)                                               AS people_cost_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN people_cost_value_lcy
      END)                                               AS people_cost_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN rent_and_utilities_value_lcy
      END)                                               AS rent_and_utilities_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN rent_and_utilities_value_lcy
      END)                                               AS rent_and_utilities_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN transport_value_lcy
      END)                                               AS transport_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN transport_value_lcy
      END)                                               AS transport_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN writeoffs_value_lcy
      END)                                               AS writeoffs_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN writeoffs_value_lcy
      END)                                               AS writeoffs_fact_value_lcy
    , 'Россия'::VARCHAR                                  AS country_name
  FROM (
    -- 4. Если на текущий месяц выпала искусственная запись, то подменяем ей дату
    SELECT "_etl_processed_dttm"
      , courier_acquisition_lcy
      , fact_flg                        AS fiscal_year_closed_period_flg
      , franchising_royalty_lcy
      , marketing_lcy
      , CASE
          WHEN is_fake = TRUE
            THEN date_trunc('month', (now() AT TIME ZONE 'Europe/Moscow'))::DATE
          ELSE month_dt
        END                             AS month_dt
      , other_logistics_lcy
      , other_revenue_lcy
      , overheads_adj_hr_expenses_lcy
      , overheads_general_and_other_lcy
      , overheads_rent_hq_lcy
      , support_lcy
      , utc_business_dttm
      , utc_created_dttm
      , utc_updated_dttm
      , easy_logistics_lcy
      , acquiring_value_lcy
      , brand_royalty_value_lcy
      , cogs_value_lcy
      , courier_logistics_w_easy_logistics_value_lcy
      , cwh_total_value_lcy
      , gmv_w_vat_lcy
      , gross_revenue_delivery_fee_value_lcy
      , gross_revenue_sales_wo_vat_lcy
      , incentives_total_value_lcy
      , insurance_and_sms_value_lcy
      , last_mile_revenue_value_lcy
      , packaging_value_lcy
      , people_cost_value_lcy
      , rent_and_utilities_value_lcy
      , transport_value_lcy
      , writeoffs_value_lcy
      , is_fake
    FROM (
      -- 3. Оставляем записи для предыдущего и более ранних месяцев + разбираемся с записями для текущего месяца
      SELECT *
      FROM (
        -- 2. Задваиваем запись с планом на предпоследний месяц + вычисляем максимальный месяц, имеющийся в таблице
        SELECT mc.*
          , CASE
              WHEN fake.is_fake IS NULL
                THEN FALSE
              ELSE fake.is_fake
            END                      AS is_fake
          , date_trunc(
              'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
            )::DATE                  AS previous_month_from_now
          , MAX(mc.month_dt) OVER () AS maximal_month_at_table
        FROM {pnl_ru_manual_correction} AS mc
        LEFT JOIN (
          -- 1. Создаем ДВЕ записи с предпоследним месяцем - из одной будем делать текущий месяц, если его нет
          SELECT *
          FROM (
            SELECT date_trunc(
                     'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
                   )::DATE AS month_dt
          ) AS prev_month
          CROSS JOIN (VALUES (TRUE), (FALSE)) AS tf(is_fake)
        ) AS fake
          ON mc.month_dt = fake.month_dt
          AND mc.fact_flg = FALSE
        WHERE mc.month_dt <= (now() AT TIME ZONE 'Europe/Moscow')::DATE
      ) AS mc
      WHERE     month_dt < previous_month_from_now
         OR     month_dt = previous_month_from_now AND is_fake = FALSE
         OR (   month_dt = previous_month_from_now AND month_dt = maximal_month_at_table AND is_fake = TRUE
             OR month_dt > previous_month_from_now AND month_dt = maximal_month_at_table
            )
    ) AS mc
  ) AS mc
  GROUP BY month_dt
) DISTRIBUTED BY (month_dt);
ANALYZE ru_manual_correction;

CREATE TEMPORARY TABLE il_manual_correction
  ON COMMIT DROP AS (
-- 5. Для каждого месяца схлопываем две записи (план + факт) в одну
  SELECT month_dt
    , CASE WHEN MAX(fiscal_year_closed_period_flg::INT) = 1
        THEN TRUE
        ELSE FALSE
      END                                                AS fiscal_year_closed_period_flg
    , CASE WHEN MAX(is_fake::INT) = 1
        THEN TRUE
        ELSE FALSE
      END                                                AS got_from_previous_month_flg
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN courier_acquisition_lcy
      END)                                               AS courier_acquisition_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN courier_acquisition_lcy
      END)                                               AS courier_acquisition_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN franchising_royalty_lcy
      END)                                               AS franchising_royalty_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN franchising_royalty_lcy
      END)                                               AS franchising_royalty_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN marketing_lcy
      END)                                               AS marketing_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN marketing_lcy
      END)                                               AS marketing_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN other_logistics_lcy
      END)                                               AS other_logistics_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN other_logistics_lcy
      END)                                               AS other_logistics_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN other_revenue_lcy
      END)                                               AS other_revenue_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN other_revenue_lcy
      END)                                               AS other_revenue_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_adj_hr_expenses_lcy
      END)                                               AS overheads_adj_hr_expenses_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_adj_hr_expenses_lcy
      END)                                               AS overheads_adj_hr_expenses_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_general_and_other_lcy
      END)                                               AS overheads_general_and_other_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_general_and_other_lcy
      END)                                               AS overheads_general_and_other_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN overheads_rent_hq_lcy
      END)                                               AS overheads_rent_hq_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN overheads_rent_hq_lcy
      END)                                               AS overheads_rent_hq_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN support_lcy
      END)                                               AS support_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN support_lcy
      END)                                               AS support_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN easy_logistics_lcy
      END)                                               AS easy_logistics_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN easy_logistics_lcy
      END)                                               AS easy_logistics_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN acquiring_value_lcy
      END)                                               AS acquiring_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN acquiring_value_lcy
      END)                                               AS acquiring_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN brand_royalty_value_lcy
      END)                                               AS brand_royalty_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN brand_royalty_value_lcy
      END)                                               AS brand_royalty_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN cogs_value_lcy
      END)                                               AS cogs_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN cogs_value_lcy
      END)                                               AS cogs_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN courier_logistics_w_easy_logistics_value_lcy
      END)                                               AS courier_logistics_w_easy_logistics_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN courier_logistics_w_easy_logistics_value_lcy
      END)                                               AS courier_logistics_w_easy_logistics_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN cwh_total_value_lcy
      END)                                               AS cwh_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN cwh_total_value_lcy
      END)                                               AS cwh_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gmv_w_vat_lcy
      END)                                               AS gmv_w_vat_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gmv_w_vat_lcy
      END)                                               AS gmv_w_vat_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gross_revenue_delivery_fee_value_lcy
      END)                                               AS gross_revenue_delivery_fee_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gross_revenue_delivery_fee_value_lcy
      END)                                               AS gross_revenue_delivery_fee_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN gross_revenue_sales_wo_vat_lcy
      END)                                               AS gross_revenue_sales_wo_vat_plan_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN gross_revenue_sales_wo_vat_lcy
      END)                                               AS gross_revenue_sales_wo_vat_fact_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN incentives_total_value_lcy
      END)                                               AS incentives_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN incentives_total_value_lcy
      END)                                               AS incentives_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN insurance_and_sms_value_lcy
      END)                                               AS insurance_and_sms_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN insurance_and_sms_value_lcy
      END)                                               AS insurance_and_sms_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN last_mile_revenue_value_lcy
      END)                                               AS last_mile_revenue_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN last_mile_revenue_value_lcy
      END)                                               AS last_mile_revenue_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN packaging_value_lcy
      END)                                               AS packaging_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN packaging_value_lcy
      END)                                               AS packaging_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN people_cost_value_lcy
      END)                                               AS people_cost_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN people_cost_value_lcy
      END)                                               AS people_cost_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN rent_and_utilities_value_lcy
      END)                                               AS rent_and_utilities_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN rent_and_utilities_value_lcy
      END)                                               AS rent_and_utilities_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN transport_value_lcy
      END)                                               AS transport_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN transport_value_lcy
      END)                                               AS transport_fact_value_lcy
    , MAX(CASE WHEN NOT fiscal_year_closed_period_flg
          THEN writeoffs_value_lcy
      END)                                               AS writeoffs_plan_value_lcy
    , MAX(CASE WHEN fiscal_year_closed_period_flg
          THEN writeoffs_value_lcy
      END)                                               AS writeoffs_fact_value_lcy
    , 'Израиль'::VARCHAR                                 AS country_name
  FROM (
    -- 4. Если на текущий месяц выпала искусственная запись, то подменяем ей дату
    SELECT "_etl_processed_dttm"
      , NULL::NUMERIC                                      AS courier_acquisition_lcy
      , fact_flg                                           AS fiscal_year_closed_period_flg
      , NULL::NUMERIC                                      AS franchising_royalty_lcy
      , NULL::NUMERIC                                      AS marketing_lcy
      , NULL::NUMERIC                                      AS other_logistics_lcy
      , CASE
          WHEN is_fake = TRUE
            THEN date_trunc('month', (now() AT TIME ZONE 'Europe/Moscow'))::DATE
          ELSE month_dt
        END                             AS month_dt
      , other_revenue_value_rub                            AS other_revenue_lcy
      , NULL::NUMERIC                                      AS overheads_adj_hr_expenses_lcy
      , NULL::NUMERIC                                      AS overheads_general_and_other_lcy
      , NULL::NUMERIC                                      AS overheads_rent_hq_lcy
      , support_value_rub                                  AS support_lcy
      , utc_business_dttm
      , utc_created_dttm
      , utc_updated_dttm
      , NULL::NUMERIC                                      AS easy_logistics_lcy
      , acquiring_value_rub                                AS acquiring_value_lcy
      , NULL::NUMERIC                                      AS brand_royalty_value_lcy
      , cogs_value_rub                                     AS cogs_value_lcy
      , courier_logistics_total_value_rub                  AS courier_logistics_w_easy_logistics_value_lcy
      , cwh_total_value_rub                                AS cwh_total_value_lcy
      , gmv_value_rub                                      AS gmv_w_vat_lcy
      , delivery_fee_value_rub                             AS gross_revenue_delivery_fee_value_lcy
      , revenue_from_sales_value_rub                       AS gross_revenue_sales_wo_vat_lcy
      , incentives_total_value_rub                         AS incentives_total_value_lcy
      , NULL::NUMERIC                                      AS insurance_and_sms_value_lcy
      , NULL::NUMERIC                                      AS last_mile_revenue_value_lcy
      , packaging_value_rub                                AS packaging_value_lcy
      , NULL::NUMERIC                                      AS people_cost_value_lcy
      , NULL::NUMERIC                                      AS rent_and_utilities_value_lcy
      , NULL::NUMERIC                                      AS transport_value_lcy
      , writeoffs_value_rub                                AS writeoffs_value_lcy
      , is_fake
    FROM (
      -- 3. Оставляем записи для предыдущего и более ранних месяцев + разбираемся с записями для текущего месяца
      SELECT *
      FROM (
        -- 2. Задваиваем запись с планом на предпоследний месяц + вычисляем максимальный месяц, имеющийся в таблице
        SELECT mc.*
          , CASE
              WHEN fake.is_fake IS NULL
                THEN FALSE
              ELSE fake.is_fake
            END                      AS is_fake
          , date_trunc(
              'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
            )::DATE                  AS previous_month_from_now
          , MAX(mc.month_dt) OVER () AS maximal_month_at_table
        FROM {pnl_il_manual_correction} AS mc
        LEFT JOIN (
          -- 1. Создаем ДВЕ записи с предпоследним месяцем - из одной будем делать текущий месяц, если его нет
          SELECT *
          FROM (
            SELECT date_trunc(
                     'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
                   )::DATE AS month_dt
          ) AS prev_month
          CROSS JOIN (VALUES (TRUE), (FALSE)) AS tf(is_fake)
        ) AS fake
          ON mc.month_dt = fake.month_dt
          AND mc.fact_flg = FALSE
        WHERE mc.month_dt <= (now() AT TIME ZONE 'Europe/Moscow')::DATE
      ) AS mc
      WHERE     month_dt < previous_month_from_now
         OR     month_dt = previous_month_from_now AND is_fake = FALSE
         OR (   month_dt = previous_month_from_now AND month_dt = maximal_month_at_table AND is_fake = TRUE
             OR month_dt > previous_month_from_now AND month_dt = maximal_month_at_table
            )
    ) AS mc
  ) AS mc
  GROUP BY month_dt
) DISTRIBUTED BY (month_dt);
ANALYZE il_manual_correction;

DROP TABLE IF EXISTS {stg_manual_correction};
CREATE TABLE {stg_manual_correction}
  AS (
    SELECT *
    FROM ru_manual_correction
    UNION ALL
    SELECT *
    FROM il_manual_correction
) DISTRIBUTED BY (month_dt);
ANALYZE {stg_manual_correction};
GRANT ALL ON {stg_manual_correction} TO "ed-avetisyan";
GRANT ALL ON {stg_manual_correction} TO agabitashvili;
GRANT ALL ON {stg_manual_correction} TO "robot-lavka-analyst";
