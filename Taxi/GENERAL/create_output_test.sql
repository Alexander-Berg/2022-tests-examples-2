use hahn;

PRAGMA Library("create_output.sql");
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

import create_output SYMBOLS $create_output;


$unfitered_path = "temp_unfilteres";
$filtered_path = "temp_filteres";
$prestable_segment_path = "temp_prestable";

--$campaign_log_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_output_campaign_log";
--$output_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/create_output_segments_path_filtered";

$campaign_log_path = "{{campaign_log}}";
$output_path = "{{output_path}}";
$output_banned_path = "{{output_banned_path}}";
$test_results = "{{test_results}}";



INSERT INTO $campaign_log_path WITH TRUNCATE 
select 
    cast(1 as string?) as campaign_id,
    cast('create_outout_sc1_test1' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'resolved' as status,
    cast(False as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_outout_sc1_test1' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL
select 
    cast(2 as string?) as campaign_id,
    cast('create_outout_sc1_test2' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'skipped' as status,
    cast(True as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_outout_sc1_test2' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL 
select 
    cast(3 as string?) as campaign_id,
    cast('create_outout_sc1_test3' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'resolved' as status,
    cast(True as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_outout_sc1_test2' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL 
select 
    cast(4 as string?) as campaign_id,
    cast('create_outout_sc1_test4' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'prestable_analysis' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_outout_sc1_test4' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
UNION ALL 
select 
    cast(5 as string?) as campaign_id,
    cast('create_outout_sc1_test5' as string?) as group_name,
    cast('channel_sc1' as string?) as channel_type,
    'not_filled' as status,
    cast(NULL as bool?) as resolution,
    cast(CurrentUtcDateTime() as Datetime?) as last_status_update,
    cast(CurrentUtcDateTime() as Datetime?) as resolution_time,
    'create_outout_sc1_test5' as reason,
    cast(0 as Int64?) as prestable_test_user_needed,
    cast(0 as Int64?) as prestable_loc_control_user_needed,
    cast(0 as Int64?) as prestable_glob_control_user_needed,
    cast(NULL as Double?) as prestable_exp_segment,
    cast(NULL as Yson?) as details
;


insert into @$unfitered_path WITH TRUNCATE 
    (select 
        cast(1 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_1" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test1" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(1 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_2" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test1" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(2 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_3" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test2" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(2 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_4" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test2" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(3 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_5" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test3" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(3 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_6" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test3" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(4 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_7" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test4" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(4 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_8" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test4" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(5 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_9" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test5" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(5 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("unfiltered_10" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test5" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
;


insert into @$filtered_path WITH TRUNCATE 
    (select 
        cast(-5 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("filtered_1" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test1" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(100 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("filtered_2" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test1" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
;

insert into @$prestable_segment_path WITH TRUNCATE 
    (select 
        cast(4 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("prestable_1" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test4" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('prestable_analysis' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
    UNION ALL 
    (select 
        cast(4 as string?) as campaign_id,
        cast("channel_sc1" as string?) as channel_type,
        cast("prestable_2" as string?) as entity_id,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        cast("create_outout_sc1_test4" as string?) as group_name,
        cast(False as bool) as is_glob_control_prestable,
        cast(False as bool) as is_loc_control_prestable,   
        cast(False as bool) as is_test_prestable,
        cast('prestable_analysis' as string) as status,
        cast(CurrentUtcDateTime() as DateTime) as upd_time
    ) 
;

COMMIT;

DO $create_output(
    $campaign_log_path,
    $unfitered_path,
    $filtered_path,
    $prestable_segment_path,
    $output_path,
    $output_banned_path
);
COMMIT;

$aggs_result = (select 
    campaign_id,
    channel_type,
    group_name,
    resolution,
    status,
    count(o.entity_id) as n_users,
    count(b.entity_id) as n_banned_users
from 
    $campaign_log_path as c 
    full join $output_path as o
    on (c.campaign_id = o.campaign_id
        and c.channel_type = o.channel_type
        and c.group_name = o.group_name)
    full join $output_banned_path as b
    on (c.campaign_id = b.campaign_id
        and c.channel_type = b.channel_type
        and c.group_name = b.group_name)
group by 
    c.campaign_id as campaign_id,
    c.channel_type as channel_type,
    c.group_name as group_name,
    c.resolution as resolution,
    c.status as status
);


INSERT INTO $test_results with truncate
SELECT 
    campaign_id,
    channel_type,
    group_name,
    resolution,
    status,
    n_users,
    IF(
        (
            (n_users > 0) 
            and (n_banned_users = 0)
            and (campaign_id is NULL 
                or resolution = True 
                or (resolution is NULL and status = 'prestable_analysis'))
        ) 
        or ((n_users = 0)
            and (n_banned_users > 0)
            and resolution = False
        ), 
        True, 
        False ) as test_passed
from 
    $aggs_result
;

