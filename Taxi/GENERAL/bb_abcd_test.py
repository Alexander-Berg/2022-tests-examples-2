# coding: utf-8

import pandas as pd
import numpy as np
import time
import requests
from mylib import hahn, ensure_unicode
from datetime import date, timedelta

hahn.base_path = 'home/taxi-analytics/kvdavydova/{}'

today = str(pd.datetime.now().date())
print today

yesterday = str(date.today() - timedelta(1))
print yesterday

# Скорринг водителей по окну в поездках и днях

hahn("""
USE hahn;
PRAGMA SimpleColumns;
pragma yt.InferSchema;

$today = DateTime::ToDate(YQL::Now());
$date_from = DateTime::ToDate(YQL::Now() - DateTime::FromDays(60));         -- смотрим за последние 60 дней
$month_from = String::SplitToList(DateTime::ToString(YQL::Now() - DateTime::FromDays(60)), '-'){{0}} || '-' || String::SplitToList(DateTime::ToString(YQL::Now() - DateTime::FromDays(60)), '-'){{1}};
$orders_window = (SELECT orders_window FROM [home/taxi-analytics/mminnekaev/BigBrother2/criteria_window]);
$days_window = (SELECT days_window FROM [home/taxi-analytics/mminnekaev/BigBrother2/criteria_window]);
$days_window_start_dt = DateTime::ToDate(DateTime::FromString($today) - DateTime::FromDays($days_window));

$days_7_ago = DateTime::ToDate(DateTime::FromString($today) - DateTime::FromDays(7));         -- окно в 7 дней для определения тарифа

$cities = (
SELECT distinct city,
city_start_date
FROM [home/taxi-analytics/kvdavydova/big_brother/criteria_config_abcd] 
);


-- 1. Нумеруем заказы с оценками по водителям
$enumerated_orders = (
SELECT qm.driver_license as driver_license
    ,row_number() over w as num
    ,qm.utc_order_dttm as utc_order_dttm
    ,qm.order_id as order_id
    ,qm.driver_id as driver_id
    ,qm.city as city
    ,qm.rating_value as rating_value
    ,qm.order_tariff as order_tariff
    ,qm.car_number as car_number
    ,tag_badroute
    ,tag_carcondition
    ,tag_driverlate
    ,tag_smellycar
    ,tag_notrip
    ,tag_nochange
    ,tag_rudedriver
    ,cancel_driverrequest
    ,cancel_droveaway
    ,cancel_longwait
    ,call_passenger
    ,smoking
    ,id_24 ?? 0 as id_24  --"Курит в салоне"
    ,id_26 ?? 0 as id_26  --"Платная отмена по вине водителя"
    ,id_29 ?? 0 as id_29  --"Водитель позвонил и попросил отменить заказ"
    ,id_38 ?? 0 as id_38   --"Неприятный запах в салоне (табак/пот/духи)"
    ,id_39 ?? 0 as id_39  --"Нарушает ПДД"
    ,id_50 ?? 0 as id_50  --"Грубый водитель"
FROM [home/taxi-analytics/mminnekaev/quality_rate/quality_metrics] as qm
LEFT JOIN RANGE([home/taxi_ml/lichi/comments_analyzed_business_analytics/comments_processed], $date_from) as ml
    ON qm.order_id = ml.order_id
JOIN $cities as c
    ON qm.city = c.city
left join range([home/taxi-analytics/kvdavydova/big_brother/action_history], $month_from) as hist
    on qm.driver_license = hist.driver_license
WHERE qm.utc_order_dt >= $date_from
    and unreliable_feedback = 0
    and qm.driver_license <> ''
    and qm.utc_order_dt >= c.city_start_date
    and unreliable_feedback == 0
    and (qm.utc_order_dttm < hist.period_last_order_dttm or qm.utc_order_dttm > hist.action_datetime or hist.driver_license is null)
WINDOW w as (PARTITION BY qm.driver_license ORDER BY qm.utc_order_dttm desc)
);

-- 1.1. Ищем макс тариф водителя
$driver_tariff = (
SELECT
    driver_license,
    max_by(order_tariff, h.level) as max_tariff, -- максимальный тариф по которому проехал водитель
    max(h.level) as max_tariff_level
FROM $enumerated_orders as o
LEFT JOIN [home/taxi-analytics/mminnekaev/BigBrother2/tariff_hierarchy] as h
    ON o.order_tariff = h.tariff
WHERE utc_order_dttm >= $days_7_ago
GROUP BY o.driver_license as driver_license
);


-- 2. Считаем тэги за N последних заказов
INSERT INTO [home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_scorring_order_window/{dt}]
WITH TRUNCATE
SELECT
    driver_license
    ,$today as dt
    ,Yson::Serialize(Yson::From(AsStruct(
        (
        count_if(tag_badroute >= 1), 
        min_by(order_id, if(tag_badroute >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_badroute >= 1, 1, 999999) * num)
        ) as badroute
        ,(
        count_if(tag_carcondition >= 1),
        min_by(order_id, if(tag_carcondition >= 1, 1, 999999)  * num),
        min_by(car_number, if(tag_carcondition >= 1, 1, 999999)  * num)
        ) as carcondition
        ,(
        count_if(tag_driverlate >= 1),
        min_by(order_id, if(tag_driverlate >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_driverlate >= 1, 1, 999999) * num)
        ) as driverlate
        ,(
        count_if(tag_smellycar + id_38 >= 1),
        min_by(order_id, if(tag_smellycar + id_38 >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_smellycar + id_38 >= 1, 1, 999999) * num)
        ) as smellycar
        ,(
        count_if(tag_notrip >= 1),
        min_by(order_id, if(tag_notrip >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_notrip >= 1, 1, 999999) * num)
        ) as notrip
        ,(
        count_if(tag_nochange >= 1), 
        min_by(order_id, if(tag_nochange >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_nochange >= 1, 1, 999999) * num)
        ) as nochange
        ,(
        count_if(tag_rudedriver + id_50 >= 1),
        min_by(order_id, if(tag_rudedriver + id_50 >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_rudedriver + id_50 >= 1, 1, 999999) * num)
        ) as rude
        ,(
        count_if(smoking + id_24 >= 1),
        min_by(order_id, if(smoking + id_24 >= 1, 1, 999999) * num),
        min_by(car_number, if(smoking + id_24 >= 1, 1, 999999) * num)
        ) as smoking
        ,(
        count_if(id_39 >= 1),
        min_by(order_id, if(id_39 >= 1, 1, 999999) * num),
        min_by(car_number, if(id_39 >= 1, 1, 999999) * num)
        ) as PDD
        ,(
        count_if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1),
        min_by(order_id, if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1, 1, 999999) * num),
        min_by(car_number, if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1, 1, 999999) * num)
        ) as cancel
        ,(
        count(order_id),
        min_by(order_id, num),
        min_by(car_number, num)
        ) as orders
    ))) as values
    ,max_by(utc_order_dttm, num) as window_start_dttm
    ,min_by(utc_order_dttm, num) as window_end_dttm
    ,min_by(driver_id, num) as last_driver_id
    ,min_by(order_id, num) as last_order_id
    ,min_by(city, num) as last_city
    ,min_by(max_tariff, num) ?? 'econom' as max_tariff
    ,min_by(max_tariff_level, num) ?? 30 as max_tariff_level
    ,min_by(car_number, num) as car_number
FROM $enumerated_orders as o
LEFT JOIN $driver_tariff as t
    ON o.driver_license = t.driver_license
WHERE num <= $orders_window
GROUP BY
    o.driver_license as driver_license
;


-- 3. Считаем тэги за M последних дней
INSERT INTO [home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_scorring_time_window/{dt}]
WITH TRUNCATE
SELECT
    driver_license
    ,$today as dt
    ,Yson::Serialize(Yson::From(AsStruct(
        (
        count_if(tag_badroute >= 1), 
        min_by(order_id, if(tag_badroute >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_badroute >= 1, 1, 999999) * num)
        ) as badroute
        ,(
        count_if(tag_carcondition >= 1),
        min_by(order_id, if(tag_carcondition >= 1, 1, 999999)  * num),
        min_by(car_number, if(tag_carcondition >= 1, 1, 999999)  * num)
        ) as carcondition
        ,(
        count_if(tag_driverlate >= 1),
        min_by(order_id, if(tag_driverlate >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_driverlate >= 1, 1, 999999) * num)
        ) as driverlate
        ,(
        count_if(tag_smellycar + id_38 >= 1),
        min_by(order_id, if(tag_smellycar + id_38 >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_smellycar + id_38 >= 1, 1, 999999) * num)
        ) as smellycar
        ,(
        count_if(tag_notrip >= 1),
        min_by(order_id, if(tag_notrip >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_notrip >= 1, 1, 999999) * num)
        ) as notrip
        ,(
        count_if(tag_nochange >= 1), 
        min_by(order_id, if(tag_nochange >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_nochange >= 1, 1, 999999) * num)
        ) as nochange
        ,(
        count_if(tag_rudedriver + id_50 >= 1),
        min_by(order_id, if(tag_rudedriver + id_50 >= 1, 1, 999999) * num),
        min_by(car_number, if(tag_rudedriver + id_50 >= 1, 1, 999999) * num)
        ) as rude
        ,(
        count_if(smoking + id_24 >= 1),
        min_by(order_id, if(smoking + id_24 >= 1, 1, 999999) * num),
        min_by(car_number, if(smoking + id_24 >= 1, 1, 999999) * num)
        ) as smoking
        ,(
        count_if(id_39 >= 1),
        min_by(order_id, if(id_39 >= 1, 1, 999999) * num),
        min_by(car_number, if(id_39 >= 1, 1, 999999) * num)
        ) as PDD
        ,(
        count_if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1),
        min_by(order_id, if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1, 1, 999999) * num),
        min_by(car_number, if(cancel_driverrequest + cancel_droveaway + id_26 + id_29 >= 1, 1, 999999) * num)
        ) as cancel
        ,(
        count(order_id),
        min_by(order_id, num),
        min_by(car_number, num)
        ) as orders
    ))) as values
    ,max_by(utc_order_dttm, num) as window_start_dttm
    ,min_by(utc_order_dttm, num) as window_end_dttm
    ,min_by(driver_id, num) as last_driver_id
    ,min_by(order_id, num) as last_order_id
    ,min_by(city, num) as last_city
    ,min_by(max_tariff, num) ?? 'econom' as max_tariff
    ,min_by(max_tariff_level, num) ?? 30 as max_tariff_level
FROM $enumerated_orders as o
LEFT JOIN $driver_tariff as t
    ON o.driver_license = t.driver_license
WHERE utc_order_dttm >= $days_window_start_dt
GROUP BY
    o.driver_license as driver_license
""".format(dt = yesterday))

