-- Для Unit Economics Report: Шаг 3 Добавляем к base c CPO остальные затраты
drop table if exists share_shop;
create temporary table share_shop as (
        select date_trunc('month',coalesce(o.msk_place_confirmed_dttm, o.msk_created_dttm))::date as mnth,
               region_name,
            count(case when flow_type = 'shop' then order_nr end) as shop_order,
           1.0 * count(case when flow_type = 'shop' then order_nr end)/count(order_nr) as share_shop
        from eda_cdm_marketplace.dm_order as o
        where flow_type in ('shop', 'retail') and confirmed_flg
        group by 1, 2
    );

drop table if exists costs;
create temporary table costs as (
        select country,
               region,
               case
                   when type = 'BK' then 'burger_king'
                   when type = 'QSR_other' then 'other_qsr'
                   when type = 'McD' then 'mcdonalds'
                   when type = 'MP' then 'marketplace'
                   when type = 'OD_other' then 'native_not_qsr'
                  -- when type = 'Store' then 'store'
                   when type = 'Pharmacy' then 'pharmacy'
                   when type = 'KFC' then 'kfc'
                   else type end                                                   as place_type,
               month::date                                                         as mnth,
               brand_name                                                          as brand_name,
               coalesce(sum(case when metric = 'Logistics_Ops' then value end), 0) as logistcs_ops,
               coalesce(sum(case when metric = 'LogOps_Bags' then value end), 0)   as logistcs_ops_bags,
               coalesce(sum(case when metric = 'LogOps_Hiring' then value end), 0) as logistcs_ops_hiring,
               coalesce(sum(case when metric = 'LogOps_Hiring_Courier' then value end), 0) as logistcs_ops_hiring_courier,
               coalesce(sum(case when metric = 'LogOps_Hiring_Picker' then value end), 0)  as logistcs_ops_hiring_picker,
               coalesce(sum(case when metric = 'LogOps_Hubs' then value end), 0)   as logistcs_ops_hubs,
               coalesce(sum(case when metric = 'Rest_Ops' then value end), 0)      as rest_ops,
               coalesce(sum(case when metric = 'Support' then value end), 0)       as support,
               coalesce(sum(case when metric = 'COVID_19' then value end), 0)      as covid,
               coalesce(sum(case when metric = 'Support_sms' then value end), 0)   as support_sms,
               --coalesce(sum(case when metric = 'PaymentNotReceived' then value end), 0)
               0                                                                   as payment_not_received
        from snb_eda.krechin_max_ue_report_costs_fact
        where type <> 'Store' or brand_name <> '_all_'
        group by 1, 2, 3, 4, 5

        union all

        select country,
               region,
               'store'                                                 as place_type,
               month::date                                             as mnth,
               '_all_'                                                 as brand_name,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'Logistics_Ops' then value end), 0) as logistcs_ops,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'LogOps_Bags' then value end), 0)   as logistcs_ops_bags,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'LogOps_Hiring' then value end), 0) as logistcs_ops_hiring,
               0 as logistcs_ops_hiring_courier,
               0 as logistcs_ops_hiring_picker,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'LogOps_Hubs' then value end), 0)   as logistcs_ops_hubs,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'Rest_Ops' then value end), 0)      as rest_ops,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'Support' then value end), 0)       as support,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'COVID_19' then value end), 0)      as covid,
               coalesce(ss.share_shop,1.0)*coalesce(sum(case when metric = 'Support_sms' then value end), 0)   as support_sms,
               0                                                                                               as payment_not_received
        from snb_eda.krechin_max_ue_report_costs_fact
        left join share_shop as ss on ss.mnth = month::date and ss.region_name = region
        where type = 'Store' and brand_name = '_all_'
        group by 1, 2, 3, 4, ss.share_shop

        union all

        select country,
               region,
               'retail'                                                as place_type,
               month::date                                             as mnth,
               '_all_'                                                 as brand_name,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'Logistics_Ops' then value end), 0) as logistcs_ops,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'LogOps_Bags' then value end), 0)   as logistcs_ops_bags,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'LogOps_Hiring' then value end), 0) as logistcs_ops_hiring,
               0 as logistcs_ops_hiring_courier,
               0 as logistcs_ops_hiring_picker,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'LogOps_Hubs' then value end), 0)   as logistcs_ops_hubs,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'Rest_Ops' then value end), 0)      as rest_ops,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'Support' then value end), 0)       as support,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'COVID_19' then value end), 0)      as covid,
               coalesce(1 - ss.share_shop,0.0)*coalesce(sum(case when metric = 'Support_sms' then value end), 0)   as support_sms,
               --1 * coalesce(sum(case when metric = 'PaymentNotReceived' then value end), 0)
               0                                                                                                   as payment_not_received
        from snb_eda.krechin_max_ue_report_costs_fact
        left join share_shop as ss on ss.mnth = month::date and ss.region_name = region
        where type = 'Store' and brand_name = '_all_'
        group by 1, 2, 3, 4, ss.share_shop
    );
