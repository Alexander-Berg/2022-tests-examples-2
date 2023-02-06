SELECT toHour(StartTime) AS `ym:s:hour`,
       max(concat(substring(toString(StartTime),12,2),':00')) AS `ym:s:maxHourName`,
       sum(Sign) AS `ym:s:visits`,
       sum((PageViews)*Sign) AS `ym:s:pageviews`,
       uniqExactIf(UserID, UserID != 0) AS `ym:s:users`,
       (sum((IsBounce)*Sign) / sum(Sign) * 100) AS `ym:s:bounceRate`,
       (sum((PageViews)*Sign) / sum(Sign)) AS `ym:s:pageDepth`,
       (sum((Duration)*Sign) / sum(Sign)) AS `ym:s:avgVisitDurationSeconds`,
       (sum(Sign)) / 31 AS `ym:s:visitsPerDay`
FROM visits_layer  SAMPLE 1.0
WHERE ((StartDate >= toDate('2015-01-01')) AND
(StartDate <= toDate('2015-01-31')) AND (CounterID = 101024)) AND
(toHour(StartTime) != -2)  GROUP BY `ym:s:hour`  WITH TOTALS
HAVING sum(Sign) > 0  ORDER BY `ym:s:hour`  LIMIT 0, 50 FORMAT JSONCompact