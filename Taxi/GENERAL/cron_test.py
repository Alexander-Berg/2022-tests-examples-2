# -*- coding: utf-8 -*-

from business_models.databases import gdocs
from business_models import greenplum, hahn
import pandas as pd

# END of dates for daily sample of converting sm data from week to month: def drivers_plan_sm(). insert last Monday date of current year.
last_monday_date = '2021-12-27'
'''
sheet_id_82 = '1n3kP6nLx3p0w9_1Ee0kv2ytkYaKyuNByUr3cXKCHeko'
sheet_id_100 = '1UJjkvXB23DZK9JNDclsdippRqWGwWCY885Xa0bO1o2k'
forecast_82 = '1p1n_KASme8C0dZcPaoBw7eZGSXD-uQmqcExWs2a9bjU'

finance_plan_d = gdocs.read(table_name='finance_plan', sheet_id=forecast_82, header=1)
finance_plan_d['cfo'] = 'YTMS82'
finance_plan_smz = gdocs.read(table_name='finance_plan', sheet_id=sheet_id_100, header=1)
finance_plan_smz['cfo'] = 'YTM100'

finance_plan = pd.concat([finance_plan_d, finance_plan_smz])
finance_plan['type'] = 'Plan'
greenplum("""drop table if exists snb_da.pnl__tmp__gd_finance_plan""")
greenplum.write_table('snb_da.pnl__tmp__gd_finance_plan', finance_plan)
'''
#greenplum("""alter table snb_da.pnl__tmp__gd_finance_plan owner to analyst;""")


#######################################             drivers            ############################################

def drivers_fact():
    drivers_fact_wo_referral = greenplum("""
        with drivers as (
            SELECT distinct t1.driver_license_id as driver_license_normalized
                   , date_trunc('day', t1.utc_dt)::date AS date
                   , case
                        when t1.medium = 'agents' then 'Agents'
                        when t1.medium = 'leadgens' then 'Leadgens'
                        when (t1.medium in ('online', 'online_organic') and t1.utc_dt::date >= '2020-07-01') then 'Online Organic'
                        when t1.medium = 'online_paid' and t1.utc_dt::date >= '2020-07-01' then 'Online Paid'
                        when (t1.medium in ('online', 'online_organic', 'online_paid') and t1.utc_dt::date < '2020-07-01') then 'Online'
                        when t1.medium = 'selfreg_organic' then 'Selfregistration Organic'
                        when t1.medium = 'selfreg_paid' then 'Selfregistration Paid'
                        when t1.medium = 'mass_recruitment' then 'Mass recruitment'
                        when t1.medium = 'scouts' then 'Scouts'
                        when t1.medium = 'parks_motivation' then 'Partners'
                        when t1.medium in ('offline', 'offline_sales') then 'Offline'
                        when t1.medium = 'selfreg_callcenter' then 'Selfregistration'
                        when t1.medium = 'organic' then 'Organic'
                        when t1.medium = 'agent_partner_freelance' then 'Freelance'
                        when t1.medium in ('referral_program', 'referal', 'referral_drivers') then 'Referral Program'
                        else t1.medium
                     end as medium
                   , tz_country_name_en as country
                   , case when t1.utc_dt >= '2020-07-01' then tz_aggl_name_en else null end as city
                   , case when t1.utc_dt >= '2020-07-01' then geo.node_id else null end as geo_node_id
                   , case when t1.utc_dt >= '2020-07-01' then geo.population_group else null end as population_group
                   , 'YTMS82' as cfo
                   , CASE
                       when t1.utc_dt < '2020-07-01' then 'drivers'
                       --when flg_selfemployed = 'SMZ' then 'drivers'
                       when max_class in ('delivery','walking_courier','auto_courier') then 'delivery'
                       when max_class = 'cargo' then 'cargo'
                       when max_class in ('econom','higher_class','other_drivers','ultima') then 'drivers'
                       when max_class is null then 'drivers'
                      ELSE max_class
                     END AS tariff
                    , flg_selfemployed
                    , utc_dt
            FROM snb_taxi.da_fact_drivers AS t1
                JOIN(
                        select
                            DISTINCT node_id
                            , tz_country_name_en
                            , tz_aggl_name_ru
                            , tz_aggl_name_en
                            , population_group
                        from core_cdm_geo.v_dim_full_geo_hierarchy
                        where node_type = 'agglomeration'
                            and root_node_id = 'fi_root'
                ) geo
                    on t1.region = geo.tz_aggl_name_ru
            where t1.utc_dt >= '2019-01-01' and not flg_davos_driver
        ),
        res as (
            select
                date,medium as channel,country,city,geo_node_id,population_group,cfo,tariff
                , count(distinct driver_license_normalized) as drivers
                , 'Fact'::text as type
                , 'GP wo referral city'::text as source
            from drivers
            group by 1,2,3,4,5,6,7,8
        )
        select date,channel,country,city,geo_node_id,population_group,cfo,tariff,type,source,drivers
        from res
    """)

    drivers_fact_referral = greenplum("""
        select
            date::date as date
            , 'Referral Program' as channel
            , tz_country_name_en as country
            , case when date >= '2020-07-01' then tz_aggl_name_en else null end as city
            , case when date >= '2020-07-01' then node_id else null end as geo_node_id
            , case when date >= '2020-07-01' then population_group else null end as population_group
            , 'YTMS82' as cfo
            , 'drivers' as tariff
            , 'Fact' as type
            , drivers
        from(
            select * from(
                select
                    case when country = 'Кот-д’Ивуар' then 'Кот-д''Ивуар' else country end as country
                    ,city
                    ,dt::date as date
                    ,sum(promo) as drivers
                from analyst.martianov_refferal_stat
                where dt is not null
                GROUP BY 1,2,3
            ) t1
            LEFT JOIN(
                select
                    DISTINCT tz_country_name_en
                    , tz_aggl_name_ru
                    , tz_aggl_name_en
                    , population_group
                    , node_id
                from core_cdm_geo.v_dim_full_geo_hierarchy
                where node_type = 'agglomeration' and root_node_id = 'fi_root'
            ) geo
                on t1.city = geo.tz_aggl_name_ru
        ) t
    """)
    drivers_fact_referral['source'] = 'GP referral city'
    fact_drivers = pd.concat([drivers_fact_wo_referral, drivers_fact_referral])
    return fact_drivers

