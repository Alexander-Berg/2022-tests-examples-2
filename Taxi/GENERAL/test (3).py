# coding: utf-8
from business_models import hahn, greenplum
from business_models.greenplum import GreenplumManager
greenplum = GreenplumManager(user='robot-corploader')#, sslmode='require')
import numpy as np
import pandas as pd
query = '''
drop table if exists snb_taxi.ravaev_conversion_all_dash;
create table snb_taxi.ravaev_conversion_all_dash as
WITH data_temp_table as (
    select current_timestamp,
           date(a.add_time)                                             as add_date,
           a.id                                                         as deal_id,
           a.record_date                                                as record_date,
           a.lost_reason                                                as lost_reason,
           a.crm                                                        as which_crm,
           a.status                                                     as status,
           a.last_activity_date                                         as last_activity_date,
           a.contract_id                                                as contract_id,
           a.update_time                                                as update_time,
           --activ_date.activated_date                                    as activated_date,
           first_trip_day.day                                           as day_first_trip,
           case
               when coalesce(a.value, 0) = 0 then '0'
               when coalesce(a.value, 0) > 0 and coalesce(a.value, 0) <= 100 then 'less_100'
               when coalesce(a.value, 0) > 100 and coalesce(a.value, 0) <= 250 then 'less_250'
               when coalesce(a.value, 0) > 250 and coalesce(a.value, 0) <= 500 then 'less_500'
               when coalesce(a.value, 0) > 500 and coalesce(a.value, 0) <= 1000 then 'less_1000'
               when coalesce(a.value, 0) > 1000 and coalesce(a.value, 0) <= 1500 then 'less_1500'
               when coalesce(a.value, 0) > 1500 then 'more_1500'
               end                                                      as potential,
           replace(coalesce(segment_value, org_segment_value), '"', '') as segment_result,
           lead_name_first || ' ' || lead_name_last                     as lead_name,
           lead_login,
           org_id,
           m.login                                                      as manager_login,
           name                                                         as manager_name,
           m.hierarchy                                                  as hierarchy,
           case
               when product_value is not null then product_value
               when a.which_crm = 6 then 'ДОСТАВКА/ГРУЗЫ'
               else 'ТАКСИ'
               end                                                      as product_value,
           cancelled_dt,
           currency,
           finish_dt,
           is_deactivated,
           suspended_dt,
           contract_type,
           payment_type,
           faxed_dt,
           channel_value,
           type_value                                                   as type_of_contract,
           start_dt,
           connected_deal,
           stage_name,
           funnel_name,
           communication_with_BA,
           bh.balance_rub                                               as balance,
           bh.client_name                                               as client_name,
           bh.contract_status                                           as status_from_balance,
           bh.deactivate_threshold_rub                                  as deactivate_threshold_rub
    from (
             select *
             from (
                      select *,
                             ROW_NUMBER()
                             OVER (PARTITION BY id, crm, record_date ORDER BY update_time desc) as rn
                      from (
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '3c226725e7feca6cbd7e7e6ca26ffae5f4219ac4' as contract_id,
                                      custom_fields ->> '23076f44b238c77e85159ff67189f42f5e235066' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '61d893466026ae650198c4f6f94a5d280c291107' as channel,
                                      custom_fields ->> 'f122996cbf393aeeeb686cccde00329c24775562' as type_of_contract,
                                      custom_fields ->> '3df564783f1632c5458d21823fc2f73c0998115f' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 2
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5f8c9c624091f5861ae66d6f95a29bacf83b9acb' as contract_id,
                                      custom_fields ->> 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361' as segment,
                                      custom_fields ->> '5bac18975d5257cf98f905dc219a05eaef604eab' as product_key,
                                      custom_fields ->> '25f3004a1c052739b4081f3fc764b755d4439536' as channel,
                                      custom_fields ->> '6e5fed220a3295084c4b362a14293a720a9bc306' as type_of_contract,
                                      custom_fields ->> '2728cdafd9aa8f1fed33c464560c4d5ec39f59ca' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 0
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '0c886554df85907470227fe1cfe6b072207bc86b' as contract_id,
                                      custom_fields ->> '60d803d64af12b5fe955671511fe816f81b5fb8d' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> 'eb8b26a6266d99ae6f1098d33b66bb620391f172' as channel,
                                      custom_fields ->> 'e54a319c8628880942a56d5800075673ab3abe0e' as type_of_contract,
                                      null                                                         as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 5
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5b46472f62d243f28c789cfa00dc4859a06973a8' as contract_id,
                                      null                                                         as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '07d4db4f54185adb5764b984c15bd99af4d744a6' as channel,
                                      custom_fields ->> '2309f45a7f595fb1f1a2b6717b543fdeb125b476' as type_of_contract,
                                      null                                                         as connected_deal,
                                      custom_fields ->> 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2' as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 6
                           ) as d
                  ) as f
             where f.rn = 1
         ) as a
             left join
         analyst.voytekh_view_pd_user as d
         on a.user_id = d.pd_id and a.which_crm = d.which_crm
             left join
         (
             select login, lead_login, lead_name_first, lead_name_last, hierarchy
             from analyst.voytekh_manager_v2
         ) as m
         on lower(split_part(d.email, '@', 1)) = m.login
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as product_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as product_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '5bac18975d5257cf98f905dc219a05eaef604eab'
                  ) as s
         ) as l
         on a.crm = l.which_crm and a.product_key = l.product_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as type_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as type_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '6e5fed220a3295084c4b362a14293a720a9bc306'
                      or key = 'f122996cbf393aeeeb686cccde00329c24775562'
                      or key = 'e54a319c8628880942a56d5800075673ab3abe0e'
                      or key = '2309f45a7f595fb1f1a2b6717b543fdeb125b476'
                  ) as s
         ) as h
         on a.crm = h.which_crm and a.type_of_contract = h.type_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as channel_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as channel_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '25f3004a1c052739b4081f3fc764b755d4439536'
                      or key = '61d893466026ae650198c4f6f94a5d280c291107'
                      or key = 'eb8b26a6266d99ae6f1098d33b66bb620391f172'
                      or key = '07d4db4f54185adb5764b984c15bd99af4d744a6'
                  ) as s
         ) as g
         on a.crm = g.which_crm and a.channel = g.channel_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '23076f44b238c77e85159ff67189f42f5e235066'
                      or key = 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361'
                      or key = '60d803d64af12b5fe955671511fe816f81b5fb8d'
                  ) as s
         ) as z
         on a.crm = z.which_crm and a.segment = z.segment_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as communication_with_BA_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as communication_with_BA
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2'
                  ) as s
         ) as zc
         on a.crm = zc.which_crm and a.communication_with_BA_key = zc.communication_with_BA_key
             left join
         (
             select id,
                    which_crm,
                    name          as org_name,
                    split_part(coalesce(
                                       custom_fields ->> 'e667a4f1b486b96695f0cd964a1a548945ad6d3e',
                                       custom_fields ->> '8cda0a729605af0b786b69a88ea82c2487aa2dfb',
                                       null), ',',
                               1) as org_segment
             from (
                      select *,
                             row_number()
                             over (partition by id, which_crm, name ORDER BY update_time desc) as rn
                      from analyst.voytekh_pd2_org
                  ) as t
             where rn = 1
         ) as u
         on a.crm = u.which_crm and a.org_id = u.id
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as org_segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as org_segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_pd2_org_field
                   where key = 'e667a4f1b486b96695f0cd964a1a548945ad6d3e'
                      or key = '8cda0a729605af0b786b69a88ea82c2487aa2dfb'
                  ) as s
         ) as o
         on u.which_crm = o.which_crm and u.org_segment = o.org_segment_key
             left join
         (
             SELECT contract,
                    cancelled_dt,
                    currency,
                    finish_dt,
                    is_deactivated,
                    suspended_dt,
                    contract_type,
                    payment_type,
                    faxed_dt
             FROM (
                      SELECT contract,
                             cancelled_dt,
                             currency,
                             finish_dt,
                             is_deactivated,
                             suspended_dt,
                             contract_type,
                             payment_type,
                             faxed_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt desc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as kk
         on a.contract_id = kk.contract
             left join
         (
             SELECT contract, start_dt
             FROM (
                      SELECT contract,
                             start_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt asc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as k
         on a.contract_id = k.contract
             left join
         (
             select pd_id, name as stage_name, which_crm, pipeline
             from analyst.voytekh_pd_stage
         ) as pp
         on pp.pd_id = a.stage_id and a.which_crm = pp.which_crm
             left join
         (
             select which_crm, pd_id, name as funnel_name
             from analyst.voytekh_pd_pipeline
         ) as rr
         on rr.which_crm = a.which_crm and rr.pd_id = pp.pipeline
             left join
         (
             select balance_rub,
                    client_name,
                    contract_status,
                    deactivate_threshold_rub,
                    contract_id,
                    fielddate
             from analyst.voytova_b2b_balance_on_all_dates
         ) as bh
         on a.contract_id = bh.contract_id and
            cast(a.record_date as date) = cast(bh.fielddate as date)
              left join
         (
             select corp_contract_id,
                    day
             from (
                      select *
                      from (
                               select corp_contract_id,
                                      order_id,
                                      utc_order_dt                                                            as day,
                                      order_tariff,
                                      row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                               from summary.dm_order
                               where corp_order_flg
--       utc_order_dt >= '2020-05-01'
                                 and success_order_flg
                                 and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                           ) as first_trips
                      where rn = 1
                  ) as ftr_all
         ) as first_trip_day
         on a.contract_id = first_trip_day.corp_contract_id
)
--------- all dash wo step by step ---
------------------------------------
-- основной скрипт добавил активацию и поездки
-------------------------------------------------------
select count(*)                            as cnt_deal_id,
                coalesce(lost_reason, 'empty')      as lost_reason,
                which_crm,
                record_date,
                status,
                coalesce(segment_result, 'empty')   as segment_result,
                coalesce(lead_name, 'empty')        as lead_name,
                coalesce(lead_login, 'empty')       as lead_login,
                coalesce(manager_login, 'empty')    as manager_login,
                coalesce(manager_name, 'empty')     as manager_name,
                product_value,
                coalesce(currency, 'empty')         as currency,
                coalesce(contract_type, 'empty')    as contract_type,
                coalesce(payment_type, 'empty')     as payment_type,
                coalesce(channel_value, 'empty')    as channel_value,
                coalesce(type_of_contract, 'empty') as type_of_contract,
                start_dt,
                stage_name,
                funnel_name,
                add_date,
                potential,
                stg_nm,
                'SALES' as fun_nm
         from (
                  select *
                  from (
                           select *,
                                  row_number() over (partition by deal_id, stg_nm order by add_date) as rn
                           from (
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ИНТЕРЕС' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПЕРЕГОВОРЫ', 'НАПРАВЛЕНО ПРЕДЛОЖЕНИЕ', 'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ',
                                           'ОБРАТНАЯ СВЯЗЬ',
                                           'ЖДЕМ ДОГОВОР', 'ПРИНЯТО РЕШЕНИЕ', 'ИНТЕРЕС'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ОБРАТНАЯ СВЯЗЬ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПЕРЕГОВОРЫ', 'НАПРАВЛЕНО ПРЕДЛОЖЕНИЕ', 'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ',
                                           'ОБРАТНАЯ СВЯЗЬ',
                                           'ЖДЕМ ДОГОВОР', 'ПРИНЯТО РЕШЕНИЕ'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'НАПРАВЛЕНО ПРЕДЛОЖЕНИЕ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПЕРЕГОВОРЫ', 'НАПРАВЛЕНО ПРЕДЛОЖЕНИЕ', 'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ',
                                           'ЖДЕМ ДОГОВОР',
                                           'ПРИНЯТО РЕШЕНИЕ'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПЕРЕГОВОРЫ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПЕРЕГОВОРЫ', 'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ', 'ЖДЕМ ДОГОВОР', 'ПРИНЯТО РЕШЕНИЕ'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ТЕСТИРОВАНИЕ/ИНТЕГРАЦИЯ', 'ЖДЕМ ДОГОВОР', 'ПРИНЯТО РЕШЕНИЕ'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПРИНЯТО РЕШЕНИЕ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ЖДЕМ ДОГОВОР', 'ПРИНЯТО РЕШЕНИЕ'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ЖДЕМ ДОГОВОР' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 6
                                      and funnel_name in ('SALES')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                              'ЖДЕМ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select *
                                                            from analyst.voytova_b2b_contracts_info_all
                                                            where activated_dt is not null
                                             ) as activ_cont
                                                           on
                                                               asdf.contract_id = activ_cont.contract_id
                                             where asdf.which_crm = 6
--   and funnel_name in ('SALES')
                                               and asdf.record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdfd
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES'
--     and record_date = current_date
                                          and which_crm = 6
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm) as stg_nm_all
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select corp_contract_id,
                                                                   day
                                                            from (
                                                                     select *
                                                                     from (
                                                                              select corp_contract_id,
                                                                                     order_id,
                                                                                     utc_order_dt                                                            as day,
                                                                                     order_tariff,
                                                                                     row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                                              from summary.dm_order
                                                                              where corp_order_flg
                                                                                and success_order_flg
                                                                                and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                                                          ) as first_trips
                                                                     where rn = 1
                                                                 ) as ftr_all
                                             ) as date_first_trip
                                                           on
                                                               asdf.contract_id = date_first_trip.corp_contract_id
                                             where which_crm = 6
--   and funnel_name in ('SALES')
                                               and record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdf
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES'
--     and record_date = current_date
                                          and which_crm = 6
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm
                                        union all
                                        select 'ЕСТЬ ПОЕЗДКА' as stg_nm) as stg_nm_all
                                ) as all_stage_wo_rn
                       ) as all_stage_rn
             where rn = 1
              ) as all_stage
         group by potential,
                  lost_reason,
                  which_crm,
                  status,
                  segment_result,
                  lead_name,
                  lead_login,
                  manager_login,
                  manager_name,
                  product_value,
                  currency,
                  contract_type,
                  payment_type,
                  channel_value,
                  type_of_contract,
                  start_dt,
                  stage_name,
                  funnel_name,
                  add_date,
                  stg_nm,
                  record_date,
                  fun_nm
union all
select count(*)                            as cnt_deal_id,
                coalesce(lost_reason, 'empty')      as lost_reason,
                which_crm,
                record_date,
                status,
                coalesce(segment_result, 'empty')   as segment_result,
                coalesce(lead_name, 'empty')        as lead_name,
                coalesce(lead_login, 'empty')       as lead_login,
                coalesce(manager_login, 'empty')    as manager_login,
                coalesce(manager_name, 'empty')     as manager_name,
                product_value,
                coalesce(currency, 'empty')         as currency,
                coalesce(contract_type, 'empty')    as contract_type,
                coalesce(payment_type, 'empty')     as payment_type,
                coalesce(channel_value, 'empty')    as channel_value,
                coalesce(type_of_contract, 'empty') as type_of_contract,
                start_dt,
                stage_name,
                funnel_name,
                add_date,
                potential,
                stg_nm,
                'SALES_MM' as fun_nm
         from (
                  select *
                  from (
                           select *,
                                  row_number() over (partition by deal_id, stg_nm order by add_date) as rn
                           from (
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ИЗУЧИТЬ КЛИЕНТА' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES MM')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ИЗУЧИТЬ КЛИЕНТА',
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ',
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES MM')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ',
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПОЛУЧИТЬ РЕШЕНИЕ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES MM')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'СОГЛАСОВАТЬ ДОГОВОР' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES MM')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES MM')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР (СКАН)'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select *
                                                            from analyst.voytova_b2b_contracts_info_all
                                                            where activated_dt is not null
                                             ) as activ_cont
                                                           on
                                                               asdf.contract_id = activ_cont.contract_id
                                             join (select *
                                                from ( select * from
                                                                  (
                                                                        select deal_id,
                                                                               which_crm,
                                                                               record_date,
                                                                               funnel_name,
                                                                               row_number()
                                                                               over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                        from (select * from data_temp_table) as dataframe_all
                                                                        where true
                                                                          and which_crm = 0
                                                                          and funnel_name in ( 'SALES MM' ,'SALES T1' )
                                                                    ) as deals
                                                                  where rn = 1 ) as dataframe_sales
                                                 where funnel_name = 'SALES MM' ) as deal_in_sales
                                              on asdf.deal_id = deal_in_sales.deal_id
                                             where true
                                               and asdf.which_crm = 0
--                                                and asdf.funnel_name in ('SALES MM')
                                               and asdf.record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdfd
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES MM'
--     and record_date = current_date
                                          and which_crm = 0
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm) as stg_nm_all
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select corp_contract_id,
                                                                   day
                                                            from (
                                                                     select *
                                                                     from (
                                                                              select corp_contract_id,
                                                                                     order_id,
                                                                                     utc_order_dt                                                            as day,
                                                                                     order_tariff,
                                                                                     row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                                              from summary.dm_order
                                                                              where corp_order_flg
                                                                                and success_order_flg
                                                                                and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                                                          ) as first_trips
                                                                     where rn = 1
                                                                 ) as ftr_all
                                             ) as date_first_trip
                                                          on
                                                               asdf.contract_id = date_first_trip.corp_contract_id
                                             join (select *
                                                from (
                                                    select * from
                                                                  (
                                                                        select deal_id,
                                                                               which_crm,
                                                                               record_date,
                                                                               funnel_name,
                                                                               row_number()
                                                                               over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                        from (select * from data_temp_table) as dataframe_all
                                                                        where true
                                                                          and which_crm = 0
                                                                          and funnel_name in ( 'SALES MM' ,'SALES T1' )
                                                                    ) as deals
                                                                  where rn = 1
                                                     ) as dataframe_sales
                                                 where funnel_name = 'SALES MM'
                                                 ) as deal_in_sales
                                                on
                                                    asdf.deal_id = deal_in_sales.deal_id
                                             where true
                                               and asdf.which_crm = 0
--                                                and asdf.funnel_name in ('SALES MM')
                                               and asdf.record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdf
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES MM'
--     and record_date = current_date
                                          and which_crm = 0
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm
                                        union all
                                        select 'ЕСТЬ ПОЕЗДКА' as stg_nm) as stg_nm_all
                                ) as all_stage_wo_rn
                       ) as all_stage_rn
             where rn = 1
              ) as all_stage
         group by potential,
                  lost_reason,
                  which_crm,
                  status,
                  segment_result,
                  lead_name,
                  lead_login,
                  manager_login,
                  manager_name,
                  product_value,
                  currency,
                  contract_type,
                  payment_type,
                  channel_value,
                  type_of_contract,
                  start_dt,
                  stage_name,
                  funnel_name,
                  add_date,
                  stg_nm,
                  record_date,
                  fun_nm
union all
select count(*)                            as cnt_deal_id,
                coalesce(lost_reason, 'empty')      as lost_reason,
                which_crm,
                record_date,
                status,
                coalesce(segment_result, 'empty')   as segment_result,
                coalesce(lead_name, 'empty')        as lead_name,
                coalesce(lead_login, 'empty')       as lead_login,
                coalesce(manager_login, 'empty')    as manager_login,
                coalesce(manager_name, 'empty')     as manager_name,
                product_value,
                coalesce(currency, 'empty')         as currency,
                coalesce(contract_type, 'empty')    as contract_type,
                coalesce(payment_type, 'empty')     as payment_type,
                coalesce(channel_value, 'empty')    as channel_value,
                coalesce(type_of_contract, 'empty') as type_of_contract,
                start_dt,
                stage_name,
                funnel_name,
                add_date,
                potential,
                stg_nm,
                'SALES_T1' as fun_nm
         from (
                  select *
                  from (
                           select *,
                                  row_number() over (partition by deal_id, stg_nm order by add_date) as rn
                           from (
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ИЗУЧИТЬ КЛИЕНТА' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ИЗУЧИТЬ КЛИЕНТА',
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ',
                                           'ПРОВЕСТИ ПРЕЗЕНТАЦИЮ',
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ДОГОВОРИТЬСЯ О ПРЕЗЕНТАЦИИ',
                                           'ПРОВЕСТИ ПРЕЗЕНТАЦИЮ',
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПРОВЕСТИ ПРЕЗЕНТАЦИЮ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПРОВЕСТИ ПРЕЗЕНТАЦИЮ',
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПОЛУЧИТЬ РЕШЕНИЕ' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПОЛУЧИТЬ РЕШЕНИЕ',
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'СОГЛАСОВАТЬ ДОГОВОР' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'СОГЛАСОВАТЬ ДОГОВОР',
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР' as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as asdf
                                    where which_crm = 0
                                      and funnel_name in ('SALES T1')
                                      and record_date = current_date
                                      and stage_name in
                                          (
                                           'ПОЛУЧИТЬ ПОДПИСАННЫЙ ДОГОВОР'
                                              )
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select *
                                                            from analyst.voytova_b2b_contracts_info_all
                                                            where activated_dt is not null
                                             ) as activ_cont
                                                           on
                                                               asdf.contract_id = activ_cont.contract_id
                                             join (select *
                                                from ( select * from
                                                                  (
                                                                        select deal_id,
                                                                               which_crm,
                                                                               record_date,
                                                                               funnel_name,
                                                                               row_number()
                                                                               over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                        from (select * from data_temp_table) as dataframe_all
                                                                        where true
                                                                          and which_crm = 0
                                                                          and funnel_name in ( 'SALES MM' ,'SALES T1' )
                                                                    ) as deals
                                                                  where rn = 1 ) as dataframe_sales
                                                 where funnel_name = 'SALES T1' ) as deal_in_sales
                                              on asdf.deal_id = deal_in_sales.deal_id
                                             where true
                                               and asdf.which_crm = 0
--                                             and asdf.funnel_name in ('SALES T1')
                                               and asdf.record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdfd
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES T1'
--     and record_date = current_date
                                          and which_crm = 0
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm) as stg_nm_all
                                    union all
                                    select deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           contract_id,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           cancelled_dt,
                                           currency,
                                           is_deactivated,
                                           suspended_dt,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           start_dt,
                                           connected_deal,
                                           stage_name,
                                           stg_nm_all.stg_nm as stg_nm,
                                           funnel_name,
                                           add_date,
                                           potential,
                                           record_date
                                    from (
                                             select asdf.*
                                             from (
                                                      select *
                                                      from data_temp_table
                                                  ) as asdf
                                                      join (select corp_contract_id,
                                                                   day
                                                            from (
                                                                     select *
                                                                     from (
                                                                              select corp_contract_id,
                                                                                     order_id,
                                                                                     utc_order_dt                                                            as day,
                                                                                     order_tariff,
                                                                                     row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                                              from summary.dm_order
                                                                              where corp_order_flg
                                                                                and success_order_flg
                                                                                and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                                                          ) as first_trips
                                                                     where rn = 1
                                                                 ) as ftr_all
                                             ) as date_first_trip
                                                          on
                                                               asdf.contract_id = date_first_trip.corp_contract_id
                                             join (select *
                                                from (
                                                    select * from
                                                                  (
                                                                        select deal_id,
                                                                               which_crm,
                                                                               record_date,
                                                                               funnel_name,
                                                                               row_number()
                                                                               over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                        from (select * from data_temp_table) as dataframe_all
                                                                        where true
                                                                          and which_crm = 0
                                                                          and funnel_name in ( 'SALES MM' ,'SALES T1' )
                                                                    ) as deals
                                                                  where rn = 1
                                                     ) as dataframe_sales
                                                 where funnel_name = 'SALES T1'
                                                 ) as deal_in_sales
                                                on
                                                    asdf.deal_id = deal_in_sales.deal_id
                                             where true
                                               and asdf.which_crm = 0
--                                                and asdf.funnel_name in ('SALES T1')
                                               and asdf.record_date = current_date
                                               and asdf.contract_id is not null
                                               and asdf.contract_id != ''
                                         ) as asdf
                                             cross join (
                                        select distinct stage_name as stg_nm
                                        from (
                                                 select *
                                                 from data_temp_table
                                             ) as foooof
                                        where true
                                          and funnel_name like 'SALES T1'
--     and record_date = current_date
                                          and which_crm = 0
                                        union all
                                        select 'ДОГОВОР АКТИВИРОВАН' as stg_nm
                                        union all
                                        select 'ЕСТЬ ПОЕЗДКА' as stg_nm) as stg_nm_all
                                ) as all_stage_wo_rn
                       ) as all_stage_rn
             where rn = 1
              ) as all_stage
         group by potential,
                  lost_reason,
                  which_crm,
                  status,
                  segment_result,
                  lead_name,
                  lead_login,
                  manager_login,
                  manager_name,
                  product_value,
                  currency,
                  contract_type,
                  payment_type,
                  channel_value,
                  type_of_contract,
                  start_dt,
                  stage_name,
                  funnel_name,
                  add_date,
                  stg_nm,
                  record_date,
                  fun_nm
;
'''
greenplum(query)
greenplum('grant select on snb_taxi.ravaev_conversion_all_dash to rawy, voytova, voytekh')


