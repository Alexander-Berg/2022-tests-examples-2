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
use hahn;

/*
Именно такие названия полей
primary_key == должен быть уникальным для каждого штрафа и отсортирован. Порядок записей не должен меняться! Напирмер, {time}_{taxi_order_id}_{fine_id}
fine_id == id из таблицы cancellations
cancel_id
cargo_cancel_reason
park_id
driver_id
taxi_order_id
cargo_order_id
*/

$pre = (
SELECT
    cast(DateTime::FromSeconds(CAST(created_ts as Uint32)) as String)||'_'||taxi_order_id||'_'||cast(id as String) as primary_key
    , id as fine_id
    , cancel_id
    , cargo_cancel_reason
    , park_id
    , driver_id
    , taxi_order_id
    , cargo_order_id
    , created_ts
    , updated_ts
    , 'a' as a 
    , payload
FROM
    `//home/taxi/testing/replica/postgres/cargo_performer_fines/cancellations`
where
    1=1
    and guilty = True
);

$b = (select max(primary_key) as max_primary_key
, 'a' as a  from `//home/taxi/testing/services/cargo-performer-fines/order-fines/performer-fines`);

$pre2 = (
select 
    primary_key
    , fine_id
    , cancel_id
    , cargo_cancel_reason
    , park_id
    , driver_id
    , taxi_order_id
    , cargo_order_id
    , created_ts
    , updated_ts
    , payload
    , a.a as a
FROM 
    $pre as a 
    inner join $b as b 
        on a.a = b.a 
where 
    1=1
    and a.primary_key > b.max_primary_key
);

insert into `//home/taxi/testing/services/cargo-performer-fines/order-fines/performer-fines`
select 
    *
FROM (
select
    a.*
FROM
    $pre2 as a 
    left join `//home/taxi/testing/services/cargo-performer-fines/order-fines/performer-fines` as b  
        on a.primary_key = b.primary_key
WHERE 
    b.primary_key is null 
)
order by primary_key
    '''
hahn(script, syntax_version=1.0)
print (1)