fact_drivers = drivers_fact()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 8
    """
)

def drivers_plan_sm():
    drivers_sm = greenplum("""
        select
            case
                when medium = 'agents' then 'Agents'
                when medium = 'leadgens' then 'Leadgens'
                when (medium in ('online','online_organic') and date::date >= '2020-07-01') then 'Online Organic'
                when medium = 'online_paid' and date::date >= '2020-07-01' then 'Online Paid'
                when (medium in ('online','online_organic','online_paid') and date::date<'2020-07-01') then 'Online'
                when medium in ('selfreg','selfreg_organic') then 'Selfregistration Organic'
                when medium = 'selfreg_paid' then 'Selfregistration Paid'
                when medium = 'mass_recruitment' then 'Mass recruitment'
                when medium = 'scouts' then 'Scouts'
                when medium = 'parks_motivation' then 'Partners'
                when medium in ('offline','offline_sales') then 'Offline'
                when medium = 'selfreg_callcenter' then 'Selfregistration'
                when medium = 'organic' then 'Organic'
                when medium = 'agent_partner_freelance' then 'Freelance'
                when medium in ('referral_program','referal','referral_drivers') then 'Referral Program'
             else medium
            end as channel
            , tz_country_name_en as country
            , case when date >= '2020-07-01' then tz_aggl_name_en else null end as city
            , case when date >= '2020-07-01' then node_id else null end as geo_node_id
            , case when date >= '2020-07-01' then population_group else null end as population_group
            , date::date as date
            , 'Supply Menu' as type
            , 'YTMS82' as cfo
            , 'drivers' as tariff
            , sum(drivers) as drivers
        FROM(
    -- sm data has only week scale, but pnl required month scale. converting from week to day is below
            select * from (
                select
                    sm_date::date as date
                    , date(date_trunc('week',sm_date::date)) as dft_week
                    , drivers/7 as drivers
                    , drivers as drivers_weekly
                    , medium
                    , region_id
                from (SELECT generate_series('2018-12-31', '{}', '1 day'::interval)::date as sm_date) t0
                left join snb_taxi.sm_newbies_kpi t1
                    on date(date_trunc('week',t0.sm_date::date)) = t1.date
                where last_flg = true and medium not in ('orders_decrease_income_lost', 'work+X_every_day',
               'churn_month_lost_14-21', 'churn_month_lost_21-45',
               'churn_month_lost_45-180', 'churn_month_lost_180')
            ) as t1
            LEFT JOIN(
                select
                    DISTINCT node_id
                    , tz_country_name_en
                    , tz_aggl_name_ru
                    , tz_aggl_name_en
                    , population_group
                from core_cdm_geo.v_dim_full_geo_hierarchy
                where node_type = 'agglomeration'
                    and root_node_id = 'fi_root'
            ) geo
                on t1.region_id = geo.node_id
        ) dr1
        where medium not in ('referral_program','project_ip','other_services')
        group by 1,2,3,4,5,6
    """.format(last_monday_date))
    
    drivers_sm['source'] = 'GP supply menu city'
    pre_drivers = pd.concat([fact_drivers, drivers_sm])
    greenplum("drop table if exists snb_da.pnl__tmp__pre_drivers")
    greenplum.write_table('snb_da.pnl__tmp__pre_drivers', pre_drivers)

    greenplum('grant select on snb_da.pnl__tmp__pre_drivers to "kutikovivan"')

    drivers_plan = greenplum("""
        select
            month::date as date
            , 'month' as scale
            , channel
            , country
            , cfo
            , type
            , coalesce(tariff,'drivers') as tariff
            , sum(drivers) as drivers
        from (
        select channel
            , country
            , date(year || '-' || t1.month_num || '-01') as month
            , type
            , cfo
            , tariff
            , cast (drivers as float) as drivers
        from snb_da.pnl__tmp__gd_finance_plan as t0
        JOIN analyst.ks_konovalova__pnl__mapping__month as t1
            on t0.month = t1.month_name_en
        ) t
        group by 1,3,4,5,6,7
    """)
    drivers_plan['source'] = 'GD plan country'
    return drivers_plan

drivers_plan = drivers_plan_sm()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 9
    """
)
def drivers_total():
    weekly = greenplum("""
       select
            date_trunc('week',date)::date as date
            , 'week' as scale
            , channel
            , country
            , city
            , geo_node_id
            , population_group
            , cfo
            , tariff
            , type
            , source
            , sum(drivers) as drivers
        from snb_da.pnl__tmp__pre_drivers
        group by 1,3,4,5,6,7,8,9,10,11
    """)
    
    monthly = greenplum("""
        select
            date_trunc('month',date)::date as date
            , 'month' as scale
            , channel
            , country
            , city
            , geo_node_id
            , population_group
            , cfo
            , tariff
            , type
            , source
            , sum(drivers) as drivers
        from snb_da.pnl__tmp__pre_drivers
        group by 1,3,4,5,6,7,8,9,10,11
    """)
    drivers = pd.concat([drivers_plan, weekly, monthly])
    greenplum("drop table if exists snb_da.pnl__drivers")
    greenplum.write_table('snb_da.pnl__drivers', drivers, with_grant=True, operator='select', to='analyst')
    greenplum('grant select on snb_da.pnl__drivers to "kutikovivan"')

