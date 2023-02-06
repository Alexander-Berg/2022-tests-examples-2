# coding: utf-8
from mylib import hahn, send_mail
import pandas as pd
import StringIO
import pymongo
import requests
from datetime import datetime, timedelta
import os

hahn.base_path = 'home/taxi-analytics/iafilimonov/{}'

query_0 = '''
use hahn;

$this_week_start = DateTime::ToDate(DateTime::StartOfWeek(YQL::Now()));
$last_week_start = DateTime::ToDate(DateTime::StartOfWeek(YQL::Now()) - DateTime::FromDays(7));
$last_week_end = DateTime::ToDate(DateTime::StartOfWeek(YQL::Now()) - DateTime::FromDays(1));
$last_month = substring(DateTime::ToDate(DateTime::StartOfMonth(YQL::Now() - DateTime::FromDays(30))), 0, 7);
-- $this_month = Substring($this_week,0,7);
-- $week_before_month = Substring($one_week_before,0,7);

$python_script = @@
import json
from datetime import datetime
def has_contract(contracts_json):
    if contracts_json is not None and contracts_json <> '':
        contracts = json.loads(contracts_json)
        now_date = datetime.utcnow() 
        if contracts is not None:
            for c in contracts:
                if 'begin' in c and 'end' in c:
                    if (c.get('is_active', False) is True and
                        datetime.strptime(c['begin'][:10], '%Y-%m-%d') <= now_date and
                        datetime.strptime(c['end'][:10], '%Y-%m-%d') >= now_date):
                        return True
    return False
    
def has_vats(vats_json):
    if vats_json is not None and vats_json <> '':
        vats = json.loads(vats_json)
        now_date = datetime.utcnow() 
        if vats is not None:
            for v in vats:
                if len(v) >= 2:
                    date_A = datetime.strptime(v[0][:10], '%Y-%m-%d')
                    date_B = datetime.strptime(v[1][:10], '%Y-%m-%d') if v[1] is not None else datetime(9999, 1, 1)
                    if (date_A <= now_date and
                        date_B >= now_date):
                        return True
    return False    
@@;

$has_contract = Python::has_contract("(String?)->Bool?", $python_script);

$has_vats = Python::has_vats("(String?)->Bool?", $python_script);

$park_req_yson = Yson::Parse(p.[requirements]);

$park_reqs = Yson::ConvertToStringDict($park_req_yson);

$parks = (
select 
    p.id as id,
    p.city as city,
    p.name as name,
    COALESCE($park_reqs{'corp'}, "False") as corp_req,
    p.[account.corporate_contracts] as contract,
    $has_contract(p.[account.corporate_contracts]) as has_contract,
    p.corp_vats as corp_vats,
    $has_vats(p.[corp_vats]) as has_vats
from 
    [home/taxi-dwh/stg/mdb/parks/parks] as p
);

$countries = (
SELECT distinct
    city,
    country
from
    range([home/taxi-dwh/summary/dm_order],$last_month)
where
    utc_order_dt between $last_week_start and $last_week_end
);


$nodrivers = (
select 
    id,
    Yson::ConvertToInt64(doc.active_drivers_count) as active_drivers
from 
    [home/taxi-dwh/raw/mdb/parks/parks]
);

$orders_by_parks = (
SELECT 
    park_city,
    p.id as id,
    p.name as name,
    p.corp_req as corp_req,
    p.contract as contract,
    p.has_contract as has_contract,
    p.corp_vats as corp_vats,
    p.has_vats as has_vats,
    o.city as city,
    active_drivers,
    country,
    count(o.id) as cnt_orders
FROM 
    RANGE([home/taxi-dwh/stg/mdb/orders], $last_week_start, $last_week_end) as o
inner join 
    $parks as p 
on
    o.[performer.clid] = p.id 
left join
    $countries as c
on 
    o.city = c.city
left join 
    $nodrivers as nd
on 
    p.id = nd.id
where
    o.[status] = 'finished'
    and o.[taxi_status] = 'complete'
group by 
    p.city as park_city, 
    p.name, 
    p.has_contract as has_contract, 
    p.corp_req, 
    p.has_vats, 
    p.id, 
    p.contract, 
    p.corp_vats, 
    o.city,
    c.country as country,
    nd.active_drivers ?? 0 as active_drivers
);

$orders_by_cities = (
select
    city,
    sum(cnt_orders) as cnt_orders 
from 
    $orders_by_parks
group by
    city
);


insert into [//home/taxi-analytics/iafilimonov/corp/monitoring_last_week_new]
with truncate
select 
    p.park_city as Park_city,
    p.city as City,
    p.country as Country,
    p.name as Park,
    p.id as Clid,
    p.corp_req as Corp_req,
    p.contract as contract,
    p.has_contract as Has_contract,
    p.active_drivers as Active_drivers,
    --p.corp_vats,
    p.has_vats as Has_vats,
    p.cnt_orders as Park_orders,
    c.cnt_orders as City_orders,
    al.corp ?? False as corp_allowed,
    100*(cast(p.cnt_orders as double)/c.cnt_orders) as Park_orders_share
from 
    $orders_by_parks as p
inner join 
    $orders_by_cities as c 
on
    p.city = c.city
left join 
    (select 
        city_id,
        max(corp) as corp 
    from 
        [//home/taxi-analytics/iafilimonov/corp_allow]
    group by 
        city_id) as al 
    on
        p.city = al.city_id
order by 
    Clid
;
commit;

'''
hahn(query_0)