query = '''
drop table if exists snb_taxi.ravaev_conversion_step_by_step_sales;
create table snb_taxi.ravaev_conversion_step_by_step_sales as
WITH data_temp_table as (
    select current_timestamp,
           date(a.add_time)                                             as add_date,
           a.id                                                         as deal_id,
           a.record_date                                                as record_date,
           a.lost_reason                                                as lost_reason,
           a.crm                                                        as which_crm,
           a.status                                                     as status,
           a.last_activity_date                                         as last_activity_date,
           a.contract_id                                                as contract_id,
           a.update_time                                                as update_time,
           first_trip_day.day                                           as day_first_trip,
           case
               when coalesce(a.value, 0) = 0 then '0'
               when coalesce(a.value, 0) > 0 and coalesce(a.value, 0) <= 100 then 'less_100'
               when coalesce(a.value, 0) > 100 and coalesce(a.value, 0) <= 250 then 'less_250'
               when coalesce(a.value, 0) > 250 and coalesce(a.value, 0) <= 500 then 'less_500'
               when coalesce(a.value, 0) > 500 and coalesce(a.value, 0) <= 1000 then 'less_1000'
               when coalesce(a.value, 0) > 1000 and coalesce(a.value, 0) <= 1500 then 'less_1500'
               when coalesce(a.value, 0) > 1500 then 'more_1500'
               end                                                      as potential,
           replace(coalesce(segment_value, org_segment_value), '"', '') as segment_result,
           lead_name_first || ' ' || lead_name_last                     as lead_name,
           lead_login,
           org_id,
           m.login                                                      as manager_login,
           name                                                         as manager_name,
           m.hierarchy                                                  as hierarchy,
           case
               when product_value is not null then product_value
               when a.which_crm = 6 then 'ДОСТАВКА/ГРУЗЫ'
               else 'ТАКСИ'
               end                                                      as product_value,
           cancelled_dt,
           currency,
           finish_dt,
           is_deactivated,
           suspended_dt,
           contract_type,
           payment_type,
           faxed_dt,
           channel_value,
           type_value                                                   as type_of_contract,
           start_dt,
           connected_deal,
           stage_name,
           funnel_name,
           communication_with_BA,
           bh.balance_rub                                               as balance,
           bh.client_name                                               as client_name,
           bh.contract_status                                           as status_from_balance,
           bh.deactivate_threshold_rub                                  as deactivate_threshold_rub
    from (
             select *
             from (
                      select *,
                             ROW_NUMBER()
                             OVER (PARTITION BY id, crm, record_date ORDER BY update_time desc) as rn
                      from (
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '3c226725e7feca6cbd7e7e6ca26ffae5f4219ac4' as contract_id,
                                      custom_fields ->> '23076f44b238c77e85159ff67189f42f5e235066' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '61d893466026ae650198c4f6f94a5d280c291107' as channel,
                                      custom_fields ->> 'f122996cbf393aeeeb686cccde00329c24775562' as type_of_contract,
                                      custom_fields ->> '3df564783f1632c5458d21823fc2f73c0998115f' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 2
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5f8c9c624091f5861ae66d6f95a29bacf83b9acb' as contract_id,
                                      custom_fields ->> 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361' as segment,
                                      custom_fields ->> '5bac18975d5257cf98f905dc219a05eaef604eab' as product_key,
                                      custom_fields ->> '25f3004a1c052739b4081f3fc764b755d4439536' as channel,
                                      custom_fields ->> '6e5fed220a3295084c4b362a14293a720a9bc306' as type_of_contract,
                                      custom_fields ->> '2728cdafd9aa8f1fed33c464560c4d5ec39f59ca' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 0
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '0c886554df85907470227fe1cfe6b072207bc86b' as contract_id,
                                      custom_fields ->> '60d803d64af12b5fe955671511fe816f81b5fb8d' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> 'eb8b26a6266d99ae6f1098d33b66bb620391f172' as channel,
                                      custom_fields ->> 'e54a319c8628880942a56d5800075673ab3abe0e' as type_of_contract,
                                      null                                                         as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 5
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5b46472f62d243f28c789cfa00dc4859a06973a8' as contract_id,
                                      null                                                         as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '07d4db4f54185adb5764b984c15bd99af4d744a6' as channel,
                                      custom_fields ->> '2309f45a7f595fb1f1a2b6717b543fdeb125b476' as type_of_contract,
                                      null                                                         as connected_deal,
                                      custom_fields ->> 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2' as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 6
                           ) as d
                  ) as f
             where f.rn = 1
         ) as a
             left join
         analyst.voytekh_view_pd_user as d
         on a.user_id = d.pd_id and a.which_crm = d.which_crm
             left join
         (
             select login, lead_login, lead_name_first, lead_name_last, hierarchy
             from analyst.voytekh_manager_v2
         ) as m
         on lower(split_part(d.email, '@', 1)) = m.login
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as product_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as product_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '5bac18975d5257cf98f905dc219a05eaef604eab'
                  ) as s
         ) as l
         on a.crm = l.which_crm and a.product_key = l.product_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as type_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as type_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '6e5fed220a3295084c4b362a14293a720a9bc306'
                      or key = 'f122996cbf393aeeeb686cccde00329c24775562'
                      or key = 'e54a319c8628880942a56d5800075673ab3abe0e'
                      or key = '2309f45a7f595fb1f1a2b6717b543fdeb125b476'
                  ) as s
         ) as h
         on a.crm = h.which_crm and a.type_of_contract = h.type_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as channel_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as channel_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '25f3004a1c052739b4081f3fc764b755d4439536'
                      or key = '61d893466026ae650198c4f6f94a5d280c291107'
                      or key = 'eb8b26a6266d99ae6f1098d33b66bb620391f172'
                      or key = '07d4db4f54185adb5764b984c15bd99af4d744a6'
                  ) as s
         ) as g
         on a.crm = g.which_crm and a.channel = g.channel_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '23076f44b238c77e85159ff67189f42f5e235066'
                      or key = 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361'
                      or key = '60d803d64af12b5fe955671511fe816f81b5fb8d'
                  ) as s
         ) as z
         on a.crm = z.which_crm and a.segment = z.segment_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as communication_with_BA_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as communication_with_BA
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2'
                  ) as s
         ) as zc
         on a.crm = zc.which_crm and a.communication_with_BA_key = zc.communication_with_BA_key
             left join
         (
             select id,
                    which_crm,
                    name          as org_name,
                    split_part(coalesce(
                                       custom_fields ->> 'e667a4f1b486b96695f0cd964a1a548945ad6d3e',
                                       custom_fields ->> '8cda0a729605af0b786b69a88ea82c2487aa2dfb',
                                       null), ',',
                               1) as org_segment
             from (
                      select *,
                             row_number()
                             over (partition by id, which_crm, name ORDER BY update_time desc) as rn
                      from analyst.voytekh_pd2_org
                  ) as t
             where rn = 1
         ) as u
         on a.crm = u.which_crm and a.org_id = u.id
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as org_segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as org_segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_pd2_org_field
                   where key = 'e667a4f1b486b96695f0cd964a1a548945ad6d3e'
                      or key = '8cda0a729605af0b786b69a88ea82c2487aa2dfb'
                  ) as s
         ) as o
         on u.which_crm = o.which_crm and u.org_segment = o.org_segment_key
             left join
         (
             SELECT contract,
                    cancelled_dt,
                    currency,
                    finish_dt,
                    is_deactivated,
                    suspended_dt,
                    contract_type,
                    payment_type,
                    faxed_dt
             FROM (
                      SELECT contract,
                             cancelled_dt,
                             currency,
                             finish_dt,
                             is_deactivated,
                             suspended_dt,
                             contract_type,
                             payment_type,
                             faxed_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt desc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as kk
         on a.contract_id = kk.contract
             left join
         (
             SELECT contract, start_dt
             FROM (
                      SELECT contract,
                             start_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt asc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as k
         on a.contract_id = k.contract
             left join
         (
             select pd_id, name as stage_name, which_crm, pipeline
             from analyst.voytekh_pd_stage
         ) as pp
         on pp.pd_id = a.stage_id and a.which_crm = pp.which_crm
             left join
         (
             select which_crm, pd_id, name as funnel_name
             from analyst.voytekh_pd_pipeline
         ) as rr
         on rr.which_crm = a.which_crm and rr.pd_id = pp.pipeline
             left join
         (
             select balance_rub,
                    client_name,
                    contract_status,
                    deactivate_threshold_rub,
                    contract_id,
                    fielddate
             from analyst.voytova_b2b_balance_on_all_dates
         ) as bh
         on a.contract_id = bh.contract_id and
            cast(a.record_date as date) = cast(bh.fielddate as date)
              left join
         (
             select corp_contract_id,
                    day
             from (
                      select *
                      from (
                               select corp_contract_id,
                                      order_id,
                                      utc_order_dt                                                            as day,
                                      order_tariff,
                                      row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                               from summary.dm_order
                               where corp_order_flg
--       utc_order_dt >= '2020-05-01'
                                 and success_order_flg
                                 and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                           ) as first_trips
                      where rn = 1
                  ) as ftr_all
         ) as first_trip_day
         on a.contract_id = first_trip_day.corp_contract_id
)
select *,
       'SALES' as fun_nm
from (
select
       stage_name,
       count(deal_id) as cnt_deal,
       sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
       potential, lost_reason, which_crm, status, segment_result,
       lead_name,
       lead_login, manager_login, manager_name, product_value, currency,
       contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
from (
select
       name_stage.stage_name as stage_name,
       name_stage.deal_id as deal_id,
       coalesce(day_in_stage_by_deal.cnt_day_in_stage_name, 0) as cnt_day_in_stage_name,
       deal_info.potential as potential,
       deal_info.lost_reason as lost_reason,
       deal_info.which_crm as which_crm,
       deal_info.status as status,
       deal_info.segment_result as segment_result,
       deal_info.lead_name as lead_name,
       deal_info.lead_login as lead_login,
       deal_info.manager_login as manager_login,
       deal_info.manager_name as manager_name,
       deal_info.product_value as product_value,
       deal_info.currency as currency,
       deal_info.contract_type as contract_type,
       deal_info.payment_type as payment_type,
       deal_info.channel_value as channel_value,
       deal_info.type_of_contract as type_of_contract,
       deal_info.funnel_name as funnel_name,
       deal_info.add_date as add_date
from (
    select *
    from (
             select *
             from (select distinct stage_name as stage_name
                   from (
                            select * from data_temp_table
                        ) as foooof
                   where true
                     and funnel_name like 'SALES'
--     and record_date = current_date
                     and which_crm = 6) as stages_names
                      cross join
                  (select distinct deal_id as deal_id
                   from (
                            select * from data_temp_table
                        ) as foooof
                   where true
                     and funnel_name like 'SALES'
--     and record_date = current_date
                     and which_crm = 6) as deal_id_all
         ) as all_funnel
        ) as name_stage
left join
    (
    select
       count(distinct record_date) as cnt_day_in_stage_name,
       deal_id, stage_name
    from (
    select * from data_temp_table
          ) as cascn
        where true
        and funnel_name like 'SALES'
    --     and record_date = current_date
        and status not in ('lost')
        and which_crm = 6
    group by
             deal_id,
             stage_name
    ) as day_in_stage_by_deal
on
    name_stage.stage_name = day_in_stage_by_deal.stage_name and
    name_stage.deal_id = day_in_stage_by_deal.deal_id
join
    (
    select add_date, deal_id, lost_reason, which_crm, status,  potential, segment_result, lead_name, lead_login, org_id, manager_login, manager_name,
           product_value, currency, contract_type, payment_type, channel_value, type_of_contract, stage_name, funnel_name,
           contract_id
    from (
    select * from data_temp_table
          ) as cascn
    where true
--         and funnel_name like 'SALES'
        and record_date = current_date
        and which_crm = 6
    ) as deal_info
on name_stage.deal_id = deal_info.deal_id
    ) as datataframe
group by
    stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login, manager_login, manager_name, product_value,
    currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
union all
select stage_name,
       count(deal_id) as cnt_deal,
       sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
       potential, lost_reason, which_crm, status, segment_result,
       lead_name,
       lead_login, manager_login, manager_name, product_value, currency,
       contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
from
     (select deal_id,
       lost_reason,
       which_crm,
       status,
       contract_id,
       segment_result,
       lead_name,
       lead_login,
       org_id,
       manager_login,
       manager_name,
       product_value,
       cancelled_dt,
       currency,
       is_deactivated,
       suspended_dt,
       contract_type,
       payment_type,
       channel_value,
       type_of_contract,
       start_dt,
       connected_deal,
       'ДОГОВОР АКТИВИРОВАН' as stage_name,
       funnel_name,
       add_date,
       potential,
       record_date,
       activated_dt as activated_dt,
       date_first_trip.day as date_first_trip,
       current_date as curr_date,
       case when date_first_trip is null
           then current_date - activated_dt
           else date_first_trip.day - activated_dt end as cnt_day_in_stage_name
from (
       select asdf.*,
              activ_cont.activated_dt as activated_dt
       from ( select *
                from data_temp_table ) as asdf
                join (select *
                      from analyst.voytova_b2b_contracts_info_all
                      where activated_dt is not null ) as activ_cont
                    on
                        asdf.contract_id = activ_cont.contract_id
       where asdf.which_crm = 6
         and asdf.record_date = current_date
         and asdf.contract_id is not null
         and asdf.contract_id != ''
        ) as asdfd
left join
    ( select corp_contract_id,
                                                                   day
                                                            from (
                                                                     select *
                                                                     from (
                                                                              select corp_contract_id,
                                                                                     order_id,
                                                                                     utc_order_dt                                                            as day,
                                                                                     order_tariff,
                                                                                     row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                                              from summary.dm_order
                                                                              where corp_order_flg
                                                                                and success_order_flg
                                                                                and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                                                          ) as first_trips
                                                                     where rn = 1
                                                                 ) as ftr_all ) as date_first_trip
on
    asdfd.contract_id = date_first_trip.corp_contract_id) as fooof
group by
    stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login, manager_login, manager_name, product_value,
    currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
         ) as foof
'''
greenplum(query)
greenplum('grant select on snb_taxi.ravaev_conversion_step_by_step_sales to rawy, voytova, voytekh')