drivers_total()

hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 10
    """
)

#######################################              loss              ############################################

sheet_id_82 = '1n3kP6nLx3p0w9_1Ee0kv2ytkYaKyuNByUr3cXKCHeko'
sheet_id_100 = '1UJjkvXB23DZK9JNDclsdippRqWGwWCY885Xa0bO1o2k'
forecast_82 = '1p1n_KASme8C0dZcPaoBw7eZGSXD-uQmqcExWs2a9bjU'

def fact_country_loss():
    detalization_82 = gdocs.read(table_name='detalization', sheet_id=sheet_id_82, header=1)
    detalization_82['cfo'] = 'YTMS82'
    detalization_82['source'] = 'GD country 82'
    detalization_100 = gdocs.read(table_name='detalization', sheet_id=sheet_id_100, header=1)
    detalization_100['cfo'] = 'YTM100'
    detalization_100['source'] = 'GD country 100'
    detalization_100['task'] = 'Объект неизвестен'
    detalization = pd.concat([detalization_82, detalization_100])
    detalization.rename(columns={'program code':'program_code', 'budget item':'budget_item', 'budget sub-item':'budget_sub_item'}, inplace=True)
    detalization['type'] = 'Fact'
    greenplum("""drop table if exists snb_da.pnl__tmp__gd_country_detalization""")
    greenplum.write_table('snb_da.pnl__tmp__gd_country_detalization', detalization)

    greenplum('grant select on snb_da.pnl__tmp__gd_country_detalization to "kutikovivan"')

    loss_country = greenplum("""
            select
                channel
                , country
                , program
                , task
                , budget_item
                , budget_sub_item
                , date(year || '-' || t1.month_num || '-01')::date as date
                , case when cfo = 'YTM100' then 'drivers' else tariff end as tariff
                , cfo
                , type
                , source
                , sum(cast(cost as float))                        as cost
            from snb_da.pnl__tmp__gd_country_detalization as t0
            JOIN analyst.ks_konovalova__pnl__mapping__month as t1
                on t0.month = t1.month_name_en
            where date(year || '-' || t1.month_num || '-01')::date >= '2020-07-01' -- cities detalization
            group by 1,2,3,4,5,6,7,8,9,10,11
    """)
    greenplum("""drop table if exists snb_da.pnl__tmp__gd_country_normalized""")
    greenplum.write_table('snb_da.pnl__tmp__gd_country_normalized', loss_country)
    greenplum('grant select on snb_da.pnl__tmp__gd_country_normalized to "kutikovivan"')

fact_country_loss()    

hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 20
    """
)

def plan_loss():    
    finance_plan_d = gdocs.read(table_name='finance_plan', sheet_id=forecast_82, header=1)
    finance_plan_d['cfo'] = 'YTMS82'
    finance_plan_smz = gdocs.read(table_name='finance_plan', sheet_id=sheet_id_100, header=1)
    finance_plan_smz['cfo'] = 'YTM100'

    finance_plan = pd.concat([finance_plan_d, finance_plan_smz])
    finance_plan['type'] = 'Plan'
    greenplum("""drop table if exists snb_da.pnl__tmp__gd_finance_plan""")
    greenplum.write_table('snb_da.pnl__tmp__gd_finance_plan', finance_plan)
    #greenplum('grant select on analyst.ks_konovalova__pnl__tmp__gd_finance_plan to "matveev-ivan"')

    plan_loss = greenplum("""
        select
            date
            , channel
            , country
            , cfo
            , coalesce(tariff,'drivers') as tariff
            , type
            , sum(cost) as cost
        from (
                 select channel
                      , country
                      , date(year || '-' || t1.month_num || '-01') as date
                      , type
                      , cfo
                      , tariff
                      , cast(cost as float)                 as cost
                 from snb_da.pnl__tmp__gd_finance_plan as t0
                 JOIN analyst.ks_konovalova__pnl__mapping__month as t1
                    on t0.month = t1.month_name_en
             ) t
        group by 1,2,3,4,5,6
    """)
    plan_loss['source'] = 'GD plan country'
    return plan_loss

