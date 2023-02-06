use hahn;

pragma yt.InferSchema;

$helper_script = @@
def capitalize(string):
    return string.decode('utf-8').capitalize()
@@;

$capitalize = Python::capitalize(Callable<(String?) -> String?>, $helper_script);

$cur_date = SUBSTRING(Cast(CurrentUtcDate() + DateTime::IntervalFromDays(-35) as String), 0, 7) || '-01';
$tariffs_not_needed = ['cargo', 'courier', 'express', 'cargocorp'];

$corresp = (select distinct tariff_zone, tz_aggl_name_ru
from `//home/taxi-dwh/cdm/geo/v_dim_fi_geo_hierarchy/v_dim_fi_geo_hierarchy`
where node_type = 'agglomeration');

$agg_weekly_supply_hours = (
    select week, city, MAX_BY(country, supply_hours) as country, MAX(supply_hours) as supply_hours, MAX(hours_on_trip) as hours_on_trip
    from (select week, city, country, cast(sum(duration_sec) as double) / 3600 as supply_hours, cast(sum(on_trip) as double) / 3600 as hours_on_trip
    from (
        select driver_uuid, week, city, country, duration_sec, on_trip
        from (
            select driver_session.executor_profile_id || '_' || driver_session.park_taximeter_id as driver_uuid,
                   DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(driver_session.
msk_valid_from_dttm))) as week,
                   t3.tz_aggl_name_ru as city,
                   country_name_ru as country,
                   driver_session.duration_sec as duration_sec,
                   if (driver_session.executor_status_code = 'transporting', duration_sec) as on_trip

            from range(`//home/taxi-dwh/cdm/supply/fct_supply_state_hist`, $cur_date) as driver_session
            inner join range(`//home/taxi-dwh/cdm/marketplace/fct_order`, $cur_date) as dm_order
            on dm_order.order_id = driver_session.order_id
            inner join $corresp as t3
            on (t3.tariff_zone = driver_session.tariff_geo_zone_code)
            where driver_session.executor_status_code not in ('busy', 'verybusy', 'unavailable')
            and dm_order.tariff_class_code not in $tariffs_not_needed
        )
        flatten by city
    )
    group by week, city, country)
    group by week, city
);

$agg_weekly_completed_trips = (
    select city, week, sum(t.completed_trip_fare) / sum(t.completed_trip_fare_before_surge) as surge_multiplier,
           count(t.completed_trip) as completed_trips,
           count(t.completed_trip_via_call_center) as completed_trips_via_call_center,
           sum(t.completed_trip_fare) as gmv,
           count(distinct t.active_driver) as active_drivers,
           count(distinct t.active_rider) as active_riders,
           count_if(t.is_rft) as rfts,
           sum(t.discount_value) as total_discounts,
           count(distinct t.active_rider_via_call_center) as active_riders_via_call_center

    from (select t3.tz_aggl_name_ru as city,
                 trip.msk_order_created_dttm as request_timestamp_msk,
                 if(trip.success_order_flg, trip.order_id) as completed_trip,
                 if(trip.success_order_flg and trip.app_platform_name == 'callcenter', trip.order_id)                
                     as completed_trip_via_call_center,
                 if(trip.success_order_flg, trip.order_cost) as completed_trip_fare,
                 if(trip.success_order_flg, trip.order_before_surge_cost) as completed_trip_fare_before_surge,
                 if(trip.success_order_flg, trip.unique_driver_id) as active_driver,
                 if(trip.success_order_flg and trip.app_platform_name == 'callcenter', trip.user_phone_id)               as active_rider_via_call_center,
                 if(trip.success_order_flg, trip.user_phone_id) as active_rider,
                 trip.first_order_flg as is_rft,
                 if(trip.success_order_flg, trip.discount_compensation_value) as discount_value

          from range(`//home/taxi-dwh/cdm/marketplace/fct_order`, $cur_date) as trip
          inner join $corresp as t3
          on (t3.tariff_zone = trip.tariff_geo_zone_code)
          where not trip.mqc_order_flg
          and trip.tariff_class_code not in $tariffs_not_needed

    ) as t

    group by t.city as city,
             DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(t.request_timestamp_msk))) as week
);

$agg_weekly_dfts = (
    select city, week, count(order_id) as dfts
    from (
        select t3.tz_aggl_name_ru as city, 
               DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(trip.msk_order_created_dttm))) as week, 
               trip.order_id as order_id
        
        from `//home/taxi-dwh/cdm/supply/dm_driver_license_activity_window_ticket/dm_driver_license_activity_window_ticket` as driver
        inner join range(`//home/taxi-dwh/cdm/marketplace/fct_order`, $cur_date) as trip
        on driver.first_order_id = trip.order_id
        inner join $corresp as t3
        on (t3.tariff_zone = trip.tariff_geo_zone_code)
        where trip.tariff_class_code not in $tariffs_not_needed
    )

    group by city, week
);

$agg_weekly_rider_sessions = (
    select city, week, count(session_id) as rider_sessions
    from (
        select t3.tz_aggl_name_ru as city, 
               DateTime::MakeDate(DateTime::StartOfWeek(DateTime::MakeDate(DateTime::ParseIso8601(rider_session.utc_session_start_dttm))))
                as week, 
               rider_session.session_id as session_id
    
        from range(`//home/taxi-dwh/cdm/demand/demand_session`, $cur_date) as rider_session
        inner join $corresp as t3
        on (t3.tariff_zone = rider_session.last_tariff_zone)
        where rider_session.pin_w_wait_time_cnt > 0
        and rider_session.last_order_tariff not in $tariffs_not_needed
    )
    group by city, week
);