drop table if exists month_koeff;   --коэффициент используется для незавершенного месяца
create temporary table month_koeff as (
    select a.mnth,
       1.0 * date_part('day', max(a.mnth + interval '1 month' - interval '1 day')) /
       date_part('day', max(a.day_mnth))        as m_koeff
       --max(a.day_mnth),
       --date_part('day', max(a.day_mnth)) as day,
       --max(a.mnth + interval '1 month' - interval '1 day')::date as last_mnth_date,
       --date_part('day', max(a.mnth + interval '1 month' - interval '1 day')) as last_day_num
    from snb_eda.krechin_max_ue_report_eda_step1 as a
    group by 1
    order by 1
);

drop table if exists orders_and_requests_by_place;
create temporary table orders_and_requests_by_place as (
    select   a.mnth,
             a.region_name,
             a.brand_name,
             country_name,
             region_aggr,
             a.place_type,
             vat,
             round(sum(orders * coalesce(m_koeff, 1))) as orders,
             round(sum(case when a.taxi_delivery = 'other' then orders * coalesce(m_koeff, 1) else 0 end) ) as orders_wo_taxi
    from snb_eda.krechin_max_ue_report_eda_step1 as a
    left join month_koeff using (mnth)
    group by 1, 2, 3, 4, 5, 6, 7
    order by 1
);

drop table if exists orders_by_place_type;
create temporary table orders_by_place_type as (
     select mnth,
            region_aggr,
            place_type,
            brand_name,
            sum(orders) as orders,
            sum(orders_wo_taxi) as orders_wo_taxi
     from orders_and_requests_by_place
     group by 1, 2, 3, 4
);

-- select *
-- from orders_by_place_type
-- where mnth = '2022-02-01'
-- and brand_name = 'Магнит'