plan_loss = plan_loss()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 21
    """
)
def gd_cities():
    sheet_city_agents = '1vkNMjGWMlkAMsLjcDRnQLUe5jcDaNmIQYCDCDLvTxbk'
    city_agents = gdocs.read(table_name='detalization', sheet_id=sheet_city_agents, header=1)

    sheet_city_freelance = '1uXK9XT3jj4TvmA8S4RtizcICn7SGHhWTyAM18YFWD0I'
    city_freelance = gdocs.read(table_name='detalization', sheet_id=sheet_city_freelance, header=1)

    sheet_city_leadgens = '1Ifc5eiOATAPywqgYtgf8LUmzyCCi_zPYJFpTqB58yO4'
    city_leadgens = gdocs.read(table_name='detalization', sheet_id=sheet_city_leadgens, header=1)

    sheet_city_recruitment = '1L3wvY2l-F-7QwIOktVlbx6g2jj5JcMPH7P3mZLhTXnc'
    city_recruitment = gdocs.read(table_name='detalization', sheet_id=sheet_city_recruitment, header=1)

    sheet_city_scouts = '1dXY6077CKJsinYGJlLux6P7aOE_tXVVAOZIlWWfVr5s'
    city_scouts = gdocs.read(table_name='detalization', sheet_id=sheet_city_scouts, header=1)

    sheet_city_performance = '1ewthLs_GxnTTkBVSySm0a8jG6h8ZOBmaZE-YiJ1F8bE'
    city_performance = gdocs.read(table_name='detalization', sheet_id=sheet_city_performance, header=1)

    gd_city_detalization = pd.concat([city_agents, city_freelance, city_leadgens, city_recruitment, city_scouts, city_performance])
    gd_city_detalization.rename(columns={'program code':'program_code', 'budget item':'budget_item', 'budget sub-item':'budget_sub_item'}, inplace=True)
    gd_city_detalization = gd_city_detalization.dropna(axis=0, subset=['channel'])
    gd_city_detalization['cfo'] = 'YTMS82'
    greenplum.write_table('snb_da.pnl__tmp__gd_pre_city_detalization', gd_city_detalization)
    #greenplum('grant select on analyst.ks_konovalova__pnl__tmp__gd_pre_city_detalization to "matveev-ivan"')
    gd_cities = greenplum("""
        select
            date(year || '-' || t1.month_num || '-01') as date
            , channel
            , program
            , task
            , budget_item
            , budget_sub_item
            , country
            , city
            , tariff
            , cfo
            , 'Fact' as type
            , sum(cost::float) as cost
        from snb_da.pnl__tmp__gd_pre_city_detalization as t0
        JOIN analyst.ks_konovalova__pnl__mapping__month as t1
            on t0.month = t1.month_name_en
        group by 1,2,3,4,5,6,7,8,9,10
    """)
    #greenplum("drop table if exists snb_da.pnl__tmp__gd_pre_city_detalization")
    gd_cities['source'] = 'GD city'
    
    return gd_cities

cities = gd_cities()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 22
    """
)
def gd_partner_city():
    sheet_city_partners = '1KLpuMXYr6A5sYdP0--UXYPLBK1BXHIxQbZEaxge50gw'
    city_partners_20 = gdocs.read(table_name='2020', sheet_id=sheet_city_partners, header=1)
    city_partners_20['year'] = '2020'
    city_partners_21 = gdocs.read(table_name='2021', sheet_id=sheet_city_partners, header=1)
    city_partners_21['year'] = '2021'
    city_partners = pd.concat([city_partners_20, city_partners_21])
    
    greenplum.write_table('snb_da.pnl__tmp__gd_city_partners', city_partners)
    #greenplum('grant select on snb_da.pnl__tmp__gd_city_partners to "matveev-ivan"')
    partners = greenplum("""
        select
            date
            , channel
            , city
            , program
            , task
            , program as budget_item
            , budget_sub_item
            , tariff
            , cfo
            , 'Fact' as type
            , sum(cost) as cost
        from (
                 select
                      case
                            when type in ('ЦОВ','мотив','доставка','грузовой','СМЗ') then 'Partners'
                            when type = 'платная органика' then 'Paid Organic'
                            when type = 'скауты' then 'Scouts'
                        else 'not_defined_partners_gd'
                       end as channel
                      , case
                            when type in ('ЦОВ','мотив','доставка','платная органика','доставка','грузовой','СМЗ') then 'Partners'
                            when type = 'скауты' then 'Scouts'
                        else 'not_defined_partners_gd'
                       end as program
                      , case
                            when type in ('ЦОВ','мотив','доставка','скауты','грузовой','СМЗ') then 'Объект неизвестен'
                            when type = 'платная органика' then 'Paid organic'
                        else 'not_defined_partners_gd'
                       end as task
                      , case
                            when type in ('ЦОВ','мотив','доставка','платная органика','доставка','грузовой','СМЗ') then 'Partners'
                            when type = 'скауты' then 'ЦОВ'
                        else 'not_defined_partners_gd'
                       end as budget_sub_item
                      , case
                            when type in ('ЦОВ','мотив','платная органика','скауты') then 'drivers'
                            when type = 'доставка' then 'delivery'
                            when type = 'грузовой' then 'cargo'
                            when type = 'СМЗ' then 'drivers'
                        else 'not_defined_partners_gd'
                       end as tariff
                      , case when type = 'СМЗ' then 'YTM100' else 'YTMS82' end as cfo
                      , city
                      , date(year || '-' || t1.month_num || '-01')::date as date
                      , type
                      , cast(sum as float)                 as cost
                 from snb_da.pnl__tmp__gd_city_partners as t0
                 JOIN analyst.ks_konovalova__pnl__mapping__month as t1
                    on t0.month_ru = t1.month_name_ru
                 where date(year || '-' || t1.month_num || '-01')::date >= '2020-07-01' and sum is not null
             ) t
        group by 1,2,3,4,5,6,7,8,9
    """)
    partners['source'] = 'GD city'

    return partners
