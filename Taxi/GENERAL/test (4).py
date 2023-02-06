from business_models import hahn, greenplum
from business_models.databases import gdocs
import pandas as pd
import numpy as np
import runpy
from datetime import datetime
logger_sheet = '1Jm3vmEGufFZfRkJHrt8QO4eJDiPhz_XIhGRgOVKzAVc'

from storage import script_kwargs, dt_list, utm_source_rep, utm_campaign_rep

greenplum("""
drop table if exists snb_da.online_tmp_tmp_costs;
create table snb_da.online_tmp_tmp_costs as 
select
    dt
  , country_name as country
  , enity_name as enity
  , city_name as city
  , population_group
  , 'Online Paid' as channel --оставляем только онлайн, убираем саморег. В этой таблице именно платный онлайн
  , case
        when audience in ('Водители','Самозанятые') then 'drivers'
        when audience = 'Грузовой' then 'cargo'
        when audience = 'Доставка' then 'delivery'
        else audience
    end as tariff --аналогично pnl
  , true as paid_flg
  , sum(visits) as visits
  , sum(cost_visit) as cost
from snb_da.online_performance_cost

where channel = 'Online'
group by 1,2,3,4,5,6


    union all --соединяем платных и бесплтаных (true as paid_flg) union all (false as paid_flg) 
    
select
    utc_visit_start_dttm :: date as dt
  , country_name as country,
        coalesce(enity_name,'Unknown') as enity,
        coalesce(city_name,'Unknown') as city,
        coalesce(case
            when (g.population between 0 and 99999) or city_name is null then 'small'
            when g.enity_name = 'Москва и Московская область' then 'Москва и Московская область'
            when g.enity_name = 'Санкт-Петербург и Ленинградская область' then 'Санкт-Петербург и Ленинградская область'
            when g.population between 100000 and 199999 then '100+'
            when g.population between 200000 and 299999 then '200+'
            when g.population between 300000 and 499999 then '300+'
            when g.population between 500000 and 999999 then '500+'
            when g.population > 1000000 then '1m+' end,'unknown') as population_group
  , 'Online Organic' as channel        --реалистичная гипотеза
  , 'yandex_metrica drivers' as tariff --реалистичная гипотеза
  , false as paid_flg
  , count(*) as visits
  , 0 as cost
from taxi_ods_metrica_da.visit as m

left join snb_da.online_geobase as g 
  on g.reg_id = m.region_id

where 1 = 1
  and utc_visit_start_dttm :: date >= {dt_filter}
  and country_name in ('Азербайджан','Армения','Афганистан','Беларусь','Гана','Грузия','Израиль','Испания','Казахстан','Киргизия','Кот-д’Ивуар','Латвия','Литва','Мексика',
    'Молдова','Монголия','Нигерия','Норвегия','Россия','Румыния','Сербия','Таджикистан','Уганда','Узбекистан','Украина','Финляндия','Франция','Швеция','Эстония')
        
        and    (start_url ilike 'https://taxi.yandex.ru/rabota%'
             or start_url ilike 'https://taxi.yandex.ru/promo/rabota%'
             or start_url ilike 'https://taxi.yandex.kz/rabota%'
             or start_url ilike 'https://taxi.yandex.ru/smz%'
             or start_url ilike 'https://taxi.yandex.uz/driver%'
             or start_url ilike 'https://taxi.yandex.uz/rabota%'
             or start_url ilike 'https://taxi.yandex.rs/driver%'
             or start_url ilike 'https://taxi.yandex.md/rabota%'
             or start_url ilike 'https://taxi.yandex.lv/driver%'
             or start_url ilike 'https://taxi.yandex.lv/index%'
             or start_url ilike 'https://taxi.yandex.lt/driver%'
             or start_url ilike 'https://taxi.yandex.ee/driver%'
             or start_url ilike 'https://taxi.yandex.by/driver%'
             or start_url ilike 'https://taxi.yandex.by/rabota%'
             or start_url ilike 'https://taxi.yandex.com/driver%'
             or start_url ilike 'https://support-uber.com/signup%')
             
        and start_url not ilike '%ref=easy%'
        and start_url not ilike '%ref=mvyat%'
        and start_url not ilike '%ref=wl%'
        and start_url not ilike '%ref=rezultat%'
        and start_url not ilike '%ref=easy_kz%'
        and start_url not ilike '%ref=okoz%'
        and start_url not ilike '%ref=cpp%'
        and start_url not ilike '%ref=staffjet%'
        and utm_campaign not ilike '[%'
    group by 1,2,3,4,5,6
;""".format(**script_kwargs))

greenplum("""--только активы в дату активации
drop table if exists snb_da.online_tmp_tmp_dfts;
create table snb_da.online_tmp_tmp_dfts as 
select
      aw_dt
    , country, enity, city, population_group, paid_flg
    , count(distinct driver_uuid) as dft_cnt
    from snb_da.online_nr_online_funnel
    where 1 = 1 
        and aw_dt is not null
    group by 1,2,3,4,5,6
;""")

