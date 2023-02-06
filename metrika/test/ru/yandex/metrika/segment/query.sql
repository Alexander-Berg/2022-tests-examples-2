-- функции
$toDate = ($s) -> { return DateTime::ToDays(cast($s as date))};
-- колонки
$StartDate = DateTime::ToDays(DateTime::TimestampFromSeconds(Coalesce(StartTime,Uint32("0"))));
-- атрибуты
$isNewUser = IF($StartDate > $toDate("2014-12-03"), FirstVisit == StartTime, (FirstVisit / 1800) == (StartTime / 1800));
$trafficSource = coalesce(TraficSourceID, 0);
$expr = "(ym:s:isNewUser=='Yes')";


select UserID,StartTime, AsList(1000000002, 1000000005), AsList($isNewUser=true, $trafficSource=3)
from hahn.[logs/visit-v2-log/30min/2018-08-16T00:00:00]
where LayerID = 1 and CounterID=34
limit 10;