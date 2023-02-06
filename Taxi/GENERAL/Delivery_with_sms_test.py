# coding: utf-8
from business_models.databases import hahn, gdocs

hahn.change_token('robot_ufc_analyst_yt_token')

script = """
USE hahn;

pragma yson.DisableStrict;

$script = @@
import datetime as dt

replace_rules = (
    {'en': 'A', 'ru': u'А'},
    {'en': 'B', 'ru': u'В'},
    {'en': 'E', 'ru': u'Е'},
    {'en': 'K', 'ru': u'К'},
    {'en': 'M', 'ru': u'М'},
    {'en': 'H', 'ru': u'Н'},
    {'en': 'O', 'ru': u'О'},
    {'en': 'P', 'ru': u'Р'},
    {'en': 'C', 'ru': u'С'},
    {'en': 'T', 'ru': u'Т'},
    {'en': 'Y', 'ru': u'У'},
    {'en': 'X', 'ru': u'Х'},
)

def transliterate_by_view(s, from_lang='ru', to_lang='en'):
    if not s:
        return None
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    for rule in replace_rules:
        s = s.replace(rule[from_lang], rule[to_lang])
    return s
@@;

$render_car_number = Python2::transliterate_by_view(ParseType("(String?)->String?"), $script);
$normalizer = ($x) -> {Return $render_car_number(String::RemoveAll(String::ReplaceAll(String::ToUpper($x), ' ', ''), "-"))};

$drivers =
Select 
    $normalizer(Yson::ConvertToString(doc.license)) as DL,
    String::ReplaceAll(SUBSTRING(Yson::ConvertToString(doc.created_at), 0, 19), "T", " ") as exam_dttm,
From 
    `//home/taxi-dwh/raw/education/online_sessions/online_sessions`
WHere 1=1
    and Yson::ConvertToString(doc.program) = "Тарифы «Доставка» и «Курьер»: подтверждение через СМС-коды"
    and Yson::ConvertToInt64(doc.grade) = 5
;

-- $cities = 
-- Select 
--     driver_license,
--     max_by(city, local_order_dttm) as last_order_city
-- From range(`//home/taxi-dwh/summary/dm_order`, `2019-05`)
-- Group by driver_license_normalized as driver_license
-- ;

$cities = 
Select 
    driver_license,
    max_by(name_ru, local_order_dttm) as last_order_city
From range(`//home/taxi-dwh/summary/dm_order`, `2019-05`) as t1
Left join `//home/taxi-dwh/cdm/geo/v_dim_op_geo_hierarchy/v_dim_op_geo_hierarchy` as t2
using (tariff_zone)
Where node_type = 'agglomeration'
Group by driver_license_normalized as driver_license
;

$driver_info = 
Select
    driver_license,
    some(driver_name) as driver_name,
    String::JoinFromList(agg_list_distinct(driver_phone, 3), ", ") as driver_phones
From `//home/taxi-dwh/dds/dim_driver` as t1
Where 1=1
Group by driver_license_normalized as driver_license
;

INSERT INTO `//home/taxi-analytics/litvinov-mike/Delivery/Delivery_with_sms_test_completion`
WITH TRUNCATE
Select
    DL as driver_license,
    exam_dttm,
    driver_name,
    driver_phones,
    last_order_city ?? "No trips last year" as last_order_city,
From $drivers as t1
left join $cities as t2 on t1.DL = t2.driver_license
Left join $driver_info as t3 on t1.DL = t3.driver_license
"""

hahn(script)

table_name = "//home/taxi-analytics/litvinov-mike/Delivery/\
Delivery_with_sms_test_completion"

df = hahn.read(table_name=table_name)

df['driver_phones'] = df['driver_phones'].apply(
    lambda x: "'" + str(x))

df = df.sort_values('exam_dttm').reset_index(drop=True)

sheet_id = '1nehPZOoK6SQcz6WuhXGLCL8vTOMHGhAMXw5xWRsNVPI'

gdocs.write(
    table_name="drivers",
    sheet_id=sheet_id,
    dataframe=df)

print("ok")
