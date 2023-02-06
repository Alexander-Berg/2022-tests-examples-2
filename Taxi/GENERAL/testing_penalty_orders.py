#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import yt.wrapper as yt
import numpy as np
import os
from copy import copy
import business_models as bm
from business_models import hahn, greenplum
import warnings
warnings.filterwarnings('ignore')

script = '''
USE hahn;
pragma yt.InferSchema;
pragma SimpleColumns;
PRAGMA AnsiInForEmptyOrNullableItemsCollections;
PRAGMA yson.DisableStrict;
pragma yt.StaticPool = 'mishaboroboro';

$parse = DateTime::Parse("%Y-%m-%d %H:%M:%S");
$duration = ($x) -> {Return DateTime::ToSeconds(DateTime::MakeDatetime($parse($x)))};

$start_dt = '2021-10-01 00:00:00';
$start_ts = $duration($start_dt);


$tmp = (
select 
    cargo_cancel_reason
    , guilty
    , created_ts
    , taxi_order_id
    , park_id||'_'||driver_id as dbid_uuid
    , park_id as db_id
    , driver_id as driver_uuid
FROM 
    `//home/taxi/testing/replica/postgres/cargo_orders/performer_order_cancel` as a 
where completed = True
and a.created_ts >= $start_ts
);

$indicator_raw = (
SELECT 
    dbid_uuid
    , taxi_order_id, cargo_cancel_reason, created_ts
    , ROW_NUMBER() OVER w AS row_num
from 
    $tmp 
where 
    1=1
    and (
    (cargo_cancel_reason = 'order_cancel_reason_Pro_force_majeure' and guilty=True) or 
    (cargo_cancel_reason = 'order_cancel_reason_Pro_no_thermobox' and guilty!=True) or 
    (cargo_cancel_reason = 'order_cancel_reason_Pro_long_wait' and guilty=True) or 
    (cargo_cancel_reason = 'order_cancel_reason_Pro_company_closed' and guilty=True)  
    )
WINDOW w AS (PARTITION BY dbid_uuid ORDER BY created_ts)
);

$indicator = (
SELECT  
    dbid_uuid, taxi_order_id, cargo_cancel_reason, created_ts, 300 as penalty
FROM 
    $indicator_raw
where 
    row_num % 3 = 0
);

$always = (
SELECT 
    dbid_uuid, taxi_order_id, cargo_cancel_reason, created_ts, 300 as penalty
from 
    $tmp 
where 
    1=1
    and (
    (cargo_cancel_reason = 'order_cancel_reason_Pro_so_far' and guilty=True) or 
    (cargo_cancel_reason = 'order_cancel_reason_Pro_no_thermobox' and guilty=True) or 
    (cargo_cancel_reason = 'order_cancel_reason_Pro_overweight' and guilty=True) 
    )
);

insert into `//home/taxi-delivery/analytics/dev/mishaboroboro/LOGEFFICIENCY-440/testing-penalty-orders`
with truncate
select 
    a.* 
    , ROW_NUMBER() OVER w AS id
from 
(SELECT a.*
, String::ReplaceAll(substring(cast(DateTime::FromSeconds(cast(a.created_ts as Uint32)) as string),0,19),'T',' ') as created_dttm 
, String::ReplaceAll(substring(cast(DateTime::FromSeconds(cast(a.created_ts as Uint32)) as string),0,19),'T',' ')||'_'||taxi_order_id as created_dttm_taxi_order_id
from $always as a union all
SELECT a.*
, String::ReplaceAll(substring(cast(DateTime::FromSeconds(cast(a.created_ts as Uint32)) as string),0,19),'T',' ') as created_dttm 
, String::ReplaceAll(substring(cast(DateTime::FromSeconds(cast(a.created_ts as Uint32)) as string),0,19),'T',' ')||'_'||taxi_order_id as created_dttm_taxi_order_id
from $indicator as a
) as a 
WINDOW w AS (ORDER BY created_dttm_taxi_order_id)
order by created_dttm_taxi_order_id'''
hahn(script,syntax_version=1.0)
print 1