# Собираем для коммуникации водителей (критерий по окну в поездках)

hahn("""
USE hahn;
PRAGMA SimpleColumns;

$today = '{dt}';

--------------------------------------------------------------------------------
$criteria_raw = (
select 
    city,
    city_eng,
    'RU' as language,
    Cast(test_share as Int64) as test_share,
    a.tariff as tariff,
    level,
    comminucation_category as communication_category,
    Yson::ConvertToDict(values) as c
from 
    [home/taxi-analytics/kvdavydova/big_brother/criteria_config_abcd] as a
join 
    [home/taxi-analytics/mminnekaev/BigBrother2/tariff_hierarchy] as b 
on 
    a.tariff = b.tariff
where 
    criteria_type = 'trips'
);

$criteria = (
SELECT city, city_eng, language, communication_category, tariff, level, test_share, c.0 as category, Yson::ConvertToInt64(c.1) as criteria
FROM $criteria_raw
FLATTEN BY c
);

-- select * from $criteria;

--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
$scorring_trips_window_raw = (
SELECT driver_license
    ,last_driver_id
    ,last_city
    ,max_tariff_level
    ,max_tariff
    ,Yson::ConvertToDict(values) as values
FROM RANGE([home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_scorring_order_window], $today, $today)
);

$scorring_trips_window = (
SELECT driver_license
    ,last_driver_id
    ,last_city
    ,max_tariff_level
    ,max_tariff
    ,values.0 as category
    ,Yson::ConvertToInt64(Yson::Serialize(values.1).0) as value
    ,Yson::ConvertToString(Yson::Serialize(values.1).1) as last_order
FROM $scorring_trips_window_raw
FLATTEN BY values
);
-- --------------------------------------------------------------------------------


INSERT INTO [home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_for_communication/{dt}] 
with truncate
SELECT 
    scor.driver_license as driver_license
    ,last_driver_id as driver_id
    ,unique_driver_id
    ,db_id || '_' || driver_uuid as db_id__uuid
    ,driver_phone
    ,driver_name
    ,city
    ,city_eng
    ,c.language as language
    ,case                                                                                               -- определяем тестовую/контрольную группу
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 20 then '1_feed'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 20 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 40 then '2_bigfeed'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 40 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 60 then '3_ivr'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 60 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 80 then '4_call'
        else '0_control'
    end as [group]
    ,$today as dt
    ,'BB_abcd_script' as script
    ,'trips' as criteria_type
    ,c.communication_category as type_of_influence
    ,scor.category as category
    ,scor.value as value
    ,scor.last_order as last_order
    --,message.message as text
    ,c.level as conf_tariff_level
    ,scor.max_tariff as max_tariff
    --,comm.communication as communication
FROM $scorring_trips_window as scor
JOIN $criteria as c
    ON scor.last_city = c.city
    and scor.category = c.category
JOIN [home/taxi-dwh/dds/dim_driver] as d
    ON scor.last_driver_id = d.driver_id
WHERE value >= criteria
and c.level <= scor.max_tariff_level
""".format(dt = yesterday))