query = '''
drop table if exists snb_taxi.ravaev_conversion_step_by_step_sales_mm;
create table snb_taxi.ravaev_conversion_step_by_step_sales_mm as
WITH data_temp_table as (
    select current_timestamp,
           date(a.add_time)                                             as add_date,
           a.id                                                         as deal_id,
           a.record_date                                                as record_date,
           a.lost_reason                                                as lost_reason,
           a.crm                                                        as which_crm,
           a.status                                                     as status,
           a.last_activity_date                                         as last_activity_date,
           a.contract_id                                                as contract_id,
           a.update_time                                                as update_time,
           first_trip_day.day                                           as day_first_trip,
           case
               when coalesce(a.value, 0) = 0 then '0'
               when coalesce(a.value, 0) > 0 and coalesce(a.value, 0) <= 100 then 'less_100'
               when coalesce(a.value, 0) > 100 and coalesce(a.value, 0) <= 250 then 'less_250'
               when coalesce(a.value, 0) > 250 and coalesce(a.value, 0) <= 500 then 'less_500'
               when coalesce(a.value, 0) > 500 and coalesce(a.value, 0) <= 1000 then 'less_1000'
               when coalesce(a.value, 0) > 1000 and coalesce(a.value, 0) <= 1500 then 'less_1500'
               when coalesce(a.value, 0) > 1500 then 'more_1500'
               end                                                      as potential,
           replace(coalesce(segment_value, org_segment_value), '"', '') as segment_result,
           lead_name_first || ' ' || lead_name_last                     as lead_name,
           lead_login,
           org_id,
           m.login                                                      as manager_login,
           name                                                         as manager_name,
           m.hierarchy                                                  as hierarchy,
           case
               when product_value is not null then product_value
               when a.which_crm = 6 then 'ДОСТАВКА/ГРУЗЫ'
               else 'ТАКСИ'
               end                                                      as product_value,
           cancelled_dt,
           currency,
           finish_dt,
           is_deactivated,
           suspended_dt,
           contract_type,
           payment_type,
           faxed_dt,
           channel_value,
           type_value                                                   as type_of_contract,
           start_dt,
           connected_deal,
           stage_name,
           funnel_name,
           communication_with_BA,
           bh.balance_rub                                               as balance,
           bh.client_name                                               as client_name,
           bh.contract_status                                           as status_from_balance,
           bh.deactivate_threshold_rub                                  as deactivate_threshold_rub
    from (
             select *
             from (
                      select *,
                             ROW_NUMBER()
                             OVER (PARTITION BY id, crm, record_date ORDER BY update_time desc) as rn
                      from (
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '3c226725e7feca6cbd7e7e6ca26ffae5f4219ac4' as contract_id,
                                      custom_fields ->> '23076f44b238c77e85159ff67189f42f5e235066' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '61d893466026ae650198c4f6f94a5d280c291107' as channel,
                                      custom_fields ->> 'f122996cbf393aeeeb686cccde00329c24775562' as type_of_contract,
                                      custom_fields ->> '3df564783f1632c5458d21823fc2f73c0998115f' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 2
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5f8c9c624091f5861ae66d6f95a29bacf83b9acb' as contract_id,
                                      custom_fields ->> 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361' as segment,
                                      custom_fields ->> '5bac18975d5257cf98f905dc219a05eaef604eab' as product_key,
                                      custom_fields ->> '25f3004a1c052739b4081f3fc764b755d4439536' as channel,
                                      custom_fields ->> '6e5fed220a3295084c4b362a14293a720a9bc306' as type_of_contract,
                                      custom_fields ->> '2728cdafd9aa8f1fed33c464560c4d5ec39f59ca' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 0
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '0c886554df85907470227fe1cfe6b072207bc86b' as contract_id,
                                      custom_fields ->> '60d803d64af12b5fe955671511fe816f81b5fb8d' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> 'eb8b26a6266d99ae6f1098d33b66bb620391f172' as channel,
                                      custom_fields ->> 'e54a319c8628880942a56d5800075673ab3abe0e' as type_of_contract,
                                      null                                                         as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 5
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5b46472f62d243f28c789cfa00dc4859a06973a8' as contract_id,
                                      null                                                         as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '07d4db4f54185adb5764b984c15bd99af4d744a6' as channel,
                                      custom_fields ->> '2309f45a7f595fb1f1a2b6717b543fdeb125b476' as type_of_contract,
                                      null                                                         as connected_deal,
                                      custom_fields ->> 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2' as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 6
                           ) as d
                  ) as f
             where f.rn = 1
         ) as a
             left join
         analyst.voytekh_view_pd_user as d
         on a.user_id = d.pd_id and a.which_crm = d.which_crm
             left join
         (
             select login, lead_login, lead_name_first, lead_name_last, hierarchy
             from analyst.voytekh_manager_v2
         ) as m
         on lower(split_part(d.email, '@', 1)) = m.login
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as product_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as product_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '5bac18975d5257cf98f905dc219a05eaef604eab'
                  ) as s
         ) as l
         on a.crm = l.which_crm and a.product_key = l.product_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as type_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as type_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '6e5fed220a3295084c4b362a14293a720a9bc306'
                      or key = 'f122996cbf393aeeeb686cccde00329c24775562'
                      or key = 'e54a319c8628880942a56d5800075673ab3abe0e'
                      or key = '2309f45a7f595fb1f1a2b6717b543fdeb125b476'
                  ) as s
         ) as h
         on a.crm = h.which_crm and a.type_of_contract = h.type_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as channel_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as channel_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '25f3004a1c052739b4081f3fc764b755d4439536'
                      or key = '61d893466026ae650198c4f6f94a5d280c291107'
                      or key = 'eb8b26a6266d99ae6f1098d33b66bb620391f172'
                      or key = '07d4db4f54185adb5764b984c15bd99af4d744a6'
                  ) as s
         ) as g
         on a.crm = g.which_crm and a.channel = g.channel_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '23076f44b238c77e85159ff67189f42f5e235066'
                      or key = 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361'
                      or key = '60d803d64af12b5fe955671511fe816f81b5fb8d'
                  ) as s
         ) as z
         on a.crm = z.which_crm and a.segment = z.segment_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as communication_with_BA_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as communication_with_BA
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2'
                  ) as s
         ) as zc
         on a.crm = zc.which_crm and a.communication_with_BA_key = zc.communication_with_BA_key
             left join
         (
             select id,
                    which_crm,
                    name          as org_name,
                    split_part(coalesce(
                                       custom_fields ->> 'e667a4f1b486b96695f0cd964a1a548945ad6d3e',
                                       custom_fields ->> '8cda0a729605af0b786b69a88ea82c2487aa2dfb',
                                       null), ',',
                               1) as org_segment
             from (
                      select *,
                             row_number()
                             over (partition by id, which_crm, name ORDER BY update_time desc) as rn
                      from analyst.voytekh_pd2_org
                  ) as t
             where rn = 1
         ) as u
         on a.crm = u.which_crm and a.org_id = u.id
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as org_segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as org_segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_pd2_org_field
                   where key = 'e667a4f1b486b96695f0cd964a1a548945ad6d3e'
                      or key = '8cda0a729605af0b786b69a88ea82c2487aa2dfb'
                  ) as s
         ) as o
         on u.which_crm = o.which_crm and u.org_segment = o.org_segment_key
             left join
         (
             SELECT contract,
                    cancelled_dt,
                    currency,
                    finish_dt,
                    is_deactivated,
                    suspended_dt,
                    contract_type,
                    payment_type,
                    faxed_dt
             FROM (
                      SELECT contract,
                             cancelled_dt,
                             currency,
                             finish_dt,
                             is_deactivated,
                             suspended_dt,
                             contract_type,
                             payment_type,
                             faxed_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt desc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as kk
         on a.contract_id = kk.contract
             left join
         (
             SELECT contract, start_dt
             FROM (
                      SELECT contract,
                             start_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt asc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as k
         on a.contract_id = k.contract
             left join
         (
             select pd_id, name as stage_name, which_crm, pipeline
             from analyst.voytekh_pd_stage
         ) as pp
         on pp.pd_id = a.stage_id and a.which_crm = pp.which_crm
             left join
         (
             select which_crm, pd_id, name as funnel_name
             from analyst.voytekh_pd_pipeline
         ) as rr
         on rr.which_crm = a.which_crm and rr.pd_id = pp.pipeline
             left join
         (
             select balance_rub,
                    client_name,
                    contract_status,
                    deactivate_threshold_rub,
                    contract_id,
                    fielddate
             from analyst.voytova_b2b_balance_on_all_dates
         ) as bh
         on a.contract_id = bh.contract_id and
            cast(a.record_date as date) = cast(bh.fielddate as date)
              left join
         (
             select corp_contract_id,
                    day
             from (
                      select *
                      from (
                               select corp_contract_id,
                                      order_id,
                                      utc_order_dt                                                            as day,
                                      order_tariff,
                                      row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                               from summary.dm_order
                               where corp_order_flg
--       utc_order_dt >= '2020-05-01'
                                 and success_order_flg
                                 and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                           ) as first_trips
                      where rn = 1
                  ) as ftr_all
         ) as first_trip_day
         on a.contract_id = first_trip_day.corp_contract_id
)
select *,
                'SALES_MM' as fun_nm
         from (
                  select stage_name,
                         count(deal_id)             as cnt_deal,
                         sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
                         potential,
                         lost_reason,
                         which_crm,
                         status,
                         segment_result,
                         lead_name,
                         lead_login,
                         manager_login,
                         manager_name,
                         product_value,
                         currency,
                         contract_type,
                         payment_type,
                         channel_value,
                         type_of_contract,
                         funnel_name,
                         add_date
                  from (
                           select name_stage.stage_name                                   as stage_name,
                                  name_stage.deal_id                                      as deal_id,
                                  coalesce(day_in_stage_by_deal.cnt_day_in_stage_name, 0) as cnt_day_in_stage_name,
                                  deal_info.potential                                     as potential,
                                  deal_info.lost_reason                                   as lost_reason,
                                  deal_info.which_crm                                     as which_crm,
                                  deal_info.status                                        as status,
                                  deal_info.segment_result                                as segment_result,
                                  deal_info.lead_name                                     as lead_name,
                                  deal_info.lead_login                                    as lead_login,
                                  deal_info.manager_login                                 as manager_login,
                                  deal_info.manager_name                                  as manager_name,
                                  deal_info.product_value                                 as product_value,
                                  deal_info.currency                                      as currency,
                                  deal_info.contract_type                                 as contract_type,
                                  deal_info.payment_type                                  as payment_type,
                                  deal_info.channel_value                                 as channel_value,
                                  deal_info.type_of_contract                              as type_of_contract,
                                  deal_info.funnel_name                                   as funnel_name,
                                  deal_info.add_date                                      as add_date
                           from (
                                    select *
                                    from (
                                             select *
                                             from (select distinct stage_name as stage_name
                                                   from (
                                                            select *
                                                            from data_temp_table
                                                        ) as foooof
                                                   where true
                                                     and funnel_name like 'SALES MM'
--     and record_date = current_date
                                                     and which_crm = 0) as stages_names
                                                      cross join
                                                  (select distinct deal_id as deal_id
                                                   from (
                                                            select *
                                                            from data_temp_table
                                                        ) as foooof
                                                   where true
                                                     and funnel_name like 'SALES MM'
--     and record_date = current_date
                                                     and which_crm = 0) as deal_id_all
                                         ) as all_funnel
                                ) as name_stage
                                    left join
                                (
                                    select count(distinct record_date) as cnt_day_in_stage_name,
                                           deal_id,
                                           stage_name
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as cascn
                                    where true
                                      and funnel_name like 'SALES MM'
                                      --     and record_date = current_date
                                      and status not in ('lost')
                                      and which_crm = 0
                                    group by deal_id,
                                             stage_name
                                ) as day_in_stage_by_deal
                                on
                                        name_stage.stage_name = day_in_stage_by_deal.stage_name and
                                        name_stage.deal_id = day_in_stage_by_deal.deal_id
                                    join
                                (
                                    select add_date,
                                           deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           potential,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           currency,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           stage_name,
                                           funnel_name,
                                           contract_id
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as cascn
                                    where true
--                                       and funnel_name like 'SALES MM'
                                      and record_date = current_date
                                      and which_crm = 0
                                ) as deal_info
                                on name_stage.deal_id = deal_info.deal_id
                       ) as datataframe
                  group by stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login,
                           manager_login, manager_name, product_value,
                           currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
                  union all
                  select stage_name,
                         count(deal_id)             as cnt_deal,
                         sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
                         potential,
                         lost_reason,
                         which_crm,
                         status,
                         segment_result,
                         lead_name,
                         lead_login,
                         manager_login,
                         manager_name,
                         product_value,
                         currency,
                         contract_type,
                         payment_type,
                         channel_value,
                         type_of_contract,
                         funnel_name,
                         add_date
                  from (select deal_id,
                               lost_reason,
                               which_crm,
                               status,
                               contract_id,
                               segment_result,
                               lead_name,
                               lead_login,
                               org_id,
                               manager_login,
                               manager_name,
                               product_value,
                               cancelled_dt,
                               currency,
                               is_deactivated,
                               suspended_dt,
                               contract_type,
                               payment_type,
                               channel_value,
                               type_of_contract,
                               start_dt,
                               connected_deal,
                               'ДОГОВОР АКТИВИРОВАН'                           as stage_name,
                               funnel_name,
                               add_date,
                               potential,
                               record_date,
                               activated_dt                                    as activated_dt,
                               date_first_trip.day                             as date_first_trip,
                               current_date                                    as curr_date,
                               case
                                   when date_first_trip is null
                                       then current_date - activated_dt
                                   else date_first_trip.day - activated_dt end as cnt_day_in_stage_name
                        from (
                                 select asdf.*,
                                        activ_cont.activated_dt as activated_dt
                                 from (select *
                                       from data_temp_table) as asdf
                                          join (select *
                                                from analyst.voytova_b2b_contracts_info_all
                                                where activated_dt is not null) as activ_cont
                                               on asdf.contract_id = activ_cont.contract_id
                                          join (select *
                                                from (
                                                         select *
                                                         from (
                                                                  select deal_id,
                                                                         which_crm,
                                                                         record_date,
                                                                         funnel_name,
                                                                         row_number()
                                                                         over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                  from (select * from data_temp_table) as dataframe_all
                                                                  where true
                                                                    and which_crm = 0
                                                                    and funnel_name in ('SALES MM', 'SALES T1')
                                                              ) as deals
                                                         where rn = 1
                                                     ) as dataframe_sales
                                                where funnel_name = 'SALES MM') as deal_in_sales
                                               on asdf.deal_id = deal_in_sales.deal_id
                                 where asdf.which_crm = 0
                                   and asdf.record_date = current_date
                                   and asdf.contract_id is not null
                                   and asdf.contract_id != ''
                             ) as asdfd
                                 left join
                             (select corp_contract_id,
                                     day
                              from (
                                       select *
                                       from (
                                                select corp_contract_id,
                                                       order_id,
                                                       utc_order_dt                                                            as day,
                                                       order_tariff,
                                                       row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                from summary.dm_order
                                                where corp_order_flg
                                                  and success_order_flg
                                                  and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                            ) as first_trips
                                       where rn = 1
                                   ) as ftr_all) as date_first_trip
                             on
                                 asdfd.contract_id = date_first_trip.corp_contract_id) as fooof
                  group by stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login,
                           manager_login, manager_name, product_value,
                           currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
              ) as foof
'''
greenplum(query)
greenplum('grant select on snb_taxi.ravaev_conversion_step_by_step_sales_mm to rawy, voytova, voytekh')