greenplum("""--только активы в дату создания тикета
drop table if exists snb_da.online_tmp_tmp_main;
create table snb_da.online_tmp_tmp_main as
select
      ticket_created_dt as ticket_dt --дата создания тикета
    , country, enity, city, population_group, paid_flg
    , count(distinct ticket_id) as ticket_cnt
    , count(distinct driver_uuid) as active_cnt
    --, count(distinct case when active_flg then ticket_id else null end) as active_in_service
from snb_da.online_nr_online_funnel
group by 1,2,3,4,5,6
;""")

greenplum("""--план
drop table if exists snb_da.online_tmp_tmp_pre_plan;
create table snb_da.online_tmp_tmp_pre_plan as 
select
      dt + generate_series(0,6) as dt
    , split_part(geo,'±',1) as country
    , split_part(geo,'±',2) as enity
    , split_part(geo,'±',3) as city
    , population_group
    , paid_flg
    , active_plan / 7 as active_plan
    , dft_plan / 7 as dft_plan
    , tickets_plan /7 as tickets_plan
    , budget / 7 as budget
from (
  select
     date :: date as dt
   , coalesce(g.country_name || '±' || g.enity_name || '±' || g.city_name,replace(replace(replace(k.country,'Белоруссия','Беларусь'),'Молдавия','Молдова'),'Кот-д''Ивуар','Кот-д’Ивуар') || '±' || 'Unknown'|| '±' || 'Unknown')
            as geo
   , coalesce(case
                when g.enity_name = 'Москва и Московская область' then 'Москва и Московская область'
                when g.enity_name = 'Санкт-Петербург и Ленинградская область' then 'Санкт-Петербург и Ленинградская область'
                when g.population between 0 and 99999 then 'small'
                when g.population between 100000 and 199999 then '100+'
                when g.population between 200000 and 299999 then '200+'
                when g.population between 300000 and 499999 then '300+'
                when g.population between 500000 and 999999 then '500+'
                when g.population > 1000000 then '1m+' end,'unknown')
        as population_group
    , case when medium = 'online_paid' then true else false end as paid_flg
    , sum(drivers_by_ticket) as active_plan
    , sum(drivers) as dft_plan
    , sum(leads) as tickets_plan
    , sum(case when total_money > 0 then total_money else 0 end) as budget
  from snb_taxi.sm_newbies_kpi as k
 
  left join snb_da.online_geo as g 
      on g.country_name = replace(replace(replace(k.country,'Белоруссия','Беларусь'),'Молдавия','Молдова'),'Кот-д''Ивуар','Кот-д’Ивуар')
        and g.city_name = k.region
  
  where 1 = 1
      and last_flg is true
      and medium in ('online_paid','online_organic')
      and date :: date >= '2020-02-17'
   group by 1,2,3,4
) as pre_plan
;""")

greenplum("""
drop table if exists snb_da.online_nr_online_test;
create table snb_da.online_nr_online_test as
select
      coalesce(m.ticket_dt, c.dt, p.dt, d.aw_dt) as dt
    , coalesce(m.country, c.country, p.country, d.country) as country
    , coalesce(m.enity, c.enity, p.enity, d.enity) as enity
    , coalesce(m.city, c.city, p.city, d.city) as city
    , coalesce(m.population_group, c.population_group, p.population_group, d.population_group) as population_group
    , coalesce(m.paid_flg, c.paid_flg, p.paid_flg, d.paid_flg) as paid_flg
    
    , c.channel --корректость этих двух строк "с." обеспечивает "m.paid_flg = c.paid_flg"
    , c.tariff

    , m.ticket_cnt
    , p.tickets_plan
    
    , m.active_cnt
    , p.active_plan
    
    , d.dft_cnt
    , p.dft_plan
    
    , m.cost
    , p.budget
    
    , m.visits
    , now() :: timestamp(0) as update_dttm
    --, active_in_service
from snb_da.online_tmp_tmp_main as m

full join snb_da.online_tmp_tmp_dfts as d 
    on m.dt = d.aw_dt
        and m.country = d.country and m.enity = d.enity and m.city = d.city and m.population_group = d.population_group and m.paid_flg = d.paid_flg

full join snb_da.online_tmp_tmp_costs as c
    on m.dt = c.dt 
        and m.country = c.country and m.enity = c.enity and m.city = c.city and m.population_group = c.population_group and m.paid_flg = c.paid_flg

full join snb_da.online_tmp_tmp_pre_plan as p
    on m.dt = p.dt 
        and m.country = p.country and m.enity = p.enity and m.city = p.city and m.population_group = p.population_group and m.paid_flg = p.paid_flg
""".format(**script_kwargs))
