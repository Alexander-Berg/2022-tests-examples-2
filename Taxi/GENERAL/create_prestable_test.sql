use hahn;

PRAGMA library('create_prestable.sql');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

IMPORT create_prestable SYMBOLS $create_prestable;
commit;

$unfiltered_segment_path = "temp_unfilteres";
$prestable_segment_path = "temp_prestable";

--$campaign_log_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_prestable_campaign_log";
--$settings_log_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_prestable_settings_log";
--$cmpg_segment_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_prestable_segment_path";
--$cmpg_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_prestable_campaign_path";
--$effeciency_segments_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_prestable_efficiency_segments";



$campaign_log_path = "{{campaign_log}}";
$settings_log_path = "{{settings_log_path}}";
$cmpg_segment_path = "{{cmpg_segment_path}}";
$cmpg_path = "{{cmpg_path}}";
$effeciency_segments_path = "{{effeciency_segments_path}}";
$test_results = "{{test_results}}";

$prestable_size = 100;
$control_part = 0.1;
$global_control_part = 0.05;

INSERT INTO $cmpg_segment_path WITH TRUNCATE
select 1 as id,  $control_part as control
UNION ALL 
select 2 as id,  $control_part as control
UNION ALL 
select 3 as id,  $control_part as control
;


INSERT INTO $campaign_log_path WITH TRUNCATE 
select 
    cast(1 as string?) as campaign_id,
    cast('create_prestable_sc1_test1' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
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

INSERT INTO $settings_log_path WITH TRUNCATE 
select 
    cast(1 as string?) as campaign_id,
    cast('create_prestable_sc1_test1' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'User' as entity_type,
    CurrentUtcDatetime() as upd_time,
    $prestable_size as prestable_size
;

$call_listgen = Python::listgen(Callable<(Int64?, Int64?)->List<Int64?>>, 
@@

def listgen(n_start, n_end):
    return [i for i in range(n_start, n_end)]
    
@@);

INSERT INTO $effeciency_segments_path WITH TRUNCATE 
select 
    campaign_id,
    channel_type,
    cast(user_id as String?) as entity_id,
    entity_type,
    experiment_id,
    group_name,
    if(user_id > $prestable_size*(1.0 + $control_part) and user_id <= $prestable_size*(1.0 + $control_part + $global_control_part), True, False) as is_glob_control_prestable,
    if(user_id <= $prestable_size*(1.0 + $control_part) and user_id >= $prestable_size , True, False) as is_loc_control_prestable,   
    if(user_id < $prestable_size, True, False) as is_test_prestable,
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
        $call_listgen(1, cast($prestable_size*1.15 as Int64) + 1) as user_id)
        FLATTEN LIST BY user_id
;

INSERT INTO @$unfiltered_segment_path with truncate
SELECT  
    campaign_id,
    channel_type,
    cast(user_id as string) as entity_id,
    entity_type,
    experiment_id,
    group_id_id,
    group_name,
    recipient_context,
    segment_id,
    utc_policy_channel_free_datetime
from 
    (select 
        cast(2 as String?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        22 as group_id_id,
        cast("create_prestable_sc1_test2" as string?) as group_name,
        cast(NULL as Json?) as recipient_context,
        2 as segment_id,
        cast(NULL as DateTime?) as utc_policy_channel_free_datetime,
        $call_listgen(cast($prestable_size*(1.0 + $control_part + $global_control_part) as Int64) + 1, 
            cast($prestable_size*(1.0 + $control_part + $global_control_part) as Int64) + 1 + $prestable_size) as user_id)
    FLATTEN LIST BY user_id
UNION ALL
SELECT  
    campaign_id,
    channel_type,
    cast(user_id as string) as entity_id,
    entity_type,
    experiment_id,
    group_id_id,
    group_name,
    recipient_context,
    segment_id,
    utc_policy_channel_free_datetime
from 
    (select 
        cast(3 as String?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        33 as group_id_id,
        cast("create_prestable_sc1_test3" as string?) as group_name,
        cast(NULL as Json?) as recipient_context,
        3 as segment_id,
        cast(NULL as DateTime?) as utc_policy_channel_free_datetime,
        $call_listgen(cast($prestable_size*(1.0 + $control_part + $global_control_part) as Int64) + 1 + $prestable_size, 
            cast($prestable_size*(1.0 + $control_part + $global_control_part) as Int64) + 1 + $prestable_size*100) as user_id)
    FLATTEN LIST BY user_id
;
COMMIT;

DO $create_prestable($unfiltered_segment_path,
                                  $campaign_log_path,
                                  $cmpg_segment_path,
                                  $cmpg_path,
                                  $effeciency_segments_path,
                                  $prestable_segment_path,
                                  $settings_log_path
                                  );
commit;

$prestable_segm = (select 
    campaign_id,
    channel_type, 
    group_name,
    count(distinct entity_id) as p_count
from 
    @$prestable_segment_path
group by
    campaign_id,
    channel_type, 
    group_name)   
;

$eff_segm = (select 
    campaign_id,
    channel_type, 
    group_name,
    count(distinct entity_id) as e_count
from 
    $effeciency_segments_path
group by
    campaign_id,
    channel_type, 
    group_name)   
;

INSERT INTO $test_results WITH TRUNCATE
select 
    c.campaign_id,
    c.channel_type, 
    c.group_name,
    c.status,
    c.resolution,
    IF( ((c.status = 'skipped') and e.e_count is NULL and p.p_count is NULL)
        or (
            c.status = 'prestable_ready' and e.e_count > 0 and p.p_count = ($prestable_size - 1)
        )
        or (
            c.status = 'resolved' and e.e_count > 0 and p.p_count is NULL
        )
        OR (
            c.status = 'not_filled'
        ),
        True, False
    ) as test_result
from 
    $campaign_log_path as c
    left join $eff_segm as e
        on c.campaign_id = e.campaign_id
            and c.channel_type = e.channel_type 
            and c.group_name = e.group_name
    left join $prestable_segm as p
        on c.campaign_id = p.campaign_id
            and c.channel_type = p.channel_type 
            and c.group_name = p.group_name
    ;