query = '''
drop table if exists snb_taxi.ravaev_conversion_step_by_step_sales_t;
create table snb_taxi.ravaev_conversion_step_by_step_sales_t as
WITH data_temp_table as (
    select current_timestamp,
           date(a.add_time)                                             as add_date,
           a.id                                                         as deal_id,
           a.record_date                                                as record_date,
           a.lost_reason                                                as lost_reason,
           a.crm                                                        as which_crm,
           a.status                                                     as status,
           a.last_activity_date                                         as last_activity_date,
           a.contract_id                                                as contract_id,
           a.update_time                                                as update_time,
           first_trip_day.day                                           as day_first_trip,
           case
               when coalesce(a.value, 0) = 0 then '0'
               when coalesce(a.value, 0) > 0 and coalesce(a.value, 0) <= 100 then 'less_100'
               when coalesce(a.value, 0) > 100 and coalesce(a.value, 0) <= 250 then 'less_250'
               when coalesce(a.value, 0) > 250 and coalesce(a.value, 0) <= 500 then 'less_500'
               when coalesce(a.value, 0) > 500 and coalesce(a.value, 0) <= 1000 then 'less_1000'
               when coalesce(a.value, 0) > 1000 and coalesce(a.value, 0) <= 1500 then 'less_1500'
               when coalesce(a.value, 0) > 1500 then 'more_1500'
               end                                                      as potential,
           replace(coalesce(segment_value, org_segment_value), '"', '') as segment_result,
           lead_name_first || ' ' || lead_name_last                     as lead_name,
           lead_login,
           org_id,
           m.login                                                      as manager_login,
           name                                                         as manager_name,
           m.hierarchy                                                  as hierarchy,
           case
               when product_value is not null then product_value
               when a.which_crm = 6 then 'ДОСТАВКА/ГРУЗЫ'
               else 'ТАКСИ'
               end                                                      as product_value,
           cancelled_dt,
           currency,
           finish_dt,
           is_deactivated,
           suspended_dt,
           contract_type,
           payment_type,
           faxed_dt,
           channel_value,
           type_value                                                   as type_of_contract,
           start_dt,
           connected_deal,
           stage_name,
           funnel_name,
           communication_with_BA,
           bh.balance_rub                                               as balance,
           bh.client_name                                               as client_name,
           bh.contract_status                                           as status_from_balance,
           bh.deactivate_threshold_rub                                  as deactivate_threshold_rub
    from (
             select *
             from (
                      select *,
                             ROW_NUMBER()
                             OVER (PARTITION BY id, crm, record_date ORDER BY update_time desc) as rn
                      from (
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '3c226725e7feca6cbd7e7e6ca26ffae5f4219ac4' as contract_id,
                                      custom_fields ->> '23076f44b238c77e85159ff67189f42f5e235066' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '61d893466026ae650198c4f6f94a5d280c291107' as channel,
                                      custom_fields ->> 'f122996cbf393aeeeb686cccde00329c24775562' as type_of_contract,
                                      custom_fields ->> '3df564783f1632c5458d21823fc2f73c0998115f' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 2
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5f8c9c624091f5861ae66d6f95a29bacf83b9acb' as contract_id,
                                      custom_fields ->> 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361' as segment,
                                      custom_fields ->> '5bac18975d5257cf98f905dc219a05eaef604eab' as product_key,
                                      custom_fields ->> '25f3004a1c052739b4081f3fc764b755d4439536' as channel,
                                      custom_fields ->> '6e5fed220a3295084c4b362a14293a720a9bc306' as type_of_contract,
                                      custom_fields ->> '2728cdafd9aa8f1fed33c464560c4d5ec39f59ca' as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 0
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '0c886554df85907470227fe1cfe6b072207bc86b' as contract_id,
                                      custom_fields ->> '60d803d64af12b5fe955671511fe816f81b5fb8d' as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> 'eb8b26a6266d99ae6f1098d33b66bb620391f172' as channel,
                                      custom_fields ->> 'e54a319c8628880942a56d5800075673ab3abe0e' as type_of_contract,
                                      null                                                         as connected_deal,
                                      null                                                         as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 5
                               union all
                               select *,
                                      which_crm                                                    as crm,
                                      custom_fields ->> '5b46472f62d243f28c789cfa00dc4859a06973a8' as contract_id,
                                      null                                                         as segment,
                                      null                                                         as product_key,
                                      custom_fields ->> '07d4db4f54185adb5764b984c15bd99af4d744a6' as channel,
                                      custom_fields ->> '2309f45a7f595fb1f1a2b6717b543fdeb125b476' as type_of_contract,
                                      null                                                         as connected_deal,
                                      custom_fields ->> 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2' as communication_with_BA_key
                               from analyst.voytekh_view_pd2_deal_history
                               where which_crm = 6
                           ) as d
                  ) as f
             where f.rn = 1
         ) as a
             left join
         analyst.voytekh_view_pd_user as d
         on a.user_id = d.pd_id and a.which_crm = d.which_crm
             left join
         (
             select login, lead_login, lead_name_first, lead_name_last, hierarchy
             from analyst.voytekh_manager_v2
         ) as m
         on lower(split_part(d.email, '@', 1)) = m.login
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as product_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as product_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '5bac18975d5257cf98f905dc219a05eaef604eab'
                  ) as s
         ) as l
         on a.crm = l.which_crm and a.product_key = l.product_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as type_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as type_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '6e5fed220a3295084c4b362a14293a720a9bc306'
                      or key = 'f122996cbf393aeeeb686cccde00329c24775562'
                      or key = 'e54a319c8628880942a56d5800075673ab3abe0e'
                      or key = '2309f45a7f595fb1f1a2b6717b543fdeb125b476'
                  ) as s
         ) as h
         on a.crm = h.which_crm and a.type_of_contract = h.type_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as channel_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as channel_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '25f3004a1c052739b4081f3fc764b755d4439536'
                      or key = '61d893466026ae650198c4f6f94a5d280c291107'
                      or key = 'eb8b26a6266d99ae6f1098d33b66bb620391f172'
                      or key = '07d4db4f54185adb5764b984c15bd99af4d744a6'
                  ) as s
         ) as g
         on a.crm = g.which_crm and a.channel = g.channel_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = '23076f44b238c77e85159ff67189f42f5e235066'
                      or key = 'cb1f0cea8c4dcf8383fa970dedf8dde8cc7ea361'
                      or key = '60d803d64af12b5fe955671511fe816f81b5fb8d'
                  ) as s
         ) as z
         on a.crm = z.which_crm and a.segment = z.segment_key
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as communication_with_BA_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as communication_with_BA
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_view_pd2_deal_field
                   where key = 'd27a2b037f9c5fe3943605eae01cf63afac3eaa2'
                  ) as s
         ) as zc
         on a.crm = zc.which_crm and a.communication_with_BA_key = zc.communication_with_BA_key
             left join
         (
             select id,
                    which_crm,
                    name          as org_name,
                    split_part(coalesce(
                                       custom_fields ->> 'e667a4f1b486b96695f0cd964a1a548945ad6d3e',
                                       custom_fields ->> '8cda0a729605af0b786b69a88ea82c2487aa2dfb',
                                       null), ',',
                               1) as org_segment
             from (
                      select *,
                             row_number()
                             over (partition by id, which_crm, name ORDER BY update_time desc) as rn
                      from analyst.voytekh_pd2_org
                  ) as t
             where rn = 1
         ) as u
         on a.crm = u.which_crm and a.org_id = u.id
             left join
         (
             select key,
                    which_crm,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            1) as org_segment_key,
                    split_part(
                            replace(replace(cast(custom_fields as varchar), '(', ''), ')', ''),
                            ',',
                            2) as org_segment_value
             from (select key,
                          which_crm,
                          json_each_text(options) as custom_fields
                   from analyst.voytekh_pd2_org_field
                   where key = 'e667a4f1b486b96695f0cd964a1a548945ad6d3e'
                      or key = '8cda0a729605af0b786b69a88ea82c2487aa2dfb'
                  ) as s
         ) as o
         on u.which_crm = o.which_crm and u.org_segment = o.org_segment_key
             left join
         (
             SELECT contract,
                    cancelled_dt,
                    currency,
                    finish_dt,
                    is_deactivated,
                    suspended_dt,
                    contract_type,
                    payment_type,
                    faxed_dt
             FROM (
                      SELECT contract,
                             cancelled_dt,
                             currency,
                             finish_dt,
                             is_deactivated,
                             suspended_dt,
                             contract_type,
                             payment_type,
                             faxed_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt desc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as kk
         on a.contract_id = kk.contract
             left join
         (
             SELECT contract, start_dt
             FROM (
                      SELECT contract,
                             start_dt,
                             ROW_NUMBER() OVER (PARTITION BY contract ORDER BY start_dt asc) rn
                      FROM analyst.voytekh_view_corporate_contracts
                  ) t
             WHERE t.rn = 1
         ) as k
         on a.contract_id = k.contract
             left join
         (
             select pd_id, name as stage_name, which_crm, pipeline
             from analyst.voytekh_pd_stage
         ) as pp
         on pp.pd_id = a.stage_id and a.which_crm = pp.which_crm
             left join
         (
             select which_crm, pd_id, name as funnel_name
             from analyst.voytekh_pd_pipeline
         ) as rr
         on rr.which_crm = a.which_crm and rr.pd_id = pp.pipeline
             left join
         (
             select balance_rub,
                    client_name,
                    contract_status,
                    deactivate_threshold_rub,
                    contract_id,
                    fielddate
             from analyst.voytova_b2b_balance_on_all_dates
         ) as bh
         on a.contract_id = bh.contract_id and
            cast(a.record_date as date) = cast(bh.fielddate as date)
              left join
         (
             select corp_contract_id,
                    day
             from (
                      select *
                      from (
                               select corp_contract_id,
                                      order_id,
                                      utc_order_dt                                                            as day,
                                      order_tariff,
                                      row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                               from summary.dm_order
                               where corp_order_flg
--       utc_order_dt >= '2020-05-01'
                                 and success_order_flg
                                 and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                           ) as first_trips
                      where rn = 1
                  ) as ftr_all
         ) as first_trip_day
         on a.contract_id = first_trip_day.corp_contract_id
)
select *,
                'SALES_T1' as fun_nm
         from (
                  select stage_name,
                         count(deal_id)             as cnt_deal,
                         sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
                         potential,
                         lost_reason,
                         which_crm,
                         status,
                         segment_result,
                         lead_name,
                         lead_login,
                         manager_login,
                         manager_name,
                         product_value,
                         currency,
                         contract_type,
                         payment_type,
                         channel_value,
                         type_of_contract,
                         funnel_name,
                         add_date
                  from (
                           select name_stage.stage_name                                   as stage_name,
                                  name_stage.deal_id                                      as deal_id,
                                  coalesce(day_in_stage_by_deal.cnt_day_in_stage_name, 0) as cnt_day_in_stage_name,
                                  deal_info.potential                                     as potential,
                                  deal_info.lost_reason                                   as lost_reason,
                                  deal_info.which_crm                                     as which_crm,
                                  deal_info.status                                        as status,
                                  deal_info.segment_result                                as segment_result,
                                  deal_info.lead_name                                     as lead_name,
                                  deal_info.lead_login                                    as lead_login,
                                  deal_info.manager_login                                 as manager_login,
                                  deal_info.manager_name                                  as manager_name,
                                  deal_info.product_value                                 as product_value,
                                  deal_info.currency                                      as currency,
                                  deal_info.contract_type                                 as contract_type,
                                  deal_info.payment_type                                  as payment_type,
                                  deal_info.channel_value                                 as channel_value,
                                  deal_info.type_of_contract                              as type_of_contract,
                                  deal_info.funnel_name                                   as funnel_name,
                                  deal_info.add_date                                      as add_date
                           from (
                                    select *
                                    from (
                                             select *
                                             from (select distinct stage_name as stage_name
                                                   from (
                                                            select *
                                                            from data_temp_table
                                                        ) as foooof
                                                   where true
                                                     and funnel_name like 'SALES T1'
--     and record_date = current_date
                                                     and which_crm = 0) as stages_names
                                                      cross join
                                                  (select distinct deal_id as deal_id
                                                   from (
                                                            select *
                                                            from data_temp_table
                                                        ) as foooof
                                                   where true
                                                     and funnel_name like 'SALES T1'
--     and record_date = current_date
                                                     and which_crm = 0) as deal_id_all
                                         ) as all_funnel
                                ) as name_stage
                                    left join
                                (
                                    select count(distinct record_date) as cnt_day_in_stage_name,
                                           deal_id,
                                           stage_name
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as cascn
                                    where true
                                      and funnel_name like 'SALES T1'
                                      --     and record_date = current_date
                                      and status not in ('lost')
                                      and which_crm = 0
                                    group by deal_id,
                                             stage_name
                                ) as day_in_stage_by_deal
                                on
                                        name_stage.stage_name = day_in_stage_by_deal.stage_name and
                                        name_stage.deal_id = day_in_stage_by_deal.deal_id
                                    join
                                (
                                    select add_date,
                                           deal_id,
                                           lost_reason,
                                           which_crm,
                                           status,
                                           potential,
                                           segment_result,
                                           lead_name,
                                           lead_login,
                                           org_id,
                                           manager_login,
                                           manager_name,
                                           product_value,
                                           currency,
                                           contract_type,
                                           payment_type,
                                           channel_value,
                                           type_of_contract,
                                           stage_name,
                                           funnel_name,
                                           contract_id
                                    from (
                                             select *
                                             from data_temp_table
                                         ) as cascn
                                    where true
--                                       and funnel_name like 'SALES T1'
                                      and record_date = current_date
                                      and which_crm = 0
                                ) as deal_info
                                on name_stage.deal_id = deal_info.deal_id
                       ) as datataframe
                  group by stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login,
                           manager_login, manager_name, product_value,
                           currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
                  union all
                  select stage_name,
                         count(deal_id)             as cnt_deal,
                         sum(cnt_day_in_stage_name) as sum_day_in_stage_name,
                         potential,
                         lost_reason,
                         which_crm,
                         status,
                         segment_result,
                         lead_name,
                         lead_login,
                         manager_login,
                         manager_name,
                         product_value,
                         currency,
                         contract_type,
                         payment_type,
                         channel_value,
                         type_of_contract,
                         funnel_name,
                         add_date
                  from (select deal_id,
                               lost_reason,
                               which_crm,
                               status,
                               contract_id,
                               segment_result,
                               lead_name,
                               lead_login,
                               org_id,
                               manager_login,
                               manager_name,
                               product_value,
                               cancelled_dt,
                               currency,
                               is_deactivated,
                               suspended_dt,
                               contract_type,
                               payment_type,
                               channel_value,
                               type_of_contract,
                               start_dt,
                               connected_deal,
                               'ДОГОВОР АКТИВИРОВАН'                           as stage_name,
                               funnel_name,
                               add_date,
                               potential,
                               record_date,
                               activated_dt                                    as activated_dt,
                               date_first_trip.day                             as date_first_trip,
                               current_date                                    as curr_date,
                               case
                                   when date_first_trip is null
                                       then current_date - activated_dt
                                   else date_first_trip.day - activated_dt end as cnt_day_in_stage_name
                        from (
                                 select asdf.*,
                                        activ_cont.activated_dt as activated_dt
                                 from (select *
                                       from data_temp_table) as asdf
                                          join (select *
                                                from analyst.voytova_b2b_contracts_info_all
                                                where activated_dt is not null) as activ_cont
                                               on asdf.contract_id = activ_cont.contract_id
                                          join (select *
                                                from (
                                                         select *
                                                         from (
                                                                  select deal_id,
                                                                         which_crm,
                                                                         record_date,
                                                                         funnel_name,
                                                                         row_number()
                                                                         over (partition by deal_id order by record_date desc, update_time desc, add_date) as rn
                                                                  from (select * from data_temp_table) as dataframe_all
                                                                  where true
                                                                    and which_crm = 0
                                                                    and funnel_name in ('SALES MM', 'SALES T1')
                                                              ) as deals
                                                         where rn = 1
                                                     ) as dataframe_sales
                                                where funnel_name = 'SALES T1') as deal_in_sales
                                               on asdf.deal_id = deal_in_sales.deal_id
                                 where asdf.which_crm = 0
                                   and asdf.record_date = current_date
                                   and asdf.contract_id is not null
                                   and asdf.contract_id != ''
                             ) as asdfd
                                 left join
                             (select corp_contract_id,
                                     day
                              from (
                                       select *
                                       from (
                                                select corp_contract_id,
                                                       order_id,
                                                       utc_order_dt                                                            as day,
                                                       order_tariff,
                                                       row_number() over (partition by corp_contract_id order by utc_order_dt) as rn
                                                from summary.dm_order
                                                where corp_order_flg
                                                  and success_order_flg
                                                  and utc_order_dt != current_date
--       and order_tariff in ('express', 'courier', 'cargo')
                                            ) as first_trips
                                       where rn = 1
                                   ) as ftr_all) as date_first_trip
                             on
                                 asdfd.contract_id = date_first_trip.corp_contract_id) as fooof
                  group by stage_name, potential, lost_reason, which_crm, status, segment_result, lead_name, lead_login,
                           manager_login, manager_name, product_value,
                           currency, contract_type, payment_type, channel_value, type_of_contract, funnel_name, add_date
              ) as foof
'''
greenplum(query)
greenplum('grant select on snb_taxi.ravaev_conversion_step_by_step_sales_t to rawy, voytova, voytekh')

