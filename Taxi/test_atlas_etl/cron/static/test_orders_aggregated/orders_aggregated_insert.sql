insert into atlas.{table_name} (
    city,
    car_class,
    ts_1_min,
    quadkey,
    requests_volume,
    requests_share_completed,
    requests_share_driver_cancelled,
    requests_share_rider_cancelled,
    requests_share_rider_cancelled_60,
    requests_share_burnt,
    requests_share_found,
    requests_share_chain,
    requests_dist_plan,
    requests_time_plan,
    trips_volume,
    trips_actual_price_avg,
    trips_actual_eta_avg,
    trips_eta_first_candidate_avg,
    trips_eta_performer_avg,
    trips_surge_avg_if_surged,
    trips_surge_avg,
    trips_surcharge_avg,
    trips_surcharge_amount_avg,
    trips_share_surged,
    trips_share_cash,
    trips_fact_plan_dist_deviation,
    trips_fact_plan_time_deviation,
    trips_search_time,
    offers_volume,
    offers_avg,
    offers_share_seen_timeouted,
    offers_share_accepted,
    offers_share_timeouted,
    offers_share_driver_cancelled)
with if (status = 'finished' and taxi_status = 'complete', 1, NULL) as is_completed,
     if (surge_value > 1.0, surge_value, NULL) as surge_multiplier,
     surge_alpha * surge_multiplier + coalesce(surge_beta, 0) as surcharge_multiplier,
     surge_beta * surcharge as surcharge_amount
select
    city,
    if(car_class_refined != '', car_class_refined, car_class) as car_class,
    intDiv(ts_1_min, 60) * 60 as ts_1_min,
    {quadkey_column} as quadkey,

    count(1) as requests_volume,
    coalesce(sum(is_completed) / greatest(count(1), 1), 0) as requests_share_completed,
    coalesce(sum(status = 'finished' and taxi_status in ('failed', 'cancelled') and driver_uuid != '') / greatest(count(1), 1), 0)
        as requests_share_driver_cancelled,
    coalesce(sum(status = 'cancelled') / greatest(count(1), 1), 0) as requests_share_rider_cancelled,
    coalesce(sum(status = 'cancelled' and search_time >= 60.0) / greatest(count(1), 1), 0) as requests_share_rider_cancelled_60,
    coalesce(sum(status = 'finished' and taxi_status = 'expired' and driver_uuid != '') / greatest(count(1), 1), 0) as requests_share_burnt,
    coalesce(sum(driver_uuid != '') / greatest(count(1), 1), 0) as requests_share_found,
    coalesce(sum(isNotNull(cand_perf_cp__id)) / greatest(count(1), 1), 0) as requests_share_chain,

    coalesce(if(isNaN(avg(plan_cost__distance)), 0, avg(plan_cost__distance)), 0) as requests_dist_plan,
    coalesce(if(isNaN(avg(plan_cost__time)), 0, avg(plan_cost__time)), 0) as requests_time_plan,

    coalesce(sum(is_completed), 0) as trips_volume,

    coalesce(if(isNaN(avg(is_completed * cost)), 0, avg(is_completed * cost)), 0) as trips_actual_price_avg,
    coalesce(if(isNaN(avg(is_completed * driving_time)), 0, avg(is_completed * driving_time)), 0) as trips_actual_eta_avg,
    coalesce(if(isNaN(avg(is_completed * cand_first_time)), 0, avg(is_completed * cand_first_time)), 0)
        as trips_eta_first_candidate_avg,
    coalesce(if(isNaN(avg(is_completed * cand_perf_time)), 0, avg(is_completed * cand_perf_time)), 0)
        as trips_eta_performer_avg,
    coalesce(if(isNaN(avg(is_completed * surge_multiplier)), 0,
        avg(is_completed * surge_multiplier)), 0) as trips_surge_avg_if_surged,
    coalesce(if(isNaN(avg(is_completed * coalesce(surge_multiplier, 1.0))), 0,
        avg(is_completed * coalesce(surge_multiplier, 1.0))), 0) as trips_surge_avg,
    coalesce(if(isNaN(avg(is_completed * coalesce(surcharge_multiplier, 1.0))), 0, avg(is_completed * coalesce(surcharge_multiplier, 1.0))), 0)
        as trips_surcharge_avg,
    coalesce(if(isNaN(avg(is_completed * coalesce(surcharge_amount, 0.0))), 0, avg(is_completed * coalesce(surcharge_amount, 0.0))), 0)
        as trips_surcharge_amount_avg,

    coalesce(if(sum(is_completed) = 0, 0, sum(is_completed and surge_multiplier is not NULL) / sum(is_completed)), 0) as trips_share_surged,
    coalesce(if(sum(is_completed) = 0, 0, sum(is_completed and payment_type = 'cash') / sum(is_completed)), 0) as trips_share_cash,
    -99999 as trips_fact_plan_dist_deviation,
    -99999 as trips_fact_plan_time_deviation,
    coalesce(if (isNaN(avg(is_completed * search_time)), 0, avg(is_completed * search_time)), 0) as trips_search_time,

    coalesce(sum(seen_cnt), 0) as offers_volume,
    coalesce(if (isNaN(avg(seen_cnt)), 0, avg(seen_cnt)), 0) as offers_avg,
    coalesce(if (sum(seen_cnt + seen_timeout_cnt) = 0, 0, sum(seen_timeout_cnt) / sum(seen_cnt + seen_timeout_cnt)), 0) as offers_share_seen_timeouted,
    coalesce(if (sum(seen_cnt) = 0, 0, sum(assigned_cnt) / sum(seen_cnt)), 0) as offers_share_accepted,
    coalesce(if (sum(seen_cnt) = 0, 0, sum(offer_timeout_cnt) / sum(seen_cnt)), 0) as offers_share_timeouted,
    coalesce(if (sum(seen_cnt) = 0, 0, sum(cancelled_cnt + failed_cnt) / sum(seen_cnt)), 0) as offers_share_driver_cancelled

    from atlas.ods_order final
    where
        user_fraud = 0 and
        dttm_utc_1_min >= toUnixTimestamp('{start_dttm}', 'UTC')  and
        dttm_utc_1_min < toUnixTimestamp('{end_dttm}', 'UTC')
GROUP BY ts_1_min, city, car_class, quadkey;
