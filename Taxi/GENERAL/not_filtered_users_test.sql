use hahn;

PRAGMA library('not_filtered_users.sql');
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

IMPORT not_filtered_users SYMBOLS $get_unfiltered_users;

--$segment_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/not_filtered_users_segment_path";
--$campaign_log_path = "//home/taxi-crm/srstorozhenko/mvp-test/debug/not_filtered_users_campaign_log";


$segment_path = "{{segment_path}}";
$campaign_log_path = "{{campaign_log}}";
$test_results = "{{test_results}}";

$fitered_path = 'filtered_path';
$unfitered_path = 'unfiltered_path';


$call_listgen = Python::listgen(Callable<(Int64?, Int64?)->List<Int64?>>, 
@@

def listgen(n_start, n_end):
    return [i for i in range(n_start, n_end)]
    
@@);

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

INSERT INTO $segment_path with truncate
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
        $call_listgen(1, 100) as user_id)
    FLATTEN LIST BY user_id
;
commit;

INSERT INTO $segment_path
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
        cast("PUSH" as string?) as channel_type,
        cast("User" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        22 as group_id_id,
        cast("create_prestable_sc1_test3" as string?) as group_name,
        cast(NULL as Json?) as recipient_context,
        2 as segment_id,
        cast(NULL as DateTime?) as utc_policy_channel_free_datetime,
        $call_listgen(100, 300) as user_id)
    FLATTEN LIST BY user_id
;

INSERT INTO $segment_path
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
        cast(4 as String?) as campaign_id,
        cast("PUSH" as string?) as channel_type,
        cast("Driver" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        22 as group_id_id,
        cast("create_prestable_sc1_test4" as string?) as group_name,
        cast(NULL as Json?) as recipient_context,
        2 as segment_id,
        cast(NULL as DateTime?) as utc_policy_channel_free_datetime,
        $call_listgen(300, 600) as user_id)
    FLATTEN LIST BY user_id
;

INSERT INTO $segment_path
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
        cast(5 as String?) as campaign_id,
        cast("channel_sc2" as string?) as channel_type,
        cast("Driver" as string?) as entity_type,
        cast("" as string?) as experiment_id,
        22 as group_id_id,
        cast("create_prestable_sc1_test5" as string?) as group_name,
        cast(NULL as Json?) as recipient_context,
        2 as segment_id,
        cast(NULL as DateTime?) as utc_policy_channel_free_datetime,
        $call_listgen(600, 1000) as user_id)
    FLATTEN LIST BY user_id
;
commit;

DO $get_unfiltered_users($segment_path,
                                  $campaign_log_path,
                                  $fitered_path,
                                  $unfitered_path
                                  );
commit;

$f_agg = (
    select 
        campaign_id,
        channel_type,
        group_name,
        count(distinct entity_id) as f_count
    from 
        @$fitered_path
    group by 
        campaign_id,
        channel_type,
        group_name
);

$u_agg = (
    select 
        campaign_id,
        channel_type,
        group_name,
        count(distinct entity_id) as u_count
    from 
        @$unfitered_path
    group by 
        campaign_id,
        channel_type,
        group_name
);

insert into $test_results with truncate
select 
    c.campaign_id,
    c.channel_type,
    c.group_name,
    c.status,
    c.resolution,
    IF(
        (c.campaign_id = "1" and f.f_count is NULL and u.u_count is NULL)
        or (
            c.campaign_id != "3" and c.campaign_id != "1" and f.f_count is not NULL and u.u_count is NULL
            and status = 'skipped'
        )
        or (
            c.campaign_id = "3" and f.f_count is NULL and u.u_count is not NULL
        ),
        True, False
    ) as test_result
    from 
        $campaign_log_path as c
        full join $u_agg as u 
            on c.campaign_id = u.campaign_id
                and c.channel_type = u.channel_type
                and c.group_name = u.group_name
        full join $f_agg as f
            on c.campaign_id = f.campaign_id
                and c.channel_type = f.channel_type
                and c.group_name = f.group_name