query = '''
drop table if exists snb_taxi.ravaev_conversion_step_by_step;
create table snb_taxi.ravaev_conversion_step_by_step as
select
       cast(stage_name as text) as stage_name,
       cnt_deal,
       sum_day_in_stage_name,
       coalesce(potential, 'empty') as potential,
       coalesce(lost_reason, 'empty') as lost_reason,
       which_crm as which_crm,
       coalesce(status, 'empty') as status,
       coalesce(segment_result, 'empty') as segment_result,
       coalesce(lead_name, 'empty') as lead_name,
       coalesce(lead_login, 'empty') as lead_login,
       coalesce(manager_login, 'empty') as manager_login,
       coalesce(manager_name, 'empty') as manager_name,
       coalesce(product_value, 'empty') as product_value,
       coalesce(currency, 'empty') as currency,
       coalesce(contract_type, 'empty') as contract_type,
       coalesce(payment_type, 'empty') as payment_type,
       coalesce(channel_value, 'empty') as channel_value,
       coalesce(type_of_contract, 'empty') as type_of_contract,
       coalesce(funnel_name, 'empty') as funnel_name,
       add_date as add_date,
       cast(fun_nm as text) as fun_nm
from snb_taxi.ravaev_conversion_step_by_step_sales_t
union all
select
       cast(stage_name as text) as stage_name,
       cnt_deal,
       sum_day_in_stage_name,
       coalesce(potential, 'empty') as potential,
       coalesce(lost_reason, 'empty') as lost_reason,
       which_crm as which_crm,
       coalesce(status, 'empty') as status,
       coalesce(segment_result, 'empty') as segment_result,
       coalesce(lead_name, 'empty') as lead_name,
       coalesce(lead_login, 'empty') as lead_login,
       coalesce(manager_login, 'empty') as manager_login,
       coalesce(manager_name, 'empty') as manager_name,
       coalesce(product_value, 'empty') as product_value,
       coalesce(currency, 'empty') as currency,
       coalesce(contract_type, 'empty') as contract_type,
       coalesce(payment_type, 'empty') as payment_type,
       coalesce(channel_value, 'empty') as channel_value,
       coalesce(type_of_contract, 'empty') as type_of_contract,
       coalesce(funnel_name, 'empty') as funnel_name,
       add_date as add_date,
       cast(fun_nm as text) as fun_nm
from snb_taxi.ravaev_conversion_step_by_step_sales
union all
select
       cast(stage_name as text) as stage_name,
       cnt_deal,
       sum_day_in_stage_name,
       coalesce(potential, 'empty') as potential,
       coalesce(lost_reason, 'empty') as lost_reason,
       which_crm as which_crm,
       coalesce(status, 'empty') as status,
       coalesce(segment_result, 'empty') as segment_result,
       coalesce(lead_name, 'empty') as lead_name,
       coalesce(lead_login, 'empty') as lead_login,
       coalesce(manager_login, 'empty') as manager_login,
       coalesce(manager_name, 'empty') as manager_name,
       coalesce(product_value, 'empty') as product_value,
       coalesce(currency, 'empty') as currency,
       coalesce(contract_type, 'empty') as contract_type,
       coalesce(payment_type, 'empty') as payment_type,
       coalesce(channel_value, 'empty') as channel_value,
       coalesce(type_of_contract, 'empty') as type_of_contract,
       coalesce(funnel_name, 'empty') as funnel_name,
       add_date as add_date,
       cast(fun_nm as text) as fun_nm
from snb_taxi.ravaev_conversion_step_by_step_sales_mm
'''
greenplum(query)
greenplum('grant select on snb_taxi.ravaev_conversion_step_by_step to rawy, voytova, voytekh')