partners = gd_partner_city()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 23
    """
)
def yt_scouts_city():    
    city_scouts_billing = hahn("""
        select 
            month
            , 'Scouts' as channel
            , city
            , 'Scouts' as program
            , 'Объект неизвестен' as task
            , 'Scouts' as budget_item
            , 'Билинг' as budget_sub_item
            , tariff
            , 'YTMS82' as cfo
            , 'Fact' as type
            , sum(case when c.transaction_type = 'refund' then cast(-c.amount as double) else cast(c.amount as double) end) as cost
        from range(`home/taxi-supply/billing/acquisition/scouts/billing_scout_by_dates`,`2020-07-01`)  as c
        join `home/taxi-supply/billing/acquisition/scouts/billing/full` as d using(transaction_id)
        where d.target ilike '%dr%' or d.target ilike '%cargo%'
        GROUP BY
            SUBSTRING(c.dt,0,7)||'-01' as month
            , city as city
            , case
                when target ilike '%dr%' then 'drivers'
                when target ilike '%cargo%' then 'cargo'
              else target
             end as tariff
    """)
    city_scouts_billing.rename(columns={'month':'date'}, inplace=True)
    city_scouts_billing['source'] = 'YT city'
    
    return city_scouts_billing

scouts = yt_scouts_city()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 24
    """
)
def city_geo_normalized():    
    city_detalization = pd.concat([cities, partners, scouts])
    greenplum.write_table('snb_da.pnl__tmp__city_detalization', city_detalization)
    city_geo = greenplum("""
        select date
                 , channel
                 , program
                 , task
                 , budget_item
                 , budget_sub_item
                 , coalesce(country, tz_country_name_en) as country
                 , tz_aggl_name_en    as city
                 , node_id as geo_node_id
                 , population_group
                 , city               as city_name
                 , tariff
                 , cfo
                 , type
                 , cost
                 , source
            from snb_da.pnl__tmp__city_detalization as t
            left JOIN(
                select DISTINCT tz_aggl_name_ru
                              , tz_country_name_en
                              , tz_aggl_name_en
                              , population_group
                              , node_id
                from core_cdm_geo.v_dim_full_geo_hierarchy
                where node_type = 'agglomeration'
                  and root_node_id = 'fi_root'
            ) geo
                on t.city = geo.tz_aggl_name_ru
    """)
    
    return city_geo

city_geo = city_geo_normalized()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 25
    """
)
def gp_performance_city():
    performance = greenplum("""
        select t.*
            , tz_country_name_en as country
            , tz_aggl_name_en as city
            , node_id as geo_node_id
            , population_group
        from (
            select
                date_trunc('month',dt)::date as date
                , case channel
                    when 'Online' then 'Online Paid'
                    when 'Selfregistration' then 'Selfregistration Paid'
                else channel end as channel
                , 'Performance mobile' as program
                , 'Объект неизвестен' as task
                , 'Performance' as budget_item
                , brand as budget_sub_item
                , case when city_name is null and country_name = 'Израиль' then 'Тель-Авив' else city_name end as city_name
                , ytms as cfo
                , case
                    when audience in ('Водители','Самозанятые') then 'drivers'
                    when audience = 'Грузовой' then 'cargo'
                    when audience = 'Доставка' then 'delivery'
                  else audience
                 end as tariff
                , 'Fact' as type
                , sum(cost_install + cost_visit) as cost
            from ritchie.snb_taxi.martianov_performance_cost
                where dt::date >= '2020-07-01' and ytms in ('YTMS82','YTM100')
                group by 1,2,6,7,8,9,10
        ) t
        left JOIN(
            select
                DISTINCT tz_aggl_name_ru
                , tz_country_name_en
                , tz_aggl_name_en
                , population_group
                , node_id
            from core_cdm_geo.v_dim_full_geo_hierarchy
            where node_type = 'agglomeration'
                and root_node_id = 'fi_root'
        ) geo
            on t.city_name = geo.tz_aggl_name_ru
    """)
    performance['source'] = 'GP city'
    
    return performance
performance = gp_performance_city()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 26
    """
)
def gp_referral_city():    
    referral_city = greenplum("""
        select
            date
            , 'Referral Program' as channel
            , 'Referral Program' as program
            , 'Referral Program' as task
            , tz_country_name_en as country
            , case when date >= '2020-07-01' then tz_aggl_name_en else null end as city
            , case when date >= '2020-07-01' then node_id else null end as geo_node_id
            , case when date >= '2020-07-01' then population_group else null end population_group
            , 'YTMS82' as cfo
            , 'drivers' as tariff
            , 'Fact' as type
            , cost
        from(
            select * from(
                select
                    case when country = 'Кот-д’Ивуар' then 'Кот-д''Ивуар' else country end as country
                    ,city
                    ,date_trunc('month',dt::date)::date as date
                    ,sum(referrer_bonus_by_pay) as cost
                from analyst.martianov_refferal_stat
                where dt is not null
                group by 1,2,3
                ) t1
                LEFT JOIN(
                    select
                           DISTINCT tz_country_name_en
                           , tz_aggl_name_ru
                           , tz_aggl_name_en
                           , population_group
                           , node_id
                    from core_cdm_geo.v_dim_full_geo_hierarchy
                    where node_type = 'agglomeration' and root_node_id = 'fi_root'
                ) geo
                on t1.city = geo.tz_aggl_name_ru
            ) t
    """)
    referral_city['source'] = 'GP city'
    
    return referral_city