# Собираем для коммуникации водителей (критерий по окну в днях)

hahn("""
USE hahn;
PRAGMA SimpleColumns;

$today = '{dt}';

--------------------------------------------------------------------------------
$criteria_raw = (
select 
    city,
    city_eng,
    'RU' as language,
    Cast(test_share as Int64) as test_share,
    a.tariff as tariff,
    level,
    comminucation_category as communication_category,
    Yson::ConvertToDict(values) as c
from 
    [home/taxi-analytics/kvdavydova/big_brother/criteria_config_abcd] as a
join 
    [home/taxi-analytics/mminnekaev/BigBrother2/tariff_hierarchy] as b 
on 
    a.tariff = b.tariff
where 
    criteria_type = 'days'
);

$criteria = (
SELECT city, city_eng, language, communication_category, test_share, tariff, level, c.0 as category, Yson::ConvertToInt64(c.1) as criteria
FROM $criteria_raw
FLATTEN BY c
);
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
$scorring_time_window_raw = (
SELECT driver_license
    ,last_driver_id
    ,last_city
    ,max_tariff_level
    ,max_tariff
    ,Yson::ConvertToDict(values) as values
FROM RANGE([home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_scorring_time_window], $today, $today)
);

$scorring_time_window = (
SELECT driver_license
    ,last_driver_id
    ,last_city
    ,values.0 as category
    ,max_tariff_level
    ,max_tariff
    ,Yson::ConvertToInt64(Yson::Serialize(values.1).0) as value
    ,Yson::ConvertToString(Yson::Serialize(values.1).1) as last_order
FROM $scorring_time_window_raw
FLATTEN BY values
);
--------------------------------------------------------------------------------


INSERT INTO [home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_for_communication/{dt}] 
SELECT 
    scor.driver_license as driver_license
    ,last_driver_id as driver_id
    ,unique_driver_id
    ,db_id || '_' || driver_uuid as db_id__uuid
    ,driver_phone
    ,driver_name
    ,city
    ,city_eng
    ,c.language as language
    ,case                                                                                               -- определяем тестовую/контрольную группу
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 20 then '1_feed'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 20 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 40 then '2_bigfeed'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 40 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 60 then '3_ivr'
        when Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 > 60 and Digest::MurMurHash(d.unique_driver_id || 'TAXIANALYTICS-4390') % 100 <= 80 then '4_call'
        else '0_control'
    end as [group]
    ,$today as dt
    ,'BB_abcd_script' as script
    ,'time' as criteria_type
    ,c.communication_category as type_of_influence
    ,scor.category as category
    ,scor.value as value
    ,scor.last_order as last_order
    --,message.message as text
    ,c.level as conf_tariff_level
    ,scor.max_tariff as max_tariff
    --,comm.communication as communication
FROM $scorring_time_window as scor
JOIN $criteria as c
    ON scor.last_city = c.city
    and scor.category = c.category
LEFT JOIN [home/taxi-dwh/dds/dim_driver] as d
    ON scor.last_driver_id = d.driver_id
WHERE value >= criteria
and c.level <= scor.max_tariff_level
""".format(dt = yesterday))

