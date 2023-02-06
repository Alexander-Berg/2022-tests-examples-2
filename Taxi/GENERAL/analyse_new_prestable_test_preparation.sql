use hahn;


PRAGMA library('analyse_new_prestable.sql');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

IMPORT analyse_new_prestable SYMBOLS $analyze_new_prestable;


$big_food_order_path = "{{big_food_order_path}}";
$big_food_order_revision_path = "{{big_food_order_revision_path}}";
$big_food_order_cancel_path = "{{big_food_order_cancel_path}}";
$taxi_order_path = "{{taxi_order_path}}";



$start_date = CurrentUtcDate(); 
$orders_start_date = $start_date - DateTime::IntervalFromDays(20);
$orders_start_date_str = cast($orders_start_date as String);


$big_food_order_table = $big_food_order_path||'/'||substring($orders_start_date_str,0,4)||'-01-01';


INSERT INTO $big_food_order_table WITH TRUNCATE
select 
    cast(user_id as String) as user_id,
    cast($orders_start_date + DateTime::IntervalFromDays(14) as String) as utc_created_dttm,
    IF(user_id < 1000, cast(user_id as Double), cast((user_id%5) as Double))  as cost_for_customer_lcy,
    'RUB' as currency_code,
    cast(user_id as Int64) as latest_revision_id,
    cast(user_id as Int64) as id,
    'superapp_ios' as application_platform,
    4 as status
from 
    (select 
        1 as user_id)
LIMIT 0
;


$big_food_order_revision_path_table = $big_food_order_revision_path||'/'||substring($orders_start_date_str,0,4)||'-01-01';

INSERT INTO $big_food_order_revision_path_table WITH TRUNCATE
select 
    cast(user_id as Int64) as id,
    cast(user_id as Int64) as order_id
from 
    (select 
        1 as user_id)
LIMIT 0 
;

$big_food_order_cancel_path_table = $big_food_order_cancel_path||'/'||substring($orders_start_date_str,0,4)||'-01-01';

INSERT INTO $big_food_order_cancel_path_table WITH TRUNCATE
select 
    cast(-1000 as Int64) as order_id,
    cast(-1000 as Int64) as reason_id
LIMIT 0 
;

$taxi_order_path_table = $taxi_order_path||'/'||substring($orders_start_date_str,0,7)||'-01';

INSERT INTO $taxi_order_path_table WITH TRUNCATE 
SELECT 
    cast(user_id as String) as user_phone_id,
    cast($orders_start_date + DateTime::IntervalFromDays(14) as string) as utc_order_created_dttm,
    cast(IF(user_id < 1000, cast(user_id as Double), cast((user_id%5) as Double)) as Double) as tariff_cost_w_discount,
    'RUB' as currency_code,
    NULL as corp_client_id,
    True as success_order_flg
from 
    (select 
        1 as user_id)
LIMIT 0 
;