referral_city = gp_referral_city()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 27
    """
)
def gp_call_center_city():   # not used
    city_call_center = greenplum("""
        select
            month::date as date
             , case
                when medium = 'agents' then 'Agents'
                when medium = 'online' and month::date >= '2020-07-01' then 'Online Paid'
                when medium = 'online' and month::date < '2020-07-01' then 'Online'
                when medium = 'leadgens' then 'Leadgens'
                when medium = 'mass_recruitment' then 'Mass recruitment'
              else medium
             end as channel
            , 'Call center' as budget_item
            , cost_item as budget_sub_item
            , tz_country_name_en as country
            , tz_aggl_name_en as city
            , population_group
            , 'YTMS82' as cfo
            , tariff
            , 'Fact' as type
            , cost
        from snb_taxi.lenova_sm_callcenter_money_dist_july2020_with_tariffs as t
        join (
                select DISTINCT node_id
                        , tz_country_name_en
                        , tz_aggl_name_en
                        , population_group
                from core_cdm_geo.v_dim_full_geo_hierarchy
                where node_type = 'agglomeration'
                    and root_node_id = 'fi_root'
                ) geo
                    on t.region_id = geo.node_id
    """)
    city_call_center['source'] = 'GP city'
    
    return city_call_center
city_call_center = gp_call_center_city()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 28
    """
)
greenplum("drop table if exists snb_da.pnl__tmp__city_loss")
city = pd.concat([city_geo, performance, referral_city]) # city_call_center not used
greenplum.write_table('snb_da.pnl__tmp__city_loss', city)
#greenplum('grant select on snb_da.pnl__tmp__city_loss to "matveev-ivan"')
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 29
    """
)
def country_to_city():
    country_to_city_wo_online_selfreg_w_drivers = greenplum("""
        with cost as (
            select * from (
                select date::date as date,
                       country,
                       channel,
                       tariff,
                       sum(cost) as cost
                from snb_da.pnl__tmp__gd_country_normalized
                where cfo = 'YTMS82'
                group by 1, 2, 3, 4
            ) country
            union all
            select * from (
                select date::date as date,
                       country,
                       channel,
                       tariff,
                       sum(cost) as cost
                from snb_da.pnl__tmp__city_loss
                where cfo = 'YTMS82'
                group by 1, 2, 3, 4
            ) city
        ),
        drivers as (
            select date_trunc('month', date)::date as date
                , channel
                , country
                , city
                , geo_node_id
                , population_group
                , tariff
                , sum(drivers)                    as drivers
            from snb_da.pnl__drivers as t0
            join (
                select date,channel,country,tariff,sum(cost) as cost
                from cost
                group by 1,2,3,4
            ) as t1
                using(date,channel,country,tariff)
            where 1=1
                and t1.cost > 0
                and type = 'Fact'
                and scale = 'month'
                and channel not in ('Online Organic', 'Online Paid', 'Selfregistration Organic', 'Selfregistration Paid')
            group by 1, 2, 3, 4, 5, 6, 7
        ),
        share as (
            select t0.*, drivers / drivers_total as share
            from (
                select date
                     , channel
                     , country
                     , city
                     , geo_node_id
                     , population_group
                     , tariff
                     , drivers
                from drivers as t0
            ) as t0
            join (
                select date
                     , channel
                     , country
                     , tariff
                     , sum(drivers)                    as drivers_total
                from drivers as t0
                group by 1,2,3,4
            ) t1
                using (date,channel,country,tariff)
        ),
        data as (
            select t0.date
                 , t0.channel
                 , t0.program
                 , t0.task
                 , t0.budget_item
                 , t0.budget_sub_item
                 , t0.country
                 , t1.city
                 , t1.geo_node_id
                 , t1.population_group
                 , t0.tariff
                 , t0.cfo
                 , t0.type
                 , t0.cost * t1.share as cost
                 , source
            from snb_da.pnl__tmp__gd_country_normalized as t0
                     join share as t1
                          using (date, channel, country, tariff)
            where t0.channel not in ('Online', 'Online Paid', 'Selfregistration')
              and cost * share is not null
              and cfo = 'YTMS82'
        )
        select * from data
    """)
    country_to_city_online = greenplum("""
        with share as (
            select t0.*, drivers / drivers_total as share
            from (
                     select date_trunc('month', date)::date as date
                          , channel
                          , country
                          , city
                          , geo_node_id
                          , population_group
                          , tariff
                          , sum(drivers)                    as drivers
                     from snb_da.pnl__drivers
                     where 1=1
                        and type = 'Fact'
                        and date >= '2020-07-01'
                        and channel in ('Online Organic','Online Paid')
                        and scale = 'month'
                     group by 1, 2, 3, 4, 5, 6, 7
            ) as t0
            join (
                    select date_trunc('month', date)::date as date
                         , country
                         , tariff
                         , sum(drivers)                    as drivers_total
                    from snb_da.pnl__drivers
                    where 1=1
                        and type = 'Fact'
                        and date >= '2020-07-01'
                        and channel in ('Online Organic','Online Paid')
                        and scale = 'month'
                    group by 1,2,3
            ) t1
                using (date,country,tariff)
        ),
        loss_city_w_drivers as (
            select
                 t0.date::date
                , t1.channel
                , program
                , task
                , budget_item
                , budget_sub_item
                , t0.country
                , t1.city
                , geo_node_id
                , t1.population_group
                , t0.tariff
                , t0.cfo
                , type
                , cost*share as cost
                , source
                , share
                , drivers
            from snb_da.pnl__tmp__gd_country_normalized as t0
            join share as t1
                using(date,country,tariff)
            where t0.channel = 'Online' and cfo = 'YTMS82'
        ),
        loss_city_wo_drivers as (
            select t0.date,'Online Paid' as channel,t0.country,t0.program,t0.task,t0.budget_item,t0.budget_sub_item,t0.type,t0.cfo,t0.tariff,t0.source,t0.cost
            from snb_da.pnl__tmp__gd_country_normalized as t0
            left join loss_city_w_drivers as t1
                using(date,country,tariff)
            where 1=1
                and t1.cost is null
                and t0.channel = 'Online'
                and t0.cfo = 'YTMS82'
        )
        select date::date as date,channel::text,country,program,task,budget_item,budget_sub_item,type,cfo,tariff,source,cost,null as city,null as geo_node_id,null as population_group from loss_city_wo_drivers as t0
        union all
        select date::date as date,channel,country,program,task,budget_item,budget_sub_item,type,cfo,tariff,source,cost,city,geo_node_id,population_group from loss_city_w_drivers
    """)
    
    country_to_city_selfreg = greenplum("""
        with share as (
            select t0.*, drivers / drivers_total as share
            from (
                     select date_trunc('month', date)::date as date
                          , channel
                          , country
                          , city
                          , geo_node_id
                          , population_group
                          , tariff
                          , sum(drivers)                    as drivers
                     from snb_da.pnl__drivers
                     where 1=1
                        and type = 'Fact'
                        and channel in ('Selfregistration Organic','Selfregistration Paid')
                        and scale = 'month'
                     group by 1, 2, 3, 4, 5, 6, 7
            ) as t0
            join (
                    select date_trunc('month', date)::date as date
                         , country
                         , tariff
                         , sum(drivers)                    as drivers_total
                    from snb_da.pnl__drivers
                    where 1=1
                        and type = 'Fact'
                        and channel in ('Selfregistration Organic','Selfregistration Paid')
                        and scale = 'month'
                    group by 1,2,3
            ) t1
                using (date,country,tariff)
        ),
        loss_city_w_drivers as (
            select
                 t0.date::date
                , t1.channel
                , program
                , task
                , budget_item
                , budget_sub_item
                , t0.country
                , t1.city
                , geo_node_id
                , t1.population_group
                , t0.tariff
                , t0.cfo
                , type
                , cost*share as cost
                , source
                , share
                , drivers
            from snb_da.pnl__tmp__gd_country_normalized as t0
            join share as t1
                using(date,country,tariff)
            where t0.channel = 'Selfregistration' and cfo = 'YTMS82'
        ),
        loss_city_wo_drivers as (
            select t0.date,'Selfregistration Paid' as channel,t0.country,t0.program,t0.task,t0.budget_item,t0.budget_sub_item,t0.type,t0.cfo,t0.tariff,t0.source,t0.cost
            from snb_da.pnl__tmp__gd_country_normalized as t0
            left join loss_city_w_drivers as t1
                using(date,country,tariff)
            where 1=1
                and t1.cost is null
                and t0.channel = 'Selfregistration'
                and t0.cfo = 'YTMS82'
        )
        select date::date as date,channel::text,country,program,task,budget_item,budget_sub_item,type,cfo,tariff,source,cost,null as city,null as geo_node_id,null as population_group from loss_city_wo_drivers as t0
        union all
        select date::date as date,channel,country,program,task,budget_item,budget_sub_item,type,cfo,tariff,source,cost,city,geo_node_id,population_group from loss_city_w_drivers
    """)
    
    country_wo_drivers = greenplum("""
         select date::date as date
             , channel
             , program
             , task
             , budget_item
             , budget_sub_item
             , country
             , cfo
             , type
             , tariff
             , source
             , sum(cost)   as cost
        from snb_da.pnl__tmp__gd_country_normalized as t0
        left join (
                select
                    date_trunc('month',date)::date as date
                    , case when channel in ('Selfregistration Organic','Selfregistration Paid') then 'Selfregistration'
                        else channel end as channel
                    , country
                    , tariff
                    , sum(drivers) as drivers
                from snb_da.pnl__drivers
                where 1=1
                    and type = 'Fact'
                    and scale = 'month'
                group by 1,2,3,4
                having sum(drivers) > 0
        ) as t1
            using(date,country,channel,tariff)
        where 1=1
            and date >= '2020-07-01'
            and (drivers is null or drivers = 0)
            and cfo = 'YTMS82'
        group by 1,2,3,4,5,6,7,8,9,10,11
    """)

    country_old = greenplum("""
        select
            channel
            , country
            , program
            , task
            , budget_item
            , budget_sub_item
            , date(year || '-' || t1.month_num || '-01')::date as date
            , type
            , cfo
            , tariff
            , source
            , sum(cast(cost as float))                        as cost
            from snb_da.pnl__tmp__gd_country_detalization as t0
            JOIN analyst.ks_konovalova__pnl__mapping__month as t1
                on t0.month = t1.month_name_en
            where 1=1
            and date(year || '-' || t1.month_num || '-01')::date < '2020-07-01'
            and channel != 'Selfregistration'
            and cfo = 'YTMS82'
        group by 1,2,3,4,5,6,7,8,9,10,11
    """)
    
    country_cfo_ytm100 = greenplum("""
        select
            channel
            , country
            , program
            , task
            , budget_item
            , budget_sub_item
            , date(year || '-' || t1.month_num || '-01')::date as date
            , type
            , cfo
            , 'drivers' as tariff
            , source
            , sum(cast(cost as float))                        as cost
            from snb_da.pnl__tmp__gd_country_detalization as t0
            JOIN analyst.ks_konovalova__pnl__mapping__month as t1
                on t0.month = t1.month_name_en
            where cfo = 'YTM100'
        group by 1,2,3,4,5,6,7,8,9,10,11
    """)
    
    country_to_city = pd.concat([city, country_to_city_wo_online_selfreg_w_drivers, country_to_city_online, country_to_city_selfreg, country_old, country_wo_drivers,country_cfo_ytm100])

    return country_to_city
country_to_city = country_to_city()

hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 100
    """
)
def loss_total():
    df = pd.concat([country_to_city, plan_loss])
    df['scale'] = 'month'
    greenplum("drop table if exists snb_da.pnl__tmp_loss")
    greenplum.write_table('snb_da.pnl__tmp_loss', df)
    hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 1001
    """
    )
    sheet_city_dict = '1bHaivxEKfUjPJauog3f6JCrE0gOR6UPAro9QRZ_59NY'
    city_dict = gdocs.read(table_name='dictionary', sheet_id=sheet_city_dict, header=1)
    greenplum.write_table('snb_da.pnl__tmp_city_dictionary', city_dict)
    hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 1002
    """
    )
    df = greenplum("""
        select
                date::date as date,scale,channel,program,task,budget_item,budget_sub_item
                , coalesce(t0.country,t1.country) as country
                , coalesce(t0.city,t1.city) as city
                , coalesce(t0.geo_node_id,t1.node_id) as geo_node_id
                , coalesce(t0.population_group,t1.population_group) as population_group
                , city_name as source_name
                , tariff,cfo,type,source,cost
            from snb_da.pnl__tmp_loss as t0
            left join (
                select
                    tz_aggl_name_en as city
                    , tz_country_name_en as country
                    , population_group
                    , source_name
                    , geo.node_id as node_id
                from snb_da.pnl__tmp_city_dictionary as t0
                join (
                    select DISTINCT node_id
                            , tz_country_name_en
                            , tz_aggl_name_en
                            , population_group
                    from core_cdm_geo.v_dim_full_geo_hierarchy
                    where node_type = 'agglomeration'
                      and root_node_id = 'fi_root'
                ) geo
                    using(node_id)
            ) as t1
                on t0.city_name = t1.source_name
    """)

    #greenplum("truncate table snb_da.pnl__loss")
    greenplum.write_table('snb_da.pnl__loss', df, with_grant=True, operator='select', to='analyst')
    #greenplum('grant select on analyst.ks_konovalova__pnl__loss to "matveev-ivan"')