$agg_weekly_driver_workshifts = (
    select distinct w.city as city, w.week as week
    from (select DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(workshift.created))) as week, t3.tz_aggl_name_ru as city
          from RANGE(`//home/taxi-dwh/raw/mdb/driver_workshifts`, $cur_date) as workshift
          inner join $corresp as t3
          on (t3.tariff_zone = workshift.home_zone)
    ) as w
);

$agg_weekly_driver_subvention = (
    select distinct t3.tz_aggl_name_ru as city, week
    from ((select week, Yson::ConvertToString(tariff_zone) as tariff_zone
    from (select DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(Yson::ConvertToString(doc.start)))) as week,
                    Yson::ConvertToList(doc.tariffzone) as tariff_zone

            from `home/taxi-dwh/raw/mdb/personal_subvention_rules/personal_subvention_rules`)
    flatten list by tariff_zone)
    UNION ALL
    (select week, Yson::ConvertToString(tariff_zone) as tariff_zone
    from (select DateTime::MakeDate(DateTime::StartOfWeek(DateTime::ParseIso8601(Yson::ConvertToString(doc.start)))) as week,
                    Yson::ConvertToList(doc.tariffzone) as tariff_zone

            from `home/taxi-dwh/raw/mdb/archive_personal_subvention_rules/archive_personal_subvention_rules`)
    flatten list by tariff_zone)) as t1
    inner join $corresp as t3
    on (t3.tariff_zone = t1.tariff_zone)
);

$res = (select 
       weekly_supply_hours.city as city,
       Cast(weekly_supply_hours.week as String) as week,
       weekly_supply_hours.hours_on_trip / weekly_supply_hours.supply_hours as efficiency,
       weekly_completed_trips.surge_multiplier as average_surge_multiplier,
       weekly_completed_trips.completed_trips as completed_trips,
       weekly_supply_hours.supply_hours as supply_hours,
       weekly_rider_sessions.rider_sessions as rider_sessions,
       weekly_completed_trips.gmv as gmv,
       weekly_dfts.dfts as dfts,
       weekly_completed_trips.active_drivers as active_drivers,
       weekly_completed_trips.active_riders as active_riders,
       weekly_completed_trips.rfts as rfts,
       weekly_driver_workshifts.week is not null as driver_workshifts_enabled,
       weekly_driver_subvention.week is not null as driver_subvention_enabled,
       weekly_completed_trips.total_discounts as total_discounts,
       weekly_completed_trips.completed_trips_via_call_center as completed_trips_via_call_center,
       weekly_completed_trips.active_riders_via_call_center as active_riders_via_call_center,
       weekly_supply_hours.country as country_rus

from $agg_weekly_supply_hours as weekly_supply_hours
     left join $agg_weekly_completed_trips as weekly_completed_trips
     on weekly_supply_hours.city = weekly_completed_trips.city and
        weekly_supply_hours.week = weekly_completed_trips.week

     left join $agg_weekly_rider_sessions as weekly_rider_sessions
     on weekly_supply_hours.city = weekly_rider_sessions.city and
        weekly_supply_hours.week = weekly_rider_sessions.week

     left join $agg_weekly_dfts as weekly_dfts
     on weekly_supply_hours.city = weekly_dfts.city and
        weekly_supply_hours.week = weekly_dfts.week

     left join $agg_weekly_driver_subvention as weekly_driver_subvention
     on weekly_supply_hours.city = weekly_driver_subvention.city and
        weekly_supply_hours.week = weekly_driver_subvention.week

     left join $agg_weekly_driver_workshifts as weekly_driver_workshifts
     on weekly_supply_hours.city = weekly_driver_workshifts.city and
        weekly_supply_hours.week = weekly_driver_workshifts.week

where weekly_supply_hours.week != DateTime::MakeDate(DateTime::StartOfWeek(DateTime::MakeDate(CurrentUtcDate())))
      and weekly_supply_hours.week >= DateTime::MakeDate(DateTime::MakeDate(CurrentUtcDate()) - 
                                                         DateTime::IntervalFromDays(35))

order by city, week);

$corresp = (select t1.id as city, name_eng as city_eng, total_population as population, country_id as country
from `//home/taxi-dwh/ods/mdb/city/city` as t1
inner join (select distinct tz_aggl_name_ru as city, total_population
from `//home/taxi-dwh/cdm/geo/v_dim_fi_geo_hierarchy/v_dim_fi_geo_hierarchy`
where node_type = 'agglomeration') as t2
on (t2.city = t1.id));

select country, case when city_eng = 'nizhnynovgorod' then 'Nizhny Novgorod'
        when city_eng = 'rostovondon' then 'Rostov-on-Don'
        when city_eng= 'ekb' then 'Ekaterinburg'
        when city_eng = 'spb' then 'Saint Petersburg'
    else $capitalize(city_eng) end as city_name, 
    t1.city as city_name_rus, population, week, country_rus, average_surge_multiplier, completed_trips, supply_hours, rider_sessions, gmv, dfts, active_drivers, active_riders, rfts, driver_workshifts_enabled, driver_subvention_enabled, total_discounts, completed_trips_via_call_center, active_riders_via_call_center
from $res as t1
inner join $corresp as t2
on (t2.city = t1.city);
