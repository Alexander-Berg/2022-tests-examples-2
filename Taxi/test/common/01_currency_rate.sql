/*=========================================================
 Тащим курсы валют
=========================================================*/
DROP TABLE IF EXISTS {stg_currency_rate};
CREATE TABLE {stg_currency_rate}
  AS (
    SELECT "date" AS lcl_currency_rate_dt
      , CASE
          WHEN source_cur = 'RUB' THEN 'Россия'
          WHEN source_cur = 'ILS' THEN 'Израиль'
          END AS country_name
      , MAX(CASE WHEN target_cur = 'RUB' THEN rate ELSE 1 END)::NUMERIC AS lcl_to_rub
      , MAX(CASE WHEN target_cur = 'USD' THEN rate END)::NUMERIC        AS lcl_to_usd
    FROM {dim_currency_rate}
    WHERE ((source_cur = 'RUB' AND target_cur = 'ILS')
             OR (source_cur = 'ILS' AND target_cur = 'RUB')
             OR (source_cur = 'ILS' AND target_cur = 'USD')
             OR (source_cur = 'RUB' AND target_cur = 'USD'))
      AND "date" >= '2021-10-01'
    GROUP BY "date", source_cur
) DISTRIBUTED BY (lcl_currency_rate_dt, country_name);
ANALYZE {stg_currency_rate};
GRANT ALL ON {stg_currency_rate} TO "ed-avetisyan";
GRANT ALL ON {stg_currency_rate} TO agabitashvili;
GRANT ALL ON {stg_currency_rate} TO "robot-lavka-analyst";