loss_total()
hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 110
    """
)
#########################################             RESULT             ##########################################

def result():
    pnl_object = greenplum("""
        with ltsh as (
            select
                case
                    when medium = 'agents' then 'Agents'
                    when medium = 'leadgens' then 'Leadgens'
                    when medium in ('online','online_organic') then 'Online Organic'
                    when medium = 'online_paid' then 'Online Paid'
                    when medium in ('online','online_organic','online_paid') then 'Online'
                    when medium = 'selfreg_organic' then 'Selfregistration Organic'
                    when medium = 'selfreg_paid' then 'Selfregistration Paid'
                    when medium = 'mass_recruitment' then 'Mass recruitment'
                    when medium = 'scouts' then 'Scouts'
                    when medium = 'parks_motivation' then 'Partners'
                    when medium in ('offline','offline_sales') then 'Offline'
                    when medium = 'organic' then 'Organic'
                    when medium = 'agent_partner_freelance' then 'Freelance'
                    when medium in ('referral_program','referal','referral_drivers') then 'Referral Program'
                    else medium
                    end as channel
                 , city_id as geo_node_id
                 , tz_country_name_en as country
                 , avg(ltsh_pd_avg) as ltsh
                 , 'drivers' as tariff
                 , 'YTMS82' as cfo
            from snb_taxi.da_ltsh_forecast as t0
            LEFT JOIN(
                select
                    DISTINCT node_id
                    , tz_country_name_en
                    , tz_aggl_name_ru
                    , tz_aggl_name_en
                    , population_group
                from core_cdm_geo.v_dim_full_geo_hierarchy
                where node_type = 'agglomeration'
                    and root_node_id = 'fi_root'
            ) geo
                on t0.city_id = geo.node_id
            group by 1,2,3
        )
        select t1.*, coalesce(t2.ltsh,t3.ltsh) as ltsh
        from (
            select *
            from analyst.ks_konovalova__pnl__drivers as t0
            full outer join(
                select
                    date,scale,channel,country,city,population_group,geo_node_id,cfo,tariff,type
                    , sum(cost) as cost
                from snb_da.pnl__loss
                group by 1,2,3,4,5,6,7,8,9,10
            ) as t1
                using(date,scale,channel,country,city,population_group,geo_node_id,cfo,tariff,type)
        ) as t1
        left join (
            select * from ltsh
            where ltsh is not null
        ) as t2
            using(channel,geo_node_id,tariff,cfo)
        left join (
            select channel,country,tariff,cfo,avg(ltsh) as ltsh
            from ltsh
            where ltsh is not null
            group by 1,2,3,4
        ) as t3
            on t1.channel = t3.channel
            and t1.country = t3.country
            and t1.tariff = t3.tariff
            and t1.cfo = t3.cfo
    """)
    #greenplum("truncate table snb_da.pnl__data")
    greenplum.write_table('snb_da.pnl__data', pnl_object, with_grant=True, operator='select', to='analyst,"matveev-ivan",kharchenkom')
    #greenplum('grant select on analyst.ks_konovalova__pnl__data to "matveev-ivan"')
result()

hahn(
    """
    insert into `home/taxi-analytics/kutikovivan/temp/cron_test1` with truncate
    select cast(CurrentUtcDatetime() as string), 1000
    """
)

'''
greenplum("drop table if exists snb_da.pnl__tmp__pre_drivers")
greenplum("drop table if exists snb_da.pnl__tmp_city_dictionary")
greenplum("drop table if exists snb_da.pnl__tmp_loss")
greenplum("drop table if exists snb_da.pnl__tmp__gd_country_detalization")
greenplum("drop table if exists snb_da.pnl__tmp__gd_country_normalized")
greenplum('drop table if exists snb_da.pnl__tmp__city_loss')
greenplum("drop table if exists snb_da.pnl__tmp__city_detalization")
greenplum("drop table if exists snb_da.pnl__tmp__gd_city_partners")
'''