# Собираем таблички за день для разных видов коммуникации в соответвии с иерархиями причин и видов коммуникации

hahn('''
USE hahn;
use hahn;
PRAGMA SimpleColumns;
$date = '{dt}';
-- ищем максимальную по приоритету (1 - самый высорий приоритет) коммуникацию по каждому водителю
$max_driver_communication = (
select 
    a.driver_license as driver_license,
    max(a.type_of_influence) as type_of_influence,
    max_by(b.communication, a.type_of_influence) as communication
    -- max_by(b.type, a.type_of_influence) as type
from 
    [//home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_for_communication/{dt}] as a
join 
    [home/taxi-analytics/kvdavydova/big_brother/communication_hierarchy] as b
on 
    a.type_of_influence = b.type
    and a.max_tariff = b.tariff
group by 
    a.driver_license as driver_license
);
-- берем все причины с максимальной коммуникацией по каждому водителю
$ordered_by_communication = (
select 
    a.driver_license as driver_license,
    a.category as category,
    a.type_of_influence as type_of_influence,
    b.communication as communication, 
    a.db_id__uuid as db_id__uuid,
    a.last_order as last_order,
    a.driver_id as driver_id,
    a.driver_phone as driver_phone,
    a.group as group,
    a.city as city
from
    [//home/taxi-analytics/kvdavydova/big_brother/abcd/drivers_for_communication/{dt}] as a
join 
    $max_driver_communication as b
on 
    a.driver_license = b.driver_license
    and a.type_of_influence = b.type_of_influence
);
-- ищем максимальную причину по каждому водителю по ленте и другим видам
$max_reasons = (
select 
    a.driver_license as driver_license,
    max(b.priority) as priority,
    max_by(b.reason, b.priority) as reason,
    max_by(a.group, b.priority)
from 
    $ordered_by_communication as a
join 
    [home/taxi-analytics/kvdavydova/big_brother/reason_hierarchy] as b
on 
    a.category = b.reason
group by 
    a.driver_license as driver_license
);
-- берем максимальные по приоритету причины для коммуникаций по каждому водителю
$communications = (
select
    a.driver_license as driver_license,
    max_by(a.category, b.priority) as category,
    a.type_of_influence  as type_of_influence,
    a.communication as communication,
    max_by(a.db_id__uuid, b.priority) as db_id__uuid,
    max_by(a.last_order, b.priority) as last_order,
    max_by(a.driver_id, b.priority) as driver_id,
    max_by(a.driver_phone, b.priority) as driver_phone,
    max_by(a.city, b.priority) as city,
    max_by(a.group, b.priority) as group
from (select * from
    $ordered_by_communication
    where group != '0_control') as a
join 
    $max_reasons as b
on 
    a.driver_license = b.driver_license
    and a.category = b.reason
group by 
    a.driver_license as driver_license,
    a.type_of_influence  as type_of_influence,
    a.communication as communication
);   
$tmp = (
select 
    if(type_of_influence == '2',
    if(group == '1_feed', 'lenta',
    if(group == '3_ivr', 'call',
    if(group == '2_bigfeed', 'biglenta',
    if(group == '4_call', 'call_center', communication)))), communication) as communication,
    type_of_influence,
    driver_license,
    category,
    db_id__uuid,
    last_order,
    driver_id,
    driver_phone,
    city,
    group
from 
    $communications
);
$tmp = (
select
    a.*,
    message.message as text
from 
    $tmp as a
left join (select * from
    [home/taxi-analytics/kvdavydova/big_brother/messages]
    where city = 'default') as message
on 
    message.communication = if(a.communication == 'biglenta', 'lenta', a.communication)
    and a.category = message.reason
);
insert into 
    [home/taxi-analytics/kvdavydova/big_brother/communication/{dt}]
with truncate
select 
    *
from 
    [home/taxi-analytics/kvdavydova/big_brother/communication/{dt}]
union all
select 
    *
from 
    $tmp;
'''.format(dt = yesterday))