drop table if exists base;
create temporary table base as (
    select c.region                                              as region_aggr,
         c.place_type,
         c.mnth,
         case
            when orders_wo_taxi > 0 then coalesce(logistcs_ops * 1.0 / coalesce(orders_wo_taxi, 1), 0)
            else 0 end                                                          as logistcs_ops_per_order,
         case
            when orders_wo_taxi > 0 then coalesce(logistcs_ops_bags * 1.0 / coalesce(orders_wo_taxi, 1), 0)
            else 0 end                                                          as logistcs_ops_bags_per_order,
         case
            when orders_wo_taxi > 0 then coalesce(logistcs_ops_hiring * 1.0 / coalesce(orders_wo_taxi, 1), 0)
            else 0 end                                                          as logistcs_ops_hiring_per_order,
         case
            when orders_wo_taxi > 0 then coalesce(logistcs_ops_hubs * 1.0 / coalesce(orders_wo_taxi, 1), 0)
            else 0 end                                                          as logistcs_ops_hubs_per_order,
         case
            when orders > 0 then coalesce(rest_ops * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as rest_ops_per_order,
         case
            when orders > 0 then coalesce(support * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as support_wo_sms_per_order,
         case
            when orders > 0 then  coalesce(support_sms * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as support_sms_per_order,
         case
            when orders > 0 then  coalesce(covid * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as covid_per_order,
         case
            when orders > 0 then  coalesce(payment_not_received * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as payment_not_received_per_order
    from costs as c
    left join orders_by_place_type as o
        on c.region = o.region_aggr and c.place_type = o.place_type and c.mnth = o.mnth
    where c.brand_name = '_all_'
    and c.mnth >= '2021-12-01'
         );

drop table if exists base_by_brand;
create temporary table base_by_brand as (
    select
         c.region                                              as region_aggr,
         c.brand_name,
         c.mnth,
         case
            when orders_wo_taxi > 0 then coalesce(logistcs_ops_hiring_courier * 1.0 / coalesce(orders_wo_taxi, 1), 0)
            else 0 end                                                          as logistcs_ops_hiring_courier_per_order,
         case
            when orders > 0 then coalesce(logistcs_ops_hiring_picker * 1.0 / coalesce(orders, 1), 0)
            else 0 end                                                          as logistcs_ops_hiring_picker_per_order
    from costs as c
    left join orders_by_place_type as o
        on c.region = o.region_aggr and c.brand_name = o.brand_name and c.mnth = o.mnth
    where c.brand_name <> '_all_'
    and c.mnth >= '2021-12-01'
         );
--
-- select *
-- from base_by_brand
-- where mnth = '2022-02-01'
-- and brand_name = 'Магнит'

drop table if exists all_mnth;
create temporary table all_mnth as (
     select t0.region_aggr,
            place_type,
            generate_series(min(mnth)::date, max(max_dt)::date, interval '1 month')::date as first_mnth
     from base as t0
     join (select max(date_trunc('month', msk_place_confirmed_dttm)::date) as max_dt
           from eda_cdm_marketplace.dm_order) as f on 1 = 1
     group by 1, 2
     order by 3 desc
);

drop table if exists all_mnth_by_brand;
create temporary table all_mnth_by_brand as (
     select t0.region_aggr,
            brand_name,
            generate_series(min(mnth)::date, max(max_dt)::date, interval '1 month')::date as first_mnth
     from base_by_brand as t0
     join (select max(date_trunc('month', msk_place_confirmed_dttm)::date) as max_dt
           from eda_cdm_marketplace.dm_order) as f on 1 = 1
     group by 1, 2
     order by 3 desc
);

drop table if exists hist_costs;
create temporary table hist_costs as (
     select a.region_aggr,
            a.place_type,
            avg(logistcs_ops_per_order)   as hist_logistcs_ops_per_order,
            avg(logistcs_ops_bags_per_order)   as hist_logistcs_ops_bags_per_order,
            avg(logistcs_ops_hiring_per_order)   as hist_logistcs_ops_hiring_per_order,
            avg(logistcs_ops_hubs_per_order)   as hist_logistcs_ops_hubs_per_order,
            avg(rest_ops_per_order)       as hist_rest_ops_per_order,
            avg(support_wo_sms_per_order) as hist_support_wo_sms_per_order,
            avg(covid_per_order)          as hist_covid_per_order,
            avg(support_sms_per_order)    as hist_support_sms_per_order,
            avg(payment_not_received_per_order)    as hist_payment_not_received_per_order
     from base as a
     where a.mnth >= (select (max(month)::date - interval '1 month')::date
                        from snb_eda.krechin_max_ue_report_costs_fact)
     --date_trunc('month', current_date - interval '2 month')
     group by 1, 2
);

drop table if exists hist_costs_by_brand;
create temporary table hist_costs_by_brand as (
     select a.region_aggr,
            a.brand_name,
            avg(logistcs_ops_hiring_courier_per_order)   as hist_logistcs_ops_hiring_courier_per_order,
            avg(logistcs_ops_hiring_picker_per_order)   as hist_logistcs_ops_hiring_picker_per_order
     from base_by_brand as a
     where a.mnth >= (select (max(month)::date - interval '1 month')::date
                        from snb_eda.krechin_max_ue_report_costs_fact)
     --date_trunc('month', current_date - interval '2 month')
     group by 1, 2
);

drop table if exists base_step3_costs;
create temporary table base_step3_costs as (
    select a.*,
            coalesce(logistcs_ops_per_order, hist_logistcs_ops_per_order)              as logistcs_ops_per_order,
            coalesce(logistcs_ops_bags_per_order, hist_logistcs_ops_bags_per_order)     as logistcs_ops_bags_per_order,
            coalesce(logistcs_ops_hiring_per_order, hist_logistcs_ops_hiring_per_order) as logistcs_ops_hiring_per_order,
            coalesce(logistcs_ops_hubs_per_order, hist_logistcs_ops_hubs_per_order)     as logistcs_ops_hubs_per_order,
            coalesce(rest_ops_per_order, hist_rest_ops_per_order)                      as rest_ops_per_order,
            coalesce(covid_per_order, hist_covid_per_order)                            as covid_per_order,
            coalesce(support_sms_per_order, hist_support_sms_per_order)                as support_sms_per_order,
            coalesce(support_wo_sms_per_order + support_sms_per_order,
                  hist_support_sms_per_order + hist_support_wo_sms_per_order)       as support_per_order,
            coalesce(payment_not_received_per_order, hist_payment_not_received_per_order)  as payment_not_received_per_order
    from all_mnth as a
    left join base as b
             on a.first_mnth = b.mnth and a.region_aggr = b.region_aggr and
                a.place_type = b.place_type
    left join hist_costs as c
             on a.region_aggr = c.region_aggr and a.place_type = c.place_type
);
analyze base_step3_costs;

drop table if exists base_step3_costs_by_brand;
create temporary table base_step3_costs_by_brand as (
    select a.*,
            coalesce(logistcs_ops_hiring_courier_per_order,
                    0)              as logistcs_ops_hiring_courier_per_order,
            coalesce(logistcs_ops_hiring_picker_per_order,
                    0)              as logistcs_ops_hiring_picker_per_order
    from all_mnth_by_brand as a
    left join base_by_brand as b
             on a.first_mnth = b.mnth and a.region_aggr = b.region_aggr and
                a.brand_name = b.brand_name
    left join hist_costs_by_brand as c
             on a.region_aggr = c.region_aggr and a.brand_name = c.brand_name
);
analyze base_step3_costs_by_brand;

    -- truncate table snb_taxi.ellenl_ue_report_eda_base_final;
-- DELETE
-- FROM snb_taxi.ellenl_ue_report_eda_base_final_v4
-- WHERE day_mnth >= '{msc_date_from}'
--     and day_mnth < '{msc_date_to}'
-- ;
-- Insert into snb_taxi.ellenl_ue_report_eda_base_final_v4

--INSERT INTO snb_taxi.ellenl_ue_report_eda_base_final_v4  (
    select a.*,
           case when a.taxi_delivery = 'other' then b.logistcs_ops_per_order else 0 end      as logistcs_ops_per_order,
           case
               when a.taxi_delivery = 'other' then b.logistcs_ops_bags_per_order
               else 0 end                                                                    as logistcs_ops_bags_per_order,
           case when a.taxi_delivery = 'other' then coalesce(b.logistcs_ops_hiring_per_order, 0) else 0 end
            + case when a.taxi_delivery = 'other' then coalesce(bb.logistcs_ops_hiring_courier_per_order, 0) else 0 end
            + coalesce(bb.logistcs_ops_hiring_picker_per_order, 0)                              as logistcs_ops_hiring_per_order,
           case
               when a.taxi_delivery = 'other' then b.logistcs_ops_hubs_per_order
               else 0 end                                                                    as logistcs_ops_hubs_per_order,
           b.rest_ops_per_order,
           b.covid_per_order,
           b.support_sms_per_order                                                           as support_sms_per_order,
           b.support_per_order                                                               as support_per_order,
           b.payment_not_received_per_order                                                  as payment_not_received_per_order,
           case when a.high_level_type = 'marketplace' then 0 else a.orders end              as orders_od
    INTO snb_eda.krechin_max_ue_report_eda_final_test_2022_03_29
    from snb_taxi.ellenl_ue_report_eda_base_step2_cpo_v3 as a
             left join base_step3_costs as b
                       on a.mnth = b.first_mnth and a.region_aggr = b.region_aggr and a.place_type = b.place_type
             left join base_step3_costs_by_brand as bb
                       on a.mnth = bb.first_mnth and a.region_aggr = bb.region_aggr and a.brand_name = bb.brand_name
    where day_mnth >=  '{msc_date_from}' -- '2020-01-01'
        and day_mnth <  '{msc_date_to}'
--)
;
analyze snb_eda.krechin_max_ue_report_eda_final_test_2022_03_30;

grant all on snb_eda.krechin_max_ue_report_eda_final_test_2022_03_30 to "krechin-max", sharavin

-- grant all privileges on  snb_taxi.ellenl_ue_report_eda_base_final_v4 to "robot-taxi-business";
-- grant select on  snb_taxi.ellenl_ue_report_eda_base_final_v4 to rbunin, haberr, "kostja-bobkov";