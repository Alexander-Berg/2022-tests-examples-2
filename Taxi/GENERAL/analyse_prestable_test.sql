use hahn;

PRAGMA library('analyse_prestable.sql');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

IMPORT analyse_prestable SYMBOLS $update_resolutions;

$campaign_log_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_campaign_log";
$settings_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_settings_log";
$efficiency_segments_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_eff_segm";
$user_phone_path =  "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_user_phone_path";
$users_bigfood_path =  "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_users_bigfood_path";
$campaign_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_prestable_campaign_path";
$currency_rate_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_currency_rate";
$big_food_order_cancel_reason_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_big_food_order_cancel_reason";

$experiments_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_prestable_expetiments";
$taxi_order_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_taxi_order";
$big_food_order_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_big_food_orders";
$big_food_order_revision_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_big_food_order_revision";
$big_food_order_cancel_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/analyze_new_prestable_big_food_order_cancel";
$atlas_orders_path = "{{atlas_orders_path}}";
$test_results = "{{test_results}}";

$call_listgen = Python::listgen(Callable<(Int64?, Int64?)->List<Int64?>>, 
@@

def listgen(n_start, n_end):
    return [i for i in range(n_start, n_end)]
    
@@);


$start_date = CurrentUtcDate() - DateTime::IntervalFromDays(14);
$comms_start_date_str = cast($start_date as String);
$orders_start_date = $start_date - DateTime::IntervalFromDays(30);
$orders_start_date_str = cast($orders_start_date as String);

INSERT INTO $campaign_log_path WITH TRUNCATE 
select 
    cast(1 as string?) as campaign_id,
    cast('create_prestable_sc1_test1' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'prestable_analysis' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() - DateTime::IntervalFromDays(3) as Datetime?) as last_status_update,
    cast(NULL as Datetime?) as resolution_time,
    '' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL
select 
    cast(2 as string?) as campaign_id,
    cast('create_prestable_sc1_test2' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'prestable_analysis' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() - DateTime::IntervalFromDays(3) as Datetime?) as last_status_update,
    cast(NULL as Datetime?) as resolution_time,
    '' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL
select 
    cast(3 as string?) as campaign_id,
    cast('create_prestable_sc1_test3' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'prestable_analysis' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() - DateTime::IntervalFromDays(3) as Datetime?) as last_status_update,
    cast(NULL as Datetime?) as resolution_time,
    '' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL
select 
    cast(4 as string?) as campaign_id,
    cast('create_prestable_sc1_test4' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'prestable_analysis' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() - DateTime::IntervalFromDays(3) as Datetime?) as last_status_update,
    cast(NULL as Datetime?) as resolution_time,
    '' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL
select 
    cast(5 as string?) as campaign_id,
    cast('create_prestable_sc1_test3' as string?) as group_name,
    cast('channel_sc3' as string?) as channel_type,
    'resolved' as status,
    cast(False as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_prestable_sc1_test1' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
;

insert into $settings_path WITH TRUNCATE 
select
    campaign_id,
    group_name,
    channel_type,
    'User' as entity_type,
    CurrentUtcDateTime() as upd_time,
    20000 as prestable_size,
    0.5 as pvalue_threshold,
    DateTime::IntervalFromDays(cast(campaign_id as Int32)) as resolution_timeout
from 
    $campaign_log_path
;




INSERT INTO $efficiency_segments_path WITH TRUNCATE 
(select 
    campaign_id,
    channel_type,
    cast(user_id as String?) as entity_id,
    entity_type,
    experiment_id,
    group_name,
    if(user_id > 100 and user_id <= 105, True, False) as is_glob_control_prestable,
    if(user_id <= 115 and user_id >= 105, True, False) as is_loc_control_prestable,   
    if(user_id < 100, True, False) as is_test_prestable,
    status,
    upd_time
from 
    (select 
        cast(1 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_prestable_sc1_test1" as string?) as group_name,
        cast('prestable_analysis' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time,
        $call_listgen(1, 1000) as user_id)
    FLATTEN LIST BY user_id)
UNION ALL 
(select 
    campaign_id,
    channel_type,
    cast(user_id as String?) as entity_id,
    entity_type,
    experiment_id,
    group_name,
    if(user_id > 1100 and user_id <= 1105, True, False) as is_glob_control_prestable,
    if(user_id <= 1115 and user_id >= 1105, True, False) as is_loc_control_prestable,   
    if(user_id < 1100, True, False) as is_test_prestable,
    status,
    upd_time
from 
    (select 
        cast(2 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_prestable_sc1_test2" as string?) as group_name,
        cast('prestable_analysis' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time,
        $call_listgen(1000, 2000) as user_id)
    FLATTEN LIST BY user_id
)
UNION ALL 
(select 
    campaign_id,
    channel_type,
    cast(user_id as String?) as entity_id,
    entity_type,
    experiment_id,
    group_name,
    if(user_id > 2100 and user_id <= 2105, True, False) as is_glob_control_prestable,
    if(user_id <= 2115 and user_id >= 2105, True, False) as is_loc_control_prestable,   
    if(user_id < 2100, True, False) as is_test_prestable,
    status,
    upd_time
from 
    (select 
        cast(3 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_prestable_sc1_test2" as string?) as group_name,
        cast('prestable_analysis' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time,
        $call_listgen(2000, 3000) as user_id)
    FLATTEN LIST BY user_id
);
commit;

INSERT INTO $user_phone_path WITH TRUNCATE 
(
    select 
        entity_id as phone_pd_id,
        entity_id as user_phone_id
    from 
        $efficiency_segments_path
);

INSERT INTO $users_bigfood_path WITH TRUNCATE 
(
    select 
        entity_id as user_id,
        entity_id as user_phone_pd_id
    from 
        $efficiency_segments_path
);


$start_date = CurrentUtcDate() - DateTime::IntervalFromDays(4); 
$comms_start_date_str = cast($start_date as String);
$orders_start_date = $start_date - DateTime::IntervalFromDays(20);
$orders_start_date_str = cast($orders_start_date as String);

$experiments_table = $experiments_path||'/'||$comms_start_date_str||'_cm';

INSERT INTO $experiments_table WITH TRUNCATE
select 
    cast(user_id as String) as unic_obj_id,
    cast($start_date + DateTime::IntervalFromDays(2) as String) as creation_time,
    'exp'||cast((cast(user_id as Int64) / 1000) + 1 as String) as experiment_id,
    'channel_sc1' as channel,
    'create_prestable_sc1_test1' as group_name,
    Yson::Serialize(Yson::From(ToDict([
                ('global_control', cast(0 as String)),
                ('communication_status', cast('test' as String)),
                ('control', cast('0' as String)
                )]
                ))) as properties
from 
    (select 
        $call_listgen(1, 5000) as user_id)
    FLATTEN LIST BY user_id
;

INSERT INTO $campaign_path WITH TRUNCATE 
SELECT 
    1 as id,
    'exp1' as ticket
UNION ALL
SELECT 
    2 as id,
    'exp2' as ticket
UNION ALL
SELECT 
    3 as id,
    'exp3' as ticket
UNION ALL
SELECT 
    4 as id,
    'exp4' as ticket
UNION ALL
SELECT 
    5 as id,
    'exp5' as ticket
;


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
        $call_listgen(1, 2000) as user_id)
    FLATTEN LIST BY user_id
;

$big_food_order_revision_path_table = $big_food_order_revision_path||'/'||substring($orders_start_date_str,0,4)||'-01-01';

INSERT INTO $big_food_order_revision_path_table WITH TRUNCATE
select 
    cast(user_id as Int64) as id,
    cast(user_id as Int64) as order_id
from 
    (select 
        $call_listgen(1, 2000) as user_id)
    FLATTEN LIST BY user_id
;

$big_food_order_cancel_path_table = $big_food_order_cancel_path||'/'||substring($orders_start_date_str,0,4)||'-01-01';

INSERT INTO $big_food_order_cancel_path_table WITH TRUNCATE
select 
    cast(-1000 as Int64) as order_id,
    cast(-1000 as Int64) as reason_id
;

INSERT INTO $big_food_order_cancel_reason_path WITH TRUNCATE
select 
    cast(-2000 as Int64) as id,
    cast(-2000 as Int64) as group_id
;


$taxi_order_path_table = $taxi_order_path||'/'||substring($orders_start_date_str,0,7)||'-01';

INSERT INTO $taxi_order_path_table WITH TRUNCATE 
SELECT 
    cast(user_id as String) as user_phone_id,
    cast($orders_start_date + DateTime::IntervalFromDays(14) as string) as utc_order_created_dttm,
    IF(user_id < 1000, cast(user_id as Double), cast((user_id%5) as Double)) as tariff_cost_w_discount,
    'RUB' as currency_code,
    NULL as corp_client_id,
    True as success_order_flg
from 
    (select 
        $call_listgen(1, 2000) as user_id)
    FLATTEN LIST BY user_id  
;

INSERT INTO $currency_rate_path WITH TRUNCATE 
(
Select
    'RUB' as source_cur,
    'RUB' as target_cur,
    cast(1 as Double) as rate,
    cast(CurrentUtcDate() - DateTime::IntervalFromDays(2) as String) as `date`
);
COMMIT;


$resolution_timeout = DateTime::IntervalFromDays(3);
$comm_status_filter = ('test');


DO $update_resolutions(
                      $campaign_log_path,
                      $efficiency_segments_path,
                      $experiments_path,
                      $comm_status_filter,
                      $campaign_path,
                      $user_phone_path,
                      $users_bigfood_path,
                      $big_food_order_path,
                      $big_food_order_revision_path,
                      $big_food_order_cancel_path,
                      $big_food_order_cancel_reason_path,
                      $taxi_order_path,
                      $currency_rate_path,
                      $dwh_supply_hours_path,
                      $atlas_orders_path,
                      $test_results,
                      $settings_path
);
commit;

select 
    campaign_id, 
    group_name,
    channel_type,
    status, 
    IF(campaign_id = "1" and status = 'resolved', True, 
        IF(campaign_id in ("2", "3") and status = 'skipped', True,
            IF(campaign_id = "4" and status = 'prestable_analysis', True,
                IF(campaign_id = "5", True, False )
            )
        )
    )
from 
    (select 
        campaign_id,
        group_name,
        channel_type,
        max_by(status, last_status_update) as status
    from 
        $campaign_log_path
    group by 
        campaign_id,
        group_name,
        channel_type   
        );
