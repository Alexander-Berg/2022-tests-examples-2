#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from business_models import hahn, gdocs_helper
import yt.wrapper as yt
import json
from yql.api.v1.client import YqlClient
import os
from business_models.botolib import Bot
from vault_client.instances import Production as VaultClient
from business_models.config_holder import ConfigHolder

# In[ ]:

vault_token = ConfigHolder().vault_token
vault_client = VaultClient(
    authorization='OAuth {}'.format(vault_token)
)
head_version = vault_client.get_version('sec-01ez9ax2fyn06vq04d39qwhx5t')
bot_token = head_version['value']['token']
creator = 497579811
bot = Bot(bot_token)

token = ConfigHolder().quality_robot_token
client = YqlClient(token=token)
bot.send_message(chat=creator, message='Запустился расчет карточки водителя\n')
# bot_id = "984688491:AAE5AP--L9ZuFDRsa1zFrIEQ_gf_HCPLxh4"
# justicewisdom = 342901928

# script_alarm_bot = Bot(offset=0,
#                        token=bot_id,
#                       )
#
# script_alarm_bot.send_message(justicewisdom, 'Запустился расчёт карточки качества!')


# In[ ]:


main_query = '''


use hahn;
pragma AnsiInForEmptyOrNullableItemsCollections;



$date_parse = DateTime::Parse("%Y-%m-%d");

$previous_start_day = cast(DateTime::MakeDate(DateTime::StartOfWeek(CurrentUtcDate() - DateTime::IntervalFromDays(14))) as string);
$start_day = cast(DateTime::MakeDate(DateTime::StartOfWeek(CurrentUtcDate() - DateTime::IntervalFromDays(7))) as string);
$end_day = cast(DateTime::MakeDate(DateTime::StartOfWeek(CurrentUtcDate() - DateTime::IntervalFromDays(1))) - DateTime::IntervalFromDays(1) as string);

$start_day_early = cast(DateTime::MakeDate($date_parse($start_day)) - DateTime::IntervalFromDays(1) as string);
$end_day_late = cast(DateTime::MakeDate($date_parse($end_day)) + DateTime::IntervalFromDays(1) as string);

$helping_hand_start_date = '2020-10-08';

$date2str=DateTime::Format("%Y-%m-%d");
$today=CurrentUtcDate();

$daysago180=$date2str($today - DateTime::IntervalFromDays(180));
$today_str=$date2str($today);

$next_table = '//home/taxi-analytics/fzelina/driver_card/hist/' || $start_day;
$previous_table = '//home/taxi-analytics/vvasilyev/driver_card/hist/' || $previous_start_day;
$actual = '//home/taxi-analytics/fzelina/driver_card/actual';
$comments_path = '//home/taxi-analytics/vvasilyev/driver_card/comments/' || $start_day;



$rating_cohort_1 = 0.2;
$rating_cohort_2 = 0.4;
$rating_cohort_3 = 0.6;
$rating_cohort_4 = 0.9;
$rating_cohort_5 = 1;

-- $telemetry_cohort_1 = 0.07;
-- $telemetry_cohort_2 = 0.1;
-- $telemetry_cohort_3 = 0.15;
-- $telemetry_cohort_4 = 0.3;
-- $telemetry_cohort_5 = 1;

$min_drivers = 1300; -- Минимальное число активных водителей в городе, для того, чтобы сравнивать водителей внутри города, а не внутри страны
$min_orders = 40; -- Минимальное число заказов, с которого начинаем сравнение
$do_not_show = 10; -- Минимальное число заказов, чтобы что-то вообще отображалось

-- Different level thresholds for tags
$speed_thresh_1 = 0.03;
$speed_thresh_2 = 0.095;

$cancel_thresh_1 = 0.04;
$cancel_thresh_2 = 0.08;

$tag_deal_thresh_1 = 0;
$tag_deal_thresh_2 = 1;

-- $telemetry_dangerous_thresh = 0.6;
-- $telemetry_careless_comfort_thresh = 0.46;
-- $telemetry_careless_comfortplus_thresh = 0.42;
-- $telemetry_careless_ultima_thresh = 0.28;

-- функция для месяца в формате текста-стринги

$find_month = ($month) -> {return

case $month
    when '01' then 'января'
    when '02' then 'февраля'
    when '03' then 'марта'
    when '04' then 'апреля'
    when '05' then 'мая'
    when '06' then 'июня'
    when '07' then 'июля'
    when '08' then 'августа'
    when '09' then 'сентября'
    when '10' then 'октября'
    when '11' then 'ноября'
    when '12' then 'декабря'
    else null
    end
}
;

-- конфиг с текстами
$parse_file = ListCollect(ParseFile("String", "config.txt"));
$extract_key = ($x) -> {return CAST(String::SplitToList($x, ';', False, False)[0] as string)};
$extract_data = ($x) -> {return AsStruct(
    CAST(String::SplitToList($x, ';', False, False)[1] as String) as tanker,
    CAST(String::SplitToList($x, ';', False, False)[2] as String) as text
)};
$comments_dict = ToDict(ListZip(ListMap($parse_file, $extract_key), ListMap($parse_file, $extract_data)));



-- 1. Беру данные о качестве из quality_metrics
$qm = (
    select
        order_id,
        some(utc_order_dt) as utc_order_dt,
        some(utc_order_dttm) as utc_order_dttm,
        some(order_tariff) as order_tariff,
        some(driver_license) as driver_license,
        some(driver_id) as driver_id,
        some(unique_driver_id) as unique_driver_id,
        some(country) as country,
        some(city) as city,
        some(rating_value) as rating_value,
        some(rating_comments) as rating_comments,
        some(rating_reasons) as rating_reasons,
        some(success_order_flg) as success_order_flg,
        some(tariff_zone) as tariff_zone,

        -- Теги: на негативных оценках
        max(tag_badroute ?? 0) as tag_badroute,
        max(tag_carcondition ?? 0) as tag_carcondition,
        max(tag_driverlate ?? 0) as tag_driverlate,
        max(tag_nochange ?? 0) as tag_nochange,
        max(tag_notrip ?? 0) as tag_notrip,
        max(tag_rudedriver ?? 0) as tag_rudedriver,
        max(tag_smellycar ?? 0) as tag_smellycar,
        max(tag_baddriving ?? 0) as tag_baddriving,

        -- Теги для поездок с оценкой 4
        max(tag_notcute ?? 0) as tag_notcute,

        -- Теги: положительные теги, когда ставишь 5 звезд
        max(tag_chat ?? 0) as tag_chat,
        max(tag_clean ?? 0) as tag_clean,
        max(tag_comfortride ?? 0) as tag_comfortride,
        max(tag_mood ?? 0) as tag_mood,
        max(tag_music ?? 0) as tag_music,
        max(tag_polite ?? 0) as tag_polite,

        -- Теги: причины отмены
        max(cancel_driverrequest ?? 0) as cancel_driverrequest,
        max(cancel_droveaway ?? 0) as cancel_droveaway,
        max(cancel_longwait ?? 0) as cancel_longwait,
        max(cancel_othertaxi ?? 0) as cancel_othertaxi,
        max(cancel_usererror ?? 0) as cancel_usererror,

        -- Факт плохой оценки без тега и коммента
        max(bad_mark_wo_description ?? 0) as bad_mark_wo_description,

        -- Другое
        max(high_speed_30 ?? 0) as high_speed_30,
        max(high_speed_50 ?? 0) as high_speed_50,
        max(baddriving ?? 0) as baddriving,
        max(usererror ?? 0) as usererror,
        max(droveaway ?? 0) as droveaway,
        max(longwait ?? 0) as longwait,
        max(badroute ?? 0) as badroute,
        max(nochange ?? 0) as nochange,
        max(carcondition ?? 0) as carcondition,
        max(driverrequest ?? 0) as driverrequest,
        max(rudedriver ?? 0) as rudedriver,
        max(smellycar ?? 0) as smellycar,
        max(sleeping_comment ?? 0) as sleeping_comment,
        max(smoking_comment ?? 0) as smoking_comment,
        max(customer_driver_deal ?? 0) as customer_driver_deal,

    from
        range(`home/taxi-analytics/kvdavydova/quality_rate/quality_metrics`, substring($start_day_early, 0, 7))
    where true
        and (utc_order_dt between $start_day_early and $end_day_late)
    group by
        order_id
);
-- select * from $qm;

-- 2. Беру данные о поездках из dm_order
$dm = (
    select
        *
    from
        range(`home/taxi-dwh/summary/dm_order`, substring($start_day_early, 0, 7))
    where true
        and (substring(local_order_dttm, 0, 10) between $start_day and $end_day)
);
-- select * from $dm;


-- 3. Беру данные ML по телеметрии на поездках - пока что только небезопасное вождение!
-- $ml_telemetry = (
--     select
--         order_id,
--         -- bad_driving_pred,
--         dangerous_driving_pred,
--     from
--         range(`//home/taxi_ml/production/telemetry/predictions/daily_processed`, substring($start_day_early, 0, 7))
-- );
-- select * from $ml_telemetry;


-- 4. Беру локаль водителя поо последнему активному driver_id
$drivers_with_local = (
    select
        drivers.unique_driver_id as unique_driver_id,
        (profiles.taximeter_locale_code ?? 'ru') as locale
    from (
        select
            unique_driver_id,
            String::SplitToList(max_by(driver_id, utc_order_dttm), '_')[1] as last_driver_uuid,
            max_by(db_id, utc_order_dttm) as last_db_id
        from
            $dm
        group by
            unique_driver_id
    ) as drivers
    left join `//home/taxi-dwh/cdm/supply/dim_executor_profile_act/dim_executor_profile_act` as profiles
        on drivers.last_db_id == profiles.park_taximeter_id
        and drivers.last_driver_uuid == profiles.executor_profile_id
);
-- select * from $drivers_with_local;



-- 5. Беру данные Маяка о коммуникациях - для того, чтобы использовать их в качестве блокера для коммуникации про плавное вождение

$new_mayak_communications_blocker = (
    select
        unique_driver_id,
        count(*) as new_mayak_comms_count,
    from
        range(`//home/taxi-analytics/kvdavydova/big_brother/action_history`, substring($start_day_early, 0, 7) || '-01')
    where true
        and (action_date between $start_day and $end_day)
        and (reason in ('careless_driving_telemetry', 'baddriving_telemetry', 'baddriving', 'highspeed'))
        and (driver_group == 'test')
        and (`action` not in ('stop_depriority', 'priority_low', 'decrease_depriority_to_middle', 'decrease_depriority_to_low'))
    group by
        unique_driver_id
);
-- select * from $new_mayak_communications;



-- 6. СНОВА Беру данные Маяка о коммуникациях - НО НА ЭТОТ РАЗ для того, чтобы использовать их в формуле для рейтинга

$new_mayak_communications_rating = (
    select
        unique_driver_id,
        count(*) as new_mayak_comms_count,
    from
        range(`//home/taxi-analytics/kvdavydova/big_brother/action_history`, substring($start_day_early, 0, 7) || '-01')
    where true
        and (action_date between $start_day and $end_day)
        and (reason in ('too_short_trip', 'baddriving_telemetry', 'cancel', 'customer_driver_deal', 'highspeed'))
        and (driver_group == 'test')
        and (`action` not in ('stop_depriority', 'priority_low', 'decrease_depriority_to_middle', 'decrease_depriority_to_low'))
    group by
        unique_driver_id
);
-- select * from $new_mayak_communications;



-- 6. Беру данные о качестве из quality_metrics и дополняю их данными о поездках из dm_order и из ml_telemetry
-- Рассчитывается для всех водителей
$qm_plus = (
    select
        qm.*,

        if(substring(dm.car_number_normalized, 0, 7) == 'COURIER', true, false) as walking_courier_trip_flg,

        substring(dm.local_order_dttm, 0, 10) as local_order_dt,
        dm.order_cancel_reason as order_cancel_reasons,

        -- про чаевые
        if((dm.order_tips ?? 0) > 0, 1, 0) as good_order_tips_flg,
        (dm.order_tips ?? 0) as order_tips_value,

        -- плохая поездка - рейтинг 3 или рейтинг 4+замечание
        if((qm.rating_value <= 3) or (max_of(qm.tag_notcute, qm.tag_smellycar, qm.tag_baddriving, qm.tag_badroute) > 0), 1, 0) as bad_order_report,

        (
            max_of(
                (qm.tag_rudedriver ?? 0),
                (qm.tag_smellycar ?? 0),
                (qm.tag_carcondition ?? 0),
                (qm.tag_nochange ?? 0),
                (qm.tag_badroute ?? 0),
                (qm.tag_notcute ?? 0),
                (qm.tag_baddriving ?? 0),
            )
            *
            if(qm.rating_value is null, 0, 1)
        ) as bad_order_tag,

        (
            max_of(
                (qm.tag_chat ?? 0),
                (qm.tag_clean ?? 0),
                (qm.tag_comfortride ?? 0),
                (qm.tag_mood ?? 0),
                (qm.tag_music ?? 0),
                (qm.tag_polite ?? 0),
            )
            *
            if(qm.rating_value == 5, 1, 0)
        ) as good_order_tag,

        if((dm.rating_value == 5) and (length(dm.rating_comments) > 3), 1, 0) as good_order_comment_flag,
        if((dm.rating_value == 5) and (length(dm.rating_comments) > 3), dm.rating_comments, null) as good_order_comment_value,

    from $qm as qm

    join $dm as dm
        on qm.order_id == dm.order_id
);
-- select * from $qm_plus;

-- 6. Рассчитыва все статичные показатели для водителя (кроме рейтинга и динамики) в разрезе unique_driver_id
-- Рассчитывается для всех водителей
$driver_data_wo_locale_and_mayak = (
    select
        unique_driver_id,

        mode(city)[0].Value as city,
        mode(country)[0].Value as country,
        max_by(driver_license, utc_order_dttm) as driver_license,

        -- Подсчёт значения рейтинга водителя!
        --- ВВОДНЫЕ ДЛЯ ОЧЕНЬ ВАЖНОЙ ФОРМУЛЫ

        count_if(rating_value is not null) as rated_trips_count,
        sum(rating_value ?? 0) as rating_sum,
        sum(bad_order_tag ?? 0) as bad_order_tag,

        sum(
            max_of(good_order_comment_flag, good_order_tips_flg, good_order_tag) * if(rating_value is null, 0, 1)
        ) as max_good_user_tag_sum,

        -- другие данные

        count_if(success_order_flg) as success_orders,

        count_if(rating_value is not null) as rated_orders,
        count_if(rating_value == 5) as rated_5_orders,
        count_if(rating_value == 4) as rated_4_orders,
        count_if(rating_value == 3) as rated_3_orders,
        count_if(rating_value == 2) as rated_2_orders,
        count_if(rating_value == 1) as rated_1_orders,

        count_if(good_order_tag == 1) as good_order_tag,
        count_if(good_order_tips_flg == 1) as good_order_tips,
        sum_if(order_tips_value, good_order_tips_flg == 1) as good_order_tips_value,
        count_if(good_order_comment_flag == 1) as good_order_comment,
        count_if(bad_order_report == 1) as bad_order_report,

        -- Негативные отзывы клиентов
        count_if(tag_rudedriver == 1) as tag_rudedriver,
        count_if(tag_smellycar == 1) as tag_smellycar,
        count_if(tag_carcondition == 1) as tag_carcondition,
        count_if(tag_nochange == 1) as tag_nochange,
        count_if(tag_badroute == 1) as tag_badroute,
        count_if(tag_notcute == 1) as tag_notcute,
        count_if(tag_baddriving == 1) as tag_baddriving,

        max_of(
            count_if(tag_rudedriver == 1),
            count_if(tag_smellycar == 1),
            count_if(tag_carcondition == 1),
            count_if(tag_nochange == 1),
            count_if(tag_badroute == 1),
            count_if(tag_notcute == 1),
            count_if(tag_baddriving == 1),
        ) as tag_bad_max_num,

        --Наши наблюдения

        count_if(
            true
            and (high_speed_30 >= 2)
            and (not walking_courier_trip_flg)
        ) as tag_high_speed,

        if(
            sum(customer_driver_deal) > 1,
            sum(customer_driver_deal),
            0
        ) as tag_deal,

        -- возможно, когда-то здесь появится раздел по телеметрии - после того, как мы определимся с флагами
        -- max(dangerous_driving_flg) as dangerous_driving_flg,
        -- count_if(dangerous_driving_flg) as dangerous_driving_orders,

        -- Причины отмены
        count_if((cancel_driverrequest == 1) or (cancel_droveaway == 1) or (order_cancel_reasons ilike '%dont_move%')) as cancellations,
        count_if((cancel_droveaway == 1) or (order_cancel_reasons ilike '%dont_move%')) as cancel_droveaway,
        sum(cancel_driverrequest) as cancel_driverrequest,

        -- Положительные теги
        count_if(tag_chat == 1) as tag_chat,
        count_if(tag_clean == 1) as tag_clean,
        count_if(tag_comfortride == 1) as tag_comfortride,
        count_if(tag_mood == 1) as tag_mood,
        count_if(tag_music == 1) as tag_music,
        count_if(tag_polite == 1) as tag_polite,

    from
        $qm_plus
    where true
        and (unique_driver_id is not null)
    group by
        unique_driver_id
);
-- select * from $driver_data_wo_locale;

-- Подтягиваем локаль и коммуникации по Маяку к водителю, считаем рейтинг
$driver_data_all = (
    select
        drivers.*,

        locales.locale as locale,

        (new_mayak_blocker.new_mayak_comms_count ?? 0) as total_mayak_blocker_comms_count,
        (new_mayak_rating.new_mayak_comms_count ?? 0) as total_mayak_rating_comms_count,

        -- Подсчёт значения рейтинга водителя!
        -- ОЧЕНЬ ВАЖНАЯ ФОРМУЛА

        if(
            (rated_trips_count ?? 0) > 0,
            Math::Round(
                1.0 * (
                    + 1.0 * (rating_sum ?? 0)
                    + 0.25 * (max_good_user_tag_sum ?? 0)
                    - 0.5 * (bad_order_tag ?? 0)
                    - 0.5 * ((new_mayak_rating.new_mayak_comms_count ?? 0))
                ) / (rated_trips_count ?? 0),
                -3
            ),
            0
        ) as rating_value_absolute,

    from $driver_data_wo_locale_and_mayak as drivers

    left join $drivers_with_local as locales
        on drivers.unique_driver_id == locales.unique_driver_id

    left join $new_mayak_communications_blocker as new_mayak_blocker
        on drivers.unique_driver_id == new_mayak_blocker.unique_driver_id

    left join $new_mayak_communications_rating as new_mayak_rating
        on drivers.unique_driver_id == new_mayak_rating.unique_driver_id
);
-- select * from $driver_data_all;



--- ЗДЕСЬ НАЧИНАЕТСЯ ПОДСЧЁТ ПОЗИЦИИ ВОДИТЕЛЕЙ В РЕЙТИНГЕ.

-- Считаю кол-во активных водителей в городе и смотрю не маленький ли он
-- активный - 40+ поездок

$drivers_city = (
    select
        city,
        count(distinct unique_driver_id) as active_drivers_city,
        if(count(distinct unique_driver_id) < $min_drivers, 1, 0) as small_city_flag,
    from
        $driver_data_all
    where true
        and (success_orders >= $min_orders)
    group by
        city
);
-- select * from $drivers_city;

-- Считаю кол-во активных водителей в РФ
$drivers_rus = (
    select
        count(distinct unique_driver_id)
    from
        $driver_data_all
    where true
        and (success_orders >= $min_orders)
);
-- select * from $drivers_rus;

--Считаю позицию в рейтинге в рамках города
$city_ranking = (
    select
        drivers.unique_driver_id as unique_driver_id,
        row_number() over w as rating_pos_city,
        cities.active_drivers_city as active_drivers_city,
        1.0 * (row_number() over w) / cities.active_drivers_city as rating_city,
        cities.small_city_flag as small_city_flag,
    from $driver_data_all as drivers
    left join $drivers_city as cities
        on drivers.city == cities.city
    where true
        and (success_orders >= $min_orders)
    window w as (
        partition by
            drivers.city
        order by
            rating_value_absolute desc,
            success_orders desc
    )
);
-- select * from $city_ranking;

--Считаю позицию в рейтинге в рамках каждой страны
$country_ranking = (
    select
        unique_driver_id,
        row_number() over w as rating_pos_country,
        $drivers_rus as active_drivers_country,
        1.0 * (row_number() over w) / $drivers_rus as rating_country,
    from
        $driver_data_all
    where true
        and (success_orders >= $min_orders)
    window w as (
        partition by
            country
        order by
            rating_value_absolute desc,
            success_orders desc
    )
);
-- select * from $country_ranking;

--Итоговый рейтинг (без округлений)
$driver_rating = (
    select
        drivers.unique_driver_id as unique_driver_id,
        small_city_flag,

        countries.rating_pos_country as rating_pos_country,
        countries.active_drivers_country as active_drivers_country,
        countries.rating_country as rating_country,

        cities.rating_pos_city as rating_pos_city,
        cities.active_drivers_city as active_drivers_city,
        cities.rating_city as rating_city,

        if(small_city_flag == 1, country, city) as rating_region,

        if(small_city_flag == 1, rating_pos_country, rating_pos_city) as rating_pos_final,
        if(small_city_flag == 1, active_drivers_country, active_drivers_city) as active_drivers_final,
        if(small_city_flag == 1, rating_country, rating_city) as rating_final,

    from $driver_data_all as drivers
    left join $country_ranking as countries
        on drivers.unique_driver_id == countries.unique_driver_id
    left join $city_ranking as cities
        on drivers.unique_driver_id == cities.unique_driver_id
);
-- select * from $driver_rating;

--Итоговый рейтинг (с округлениями)
$driver_rating_final = (
    select
        unique_driver_id,
        small_city_flag as country_flag,
        rating_region,
        Math::Ceil(100*rating_final) as rating_final_100,
        active_drivers_city,
        active_drivers_final,

        case
            when rating_final is null
                then null
            when rating_final <= $rating_cohort_1
                then 1
            when rating_final <= $rating_cohort_2
                then 2
            when rating_final <= $rating_cohort_3
                then 3
            when rating_final <= $rating_cohort_4
                then 4
            when rating_final <= $rating_cohort_5
                then 5
            else null
        end as rating_cohort
    from
        $driver_rating
);
-- select * from $driver_rating_final;

-- ТУТ ЗАКОНЧИЛИ СЧИТАТЬ РЕЙТИНГ



-- приклеиваю данные о рейтинге / регионе ко всем даным
$driver_data_all_plus_rating = (
    select
        drivers.*,
        rating.rating_final_100 as rating,
        rating.rating_cohort as rating_cohort,
        rating.rating_region as rating_region,
    from $driver_data_all as drivers
    left join $driver_rating_final as rating
        on drivers.unique_driver_id == rating.unique_driver_id
);
-- select * from $driver_data_all_plus_rating;

-- Собираю все данные по карточке в упорядоченном виде КРОМЕ:
-- 1. Наших комментариев (как к отзывам, так и к закаам)
-- 2. Комментариев пользователей
-- 3. success_orders_delta
-- 4. Комментов внизу

-- РЕЙТИНГ и ДИНАМИКУ, скорее всего, буду отдельно считать и джойнить
$key_driver_data = (
    select
        --ключ
        unique_driver_id,

        city,
        country,
        locale,

        if(success_orders >= $do_not_show, true, false) as show_card_flag,

        -- !!! КАРТОЧКА СВЕРХУ ВНИЗ !!!
        -- $comments_dict['title'].tanker as title,

        (
            substring($start_day, 8, 2)
            || '.' ||
            substring($start_day, 5, 2)
            || ' — ' ||
            substring($end_day, 8, 2)
            || '.' ||
            substring($end_day, 5, 2)
        ) as dates_range,

        case when substring($start_day, 5, 2) = substring($end_day, 8, 2)
            then
                (   'c ' ||
                    cast(cast(substring($start_day, 8, 2) as int64) as string)
                    || ' до ' ||
                    cast(cast(substring($end_day, 8, 2) as int64) as string)
                    || ' ' ||
                    $find_month(substring($end_day, 5, 2))
                )

            else

                (   'c ' ||
                    cast(cast(substring($start_day, 8, 2) as int64) as string)
                    || ' ' ||
                    $find_month(substring($start_day, 5, 2))
                    || ' до ' ||
                    cast(cast(substring($end_day, 8, 2) as int64) as string)
                    || ' ' ||
                    $find_month(substring($end_day, 5, 2))
                )
            end as date_range,

        -- параметры оформления
        case
            when success_orders < $min_orders
                -- жёлтый
                then '#FCB000'
            when rating_cohort == 1
                -- голубой
                then '#0596FA'
            when rating_cohort == 2
                -- зелёный
                then '#00CA50'
            when rating_cohort == 3
                -- жёлтый
                then '#FCB000'
            when rating_cohort == 4
                -- cерый
                then '#C4C2BE'
            when rating_cohort == 5
                -- cерый
                then '#C4C2BE'
            -- жёлтый
            else '#FCB000'
        end as colour_theme,

        -- красный
        '#FA3E2C' as colour_negative,

        ----НОВОЕ----
        -- основной текст
        -- чекнуть момент с падежами

        if(success_orders < $do_not_show, $comments_dict['not_enough_orders'].tanker, null) as text_not_enough_orders,
        if(success_orders < $min_orders, $comments_dict['min_orders'].tanker, null) as text_min_orders,

        case
            when success_orders < $min_orders
                then null
            when rating_cohort == 1
                -- голубой
                then $comments_dict['header_top_1'].tanker
            when rating_cohort == 2
                -- зелёный
                then $comments_dict['header_top_2'].tanker
            when rating_cohort == 3
                -- жёлтый
                then $comments_dict['header_top_3'].tanker
            when rating_cohort == 4
                -- cерый
                then $comments_dict['header_top_4'].tanker
            when rating_cohort == 5
                -- cерый
                then $comments_dict['header_top_5'].tanker
            else null
        end as text_header,

        rating,

        $min_orders as min_orders,
        $do_not_show as super_min_orders,

        -- Что используем
        success_orders,

        -- текст про то, сколько комментов и чаявых
        good_order_tag,
        good_order_tips,

        case
            when (good_order_tag == 0) and (good_order_tips == 0)
                then null
            when (good_order_tag > 0) and (good_order_tips == 0)
                then $comments_dict['good_tags_no_tips'].tanker
            when (good_order_tag > 0) and (good_order_tips > 0)
                then $comments_dict['good_tags_with_tips'].tanker
            when (good_order_tag == 0) and (good_order_tips > 0)
                then $comments_dict['good_tags_tips_only'].tanker
            else null
        end as text_good_orders,

        -- Поездки с плохой оценкой
        if(bad_order_report == 0, null, $comments_dict['bad_orders'].tanker) as text_bad_orders,
        if(bad_order_report == 0, $comments_dict['no_bad_orders'].tanker, null) as text_no_bad_orders,
        if(bad_order_report > 0, bad_order_report, null) as bad_order_report,

        -- Доп текст в самом главном верхнем разделе в самом конце, если на что-то жалуются, пишем, на что именно
        -- этот текст появляется, если тапнуть на пункт с кол-вом замечаний
        if(
            (country != 'Россия') or (Unicode::ToLower(cast(locale as Utf8)) != 'ru'),
            '',
            case
                when tag_bad_max_num == 0
                    then ''
                when tag_bad_max_num == tag_rudedriver
                    then $comments_dict['alert_tag_rudedriver'].text
                when tag_bad_max_num == tag_smellycar
                    then $comments_dict['alert_tag_smellycar'].text
                -- возможно, вот тут надо будет докрутить логику, чтобы коммент не показывался. Или не тут - но точно надо будет
                when tag_bad_max_num == tag_baddriving
                    then $comments_dict['alert_tag_baddriving'].text
                when tag_bad_max_num == tag_carcondition
                    then $comments_dict['alert_tag_carcondition'].text
                when tag_bad_max_num == tag_badroute
                    then $comments_dict['alert_tag_badroute'].text
                when tag_bad_max_num == tag_notcute
                    then $comments_dict['alert_tag_notcute'].text
                else ''
            end
        ) as alert_value,

        --------- РАЗДЕЛ ОТЗЫВЫ --------
        -- Начинаем с названия самого раздела

        $comments_dict['feedback_title'].tanker as feedback_title,

        -- кол-во хороших тегов для этого раздела
        if(tag_chat == 0, null, tag_chat) as tag_chat,
        if(tag_clean == 0, null, tag_clean) as tag_clean,
        if(tag_comfortride == 0, null, tag_comfortride) as tag_comfortride,
        if(tag_mood == 0, null, tag_mood) as tag_mood,
        if(tag_music == 0, null, tag_music) as tag_music,
        if(tag_polite == 0, null, tag_polite) as tag_polite,

        -- кол-во плохих тегов для этого раздела
        if(tag_rudedriver == 0, null, tag_rudedriver) as tag_rudedriver,
        if(tag_smellycar == 0, null, tag_smellycar) as tag_smellycar,
        if(tag_carcondition == 0, null, tag_carcondition) as tag_carcondition,
        if(tag_nochange == 0, null, tag_nochange) as tag_nochange,
        if(tag_baddriving == 0, null, tag_baddriving) as tag_baddriving,
        if(tag_notcute == 0, null, tag_notcute) as tag_notcute,

        -- остальное..? Возможно, наши наблюдения..?
        tag_deal,
        cancel_driverrequest,
        cancel_droveaway,
        cancellations,
        tag_high_speed,

        -- блокер для некоторых других коммуникаций
        total_mayak_blocker_comms_count

    from
        $driver_data_all_plus_rating as a
);
-- select * from $key_driver_data;



--------- ФУНКЦИИ, ЧТОБЫ ПОДСЧИТАТЬ ДИНАМИКУ НА НЕДЕЛЕ ДО И СЕЙЧАС --------------

$speed = ($success_orders, $tag_high_speed) -> {
    return
        case
            when ($success_orders < $do_not_show) or (($tag_high_speed ?? 0) <= 1)
                then -1
            when (1.0 * $tag_high_speed / $success_orders) < $speed_thresh_1
                then 0
            when ((1.0 * $tag_high_speed / $success_orders) between $speed_thresh_1 and $speed_thresh_2)
                then 1
            else 2
        end
};

$cancel = ($success_orders, $cancellations) -> {
    return
        case
            when ($success_orders < $do_not_show) or (($cancellations ?? 0) <= 1)
                then -1
            when (1.0 * $cancellations / $success_orders) < $cancel_thresh_1
                then 0
            when ((1.0 * $cancellations / $success_orders) between $cancel_thresh_1 and $cancel_thresh_2)
                then 1
            else 2
        end
};

$deal = ($success_orders, $tag_deal) -> {
    return
        case
            when ($success_orders < $do_not_show) or ($success_orders is null)
                then -1
            when $tag_deal == $tag_deal_thresh_1
                then 0
            when $tag_deal == $tag_deal_thresh_2
                then 1
            else 2
        end
};

$success_orders_delta = ($actual_success_orders, $previous_success_orders) -> {
    return
        if(
            ($actual_success_orders is not null) and ($previous_success_orders is not null),
            cast($actual_success_orders as int64) - cast($previous_success_orders as int64),
            null
        )
};

--------- ОКОНЧАНИЕ ФУНКЦИЙ --------------



-- Дополняю недостающие элементы
$with_tags = (
    select
        actual.* ,

        -- Сообщение в самом верхнем блоке карточки качества про то, насколько изменилось кол-во поездок на этой неделе по сравнению с предыдущей
        $success_orders_delta(actual.success_orders, previous.success_orders) as success_orders_delta,
        abs($success_orders_delta(actual.success_orders, previous.success_orders)) as success_orders_delta_abs,
        abs(Math::Ceil( 100 * (cast(actual.success_orders as int64) * 1.0 / cast(previous.success_orders as int64) - 1))) as success_orders_increment,
        case
            when $success_orders_delta(actual.success_orders, previous.success_orders) is null
                then $comments_dict['orders_info_no_hist'].tanker
            when $success_orders_delta(actual.success_orders, previous.success_orders) > 0
                then $comments_dict['orders_info_plus'].tanker
            when $success_orders_delta(actual.success_orders, previous.success_orders) < 0
                then $comments_dict['orders_info_minus'].tanker
            when $success_orders_delta(actual.success_orders, previous.success_orders) == 0
                then $comments_dict['orders_info_exact'].tanker
            else null
        end as text_orders_info,

        cast(100 - 100 * $rating_cohort_4 as int64) as bad_drivers_percentage,

        ------------- БЛОК НАШИ НАБЛЮДЕНИЯ, ТУТ ПИШЕМ ПРО ТО, ----------------------------
        ------------- КАК ЧТО-ТО ИЗМЕНИЛОСЬ ПО СРАВНЕНИЯ С ПРОШЛОЙ НЕДЕЛЕЙ -----------------

        ------------- ПРЕВЫШЕНИЯ СКОРОСТИ ------------------
        -- Решили, что хорошие комментарии оставляем только по скорости и только один

        -- if(
        --     ($speed_previous >= 1) and ($speed_actual == 0),
        --     true,
        --     null
        -- ) as quality_tag_highspeed_good_2,

        if(
            ($speed(previous.success_orders, previous.tag_high_speed) == 2) and ($speed(actual.success_orders, actual.tag_high_speed) == 1),
            true,
            null
        ) as quality_tag_highspeed_good_1,
        if(
            ($speed(previous.success_orders, previous.tag_high_speed) == 2) and ($speed(actual.success_orders, actual.tag_high_speed) == 2),
            true,
            null
        ) as quality_tag_highspeed_bad_3,
        if(
            ($speed(previous.success_orders, previous.tag_high_speed) < 2) and ($speed(actual.success_orders, actual.tag_high_speed) == 2),
            true,
            null
        ) as quality_tag_highspeed_bad_2,
        if(
            ($speed(previous.success_orders, previous.tag_high_speed) <= 1) and ($speed(actual.success_orders, actual.tag_high_speed) == 1),
            true,
            null
        ) as quality_tag_highspeed_bad_1,

        ------------- ОТМЕНЫ ------------------
        -- Не пишем хороших комментов здесь, но закоменченный код пока оставим

        --, if($cancel_previous >= 1
        --    and $cancel_actual == 0
        --    and 1.0*previous.cancel_droveaway/previous.cancellations between 0.25 and 0.75
        --    , true, null) as quality_tag_cancel_good_2

        -- , if($cancel_previous == 2
        --    and $cancel_actual == 1
        --    and not (
        --    1.0*previous.cancel_droveaway/previous.cancellations > 0.75
        --    or 1.0*previous.cancel_droveaway/previous.cancellations < 0.25)
        --    , true, null) as quality_tag_cancel_good_1
        --actual.cancellations/actual.success_orders

        if(
            ($cancel(previous.success_orders, previous.cancellations) == 2) and ($cancel(actual.success_orders, actual.cancellations) == 2),
            true,
            null
        ) as quality_tag_cancel_bad_3,
        if(
            ((1.0 * actual.cancel_droveaway / actual.cancellations) between 0.25 and 0.75)
                and ($cancel(previous.success_orders, previous.cancellations) < 2)
                and ($cancel(actual.success_orders, actual.cancellations) == 2),
            true,
            null
        ) as quality_tag_cancel_bad_2,
        if(
            ((1.0 * actual.cancel_droveaway / actual.cancellations) between 0.25 and 0.75)
                and ($cancel(actual.success_orders, actual.cancellations) == 1),
            true,
            null
        ) as quality_tag_cancel_bad_1,

        --Не покупаю
        --, if($cancel_previous >= 1
        --    and $cancel_actual == 0
        --    and 1.0*previous.cancel_driverrequest/previous.cancellations > 0.75
        --    and 1.0*actual.cancel_driverrequest/actual.cancellations > 0.75
        --    , true, null) as quality_tag_cancel_driverrequest_good_2

        --, if($cancel_previous ==2
        --    and $cancel_actual == 1
        --    and 1.0*previous.cancel_driverrequest/previous.cancellations > 0.75
        --    , true, null) as quality_tag_cancel_driverrequest_good_1
        --
        --, if(null
        --    , true, null) as quality_tag_cancel_driverrequest_bad_3
        -- We don't write this response

        if(
            ($cancel(previous.success_orders, previous.cancellations) <= 2)
                and ($cancel(actual.success_orders, actual.cancellations) == 2)
                and (1.0 * previous.cancel_driverrequest / previous.cancellations > 0.75)
                and (1.0 * actual.cancel_driverrequest / actual.cancellations > 0.75),
            true,
            null
        ) as quality_tag_cancel_driverrequest_bad_2,

        if(
            ($cancel(actual.success_orders, actual.cancellations) == 1)
                and (1.0 * previous.cancel_driverrequest / previous.cancellations > 0.75)
                and (1.0 * actual.cancel_driverrequest / actual.cancellations > 0.75),
            true,
            null
        ) as quality_tag_cancel_driverrequest_bad_1,

        --, if($cancel_previous >= 1
        --    and $cancel_actual == 0
        --    and 1.0*previous.cancel_droveaway/previous.cancellations > 0.75
        --    and 1.0*actual.cancel_droveaway/actual.cancellations > 0.75
        --    , true, null) as quality_tag_cancel_droveaway_good_2
        --, if($cancel_previous ==2
        --    and $cancel_actual == 1
        --    and 1.0*previous.cancel_droveaway/previous.cancellations > 0.75
        --    , true, null) as quality_tag_cancel_droveaway_good_1
        --, if(null
        --    , true, null) as quality_tag_cancel_droveaway_bad_3
        -- We don't write these responses

        if(
            ($cancel(previous.success_orders, previous.cancellations) != 2)
                and ($cancel(actual.success_orders, actual.cancellations) == 2)
                and (1.0 * previous.cancel_droveaway / previous.cancellations > 0.75)
                and (1.0 * actual.cancel_droveaway / actual.cancellations > 0.75),
            true,
            null
        ) as quality_tag_cancel_droveaway_bad_2,
        if(
            ($cancel(actual.success_orders, actual.cancellations) == 1)
                and (1.0 * previous.cancel_droveaway / previous.cancellations > 0.75)
                and (1.0 * actual.cancel_droveaway / actual.cancellations > 0.75),
            true,
            null
        ) as quality_tag_cancel_droveaway_bad_1,

        ------------- СГОВОР ------------------

        --, if($deal_previous >= 1 and $deal_actual == 0
        --    , true, null) as quality_tag_deal_good_2
        --, if($deal_previous == 2 and $deal_actual == 1
        --    , true, null) as quality_tag_deal_good_1
        -- $deal = ($success_orders, $tag_deal)
        if(
            ($deal(previous.success_orders, previous.tag_deal) == 2) and ($deal(actual.success_orders, actual.tag_deal) == 2),
            true,
            null
        ) as quality_tag_deal_bad_3,
        if(
            ($deal(previous.success_orders, previous.tag_deal) < 2) and ($deal(actual.success_orders, actual.tag_deal) == 2),
            true,
            null
        ) as quality_tag_deal_bad_2,
        if(
            $deal(actual.success_orders, actual.tag_deal) == 1,
            true,
            null
        ) as quality_tag_deal_bad_1

    from $key_driver_data as actual
    left join $previous_table as previous
        on actual.unique_driver_id == previous.unique_driver_id
);
-- select * from $with_tags;



--------- ФУНКЦИИ, ЧТОБЫ ПОДСЧИТАТЬ МАКСИМАЛЬНОЕ КОЛ-ВО ТЕГОВ --------------

$max_bad_tag = ($tag_baddriving, $tag_nochange, $tag_smellycar, $tag_carcondition, $tag_rudedriver) -> {
    return
        max_of(
            ($tag_baddriving ?? 0),
            ($tag_nochange ?? 0),
            ($tag_smellycar ?? 0),
            ($tag_carcondition ?? 0),
            ($tag_rudedriver ?? 0),
        )
};

$max_good_tag = ($tag_mood, $tag_comfortride, $tag_music, $tag_polite, $tag_clean, $tag_chat) -> {
    return
        max_of(
            ($tag_mood ?? 0),
            ($tag_comfortride ?? 0),
            ($tag_music ?? 0),
            ($tag_polite ?? 0),
            ($tag_clean ?? 0),
            ($tag_chat ?? 0),
        )
};

--------- ЗАКОНЧИЛИСЬ ФУНКЦИИ --------------



$with_tags_and_comments = (
    select
        a.*,

        -------- ЕСЛИ БЫЛО ЧТО-ТО ПЛОХО ИЛИ ХОРОШО ПО ТЕГАМ, ГОВОРИМ, ЧТО ИМЕННО -----------

        if(
            (country != 'Россия') or (Unicode::ToLower(cast(locale as Utf8)) != 'ru'),
            null,
            case
                -- этот кейс проставляет приоритетность!!!!!!!!!!!! действительно ли мы этого хотим?
                when success_orders < $do_not_show
                    then null

                when (
                    0
                    + if(tag_rudedriver > 0, 1, 0)
                    + if(tag_smellycar > 0, 1, 0)
                    + if(tag_carcondition > 0, 1, 0)
                    + if(tag_baddriving > 0, 1, 0)
                    + if(tag_nochange > 0, 1, 0)
                ) >= 3
                    then $comments_dict['many_bad_orders'].text

                when (tag_rudedriver >= 1) and (tag_rudedriver >= $max_bad_tag(tag_baddriving, tag_nochange, tag_smellycar, tag_carcondition, tag_rudedriver))
                    then $comments_dict['feedback_tag_rudedriver'].text
                when (tag_smellycar >= 1) and (tag_smellycar >= $max_bad_tag(tag_baddriving, tag_nochange, tag_smellycar, tag_carcondition, tag_rudedriver))
                    then $comments_dict['feedback_tag_smellycar'].text
                when (tag_carcondition >= 1) and (tag_carcondition >= $max_bad_tag(tag_baddriving, tag_nochange, tag_smellycar, tag_carcondition, tag_rudedriver))
                    then $comments_dict['feedback_tag_carcondition'].text
                when (tag_baddriving >= 1) and (tag_baddriving >= $max_bad_tag(tag_baddriving, tag_nochange, tag_smellycar, tag_carcondition, tag_rudedriver))
                    then $comments_dict['feedback_tag_baddriving'].text
                when (tag_nochange >= 1) and (tag_nochange >= $max_bad_tag(tag_baddriving, tag_nochange, tag_smellycar, tag_carcondition, tag_rudedriver))
                    then $comments_dict['feedback_tag_nochange'].text

                when (tag_mood >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    then $comments_dict['feedback_tag_mood'].text
                when (tag_polite >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    then $comments_dict['feedback_tag_polite'].text
                when (tag_music >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    then $comments_dict['feedback_tag_music'].text
                when (tag_clean >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    then $comments_dict['feedback_tag_clean'].text
                when (tag_chat >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    then $comments_dict['feedback_tag_chat'].text
                when (tag_comfortride >= $max_good_tag(tag_mood, tag_comfortride, tag_music, tag_polite, tag_clean, tag_chat))
                    -- Есть условие-антагонист: наличие в карточке плохой коммсы за скорость
                    and (quality_tag_highspeed_bad_3 is null)
                    and (quality_tag_highspeed_bad_2 is null)
                    and (quality_tag_highspeed_bad_1 is null)
                    -- Есть ещё одно условие-антагонист: получение любой коммсы по маяку за телеметрию, скорость или тег baddriving
                    and ((total_mayak_blocker_comms_count ?? 0) == 0)
                    -- вот только тогда ты получаешь хорошую коммсу за плавный стиль вождения
                        then $comments_dict['feedback_tag_comfortride'].text

                when coalesce(
                    -- положительные
                    tag_chat,
                    tag_clean,
                    tag_music,
                    tag_comfortride,
                    tag_polite,
                    tag_mood,
                    -- отрицательные
                    tag_rudedriver,
                    tag_nochange,
                    tag_baddriving,
                    tag_smellycar,
                    tag_carcondition
                ) is null
                    -- почему именно no good orders?
                    then $comments_dict['no_good_orders'].text
                else null
            end
        ) as message_feedback,

        -------- ПИШЕМ СОВЕТ ПО ИТОГАМ РАЗДЕЛА "НАШИ НАБЛЮДЕНИЯ" -----------

        if(
            (country != 'Россия') or (Unicode::ToLower(cast(locale as Utf8)) != 'ru'),
            null,
            case
                -- этот кейс проставляет приоритетность!!!!!!!!!!!! действительно ли мы этого хотим?
                when success_orders < $do_not_show
                    then null
                when quality_tag_cancel_bad_3
                    then $comments_dict['observations_cancel_bad'].text
                when quality_tag_cancel_bad_2
                    then $comments_dict['observations_cancel_bad'].text
                when quality_tag_cancel_bad_1
                    then $comments_dict['observations_cancel_bad'].text
                when quality_tag_cancel_droveaway_bad_2
                    then $comments_dict['observations_cancel_droveaway_bad'].text
                when quality_tag_cancel_droveaway_bad_1
                    then $comments_dict['observations_cancel_droveaway_bad'].text
                when quality_tag_cancel_driverrequest_bad_2
                    then $comments_dict['observations_cancel_driverrequest_bad'].text
                when quality_tag_cancel_driverrequest_bad_1
                    then $comments_dict['observations_cancel_driverrequest_bad'].text
                when quality_tag_highspeed_good_1
                    then $comments_dict['observations_highspeed_good'].text
                when quality_tag_highspeed_bad_3
                    then $comments_dict['observations_highspeed_bad'].text
                when quality_tag_highspeed_bad_2
                    then $comments_dict['observations_highspeed_bad'].text
                when quality_tag_highspeed_bad_1
                    then $comments_dict['observations_highspeed_bad'].text
                when quality_tag_deal_bad_3
                    then $comments_dict['observations_deal_bad'].text
                when quality_tag_deal_bad_2
                    then $comments_dict['observations_deal_bad'].text
                when quality_tag_deal_bad_1
                    then $comments_dict['observations_deal_bad'].text
                else
                    null
            end
        ) as message_observations

    from $with_tags as a
);
-- select * from $with_tags_and_comments;



--------- ДОБАВЛЯЕМ ХОРОШИЕ КОММЕНТЫ ОТ ПОЛЬЗОВАТЕЛЕЙ ------------------

$comments = (
    select
        unique_driver_id,
        cast(top_by('«' || unwrap(String::Strip(rating_comments)) || '»', local_order_dt, 3)[0] as string) as comment_value_1,
        cast(top_by('«' || unwrap(String::Strip(rating_comments)) || '»', local_order_dt, 3)[1] as string) as comment_value_2,
        cast(top_by('«' || unwrap(String::Strip(rating_comments)) || '»', local_order_dt, 3)[2] as string) as comment_value_3,
    from
        $comments_path
    where true
        and (status == 'Потенциально хороший')
        and (resolution == '5')
    group by
        unique_driver_id
);
-- select * from $comments;

$output_all = (
    select
        metrics.*,

        -- Хорошие комментарии от пользователей, зачем-то есть еще поля с датами, пусть будут
        comment_value_1,comment_value_2,comment_value_3,
        if(comment_value_1 is null, null, '') as comment_date_1,
        if(comment_value_2 is null, null, '') as comment_date_2,
        if(comment_value_3 is null, null, '') as comment_date_3,

        -- длина для слайда с комментами -- влезет или не влезет на картинку?
        case when comment_value_1 is not null
            then case when comment_value_2  is not null
                then case when comment_value_3 is not null
                    then  len(comment_value_1 || '\n\n' || comment_value_2  || '\n\n' || comment_value_3)
                else len(comment_value_1 || '\n\n' || comment_value_2) end
            else len(comment_value_1) end
        else null end as comment_length,

        -- Здесь проставляются флаги наличия разных блоков и заголовков
        if(
            coalesce(
                quality_tag_highspeed_good_1,
                quality_tag_highspeed_bad_3,
                quality_tag_highspeed_bad_2,
                quality_tag_highspeed_bad_1,
                quality_tag_cancel_bad_3,
                quality_tag_cancel_bad_2,
                quality_tag_cancel_bad_1,
                quality_tag_cancel_droveaway_bad_2,
                quality_tag_cancel_droveaway_bad_1,
                quality_tag_cancel_driverrequest_bad_2,
                quality_tag_cancel_driverrequest_bad_1,
                quality_tag_deal_bad_3,
                quality_tag_deal_bad_2,
                quality_tag_deal_bad_1,
            ) is null,
            null,
            true
        ) as quality_observations_title,

        -- if(a.title like '%title', true, null) as quality_title,

        -- if(a.text_good_orders like '%no_tips', true, null) as quality_good_tags_no_tips,
        -- if(a.text_good_orders like '%with_tips', true, null) as quality_good_tags_with_tips,
        if(text_good_orders like '%tips_only', true, null) as quality_good_tags_tips_only,

        -- if(a.feedback_title like '%no_bad_orders', true, null) as quality_no_bad_orders_text,
        if(feedback_title like '%title', true, null) as quality_feedback_title,

        if(tag_rudedriver is null, null, true) as quality_tag_rudedriver,
        if(tag_smellycar is null, null, true) as quality_tag_smellycar,
        if(tag_polite is null, null, true) as quality_tag_polite,
        if(tag_notcute is null, null, true) as quality_tag_notcute,
        if(tag_nochange is null, null, true) as quality_tag_nochange,
        if(tag_music is null, null, true) as quality_tag_music,
        if(tag_mood is null, null, true) as quality_tag_mood,
        if(tag_comfortride is null, null, true) as quality_tag_comfortride,
        if(tag_clean is null, null, true) as quality_tag_clean,
        if(tag_chat is null, null, true) as quality_tag_chat,
        if(tag_carcondition is null, null, true) as quality_tag_carcondition,
        if(tag_baddriving is null, null, true) as quality_tag_baddriving,
        if((bad_order_report is null) and (text_not_enough_orders is null), true, null) as quality_tag_no_bad_orders,

        -- ссылка на картинку для экранчика с отзывами
        'https://static.rostaxi.org/img/achievments.png' as image_url

    from $with_tags_and_comments as metrics

    left join $comments as comments
        on metrics.unique_driver_id == comments.unique_driver_id
);
-- select * from $output_all;



$helping_hand_all_time_trips = (
    select
        udid,
        count(*) as all_time_trips,
    from
        range(`//home/taxi-dwh/summary/dm_order`, substring($helping_hand_start_date, 0, 7))
    where true
        and success_order_flg
        and if(order_tariff in ('suv', 'premium_suv'), true, false)
        and (substring(local_order_dttm, 0, 10) between $helping_hand_start_date and $end_day)
        -- and (substring(local_order_dttm, 0, 10) between $start_day and $end_day)
    group by
        unique_driver_id as udid
);

$helping_hand_recent_trips = (
    select
        udid,
        count(*) as recent_trips,
    from
        range(`//home/taxi-dwh/summary/dm_order`, substring($helping_hand_start_date, 0, 7))
    where true
        and success_order_flg
        and if(order_tariff in ('suv', 'premium_suv'), true, false)
        -- and (substring(local_order_dttm, 0, 10) between $helping_hand_start_date and $end_day)
        and (substring(local_order_dttm, 0, 10) between $start_day and $end_day)
    group by
        unique_driver_id as udid
);

$mystery_check =
    select
        unique_driver_id
        ,max(report_link_1) as report_link_1
        ,max(report_link_2) as report_link_2
        ,max(report_link_3) as report_link_3
        ,substring(max(utc_order_dttm_1),8,2) ||'.' ||  substring(max(utc_order_dttm_1),5,2) || '.' || substring(max(utc_order_dttm_1),0,4) as mystery_utc_order_dttm_1
        ,substring(max(utc_order_dttm_2),8,2) ||'.' ||  substring(max(utc_order_dttm_2),5,2) || '.' ||  substring(max(utc_order_dttm_2),0,4) as mystery_utc_order_dttm_2
        ,substring(max(utc_order_dttm_3),8,2) ||'.' ||  substring(max(utc_order_dttm_3),5,2) || '.' ||  substring(max(utc_order_dttm_3),0,4) as mystery_utc_order_dttm_3
    from (
            select
                check_number
                , report_link
                , utc_order_dttm
                , unique_driver_id
                , if(check_number=1, report_link) as report_link_1
                , if(check_number=2, report_link) as report_link_2
                , if(check_number=3, report_link) as report_link_3
                , if(check_number=1, utc_order_dttm) as utc_order_dttm_1
                , if(check_number=2, utc_order_dttm) as utc_order_dttm_2
                , if(check_number=3, utc_order_dttm) as utc_order_dttm_3
            from (
                select
                    `action`,
                    `driver_uuid`,
                    `inspection_id`,
                    `order_id`,
                    `report_link`,
                    `unique_driver_id`,
                    `utc_order_dttm`,
                    row_number() over w as check_number
                from `//home/taxi-dwh/summary/dm_inspection_impact/dm_inspection_impact`
                where
                    substring(utc_order_dttm,0,10) between $daysago180  and $today_str
                window w as (partition by unique_driver_id order by utc_order_dttm desc)
            )
        where check_number <= 3
        )
    group by unique_driver_id
;

$output_all_w_helping_hand = (
    select
        data.*,

        case
            when (recent.recent_trips is null)
                then null
            when (recent.recent_trips == 1)
                then null
            else
                recent.recent_trips
        end as helping_hand_several_value,

        case
            when (recent.recent_trips is null)
                then null
            when (recent.recent_trips == 1)
                then null
            else
                'helping_hand_several_text'
        end as helping_hand_several_text,

        case
            when (recent.recent_trips is null)
                then null
            when (recent.recent_trips == 1)
                then 'helping_hand_one_text'
            else
                null
        end as helping_hand_one_text,

        case
            when (recent.recent_trips is null)
                then null
            when (recent.recent_trips == 1)
                then all_time.all_time_trips
            else
                all_time.all_time_trips
        end as helping_hand_value,

        report_link_1, report_link_2, report_link_3
        ,mystery_utc_order_dttm_1, mystery_utc_order_dttm_2, mystery_utc_order_dttm_3 --- тайник проверки

    from
        $output_all as data
    left join
        $helping_hand_recent_trips as recent
        on data.unique_driver_id == recent.udid
    left join
        $helping_hand_all_time_trips as all_time
        on data.unique_driver_id == all_time.udid
    left join
        $mystery_check as check
        on data.unique_driver_id = check.unique_driver_id
);


insert into $next_table
with truncate
    select
        true as quality_title,
        cast(a.helping_hand_several_value as Uint64) as helping_hand_several_value,
        cast(a.helping_hand_value as Uint64) as helping_hand_value,
        a.* without a.feedback_title, a.helping_hand_several_value, a.helping_hand_value
    from
        $output_all_w_helping_hand as a
    where true
        --and (success_orders >= $do_not_show)
;


commit;


insert into $actual
with truncate
    select *
    from $next_table
;



'''


# In[ ]:


def main():
    yql_config = json.load(open(os.path.expanduser("~") + "/mylib_config.json"))
    token = yql_config['quality_robot_token']
    client = YqlClient(token=token)
    df = gdocs_helper.read_table(spreadsheet_id='1tyhPo6BxSgKumKhD8CtvibOW_RtxHvzUMvZNxymLmBc',
                                 range_name='Config - DO NOT TOUCH')
    df.to_csv('config.txt', encoding='utf-8', sep=';', index=False, header=False)
    request = client.query(main_query.decode('utf8'), syntax_version=1)
    request.attach_file(os.path.realpath('config.txt'), 'config.txt')
    request.run()

    print("Successful:", request.get_results().is_success)
    print("Errors:", request.errors)

    # мониторинг запроса в телеграм
    if not request.get_results().is_success:
        bot.send_message(chat=creator, message='Карточка качества упаля!\n' + str(request.errors[0]))


# In[ ]:


if __name__ == '__main__':
    main()


# In[ ]:

bot.send_message(chat=creator, message='Карточка качества собралась!\n')
# script_alarm_bot.send_message(justicewisdom, 'Карточка качества создалась!')