query_1 = '''
use hahn;

$monitoring = (
select 
    * 
from
    [//home/taxi-analytics/iafilimonov/corp/monitoring_last_week_new]
);


-- corp parks share
$part2 = (
select
    sum(Park_orders_share) as Park_orders_share,
    some(City_orders) as City_orders,
    Country,
    City
from 
    $monitoring
where
    Has_contract == true
    and Corp_req == 'True'
    --and Country == 'Россия'
group by 
    City,
    Country
);


-- corp orders are not allowed
$part3 = (
select
    City,
    Country,
    Park_city,
    Park,
    Park_orders_share,
    Active_drivers,
    Clid--,
    --Park_contract_id
from 
    $monitoring
where
    Has_contract == true
    and Corp_req == 'False'
    --and Country == 'Россия'
);

-- parks with no contracts
$part4 = (
select
    City,
    Country,
    Park_city,
    Park,
    Park_orders_share,
    City_orders,
    Clid,
    Active_drivers,
    --Park_contract_id,
    Corp_req
from 
    $monitoring
where
    Has_contract == false
    --and Country == 'Россия'

);


insert into [//home/taxi-analytics/iafilimonov/corp/monitoring_part2]
with truncate
select * from $part2
order by
    Park_orders_share
;
commit;

insert into [//home/taxi-analytics/iafilimonov/corp/monitoring_part3]
with truncate
select * from $part3
order by
    Park_orders_share desc
;
commit;

insert into [//home/taxi-analytics/iafilimonov/corp/monitoring_part4]
with truncate
select * from $part4
order by
    Park_orders_share desc
;
commit;

'''

hahn(query_1) 


for country, country_rus in zip(['rus', 'kaz', 'arm'],['Россия', 'Казахстан', 'Армения']):

    hahn('''
    use hahn;
    insert into [home/taxi-analytics/iafilimonov/corp/monitoring_part2_{country}]
    with truncate
    select * from [home/taxi-analytics/iafilimonov/corp/monitoring_part2]
    where Country = '{country_rus}'
    ;
    commit;

    insert into [home/taxi-analytics/iafilimonov/corp/monitoring_part3_{country}]
    with truncate
    select * from [home/taxi-analytics/iafilimonov/corp/monitoring_part3]
    where Country = '{country_rus}'
    ;
    commit;

    insert into [home/taxi-analytics/iafilimonov/corp/monitoring_part4_{country}]
    with truncate
    select * from [home/taxi-analytics/iafilimonov/corp/monitoring_part4]
    where Country = '{country_rus}'
    ;
    commit;
'''.format(country = country, country_rus = country_rus))
    
    
    
    
    
    
    df2 = hahn.load_result(full_path = 'home/taxi-analytics/iafilimonov/corp/monitoring_part2_' + country)

    df3 = hahn.load_result(full_path = 'home/taxi-analytics/iafilimonov/corp/monitoring_part3_' + country)
    #df3 = df3[['City', 'Country', 'Clid', 'Park', 'Park_city', 'Park_orders_share']]
    if len(df3)>0:
        df3.Park = df3.Park.apply(lambda x: x.replace(u'\ufeff'.encode('utf-8'),''))

    df4 = hahn.load_result(full_path = 'home/taxi-analytics/iafilimonov/corp/monitoring_part4_' + country)
    #df4 = df4[['City', 'Country','City_orders', 'Clid', 'Corp_req', 'Park', 'Park_city', 'Park_orders_share']]
    if len(df4) > 0:
        df4.Park = df4.Park.apply(lambda x: x.replace(u'\ufeff'.encode('utf-8'),''))






    # sending mails 
    today = str(datetime.strftime(datetime.now(), '%Y-%m-%d')).replace('-','_')

    filename2 = 'corp_share_' + today + '.csv'
    filename3 = 'corp_switched_off_' + today + '.csv'
    filename4 = 'corp_no_contract_' + today + '.csv'
    
    df2.to_csv(filename2, encoding = 'CP1251', sep=';', header = True)
    df3.to_csv(filename3, encoding = 'CP1251', sep=';', header = True)
    df4.to_csv(filename4, encoding = 'CP1251', sep=';', header = True)
    
    subj = 'final test Еженедельная выгрузка доли корпоративного вывоза, ' + country_rus
    text = '''Коллеги! Во вложении еженеденльая выгрузка по корпоративным заказам.
    '''
    addresses = ['ilosk@yandex-team.ru', 'iafilimonov@yandex-team.ru', 'zakharovr@yandex-team.ru']
    send_mail(
        'iafilimonov@yandex-team.ru',
        #[u'iafilimonov@yandex-team.ru'],
        addresses,
        subject=subj,
        text=text,
        files=[filename2,filename3,filename4]
    )
    os.remove(filename2)
    os.remove(filename3)
    os.remove(filename4)
    


